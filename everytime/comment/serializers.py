from rest_framework import serializers, exceptions
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    writer = serializers.StringRelatedField(read_only=True)
    content = serializers.CharField()
    is_anonymous = serializers.BooleanField(default=True)
    is_deleted = serializers.BooleanField(default=False)
    head_comment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    # def create(self, validated_data):
        # comment = Comment.objects.create(**validated_data)
        # return comment
