from rest_framework import serializers

from lecture.models import Course


class CourseForEvalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'title',
            'instructor',
            'semester',
        )


# class ExamInfoSerializer(serializers.Modelserializer):
#     is_mine = serializers.SerializerMethodField()
