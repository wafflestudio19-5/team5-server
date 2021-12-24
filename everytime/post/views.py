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


class PostViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
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

    @action(detail=True, methods=['POST', 'GET', 'DELETE'])
    def comment(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        data = request.data
        if request.method == 'POST':
            head_comment_id = data.get('head_comment', None)
            head_comment = get_object_or_404(Comment, id=head_comment_id) if head_comment_id else None
            if head_comment is not None and head_comment.head_comment is not None:
                return Response('답글에 답글을 달 수 없습니다.', status.HTTP_400_BAD_REQUEST)
            serializer = CommentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save()

            comment.post = post
            comment.user = user
            comment.head_comment = head_comment
            comment.save()
            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True).data)

        else:
            comment_id = request.data.get('comment', -1)    # default 값 뭐 이렇게 줘도 되나 ,,
            comment = get_object_or_404(Comment, pk=comment_id)
            if comment.head_comment is not None:
                comment.delete()
                comments = Comment.objects.filter(post=post, head_comment=None).all()
                return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_201_CREATED)
            comment.is_deleted = True
            comment.content = '삭제된 댓글입니다.'
            comment.save()
            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_201_CREATED)
