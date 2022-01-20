from django.db.transaction import atomic
from rest_framework import serializers
from everytime.exceptions import FieldError, DuplicationError, NotFound, ServerError
from .models import Friend, FriendRequest
from user.models import User

class FriendRequestSerializer(serializers.Serializer):
    sender = serializers.CharField(read_only=True)
    receiver = serializers.CharField()

    def validate(self, data):
        print(self.context)
        sender = self.context['request'].user
        receiver = data.get('receiver', None)
        if sender.username is None or receiver is None:
            raise FieldError()
        try:
            receiver = User.objects.get(username=receiver)
        except User.DoesNotExist:
            raise NotFound('올바르지 않은 상대입니다.')
        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            raise DuplicationError('이미 친구 요청을 보낸 상대입니다.\n상대방이 수락하면 친구가 맺어집니다.')
        if Friend.objects.filter(user=sender, friend=receiver).exists():
            raise DuplicationError('이미 친구인 상대입니다.')
        data['sender'] = sender
        data['receiver'] = receiver
        return data

    def create(self, validated_data):
        return FriendRequest.objects.create(**validated_data)


class FriendSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    friend = serializers.IntegerField()

    class Meta:
        model = Friend
        fields = '__all__'

    def validate(self, data):
        print(data)
        user = self.context['request'].user
        friend = data.get('friend', None)
        if friend is None:
            raise FieldError()
        try:
            friend = User.objects.get(pk=friend)
        except:
            raise NotFound('존재하지 않는 유저입니다.')
        if not FriendRequest.objects.filter(sender=friend, receiver=user).exists():
            raise NotFound('친구 요청이 존재하지 않습니다.')
        if Friend.objects.filter(user=user, friend=friend).exists():
            raise DuplicationError('이미 친구인 상대입니다.')
        data['user'] = user
        data['friend'] = friend
        print(data)
        return data

    def create(self, validated_data):
        with atomic():
            friend_request = FriendRequest.objects.get(sender=validated_data['friend'], receiver=validated_data['user'])
            friend_request.delete()
            Friend.objects.create(user=validated_data['friend'], friend=validated_data['user'])
            return Friend.objects.create(**validated_data)
