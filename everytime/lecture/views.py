from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from lecture.models import Course, LectureEvaluation, Semester
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


# class MyCourseView:
#     pass
#
#
# class EvalSummaryView:
#     pass
#
#
# class ExamInfoView:
#     pass
#
#
# class CourseSearchView:
#     pass
#
#
# class LikeEvaluationView:
#     pass
#
#
# class LikeExamInfoView:
#     pass
#
#
# class UsePointView:
#     pass
