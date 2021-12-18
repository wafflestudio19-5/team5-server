from django.shortcuts import render, get_object_or_404

from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Tag
from .serializers import PostSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class PostViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def create(self, request):
        data = request.data
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

        if post.writer_id is not user.id:
            raise exceptions.AuthenticationFailed('글 작성자가 아니므로 글을 수정할 수 없습니다.')
        serializer = self.get_serializer(post, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)