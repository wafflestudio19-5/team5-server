from django.shortcuts import render, get_object_or_404

from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Tag
from .serializers import PostSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# request.data안에 새로운 Tag를 찾아서 데이터베이스에 저장
def create_tag(data):
    if 'tags' in data:
        all_tag = Tag.objects.all()
        for tag_name in data.getlist('tags'):
            tag_name = tag_name.upper()
            if not all_tag.filter(tag__iexact=tag_name).exists():
                Tag.objects.create(tag=tag_name)


class PostViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def create(self, request):
        data = request.data

        create_tag(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

    def list(self, request):
        board = request.query_params.get('board')
        posts = self.get_queryset().filter(board=board).all()
        return Response(self.get_serializer(posts, many=True).data)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        data = request.data
        user = request.user

        create_tag(data)

        if post.writer_id is not user.id:
            raise exceptions.AuthenticationFailed('글 작성자가 아니므로 글을 수정할 수 없습니다.')

        serializer = self.get_serializer(post, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)