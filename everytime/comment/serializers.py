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
        if comment.is_anonymous:
            if comment.writer == comment.post.writer:
                nickname = '익명(글쓴이)'
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

