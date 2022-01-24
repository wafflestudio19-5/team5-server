from rest_framework import serializers
from .models import Post, Tag, PostImage, PostTag
from board.models import Board
from everytime.exceptions import FieldError, NotFound


class PostImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PostImage
        fields = ['image']


class PostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    board = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    title = serializers.CharField(required=False, max_length=100)
    content = serializers.CharField()
    num_of_comments = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    images = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    is_anonymous = serializers.BooleanField(default=False)
    is_question = serializers.BooleanField(default=False)
    profile_picture = serializers.SerializerMethodField()
    thumbnail_picture = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'board',
            'writer',
            'profile_picture',
            'thumbnail_picture',
            'title',
            'content',
            'num_of_likes',
            'num_of_scrap',
            'num_of_comments',
            'tags',
            'images',
            'is_mine',
            'is_anonymous',
            'is_question',
            'created_at',
        )
        read_only_fields = ['id', 'board', 'writer', 'is_mine', 'created_at', 'num_of_likes', 'num_of_scrap', 'num_of_comments']

    def get_board(self, obj):
        if obj.board.head_board is None:
            return {
                'id': obj.board.id,
                'title': obj.board.title
            }
        else:
            return {
                'id': obj.board.head_board.id,
                'title': obj.board.head_board.title
            }

    def get_writer(self, post):
        if post.writer is None:
            return None
        if post.is_anonymous:
            return '익명'
        return post.writer.nickname

    def get_images(self, obj):
        image = obj.postimage_set.all()
        return PostImageSerializer(instance=image, many=True).data

    def get_num_of_comments(self, obj):
        return obj.comment_set.count()

    def get_is_mine(self, obj):
        if obj.writer == self.context['request'].user:
            return True
        return False

    def get_profile_picture(self, obj):
        if obj.writer and not obj.is_anonymous:
            return obj.writer.profile_picture.url
        return "https://t5backendbucket.s3.ap-northeast-2.amazonaws.com/media/images/profile/default.png"

    def get_thumbnail_picture(self, obj):
        if obj.postimage_set.all():
            return obj.postimage_set.all()[0].image.url
        return None

    def validate(self, data):
        request = self.context['request']

        user = request.user
        data['writer'] = user

        tags = []
        if hasattr(request.data, 'getlist'):
            for tag in request.data.getlist('tags'):
                tags.append(Tag.objects.get(name__iexact=tag))
        if len(tags) != 0:
            data['tags']=tags

        return data
    
    def create(self, validated_data):
        request = self.context['request']

        # board 검증
        board = request.query_params.get('board')
        if board is None:
            raise FieldError("board를 query parameter로 입력해주세요.")

        try:
            board = Board.objects.get(id=board)
            validated_data['board'] = board
        except Board.DoesNotExist:
            raise NotFound("존재하지 않는 게시판입니다. board를 확인해주세요.")

        # tags 따로 저장하기
        tags = validated_data.pop('tags') if 'tags' in validated_data else None

        # 게시글 생성
        try:
            post = Post.objects.create(**validated_data)
        except TypeError:
            raise FieldError('올바르지 않은 타입을 입력하셨습니다.')

        # 게시글과 태그 연결
        if tags is not None:
            for tag in tags:
                PostTag.objects.create(post=post, tag=tag)

        # 이미지 저장 및 업로드
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            PostImage.objects.create(post=post, image=image_data)

        return post

    def update(self, post, validated_data):
        # 기존 이미지 삭제 후 교체 -> 근데 변경된 이미지만 부분적으로 바꾸거나 추가하는 방법이 있을까?
        image_set = self.context['request'].FILES
        for existing_image in post.postimage_set.all():
            existing_image.delete()
        for image_data in image_set.getlist('image'):
            PostImage.objects.create(post=post, image=image_data)

        # 기존 태그에서 사라진 부분은 제거 후 새로 생긴 태그 추가
        new_tags = validated_data.pop('tags') if 'tags' in validated_data else None
        if new_tags is not None:
            post.posttag_set.exclude(tag__in=[tag.name for tag in new_tags]).delete()
            past_tags = post.tags.all()
            for tag in new_tags:
                if tag not in past_tags:
                    PostTag.objects.create(post=post, tag=tag)
        else: # new_tags is None
            post.posttag_set.all().delete()

        # 입력된 값들에 한해서 기존 게시글 수정 (e.g. title key가 없으면 제목은 수정 안 함)
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        post.save()

        return post


class LiveTopSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField()
    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'board',
            'title',
            'content',
            'num_of_likes',
            'num_of_comments'
        )

    def get_board(self, obj):
        if obj.board.head_board is None:
            return {
                'id': obj.board.id,
                'title': obj.board.title
            }
        else:
            return {
                'id': obj.board.head_board.id,
                'title': obj.board.head_board.title
            }

    def get_num_of_comments(self, obj):
        return obj.comment_set.count()


class HotSerializer(serializers.ModelSerializer):
    title_content = serializers.SerializerMethodField()
    board = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'board',
            'title_content',
            'created_at'
        )

    def get_board(self, obj):
        if obj.board.head_board is None:
            return {
                'id': obj.board.id,
                'title': obj.board.title
            }
        else:
            return {
                'id': obj.board.head_board.id,
                'title': obj.board.head_board.title
            }

    def get_title_content(self, post):
        return post.title + ' ' + post.content

class TitleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'created_at'
        )

class ContentListSerializer(serializers.ModelSerializer):
    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'content',
            'created_at',
            'num_of_likes',
            'num_of_comments'
        )

    def get_num_of_comments(self, obj):
        return obj.comment_set.count()
