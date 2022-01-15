from rest_framework import serializers

from lecture.models import Course, LectureEvaluation


class CourseForEvalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'title',
            'instructor',
            'semester',
        )


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
        exclude = ['course', 'like_users']

    def validate(self, data):
        content = data.get('content')
        if content is None or len(content) < 20:
            raise serializers.ValidationError("좀 더 성의있는 내용 작성을 부탁드립니다 :)")

        return data

    def create(self, validated_data):
        eval = LectureEvaluation.objects.create(**validated_data)
        return eval

# class ExamInfoSerializer(serializers.Modelserializer):
#     is_mine = serializers.SerializerMethodField()
