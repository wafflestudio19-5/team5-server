from rest_framework import serializers, exceptions

from post.models import Post
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)
    is_anonymous = serializers.BooleanField(default=False)
    replys = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'nickname',
            'content',
            'created_at',
            'num_of_likes',
            'is_anonymous',
            'is_deleted',
            'replys',
        )
        read_only_fields = ['created_at', 'num_of_likes', 'is_deleted']

    def get_replys(self, comment):
        tail_comments = comment.tail_comments.all()
        return ReplySerializer(tail_comments, many=True).data

    def validate(self, data):
        data['writer'] = self.context['user']
        data['post'] = self.context['post']

        head_comment = data.get('head_comment')
        post = data.get('post')
        if head_comment is not None and head_comment.head_comment is not None:
            raise serializers.ValidationError('답글에 답글을 달 수 없습니다.')
        if head_comment and post != head_comment.post:
            raise serializers.ValidationError('대댓글은 댓글과 서로 다른 게시글을 가져서는 안된다!')
        return data

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        current_comment = comment.id
        comment_set = comment.post.comment_set  # 지금 작성한 댓글이 쓰인 게시글의 모든 댓글 set, 지금 작성한 댓글도 포함되어 있을것
        if comment.is_anonymous:
            if comment.writer == comment.post.writer:
                nickname = '익명(글쓴이)'
                comment.nickname = nickname
            # 댓글 작성자가 이전에 이미 익명으로 그 글에 댓글을 작성했었을때
            elif comment_set.filter(is_anonymous=True, writer=comment.writer).exclude(id=current_comment).exists():
                nickname = comment_set.filter(is_anonymous=True, writer=comment.writer).exclude(id=current_comment)[0].nickname
                comment.nickname = nickname
            else:
                nickname = f'익명{comment.post.anonymous_comment_num}'
                comment.nickname = nickname
                comment.post.anonymous_comment_num += 1
                comment.post.save()
        else:
            comment.nickname = str(comment.writer)

        comment.save()
        return comment


class ReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            'id',
            'nickname',
            'content',
            'created_at',
            'num_of_likes',
            'is_anonymous',
            'is_deleted',
        )

