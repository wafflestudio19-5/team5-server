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
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    nickname = serializers.CharField(required=True)
    studentid = serializers.CharField(required=False, validators=[RegexValidator(regex=r'^\d\d\d\d-\d\d\d\d\d$', message='학번 포맷을 확인해주세요.')])
    university = serializers.CharField(required=False)

    def validate(self, data):
        return data

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        nickname = validated_data.get('nickname')
        studentid = validated_data.get('studentid')
        university = validated_data.get('university')

        user = User.objects.create_user(username, email, password, nickname=nickname, studentid=studentid, university=university)
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
            raise serializers.ValidationError('아이디 또는 비밀번호를 확인하십시오.')

        return {
            'username' : user.username,
            'token' : jwt_token_of(user)
        }

