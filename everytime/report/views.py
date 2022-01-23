from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from report.models import ReportedUser
from report.serializers import PostReportSerializer, CommentReportSerializer, EvaluationReportSerializer, \
    ExamInfoReportSerializer


class PostReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # data에 post(pk)와 type 전달
        serializer = PostReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        postreport = serializer.save()

        reported_email = postreport.post.writer.school_email

        if ReportedUser.objects.filter(school_email=reported_email).exists():
            reported_user = ReportedUser.objects.get(school_email=reported_email)
            reported_user.count += 1
            reported_user.save()
        else:
            ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class CommentReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # data에 post(pk)와 type 전달
        serializer = CommentReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        comment_report = serializer.save()

        reported_email = comment_report.comment.writer.school_email

        if ReportedUser.objects.filter(school_email=reported_email).exists():
            reported_user = ReportedUser.objects.get(school_email=reported_email)
            reported_user.count += 1
            reported_user.save()
        else:
            ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class EvaluationReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # data에 post(pk)와 type 전달
        serializer = EvaluationReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        evaluation_report = serializer.save()

        reported_email = evaluation_report.eval.writer.school_email

        if ReportedUser.objects.filter(school_email=reported_email).exists():
            reported_user = ReportedUser.objects.get(school_email=reported_email)
            reported_user.count += 1
            reported_user.save()
        else:
            ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class ExamInfoReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # data에 post(pk)와 type 전달
        serializer = ExamInfoReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        exam_info_report = serializer.save()

        reported_email = exam_info_report.post.writer.school_email

        if ReportedUser.objects.filter(school_email=reported_email).exists():
            reported_user = ReportedUser.objects.get(school_email=reported_email)
            reported_user.count += 1
            reported_user.save()
        else:
            ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


# 제한 횟수에 따른 제한 기간은 기준을 모르겠어서 우리끼리 알아서 정하면 될 거 같고,
# (10회 일주일 정지, 30회 한 달 정지, 50회 6개월 정지 등등,, 알아서)
# 이후 ReportedUser 객체의 count와 updated_at 따라 permission 조정
