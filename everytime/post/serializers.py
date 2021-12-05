from rest_framework import serializers

from .models import Post, Tag

class PostSerializer(serializers.ModelSerializer):
