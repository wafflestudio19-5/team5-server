from rest_framework import serializers, exceptions
from .models import Post, Tag, PostImage
from board.models import Board


class PostImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PostImage
        fields = ['image']


class PostSerializer(serializers.ModelSerializer):
    board = serializers.StringRelatedField(read_only=True)
    writer = serializers.StringRelatedField(read_only=True)
    title = serializers.CharField(required=False, max_length=100)
    content = serializers.CharField()
    images = serializers.SerializerMethodField()
    is_anonymous = serializers.BooleanField(default=False)
    is_question = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = (
            'board',
            'writer',
            'title',
            'content',
            'tags',
            'images',
            'is_anonymous',
            'is_question',
        )
    
    def get_images(self, obj):
        image = obj.postimage_set.all()
        return PostImageSerializer(instance=image, many=True).data

    def validate(self, data):
        request = self.context['request']
        user = request.user

        try:
            board =request.query_params['board']
        except:
            raise serializers.ValidationError("board를 query parameter로 입력해주세요")
        board = Board.objects.get(id=board)

        data['writer'] = user
        data['board'] = board
        return data
    
    def create(self, validated_data):
        # tags 따로 저장하기
        tags = validated_data.pop('tags') if 'tags' in validated_data else None

        # 게시글 생성
        try:
            post = Post.objects.create(**validated_data)
        except TypeError:
            raise exceptions.ValidationError('올바르지 않은 타입을 입력하셨습니다.')

        # 게시글과 태그 연결
        if tags is not None:
            for tag in tags:
                post.tags.add(tag)

        # 이미지 저장 및 업로드
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            PostImage.objects.create(post=post, image=image_data)

        return post

    def update(self, post, validated_data):
        # 기존 이미지 삭제 후 교체 -> 근데 변경된 이미지만 부분적으로 바꾸거나 추가하는 방법이 있을까?
        image_set = self.context['request'].FILES
        if image_set is not None:
            PostImage.objects.filter(post=post).delete()
            for image_data in image_set.getlist('image'):
                PostImage.objects.create(post=post, image=image_data)

        # 기존 태그에서 사라진 부분은 제거 후 새로 생긴 태그 추가
        new_tags = validated_data.pop('tags') if 'tags' in validated_data else None
        if new_tags is not None:
            post.tags.exclude(tag__in=[tag.tag for tag in new_tags]).delete()
            past_tags = post.tags.all()
            for tag in new_tags:
                if tag not in past_tags:
                    post.tags.add(tag)

        # 입력된 값들에 한해서 기존 게시글 수정 (e.g. title key가 없으면 제목은 수정 안 함)
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        post.save()

        return post
