from rest_framework import serializers
from everytime.exceptions import FieldError, DuplicationError, NotFound, ServerError
from .models import Friend, FriendRequest
from user.models import User

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.CharField()
    receiver = serializers.CharField()

    class Meta:
        model = Friend

    def validate(self, data):
        sender = data.get('sender', None)
        receiver = data.get('receiver', None)
        if sender in None or receiver is None:
            raise FieldError()
        try:
            sender = User.objects.get(username=sender)
        except:
            raise ServerError()
        try:
            receiver = User.objects.get(username=receiver)
        except User.DoesNotExist:
            raise NotFound('올바르지 않은 상대입니다.')
        if Friend.objects.filter(user=sender, friend=receiver).exists():
            raise DuplicationError('이미 친구인 상대입니다.')
        data['sender'] = sender
        data['receiver'] = receiver
        return data

    def create(self, validated_data):
        return FriendRequest.objects.create(**validated_data)


class FriendSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    Friend = serializers.CharField()

    class Meta:
        model = Friend

    def validate(self, data):
        user = data.get('user', None)
        friend = data.get('friend', None)
        if user in None or friend is None:
            raise FieldError()
        try:
            sender = User.objects.get(username=user)
        except:
            raise ServerError()
        try:
            friend = User.objects.get(username=friend)
        except User.DoesNotExist:
            raise NotFound('이런 상황이 있을 수 있나?')
        if Friend.objects.filter(user=user, friend=friend).exists():
            raise DuplicationError('이미 친구인 상대입니다.')
        data['user'] = sender
        data['friend'] = friend
        return data

    def create(self, validated_data):
        Friend.objects.create(user=validated_data['friend'], friend=validated_data['friend'])
        return Friend.objects.create(**validated_data)