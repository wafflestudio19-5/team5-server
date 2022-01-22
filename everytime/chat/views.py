from rest_framework import permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView

from .serializers import MessageCreateSerializer
from everytime.exceptions import FieldError, NotFound
from everytime.utils import get_object_or_404

from .models import ChatRoom, Message
from post.models import Post
from comment.models import Comment


class MessageCreateView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MessageCreateSerializer

    def post(self, request):
        user = request.user
        data = request.data

        # 어디서 메세지를 보내느냐에 따라 상대 유저 아이디를 얻는 방법이 다름
        channel = data.get('channel', None)
        if channel is None:
            raise FieldError('메세지 전달 경로를 명시해주세요.')
        elif channel == 'post':
            post_id = data.get('post_id', None)
            receiver = get_object_or_404(Post, id=post_id).writer
        elif channel == 'comment':
            comment_id = data.get('comment_id', None)
            receiver = get_object_or_404(Comment, id=comment_id).writer
        elif channel == 'chatroom':
            chatroom_id = data.get('chatroom_id', None)
            receiver = get_object_or_404(ChatRoom, id=chatroom_id).partner
        if receiver.username is None:
            raise NotFound('존재하지 않는 유저입니다.')
        serializer = self.get_serializer(data={
            'sender': user,
            'receiver': receiver,
            'content': data.get('content', None),
            'is_anonymous': data.get('is_anonymous', None)
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()