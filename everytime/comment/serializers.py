from rest_framework import serializers, exceptions

from post.models import Post, UserPost
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)
    is_anonymous = serializers.BooleanField(default=False)
    replys = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'nickname',
            'content',
            'created_at',
            'user_type',
            'head_comment',
            'num_of_likes',
            'is_anonymous',
            'is_deleted',
            'is_mine',
            'replys',
        )
        read_only_fields = ['nickname', 'created_at', 'num_of_likes', 'is_deleted']

    def get_replys(self, comment):
        tail_comments = comment.tail_comments.all()
        return ReplySerializer(tail_comments, many=True, context={'post': self.context['post'], 'user': self.context['user']}).data

    def get_writer(self, comment):
        if comment.is_anonymous:
            return 0
        if comment.writer is None:
            return None
        return comment.writer.id

    def get_is_mine(self, comment):
        if comment.writer == self.context['user']:
            return True
        return False

    def get_user_type(self, comment):
        if comment.writer == comment.post.writer:
            return '글쓴이'
        return ''

    def get_nickname(self, comment):
        if comment.writer is None:
            return None
        if comment.is_anonymous:
            if comment.writer == comment.post.writer:
                return '익명(글쓴이)'
            return comment.writer.userpost_set.get(post=comment.post).anonymous_nickname
        return comment.writer.nickname

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
        user = comment.writer
        post = comment.post
        if comment.is_anonymous and user != post.writer:
            userpost, created = UserPost.objects.get_or_create(user=user, post=post)
            if userpost.anonymous_nickname is None:
                userpost.anonymous_nickname = f'익명{post.anonymous_comment_num}'
                userpost.save()
                post.anonymous_comment_num += 1
                post.save()


        return comment



class ReplySerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'nickname',
            'content',
            'created_at',
            'user_type',
            'num_of_likes',
            'is_anonymous',
            'is_deleted',
            'is_mine',
        )

    def get_writer(self, comment):
        if comment.is_anonymous:
            return 0
        if comment.writer is None:
            return None
        return comment.writer.id

    def get_is_mine(self, comment):
        if comment.writer == self.context['user']:
            return True
        return False

    def get_user_type(self, comment):
        if comment.writer == comment.post.writer:
            return '글쓴이'
        return ''

    def get_nickname(self, comment):
        if comment.writer is None:
            return None
        if comment.is_anonymous:
            if comment.writer == comment.post.writer:
                return '익명(글쓴이)'
            return comment.writer.userpost_set.get(post=comment.post).anonymous_nickname
        return comment.writer.nickname
