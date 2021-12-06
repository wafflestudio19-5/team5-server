from rest_framework import serializers

from .models import Post, Tag

class PostSerializer(serializers.ModelSerializer):
    board = serializers.StringRelatedField(read_only=True)
    writer = serializers.StringRelatedField(read_only=True)
    title = serializers.CharField(required=False, max_length=100)
    content = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    tags = serializers.ManyRelatedField(read_only=True)
    is_anonymous = serializers.BooleanField(required=True)
    is_question = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = {
            'board',
            'writer',
            'title',
            'content',
            'image',
            'tags',
            'is_anonymous',
            'is_question'
        }

    def valide(self, data):
        return data

    def create(self, validated_data):
        post = Post.objects.create(validated_data)
        return post