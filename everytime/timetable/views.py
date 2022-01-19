from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from lecture.models import Semester, Lecture, Course, LectureTime
from .models import TimeTable
from .serializers import TimeTableSerializer, TimeTableListSerializer, SelfLectureCreateSerializer


class TimeTableViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TimeTable.objects.all()

    def get_serializer_class(self):
        if self.action in ['list']:
            return TimeTableListSerializer

        return TimeTableSerializer

    def create(self, request):
        data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        timetable = serializer.save()
        return Response(self.get_serializer(timetable).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        user = request.user
        semester_id = request.query_params.get('semester')
        semester = get_object_or_404(Semester, id=semester_id)
        queryset = TimeTable.objects.filter(user=user, semester=semester).all()
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        timetable = get_object_or_404(TimeTable, pk=pk)
        if request.user != timetable.user:
            return Response('자신의 시간표만 열람할 수 있습니다.', status=status.HTTP_403_FORBIDDEN)
        return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        timetable = get_object_or_404(TimeTable, pk=pk)
        if request.user != timetable.user:
            return Response('자신의 시간표만 삭제할 수 있습니다.', status=status.HTTP_403_FORBIDDEN)

        queryset = TimeTable.objects.filter(user=request.user, semester=timetable.semester)

        if timetable.is_default:
            semester = timetable.semester
            timetable.delete()
            try:
                default_timetable = queryset.order_by('-updated_at')[0]
                default_timetable.is_default = True
                default_timetable.save()
            except IndexError:
                default_timetable = TimeTable.objects.create(user=request.user, semester=semester, name='시간표 1', is_default=True)
                
        else:
            timetable.delete()
            try:
                default_timetable = queryset.get(is_default=True)
            except TimeTable.DoesNotExist:
                default_timetable = TimeTable.objects.create(user=request.user, semester=semester, name='시간표 1', is_default=True)

        return Response(self.get_serializer(default_timetable).data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        timetable = get_object_or_404(TimeTable, pk=pk)
        if request.user != timetable.user:
            return Response('자신의 시간표만 수정할 수 있습니다.', status=status.HTTP_403_FORBIDDEN)
        data = request.data

        serializer = self.get_serializer(timetable, data=data, partial=True)
        serializer.is_valid()
        timetable = serializer.save()

        return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['Post']
    )
    def lecture(self, request, pk=None):
        timetable = get_object_or_404(TimeTable, pk=pk)

        user = request.user
        data = request.data
        if timetable.user != user:
            return Response('자신의 시간표에만 강의를 추가/제거할 수 있습니다.', status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            serializer = SelfLectureCreateSerializer(data=data, context={'request': request, 'timetable': timetable})
            serializer.is_valid(raise_exception=True)
            lecture = serializer.save()
            timetable.lecture.add(lecture)
            
        return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='lecture/(?P<lecture_id>[^/.]+)'
    )
    def add_or_remove_lecture(self, request, pk=None, lecture_id=-1):
        timetable = get_object_or_404(TimeTable, pk=pk)
        lecture = get_object_or_404(Lecture, pk=lecture_id)
        user = request.user
        data = request.data
        if timetable.user != user:
            return Response('자신의 시간표에만 강의를 추가/제거할 수 있습니다.', status=status.HTTP_403_FORBIDDEN)
        if lecture.semester != timetable.semester:
            return Response('시간표와 수업의 학기가 서로 다릅니다.', status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            existing_lectures = timetable.lecture.all()
            if lecture in existing_lectures:
                return Response('이미 추가한 수업입니다.', status=status.HTTP_400_BAD_REQUEST)
            existing_time_set = LectureTime.objects.filter(lecture__in=existing_lectures).all()
            
            new_time_set = lecture.lecturetime_set.all()
            for new_time in new_time_set:
                existing_time_set = existing_time_set.filter(day=new_time.day)
                for existing_time in existing_time_set:
                    if new_time.start >= existing_time.end or new_time.end <= existing_time.start:
                        pass
                    else:
                        return Response(f'{lecture.course.title} 수업과 같은 시간에 이미 수업이 있습니다.',
                                        status=status.HTTP_400_BAD_REQUEST)
                    
            timetable.lecture.add(lecture)

            return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            timetable.lecture.remove(lecture)
            return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)