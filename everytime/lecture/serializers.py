from django.db.models import Avg
from rest_framework import serializers

import re

from lecture.models import Course, LectureEvaluation, ExamInfo


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


class MyCourseSerializer(serializers.ModelSerializer):
    is_evaluated = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'instructor',
            'is_evaluated',
        )

    def get_is_evaluated(self, course):
        if course.lectureevaluation_set.filter(writer=self.context['user']).exists():
            return True
        else:
            return False


class ExamInfoCreateSerializer(serializers.ModelSerializer):
    types = serializers.ListSerializer(required=False, child=serializers.ChoiceField(choices=ExamInfo.EXAM_TYPE_CHOICES), allow_empty=False)
    examples = serializers.ListSerializer(child=serializers.CharField(max_length=255), allow_empty=False)

    class Meta:
        model = ExamInfo
        exclude = ['course', 'readable_users', 'num_of_likes', 'like_users']

    def validate(self, data):
        strategy = data.get('strategy')
        if len(strategy) < 20:
            raise serializers.ValidationError("시험 전략에 대해 좀 더 성의있는 작성을 부탁드립니다 :)")

        examples = ""
        ex_input = data.get('examples') # validation 통과해야해서 무조건 존재하긴 함 (빈 배열도 불가)
        for i in range(len(ex_input)-1):
            examples += ex_input[i]
            examples += '\t'
        examples += ex_input[len(ex_input)-1]
        data['examples'] = examples

        return data

    def create(self, validated_data):
        info = ExamInfo.objects.create(**validated_data)
        return info


class ExamInfoListSerializer(serializers.ModelSerializer):
    exam = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()
    types = serializers.SerializerMethodField()
    examples = serializers.SerializerMethodField()

    class Meta:
        model = ExamInfo
        fields = (
            'id',
            'exam',
            'semester',
            'strategy',
            'types',
            'examples',
            'is_mine',
            'num_of_likes',
        )

    def get_exam(self, obj):
        return dict(ExamInfo.EXAM_CHOICES)[obj.exam]

    def get_semester(self, obj):
        sem = obj.semester.name
        return sem[2:] + " 수강자"

    def get_is_mine(self, obj):
        if obj.writer == self.context['user']:
            return True
        return False

    def get_types(self, obj):
        if not obj.types.exists():
            return None

        result = ""
        types = obj.types.all()
        for i in range(len(types)-1):
            result += (types[i].type + ", ")

        result += types.last().type
        return result

    def get_examples(self, obj):
        return obj.examples.split('\t')
