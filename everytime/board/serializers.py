from rest_framework import serializers, exceptions

from .models import Board
from user.models import User

class BoardSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=30)
    description = serializers.CharField(required=True, max_length=50)
    anonym_enabled = serializers.BooleanField(required=False, default=True)
    is_market = serializers.BooleanField(required=False, default=False)
    title_enabled = serializers.BooleanField(required=False, default=True)
    question_enabled = serializers.BooleanField(required=False, default=False)
    notice_enabled = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Board
        fields = '__all__'

    def validate(self, data):
        title = data.get('title')
        print(data)
        if Board.objects.filter(title=title).exists():
            raise serializers.ValidationError('이미 있는 게시판입니다.')
        return data

    def create(self, validated_data):

        board = Board.objects.create(**validated_data)

        return board
