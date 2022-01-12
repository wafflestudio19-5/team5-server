from rest_framework import serializers


class ExamInfoSerializer(serializers.Modelserializer):
    is_mine = serializers.SerializerMethodField()
