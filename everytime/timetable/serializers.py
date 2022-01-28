from django.db import transaction

from rest_framework import serializers, exceptions

from everytime.utils import get_object_or_404
from everytime.exceptions import FieldError, DuplicationError
from lecture.models import Semester, Lecture, Course, LectureTime
from .models import TimeTable


class LectureTimeSerializer(serializers.ModelSerializer):
    day = serializers.ChoiceField(choices=LectureTime.DAY_CHOICES)
    start = serializers.IntegerField(max_value=2400,min_value=0)
    end = serializers.IntegerField(max_value=2400, min_value=0)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    class Meta:
        model = LectureTime
        exclude = (
            'id',
            'lecture',
        )

    def validate(self, data):
        if data.get('start') >= data.get('end'):
            raise FieldError('수업 시작시간이 종료시간보다 늦을 수 없습니다.')
        return data


class LectureSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    lecture_time = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = (
            'id',
            'title',
            'instructor',
            'credits',
            'lecture_time',
        )

    def get_title(self, lecture):
        return lecture.course.title

    def get_instructor(self, lecture):
        return lecture.course.instructor

    def get_lecture_time(self, lecture):
        return LectureTimeSerializer(lecture.lecturetime_set, many=True).data


class TimeTableSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, max_length=30)
    private = serializers.ChoiceField(required=False, choices=TimeTable.PRIVATE_CHOICES)
    is_default = serializers.BooleanField(required=False)

    semester = serializers.SerializerMethodField()
    lecture = serializers.SerializerMethodField()
    credit_total = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = (
            'id',
            'semester',
            'name',
            'is_default',
            'credit_total',
            'private',
            'created_at',
            'updated_at',
            'lecture',
        )

    def get_credit_total(self, timetable):
        total = 0
        for credit in timetable.lecture.all().values_list('credits',flat=True):
            total += credit
        return total

    def get_lecture(self, timetable):
        return LectureSerializer(timetable.lecture.all(), many=True).data

    def get_semester(self, timetable):
        return timetable.semester.name

    def validate(self, data):
        return data

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        semester = request.data.get('semester')
        semester = get_object_or_404(Semester, name=semester)
        table_list = TimeTable.objects.filter(user=user, semester=semester).values_list('name', flat=True)

        success = False
        i = 1
        while not success:
            if f'시간표 {i}' in table_list:
                i += 1
            else:
                timetable = TimeTable.objects.create(user=user, semester=semester, name=f'시간표 {i}')
                success = True

        return timetable

    def update(self, timetable, validated_data):
        request = self.context['request']
        user = request.user
        name = validated_data.get('name')
        private = validated_data.get('private')
        is_default = validated_data.get('is_default')
        queryset = TimeTable.objects.filter(user=user, semester=timetable.semester)
        
        if is_default is True:
            try:
                default_timetable = queryset.get(is_default=True)
                default_timetable.is_default = False
                default_timetable.save()
            except:
                timetable.is_default = True
                timetable.save()
                pass
            timetable.is_default = True
            
        if name:
            if name in queryset.exclude(id=timetable.id).values_list('name', flat=True):
                raise DuplicationError('같은 이름의 시간표가 이미 존재합니다.')
            timetable.name = name
            
        if private:
            timetable.private = private
            
        timetable.save()
        return timetable


class TimeTableListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeTable
        fields = (
            'id',
            'name',
            'is_default',
            'private',
            'created_at',
            'updated_at',
        )


class SelfLectureCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=35)
    instructor = serializers.CharField(max_length=50)

    def validate_time(self, value):
        if len(value.split('/')) != 4:
            raise serializers.ValidationError('time 필드의 값이 부적절합니다.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        data = dict(request.data)
        time_list = data.get('time')
        if not time_list or len(time_list)==0:
            raise FieldError('time값을 입력해주세요')
        timetable = self.context['timetable']
        
        course = Course.objects.create(title=validated_data.get('title'),instructor=validated_data.get('instructor'), self_made=True)
        lecture = Lecture.objects.create(
            course=course, semester=timetable.semester, classification='/',
            degree='.', course_code='.', grade=0, lecture_code=0, credits=0, lecture=0, 
            laboratory=0, cart=0, quota=0
        )
        for time in time_list:
            t = time.split('/')
            day = t[0]
            start = int(t[1])
            end = int(t[2])
            location = t[3]
            data = {'day': day, 'start': start, 'end': end, 'location': location}
            serializer = LectureTimeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            LectureTime.objects.create(**data, lecture=lecture)

        existing_lectures = timetable.lecture.all()
        existing_time_set = LectureTime.objects.filter(lecture__in=existing_lectures).all()
        new_time_set = lecture.lecturetime_set.all()

        for new_time in new_time_set:
            existing_time_set = existing_time_set.filter(day=new_time.day)
            for existing_time in existing_time_set:
                if new_time.start >= existing_time.end or new_time.end <= existing_time.start:
                    pass
                else:
                    raise FieldError('같은 시간에 이미 수업이 있습니다.')
        
        return lecture


class FriendTimeTableListSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = (
            'id',
            'name',
            'semester',
            'is_default',
            'private',
            'created_at',
            'updated_at',
        )

    def get_semester(self, timetable):
        return timetable.semester.name