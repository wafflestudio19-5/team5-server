from everytime import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils import timezone

import datetime

from report.models import ReportedUser
from report.serializers import PostReportSerializer, CommentReportSerializer, EvaluationReportSerializer, \
    ExamInfoReportSerializer, ChatReportSerializer


class PostReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # data에 post(pk)와 type 전달
        serializer = PostReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        postreport = serializer.save()
        serializer.validated_data['post'].reporting_users.add(request.user)

        reported_email = postreport.post.writer
        if reported_email is not None:
            reported_email = reported_email.school_email
            if ReportedUser.objects.filter(school_email=reported_email).exists():
                reported_user = ReportedUser.objects.get(school_email=reported_email)
                if reported_user.count % 10 == 0 and timezone.now() < reported_user.updated_at + datetime.timedelta(days=30):
                    pass
                else:
                    reported_user.count += 1
                    reported_user.save()
            else:
                ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class CommentReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = CommentReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        comment_report = serializer.save()
        serializer.validated_data['comment'].reporting_users.add(request.user)

        reported_email = comment_report.comment.writer
        if reported_email is not None:
            reported_email = reported_email.school_email
            if ReportedUser.objects.filter(school_email=reported_email).exists():
                reported_user = ReportedUser.objects.get(school_email=reported_email)
                if reported_user.count % 10 == 0 and timezone.now() < reported_user.updated_at + datetime.timedelta(days=30):
                    pass
                else:
                    reported_user.count += 1
                    reported_user.save()
            else:
                ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class EvaluationReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = EvaluationReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        evaluation_report = serializer.save()
        serializer.validated_data['eval'].reporting_users.add(request.user)

        reported_email = evaluation_report.eval.writer
        if reported_email is not None:
            reported_email = reported_email.school_email
            if ReportedUser.objects.filter(school_email=reported_email).exists():
                reported_user = ReportedUser.objects.get(school_email=reported_email)
                if reported_user.count % 10 == 0 and timezone.now() < reported_user.updated_at + datetime.timedelta(days=30):
                    pass
                else:
                    reported_user.count += 1
                    reported_user.save()
            else:
                ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class ExamInfoReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = ExamInfoReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        exam_info_report = serializer.save()
        serializer.validated_data['examinfo'].reporting_users.add(request.user)

        reported_email = exam_info_report.examinfo.writer
        if reported_email is not None:
            reported_email = reported_email.school_email
            if ReportedUser.objects.filter(school_email=reported_email).exists():
                reported_user = ReportedUser.objects.get(school_email=reported_email)
                if reported_user.count % 10 == 0 and timezone.now() < reported_user.updated_at + datetime.timedelta(days=30):
                    pass
                else:
                    reported_user.count += 1
                    reported_user.save()
            else:
                ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')


class ChatReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = ChatReportSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        chat_report = serializer.save()

        reported_email = chat_report.chatroom.partner
        if reported_email is not None:
            reported_email = reported_email.school_email
            if ReportedUser.objects.filter(school_email=reported_email).exists():
                reported_user = ReportedUser.objects.get(school_email=reported_email)
                if reported_user.count % 10 == 0 and timezone.now() < reported_user.updated_at + datetime.timedelta(days=30):
                    pass
                else:
                    reported_user.count += 1
                    reported_user.save()
            else:
                ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')
