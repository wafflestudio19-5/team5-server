from django.db.models import Avg
from rest_framework import serializers

import re

from lecture.models import Course, LectureEvaluation


class CourseForEvalSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()
    sem_options = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'instructor',
            'semester',
            'sem_options',
        )

    def get_semester(self, course):
        semester = ""
        sem = self.context['sem']
        if sem is not None:
            for i in range(len(sem)-1):
                num = re.findall(r'\d+', sem[i])
                semester += (num[0]+"-"+num[1]+", ")

            num = re.findall(r'\d+', sem[len(sem)-1])
            semester += (num[0]+"-"+num[1])

        return semester

    def get_sem_options(self, course):
        return self.context['sem']


class EvalListSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField(read_only=True)
    semester = serializers.SerializerMethodField(read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LectureEvaluation
        fields = (
            'id',
            'course',
            'rating',
            'semester',
            'content',
            'is_mine',
            'num_of_likes'
        )

    def get_course(self, obj):
        return obj.course.title + " : " + obj.course.instructor

    def get_semester(self, obj):
        sem = obj.semester.name
        return sem[2:] + " 수강자"

    def get_is_mine(self, obj):
        if obj.writer == self.context['user']:
            return True
        return False


class EvalCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = LectureEvaluation
        exclude = ['course', 'like_users', 'num_of_likes']

    def validate(self, data):
        content = data.get('content')
        if content is None or len(content) < 20:
            raise serializers.ValidationError("좀 더 성의있는 내용 작성을 부탁드립니다 :)")

        return data

    def create(self, validated_data):
        eval = LectureEvaluation.objects.create(**validated_data)
        return eval


class CourseSearchSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'instructor',
            'rating'
        )

    def get_rating(self, course):
        evals = LectureEvaluation.objects.filter(course=course)

        if not evals.exists():
            return 0

        avg_rating = round(evals.aggregate(Avg('rating')).get('rating__avg'), 1)
        return avg_rating


# class ExamInfoSerializer(serializers.Modelserializer):
#     is_mine = serializers.SerializerMethodField()
