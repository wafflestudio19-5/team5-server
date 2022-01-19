from django.http import JsonResponse
from django_filters import rest_framework as filters

from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from lecture.models import Course, Lecture
from lecture.serializers import CourseForEvalSerializer, LectureSearchSerializer
from everytime.utils import get_object_or_404

from .filters import LectureFilter

class CourseForEvalView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)

        semesters = course.semester.split(',')
        sem_options = []

        for sem in semesters:
            sem = sem.strip()
            split = sem.split('-')
            option = split[0]+'년 '+split[1]+'학기'
            sem_options.append(option)

        return JsonResponse({
            'course': CourseForEvalSerializer(course).data,
            'semester_option': sem_options,
        }, status=status.HTTP_200_OK)


class LectureSearchViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LectureSearchSerializer
    queryset = Lecture.objects.select_related('course__department__college')\
            .filter(course__self_made=False)\
            .all().prefetch_related('lecturetime_set')\
            .order_by('id')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LectureFilter

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)
