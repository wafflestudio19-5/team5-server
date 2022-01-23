from django.db import models


class ChatRoom(models.Model):
    user = models.ForeignKey('user.User', related_name='my_chatrooms', on_delete=models.CASCADE)
    partner = models.ForeignKey('user.User', related_name='other_chatrooms', on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "partner", "is_anonymous"],
                name="chat room"
            )
        ]


class Message(models.Model):
    sender = models.ForeignKey('user.User', related_name='sent_messages', on_delete=models.SET_NULL, null=True)
    receiver = models.ForeignKey('user.User', related_name='received_messages', on_delete=models.SET_NULL, null=True)
    content = models.TextField(null=False)
    is_notice = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


class ChatRoomMessage(models.Model):
    chatroom = models.ForeignKey('ChatRoom', related_name='message_set', on_delete=models.CASCADE)
    message = models.ForeignKey('Message', related_name='chatroom_set', on_delete=models.CASCADE)


class ChatBlackList(models.Model):
    user = user = models.ForeignKey('user.User', related_name='my_blacklist', on_delete=models.CASCADE)
    partner = models.ForeignKey('user.User', related_name='other_blacklist', on_delete=models.CASCADE)