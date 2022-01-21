from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from report.models import ReportedUser, BlockedUser
from report.serializers import PostReportSerializer


class PostReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # data에 post(pk)와 type 전달
        serializer = PostReportSerializer(request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        postreport = serializer.save()

        reported_email = postreport.post.writer.school_email

        if ReportedUser.objects.filter(school_email=reported_email).exists():
            reported_user = ReportedUser.objects.get(school_email=reported_email)
            reported_user.count += 1
            reported_user.save()

            reported_cnt = reported_user.count
            if reported_cnt == 10:
                BlockedUser.objects.create(school_email=reported_email)
            elif reported_cnt == 30:
                blocked = BlockedUser.objects.get(school_email=reported_email)
                blocked.count = 2
                blocked.save()
            elif reported_cnt == 50:
                blocked = BlockedUser.objects.get(school_email=reported_email)
                blocked.count = 3
                blocked.save()
            else:
                blocked = BlockedUser.objects.get(school_email=reported_email)
                blocked.count = 4
                blocked.save()
            # 제한 횟수에 따른 제한 기간은 기준을 모르겠어서 우리끼리 알아서 정하면 될 거 같고,
            # 이후 BlockedUser 객체의 count와 updated_at 따라 permission 조정
        else:
            ReportedUser.objects.create(school_email=reported_email)

        return Response('신고하였습니다.')
