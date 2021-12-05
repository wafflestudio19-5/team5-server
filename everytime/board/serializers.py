from rest_framework import serializers

from .models import Board

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

    def create(self, validated_data):
        title = validated_data.get('title')
        description = validated_data.get('description')
        anonym_enabled = validated_data.get('anonym_enabled')
        is_market = validated_data.get('is_market')
        title_enabled = validated_data.get('title_enabled')
        question_enabled = validated_data.get('question_enabled')
        notice_enabled = validated_data.get('notice_enabled')

        board = Board.objects.create(title=title,description=description,anonym_enabled=anonym_enabled,is_market=is_market,\
                                     title_enabled=title_enabled,question_enabled=question_enabled,notice_enabled=notice_enabled)

        return board
