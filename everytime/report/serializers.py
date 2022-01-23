from rest_framework import serializers

from everytime.exceptions import NotAllowed, NotFound, DatabaseError
from everytime.utils import get_object_or_404
from post.models import Post
from comment.models import Comment
from lecture.models import LectureEvaluation, ExamInfo
from report.models import PostReport, CommentReport, EvaluationReport, ExamInfoReport


class PostReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReport
        fields = '__all__'

    def validate(self, data):
        post = data.get('post')
        if post.writer is None:
            raise NotAllowed('해당 글을 작성한 유저가 더이상 존재하지 않습니다.')
        if post.writer.school_email is None:
            raise DatabaseError('학교 인증을 마치지 않은 작성자입니다. 서버 관리자에게 문의 바랍니다.')
        if self.context['user'] in post.reporting_users.all():
            raise NotAllowed('이미 신고한 글입니다.')

        return data


class CommentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReport
        fields = '__all__'

    def validate(self, data):
        comment = data.get('comment')
        if comment.writer is None:
            raise NotAllowed('해당 글을 작성한 유저가 더이상 존재하지 않습니다.')
        if comment.writer.school_email is None:
            raise DatabaseError('학교 인증을 마치지 않은 작성자입니다. 서버 관리자에게 문의 바랍니다.')
        if self.context['user'] in comment.reporting_users.all():
            raise NotAllowed('이미 신고한 글입니다.')

        return data


class EvaluationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationReport
        fields = '__all__'

    def validate(self, data):
        eval = data.get('eval')
        if eval.writer is None:
            raise NotAllowed('해당 글을 작성한 유저가 더이상 존재하지 않습니다.')
        if eval.writer.school_email is None:
            raise DatabaseError('학교 인증을 마치지 않은 작성자입니다. 서버 관리자에게 문의 바랍니다.')
        if self.context['user'] in eval.reporting_users.all():
            raise NotAllowed('이미 신고한 글입니다.')

        return data


class ExamInfoReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamInfoReport
        fields = '__all__'

    def validate(self, data):
        examinfo = data.get('examinfo')
        if examinfo.writer is None:
            raise NotAllowed('해당 글을 작성한 유저가 더이상 존재하지 않습니다.')
        if examinfo.writer.school_email is None:
            raise DatabaseError('학교 인증을 마치지 않은 작성자입니다. 서버 관리자에게 문의 바랍니다.')
        if self.context['user'] in examinfo.reporting_users.all():
            raise NotAllowed('이미 신고한 글입니다.')

        return data