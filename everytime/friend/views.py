from django.db.transaction import atomic
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from user.models import User
from .models import Friend, FriendRequest
from .serializers import FriendRequestSerializer, FriendSerializer
from everytime import permissions
from everytime.exceptions import FieldError, ServerError, NotFound, DatabaseError

# Create your views here.
class FriendRequestView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendRequestSerializer

    def post(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.save()
        if friend_request is None:
            raise ServerError()
        return Response("친구 요청을 보냈습니다.\n상대방이 수락하면 친구가 맺어짖니다.", status=status.HTTP_201_CREATED) # 이 부분 직접 친구신청 해보고 response 수정해야됨

class FriendRequestDeleteView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendRequestSerializer

    def delete(self, request, pk=None):
        user = request.user
        if not pk:
            raise FieldError('삭제할 요청를 입력해주세요.')
        sender = User.objects.get(pk=pk)
        try:
            delete_request = FriendRequest.objects.get(sender=sender, receiver=user)
        except:
            raise DatabaseError('요청이 존재하지 않습니다. 관리자에게 문의 바랍니다.')
        delete_request.delete()
        return Response("친구 요청을 거절하였습니다.", status=status.HTTP_200_OK)


class FriendView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendSerializer

    def post(self, request, pk=None):
        user = request.user
        if not pk:
            raise FieldError('친구 신청을 확인해주세요.')
        serializer = self.get_serializer(data={'friend': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("친구 요청을 수락하였습니다.", status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        user = request.user
        if not pk:
            raise FieldError('삭제할 친구를 입력해주세요.')
        try:
            friend = User.objects.get(pk=pk)
            relation1 = Friend.objects.get(user=user, friend=friend)
            relation2 = Friend.objects.get(user=friend, friend=user)
        except:
            raise NotFound('존재하지 않는 친구입니다.')
        with atomic():
            relation1.delete()
            relation2.delete()
        return Response("친구를 삭제하였습니다.", status=status.HTTP_200_OK)

class FriendListView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendSerializer

    def get(self, request):
        user = request.user
        queryset = Friend.objects.filter(user=user)
        request_queryset = FriendRequest.objects.filter(receiver=user)
        request_exist = request_queryset.exists()
        return Response({
            "request_exist": request_exist,
            "request_list": request_queryset.values('sender__id', 'sender__nickname'),
            "friend_list": queryset.values('friend__id', 'friend__nickname')
        }, status=status.HTTP_200_OK)