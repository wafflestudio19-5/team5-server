from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from lecture.models import Course, LectureEvaluation, Semester, TimeTable
from lecture.serializers import CourseForEvalSerializer, EvalListSerializer, EvalCreateSerializer


class CourseInfoForEvalView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)

        course_sem = set()
        for obj in course.lecture_set.all():
            course_sem.add(obj.semester.name)

        course_sem = sorted(list(course_sem), reverse=True)
        serializer = CourseForEvalSerializer(course, context={'sem': course_sem})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecentEvalView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        evals = LectureEvaluation.objects.order_by('-created_at')
        serializer = EvalListSerializer(evals, many=True, context={'user': request.user})
        return Response(serializer.data, status.HTTP_200_OK)


class EvaluationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        data = request.data.copy()
        sem = data.get('semester')  # string 값이 들어왔다 치면
        # semester validation은 따로
        course_sem = []
        for obj in course.lecture_set.all():
            course_sem.append(obj.semester.name)

        if sem is None:
            return Response('semester 값을 입력하세요.', status=status.HTTP_400_BAD_REQUEST)
        if sem not in course_sem:
            return Response('해당학기에 개설되지 않은 강의입니다. 학기 정보를 확인하세요.', status=status.HTTP_400_BAD_REQUEST)

        data['semester'] = Semester.objects.get(name=sem).id

        serializer = EvalCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['writer'] = request.user
        serializer.validated_data['course'] = course
        serializer.save()

        evals = LectureEvaluation.objects.filter(course=course).order_by('-created_at')
        serializer = EvalListSerializer(evals, many=True, context={'user': request.user})
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        evals = LectureEvaluation.objects.filter(course=course).order_by('-created_at')
        serializer = EvalListSerializer(evals, many=True, context={'user': request.user})
        return Response(serializer.data, status.HTTP_200_OK)


# class MyCourseView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get(self, request):
#         timetable = TimeTable.objects.get(user=request.user, is_default=True, )


class EvalSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        evals = LectureEvaluation.objects.filter(course=course)

        if not evals.exists():
            return JsonResponse({
                'has_evals': False,
            }, status=status.HTTP_200_OK)


        avg_rating = round(evals.aggregate(Avg('rating')).get('rating__avg'), 2)
        # 아래 다섯개의 값은 most common 값을 들고오도록 함
        assignment = evals.values_list('assignment', flat=True).annotate(count=Count('assignment')).order_by("-count")[0]
        team = evals.values_list('team_project', flat=True).annotate(count=Count('team_project')).order_by("-count")[0]
        grade = evals.values_list('grade', flat=True).annotate(count=Count('grade')).order_by("-count")[0]
        attendance = evals.values_list('attendance', flat=True).annotate(count=Count('attendance')).order_by("-count")[0]
        exam_freq = evals.values_list('exam', flat=True).annotate(count=Count('exam')).order_by("-count")[0]

        # key에 해당하는 위의 값들을 value로 변환
        dict_AMOUNT_CHOICE = dict(LectureEvaluation.AMOUNT_CHOICES)
        assignment = dict_AMOUNT_CHOICE[assignment]
        team = dict_AMOUNT_CHOICE[team]
        grade = dict(LectureEvaluation.GRADE_CHOICES)[grade]
        attendance = dict(LectureEvaluation.ATTENDANCE_CHOICES)[attendance]
        exam_freq = dict(LectureEvaluation.EXAM_FREQUENCY_CHOICES)[exam_freq]

        return JsonResponse({
            'has_evals': True,
            'rating': avg_rating,
            'assignment': assignment,
            'team': team,
            'grade': grade,
            'attendance': attendance,
            'exam_freq': exam_freq,
        }, status=status.HTTP_200_OK)
#
#
# class ExamInfoView:
#     pass
#
#
# class CourseSearchView:
#     pass
#

class LikeEvaluationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, eval_pk):
        # course = get_object_or_404(Course, pk=pk) 아래 eval의 course가 이 course인지 확인할 순 있겠지만 하지 않는걸로,,
        eval = get_object_or_404(LectureEvaluation, pk=eval_pk)

        if request.user in eval.like_users.all():  # 이미 추천을 누른 사람이라면
            return JsonResponse({
                'is_success': False,
                'error_code': 1  # '이미 추천하였습니다.'를 담은 팝업창이 떠야함
            })
        else:
            eval.like_users.add(request.user)
            eval.num_of_likes += 1
            eval.save()
            return JsonResponse({
                'is_success': True,
                'value': eval.num_of_likes
            })
#
#
# class LikeExamInfoView:
#     pass
#
#
# class UsePointView:
#     pass
