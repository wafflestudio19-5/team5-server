from rest_framework import serializers

from .models import *

from everytime.exceptions import FieldError, NotAllowed


# 메세지 보낼 때 쓰는 거
class MessageCreateSerializer(serializers.ModelSerializer):
    is_anonymous = serializers.BooleanField()

    class Meta:
        model = Message
        fields = (
            'content',
            'is_anonymous'
        )

    def validate(self, data):
        print(self.context)
        sender = self.context.get('sender')
        receiver = self.context.get('receiver')
        if sender is None or receiver is None:
            raise FieldError('보낼 대상을 확인해주세요.')
        if sender == receiver:
            raise NotAllowed('자기 자신에게는 쪽지를 보낼 수 없습니다.')
        is_anonymous = data.get('is_anonymous')
        channel = self.context.get('channel')
        if channel not in ['post', 'comment', 'chatroom']:
            raise FieldError('채널 쿼리 파라미터는 post 또는 comment만 가능합니다.')
        channel_detail = self.context.get('channel_detail')

        chatroom_sender, created = ChatRoom.objects.get_or_create(user=sender, partner=receiver, is_anonymous=is_anonymous, channel=channel_detail)
        chatroom_receiver, created = ChatRoom.objects.get_or_create(user=receiver, partner=sender, is_anonymous=is_anonymous, channel=channel_detail)

        if created and is_anonymous:
            if channel == 'post':
                post = self.context.get('object')
                notice = Message.objects.create(sender=None, receiver=None, is_notice=True,
                                                content=post.board.title+'에 작성된 글을 통해 시작된 쪽지입니다.\n글 내용: '+(post.title if post.board.title_enabled else post.content))
                ChatRoomMessage.objects.create(chatroom=chatroom_sender, message=notice)
            elif channel == 'comment':
                comment = self.context.get('object')
                post = comment.post
                notice = Message.objects.create(sender=None, receiver=None, is_notice=True,
                                                content=post.board.title + '에 작성된 ' + comment.writer.userpost_set.get(post=post).anonymous_nickname + '의 댓글을 통해 시작된 쪽지입니다.\n글 내용: ' + (post.title if post.board.title_enabled else post.content))
                ChatRoomMessage.objects.create(chatroom=chatroom_sender, message=notice)

        if created:
            notice1 = Message.objects.create(sender=None, receiver=None, is_notice=True,
                                             content='쪽지 이용 시 개인정보 및 금융정보 보호에 유의해주시기 바랍니다. 광고, 스팸, 사기 등의 쪽지를 받으셨을 경우 스팸 신고를 눌러주세요.')
            ChatRoomMessage.objects.create(chatroom=chatroom_receiver, message=notice1)
            if is_anonymous:
                if channel == 'post':
                    post = self.context.get('object')
                    notice2 = Message.objects.create(sender=None, receiver=None, is_notice=True,
                                                    content=post.board.title + '에 작성된 글을 통해 시작된 쪽지입니다.\n글 내용: ' + (
                                                        post.title if post.board.title_enabled else post.content))
                    ChatRoomMessage.objects.create(chatroom=chatroom_receiver, message=notice2)
                elif channel == 'comment':
                    comment = self.context.get('object')
                    post = comment.post
                    notice2 = Message.objects.create(sender=None, receiver=None, is_notice=True,
                                                    content=post.board.title + '에 작성된 ' + comment.writer.userpost_set.get(post=post).anonymous_nickname + '의 댓글을 통해 시작된 쪽지입니다.\n글 내용: ' + (post.title if post.board.title_enabled else post.content))
                    ChatRoomMessage.objects.create(chatroom=chatroom_receiver, message=notice2)

        data['chatroom_sender'] = chatroom_sender
        data['chatroom_receiver'] = chatroom_receiver
        return data

    def create(self, data):
        sender = self.context.get('sender')
        receiver = self.context.get('receiver')
        chatroom_sender = data.get('chatroom_sender')
        chatroom_receiver = data.get('chatroom_receiver')
        content = data.get('content')
        new_message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        ChatRoomMessage.objects.create(chatroom=chatroom_sender, message=new_message)
        ChatRoomMessage.objects.create(chatroom=chatroom_receiver, message=new_message)
        chatroom_sender.updated_at = new_message.created_at
        chatroom_sender.save()
        chatroom_receiver.updated_at = new_message.created_at
        chatroom_receiver.save()
        return new_message


# 채팅룸 리스트
class ChatRoomListSerializer(serializers.ModelSerializer):
    partner = serializers.SerializerMethodField()
    recent_chat = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            'id',
            'partner',
            'updated_at',
            'recent_chat'
        )

    def get_partner(self, chatroom):
        return '익명' if chatroom.is_anonymous else chatroom.partner.nickname

    def get_recent_chat(self, chatroom):
        if not chatroom.message_set.exists():
            return 'Error'
        return chatroom.message_set.latest('message__created_at').message.content


# 특정 채팅룸의 채팅 내용
class ChatRoomSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            'id',
            'messages'
        )

    def get_messages(self, chatroom):
        messages = Message.objects.filter(id__in=chatroom.message_set.values('message__id')).order_by('-created_at')
        return MessageSerializer(messages, many=True, context=self.context).data


# 하나의 채팅에 대한 내용
class MessageSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id',
            'is_mine',
            'is_notice',
            'content',
            'created_at'
        )

    def get_is_mine(self, message):
        return message.sender == self.context['request'].user