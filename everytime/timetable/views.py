from django.http import JsonResponse
from django.db import transaction

from rest_framework import status, viewsets, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from everytime import permissions
from everytime.utils import get_object_or_404
from everytime.exceptions import NotAllowed, FieldError
from user.models import User
from lecture.models import Semester, Lecture, Course, LectureTime
from friend.models import Friend
from .models import TimeTable
from .serializers import TimeTableSerializer, TimeTableListSerializer, SelfLectureCreateSerializer, FriendTimeTableListSerializer


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
        semester_name = request.query_params.get('semester')
        semester = get_object_or_404(Semester, name=semester_name)
        queryset = TimeTable.objects.filter(user=user, semester=semester).all()
        return Response(self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        timetable = get_object_or_404(TimeTable, pk=pk)
        if request.user == timetable.user:
            return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)
        if timetable.is_default and timetable.private in ['전체공개', '친구공개']:
            if Friend.objects.filter(user=request.user, friend=timetable.user).exists():
                return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)
            else:
                raise NotAllowed('친구가 아닌 타인의 시간표는 열람할 수 없습니다.')
        else:
            raise NotAllowed('친구의 기본 시간표가 공개되어 있지 않습니다.')

    def destroy(self, request, pk=None):
        timetable = get_object_or_404(TimeTable, pk=pk)
        if request.user != timetable.user:
            raise NotAllowed('자신의 시간표만 삭제할 수 있습니다.')
        semester = timetable.semester
        queryset = TimeTable.objects.filter(user=request.user, semester=semester)

        if timetable.is_default:
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
            raise NotAllowed('자신의 시간표만 수정할 수 있습니다.')
        data = request.data

        serializer = self.get_serializer(timetable, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
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
            raise NotAllowed('자신의 시간표에만 강의를 추가/제거할 수 있습니다.')

        with transaction.atomic():
            serializer = SelfLectureCreateSerializer(data=data, context={'request': request, 'timetable': timetable})
            serializer.is_valid(raise_exception=True)
            lecture = serializer.save()
            timetable.lecture.add(lecture)
            timetable.save()
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
            raise NotAllowed('자신의 시간표에만 강의를 추가/제거할 수 있습니다.')
        if lecture.semester != timetable.semester:
            raise FieldError('시간표와 수업의 학기가 서로 다릅니다.')
        if request.method == 'POST':
            existing_lectures = timetable.lecture.all()
            if lecture in existing_lectures:
                raise FieldError('이미 추가한 수업입니다.')
            existing_time_set = LectureTime.objects.filter(lecture__in=existing_lectures).all()
            
            new_time_set = lecture.lecturetime_set.all()
            for new_time in new_time_set:
                existing_time_set = existing_time_set.filter(day=new_time.day)
                for existing_time in existing_time_set:
                    if new_time.start >= existing_time.end or new_time.end <= existing_time.start:
                        pass
                    else:
                        raise FieldError(f'{lecture.course.title} 수업과 같은 시간에 이미 수업이 있습니다.')
                    
            timetable.lecture.add(lecture)
            timetable.save()
            return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            timetable.lecture.remove(lecture)
            timetable.save()
            return Response(self.get_serializer(timetable).data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['Get'],
        url_path='friend/(?P<friend_id>[^/.]+)'
    )
    def friend(self, request, friend_id=-1):
        user = request.user
        friend = get_object_or_404(User, id=friend_id)
        if user.friends.filter(friend=friend).exists():
            timetables = TimeTable.objects.filter(user=friend, is_default=True, private__in=['전체공개','친구공개']).select_related('semester')
            return Response(FriendTimeTableListSerializer(timetables, many=True).data, status=status.HTTP_200_OK)

        else:
            raise NotAllowed('친구가 아닌 사용자의 시간표는 볼 수 없습니다.')