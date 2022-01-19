from rest_framework import serializers

from lecture.models import Course, Lecture
from timetable.serializers import LectureTimeSerializer


class CourseForEvalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'title',
            'instructor',
            'semester',
        )


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = (
            'title',
            'instructor'
        )


class LectureSearchSerializer(serializers.ModelSerializer):
    lecture_time = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        exclude = ('self_made',)

    def get_lecture_time(self, lecture):
        lecture_time_set = lecture.lecturetime_set.all()
        return LectureTimeSerializer(lecture_time_set, many=True).data

    def get_course(self, lecture):
        return CourseSerializer(lecture.course).data
# class ExamInfoSerializer(serializers.Modelserializer):
#     is_mine = serializers.SerializerMethodField()
