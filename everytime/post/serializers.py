from rest_framework import serializers, exceptions
from .models import Post, Tag
from board.models import Board

class PostSerializer(serializers.ModelSerializer):
    board = serializers.StringRelatedField(read_only=True)
    writer = serializers.StringRelatedField(read_only=True)
    title = serializers.CharField(required=False, max_length=100)
    content = serializers.CharField()
    image = serializers.ImageField(required=False)
    is_anonymous = serializers.BooleanField(default=False)
    is_question = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = (
            'board',
            'writer',
            'title',
            'content',
            'image',
            'is_anonymous',
            'is_question',
        )

    def validate(self, data):
        user = self.context['request'].user
        board = self.context['request'].query_params['board']
        board = Board.objects.get(title=board)
        data['writer'] = user
        data['board'] = board
        return data

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        return post