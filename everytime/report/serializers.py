from rest_framework import serializers

from everytime.exceptions import NotAllowed
from everytime.utils import get_object_or_404
from post.models import Post
from report.models import PostReport


class PostReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReport
        fields = '__all__'

    def validate(self, data):
        post = get_object_or_404(Post, pk=data.get('post'))

        # post에 reporting_users 추가함(마이그레이션 안함)
        if self.context['user'] in post.reporting_users.all():
            raise NotAllowed('이미 신고한 글입니다.')

        return data