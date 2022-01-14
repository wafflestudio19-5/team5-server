from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.views import APIView

from lecture.models import Course
from lecture.serializers import CourseForEvalSerializer


class CourseInfoForEvalView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # def get(self, request, pk=None):
        # course = get_object_or_404(Course, pk=pk)
        #
        # semesters = course.semester.split(',')
        # sem_options = []
        # 
        # for sem in semesters:
        #     sem = sem.strip()
        #     split = sem.split('-')
        #     option = split[0]+'년 '+split[1]+'학기'
        #     sem_options.append(option)
        #
        # return JsonResponse({
        #     'course': CourseForEvalSerializer(course).data,
        #     'semester_option': sem_options,
        # }, status=status.HTTP_200_OK)
