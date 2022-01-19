from rest_framework import viewsets, views, permissions, status
from rest_framework.response import Response
from .models import Friend
from .serializers import FriendRequestSerializer, FriendSerializer

# Create your views here.
class FreindRequestView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        data = request.data
        user = request.user
        data['sender'] = user.nickname or None
        serializer = FriendRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.save()
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED) # 이 부분 직접 친구신청 해보고 response 수정해야됨

class FriendViewset(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FriendSerializer

    def create(self, request):
        data = request.data
        user = request.user
        data['user'] = user.nickname or None
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.save()
        queryset = Friend.objects.filter(user=user)
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        user = request.user
        queryset = Friend.objects.filter(user=user)
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def delete(self, request):
        pass