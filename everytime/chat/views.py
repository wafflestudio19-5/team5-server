from django.db.models import Count

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView

from .serializers import *
from everytime.exceptions import FieldError, NotFound, NotAllowed
from everytime.utils import get_object_or_404

from .models import *
from post.models import Post
from comment.models import Comment


# 게시글 또는 댓글에서 쪽지를 보낼 때
class MessageThroughPostOrCommentView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        user = request.user
        params = request.query_params
        data = request.data

        # 어디서 메세지를 보내느냐에 따라 상대 유저 아이디를 얻는 방법이 다름
        channel = params.get('channel', None)
        if channel is None:
            raise FieldError('메세지 전달 경로를 명시해주세요.')
        elif channel == 'post':
            post_id = params.get('post_id', None)
            self.obj = get_object_or_404(Post, id=post_id)
            receiver = self.obj.writer
            is_anonymous = self.obj.is_anonymous
        elif channel == 'comment':
            comment_id = params.get('comment_id', None)
            self.obj = get_object_or_404(Comment, id=comment_id)
            receiver = self.obj.writer
            is_anonymous = self.obj.is_anonymous

        if receiver.username is None:
            raise NotFound('존재하지 않는 유저입니다.')

        serializer = MessageCreateSerializer(data={
            'content': data.get('content', None),
            'is_anonymous': is_anonymous
        }, context={
            'sender': user,
            'receiver': receiver,
            'channel': channel,
            channel: getattr(self, 'obj')
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("success", status=status.HTTP_201_CREATED)


# 채팅방에서 쪽지를 보내고 삭제할 때
class MessageThroughChatRoomView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChatRoomSerializer

    def post(self, request, pk=None):
        sender = request.user
        data = request.data
        chatroom = get_object_or_404(ChatRoom, pk=pk)
        receiver = chatroom.partner

        if receiver.username is None:
            raise NotFound('존재하지 않는 유저입니다.')

        serializer = MessageCreateSerializer(data={
            'content': data.get('content', None),
            'is_anonymous': chatroom.is_anonymous
        }, context={
            'sender': sender,
            'receiver': receiver,
            'channel': 'chatroom'
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("success", status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        user = request.user
        chatroom = get_object_or_404(ChatRoom, pk=pk)
        if chatroom.user != user:
            raise NotAllowed('자신의 채팅방만 조회할 수 있습니다.')
        return Response(self.get_serializer(chatroom).data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        get_object_or_404(ChatRoom, pk=pk).delete()
        return Response("success", status=status.HTTP_200_OK)


# 채팅방 리스트
class ChatRoomListView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChatRoomListSerializer

    def get(self, request):
        return Response(self.get_serializer(request.user.my_chatrooms.order_by('-updated_at'), many=True).data, status=status.HTTP_200_OK)


# 유저 차단
class ChatBlockView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, pk=None):
        user = request.user
        chatroom = get_object_or_404(ChatRoom, pk=pk)
        partner = chatroom.partner
        ChatBlackList.objects.get_or_create(user=user, partner=partner)

        return Response("success", status=status.HTTP_201_CREATED)