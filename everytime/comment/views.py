from django.shortcuts import render

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from django.shortcuts import get_object_or_404
from comment.models import Comment
from comment.serializers import CommentSerializer


class CommentViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(self.get_serializer(comment).data, status=status.HTTP_201_CREATED)

    # 댓글 수정 불가

    # 스웨거에 쿼리 param 추가해야함 - 공부하고 넣을게요
    def list(self, request):
        post = request.query_params.get('post')
        comments = self.get_queryset().filter(post=post).all()
        return Response(self.get_serializer(comments, many=True).data)

    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_deleted = True
        comment.save()
        return Response("%s번 댓글이 삭제되었습니다." % pk, status=status.HTTP_200_OK)
