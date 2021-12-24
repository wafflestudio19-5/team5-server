from django.shortcuts import render

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from django.shortcuts import get_object_or_404
from comment.models import Comment
from comment.serializers import CommentSerializer



######### POST API 하위 API로 넘어가면서 아래는 수정/보완 없이 그냥 놔둠, 제대로 구현 안했으니 무시할 것 ###########


# class CommentViewSet(viewsets.GenericViewSet):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = CommentSerializer
#     queryset = Comment.objects.all()
#
#     def create(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         comment = serializer.save()
#         # foreign key 참조 할 거 query param으로 처리해야하나 고민중이었는데 그냥 post 하위 API로 넘어감
#         return Response(self.get_serializer(comment).data, status=status.HTTP_201_CREATED)
#
#     # 댓글 수정 불가
#
#     # 스웨거에 쿼리 param 추가해야함
#     def list(self, request):
#         post = request.query_params.get('post')
#         comments = self.get_queryset().filter(post=post).all()
#         return Response(self.get_serializer(comments, many=True).data)
#
#     def destroy(self, request, pk=None):
#         comment = get_object_or_404(Comment, pk=pk)
#         comment.is_deleted = True
#         comment.save()
#         return Response("%s번 댓글이 삭제되었습니다." % pk, status=status.HTTP_200_OK)
