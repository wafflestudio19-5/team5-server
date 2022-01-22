from rest_framework import serializers

from .models import *
from user.models import User


class MessageCreateSerializer(serializers.ModelSerializer):
    is_anonymous = serializers.BooleanField()

    class Meta:
        model = Message
        fields = '__all__'

    def validate(self, data):
        sender = data.get('sender')
        receiver = data.get('receiver')
        is_anonymous = data.get('is_anonymous')
        chatroom_sender = ChatRoom.objects.get_or_create(user=sender, partner=receiver)
        chatroom_receiver = ChatRoom.objects.get_or_create(user=receiver, partner=sender)
        data['chatroom_sender'] = chatroom_sender
        data['chatroom_receiver'] = chatroom_receiver
        return data

    def create(self, data):
        sender = data.get('sender')
        receiver = data.get('receiver')
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

