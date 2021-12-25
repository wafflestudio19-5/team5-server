from django.shortcuts import render, get_object_or_404

from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.paginator import Paginator

from comment.models import Comment
from comment.serializers import CommentSerializer
from .models import Post, Tag
from board.models import Board
from .serializers import PostSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from everytime.utils import ViewSetActionPermissionMixin

# request.data안에 새로운 Tag를 찾아서 데이터베이스에 저장
def create_tag(data):
    if 'tags' in data:
        all_tag = Tag.objects.all()
        for tag_name in data.getlist('tags'):
            tag_name = tag_name.upper()
            if not all_tag.filter(name__iexact=tag_name).exists():
                Tag.objects.create(name=tag_name)

def delete_tag(tags):
    for tag in tags:
        if tag.posttag_set.count() == 0:
            tag.delete()


class PostViewSet(ViewSetActionPermissionMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    permission_action_classes = {
        'retrieve': (permissions.AllowAny, ),
        'list': (permissions.AllowAny, ),
        'comment': (permissions.AllowAny, )
    }
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def create(self, request):
        data = request.data.copy()

        create_tag(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('board', openapi.IN_QUERY,description="게시판 ID",type=openapi.TYPE_STRING)])
    #swagger에 쿼리 파라미터는 자동으로 적용이 안되므로, 따로 추가하기.
    #파라미터 이름, 어떤 부분에 속하는지(QUERY, BODY, PATH 등), 파라미터 설명, 어떤 타입인지를 생성자에 제공
    def list(self, request):
        board = request.query_params.get('board')
        queryset = self.get_queryset().filter(board=board).all()
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page,many=True).data
        return self.get_paginated_response(data)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        tags = list(post.tags.all())

        data = request.data
        user = request.user

        create_tag(data)
        if post.writer_id is not user.id:
            raise exceptions.AuthenticationFailed('글 작성자가 아니므로 글을 수정할 수 없습니다.')

        serializer = self.get_serializer(post, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        delete_tag(tags)
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        tags = list(post.tags.all())  # 이렇게 하지 않으면 post.delete() 이후에 tags도 비어있게 됨.
        for image in post.postimage_set.all():
            image.delete()
        post.delete()
        delete_tag(tags)
        return Response("%s번 게시글이 삭제되었습니다." % pk, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'GET'],
    )
    def comment(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        data = request.data
        if request.method == 'POST':
            if user.id is None:
                return Response('댓글을 작성하려면 로그인을 하십시오.', status.HTTP_400_BAD_REQUEST)
            head_comment_id = data.get('head_comment', None)
            head_comment = get_object_or_404(Comment, id=head_comment_id) if head_comment_id else None
            if head_comment is not None and head_comment.head_comment is not None:
                return Response('답글에 답글을 달 수 없습니다.', status.HTTP_400_BAD_REQUEST)
            serializer = CommentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save()

            comment.post = post
            comment.writer = user
            comment.head_comment = head_comment
            comment.save()
            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['DELETE'],
        url_path='comment/(?P<comment_id>[^/.]+)'
    )
    def destroy_comment(self, request, pk=None, comment_id=-1):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.writer != user:
            return Response('작성자가 아닙니다.', status.HTTP_400_BAD_REQUEST)
        if comment.head_comment is not None:                # 지울려는 댓글이 대댓글인 경우 -> 댓글 삭제
            comment.delete()
            if not comment.head_comment.tail_comments.exists() \
                    and comment.head_comment.is_deleted:    # head comment가 삭제되었고 답글도 모두 지워진 경우 -> head comment 삭제
                comment.head_comment.delete()
        elif not comment.tail_comments.exists():            # 지울려는 댓글에 답글이 달리지 않은 경우 -> 댓글 삭제
            comment.delete()
        else:                                               # 지울려는 댓글이 대댓글이 아닌 경우 -> is_deleted = True
            comment.is_deleted = True
            comment.content = '삭제된 댓글입니다.'
            comment.save()
        comments = Comment.objects.filter(post=post, head_comment=None).all()
        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)