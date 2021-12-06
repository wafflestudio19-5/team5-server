from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

User = get_user_model()
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


def jwt_token_of(user):
    payload = JWT_PAYLOAD_HANDLER(user)
    jwt_token = JWT_ENCODE_HANDLER(payload)
    return jwt_token


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=100)
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, max_length=255)
    nickname = serializers.CharField(required=True, max_length=30)
    univ = serializers.CharField(required=True, max_length=50)
    admission_year = serializers.ChoiceField(choices=User.YEAR_CHOICES, required=True)
    profile_picture = serializers.ImageField(required=False, default="images/profile/default.png")

    def validate(self, data):
        # singup 과정에서 validate 함수 만들기
        admission_year = data.get('admission_year')
        if (admission_year, admission_year) not in User.YEAR_CHOICES:
            raise serializers.ValidationError('학번을 올바르게 입력하세요.')

        username = data.get('username')
        email = data.get('email')
        nickname = data.get('nickname')

        queryset = User.objects.filter(username=username) | User.objects.filter(email=email) | User.objects.filter(nickname=nickname)

        if queryset.filter(username=username).exists():
            raise serializers.ValidationError('이미 존재하는 아이디입니다.')
        if queryset.filter(email=email).exists():
            raise serializers.ValidationError('이미 존재하는 이메일입니다.')
        if queryset.filter(nickname=nickname).exists():
            raise serializers.ValidationError('이미 존재하는 닉네임입니다.')

        return data

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        nickname = validated_data.get('nickname')
        admission_year = validated_data.get('admission_year')
        univ = validated_data.get('univ')
        profile_picture = validated_data.get('profile_picture')
        user = User.objects.create_user(username, email, password, nickname=nickname, admission_year=admission_year, univ=univ, profile_picture=profile_picture)
        jwt_token = jwt_token_of(user)
        return user, jwt_token

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('아이디 또는 비밀번호를 확인하세요.')

        return {
            'username' : user.username,
            'token' : jwt_token_of(user)
        }

