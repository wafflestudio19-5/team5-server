from rest_framework import serializers, exceptions
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.StringRelatedField(read_only=True)
    writer = serializers.StringRelatedField(read_only=True)
    is_anonymous = serializers.BooleanField(default=True)
    is_deleted = serializers.BooleanField(default=False)
    head_comment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        request = self.context['request']

        try:
            board = request.query_params['board']
            board = Board.objects.get(id=board)
            validated_data['board'] = board
        except:
            raise serializers.ValidationError("board를 query parameter로 입력해주세요")

        comment = Comment.objects.create(**validated_data)
        return comment
