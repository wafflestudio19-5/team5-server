from rest_framework import serializers, exceptions
from rest_framework.utils import model_meta
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
            'images',
            'is_anonymous',
            'is_question',
        )
    
    def get_images(self, obj):
        image = obj.postimage_set.all()
        return PostImageSerializer(instance=image, many=True).data

    def validate(self, data):
        user = self.context['request'].user
        try:
            board = self.context['request'].query_params['board']
        except:
            raise serializers.ValidationError("board를 query parameter로 입력해주세요")
        board = Board.objects.get(id=board)
        data['writer'] = user
        data['board'] = board
        return data
    
    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            PostImage.objects.create(post=post, image=image_data)
        return post

    def update(self, post, validated_data):
        PostImage.objects.filter(post=post).delete()
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            PostImage.objects.create(post=post, image=image_data)

        info = model_meta.get_field_info(post)
        m2m_fields = []

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(post, attr, value)

        post.save()

        for attr, value in m2m_fields:
            field = getattr(post, attr)
            field.set(value)

        return post
