from rest_framework import serializers, exceptions

from post.models import Post
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    replys = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'content',
            'replys',
            'created_at',
            'num_of_likes',
            'is_anonymous',
            'is_deleted',
        )
        read_only_fields = ['writer', 'created_at', 'num_of_likes', 'is_deleted']

    def get_replys(self, comment):
        tail_comments = comment.tail_comments.all()
        return ReplySerializer(tail_comments, many=True).data

    def create(self, validated_data):

        # Comment API를 Post API의 하위 API로 만들지 않으면 아래와 같은 처리를 post, writer, head_comment에 해줘야할 것
        # request = self.context['request']
        # try:
        #     post = request.query_params['post']
        #     post = Post.objects.get(id=post)
        #     validated_data['post'] = post
        # except:
        #     raise serializers.ValidationError("post를 query parameter로 입력해주세요")

        # Post API의 하위 API로 만든다면 post, writer, head_comment 등은 view에서 다 처리하므로 일단은 아래로도 충분한듯 (충분한가,,?)
        # content랑 is_anonymous만 일단 validate
        comment = Comment.objects.create(**validated_data)
        return comment

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'content',
            'created_at',
            'num_of_likes',
            'is_anonymous',
            'is_deleted'
        )