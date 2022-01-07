from rest_framework import serializers, exceptions

from .models import Board


class BoardSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=30)
    description = serializers.CharField(required=True, max_length=50)
    anonym_enabled = serializers.BooleanField(required=False, default=True)
    is_market = serializers.BooleanField(required=False, default=False)
    title_enabled = serializers.BooleanField(required=False, default=True)
    question_enabled = serializers.BooleanField(required=False, default=False)
    notice_enabled = serializers.BooleanField(required=False, default=False)
    board_type = serializers.IntegerField(required=True)
    sub_boards = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Board
        fields = '__all__'

    def get_sub_boards(self, board):
        sub_boards = board.sub_boards.all()
        serializer = BoardNameSerializer(sub_boards, many=True)
        return serializer.data

    def validate(self, data):
        title = data.get('title')
        if Board.objects.filter(title=title).exists():
            raise serializers.ValidationError('이미 있는 게시판입니다.')

        return data

    def create(self, validated_data):
        board = Board.objects.create(**validated_data)

        return board


class BoardNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = (
            'id',
            'title',
        )