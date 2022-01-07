from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.core.validators import RegexValidator
from rest_framework import serializers
# 더 이상 안 쓰는 API임 (simple JWT로 변경함)
# from rest_framework_jwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import SocialAccount

User = get_user_model()
# 더 이상 안 쓰는 API임 (simple JWT로 변경함)
# JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
# JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


def jwt_token_of(user):
    # 더 이상 안 쓰는 API임 (simple JWT로 변경함)
    # payload = JWT_PAYLOAD_HANDLER(user)
    # jwt_token = JWT_ENCODE_HANDLER(payload)
    refresh = RefreshToken.for_user(user)
    jwt_token = {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }
    return jwt_token


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=100)
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, max_length=255)
    nickname = serializers.CharField(required=True, max_length=30)
    univ = serializers.CharField(required=True, max_length=50)
    admission_year = serializers.ChoiceField(choices=User.YEAR_CHOICES, required=True)
    profile_picture = serializers.ImageField(required=False, default="images/profile/default.png")

    def validate(self, data):
        # singup 과정에서 validate 함수 만들기
        pw1 = data.get('password1')
        pw2 = data.get('password2')
        if pw1 != pw2:
            raise serializers.ValidationError('입력한 두 비밀번호가 다릅니다. 비밀번호를 확인해주세요.')

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
            user = User.objects.get(email=email)
            if SocialAccount.objects.filter(user=user).exists():
                # 해당 이메일을 활용하여 소셜로그인/가입을 먼저 한 경우
                raise serializers.ValidationError('소셜계정으로 가입된 이메일입니다. 소셜로그인을 활용해주세요.')
            else:
                raise serializers.ValidationError('이미 존재하는 이메일입니다.')
        if queryset.filter(nickname=nickname).exists():
            raise serializers.ValidationError('이미 존재하는 닉네임입니다.')

        return data

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password1')
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


class SocialUserCreateSerializer(serializers.Serializer):
    nickname = serializers.CharField(required=True, max_length=30)
    univ = serializers.CharField(required=True, max_length=50)
    admission_year = serializers.ChoiceField(choices=User.YEAR_CHOICES, required=True)
    profile_picture = serializers.ImageField(required=False, default="images/profile/default.png")

    def validate(self, data):
        # singup 과정에서 validate 함수 만들기
        admission_year = data.get('admission_year')
        if (admission_year, admission_year) not in User.YEAR_CHOICES:
            raise serializers.ValidationError('학번을 올바르게 입력하세요.')

        nickname = data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError('이미 존재하는 닉네임입니다.')

        return data

    def create(self, validated_data):
        username = validated_data.get('social_id')
        provider = validated_data.get('provider')
        email = validated_data.get('email')
        nickname = validated_data.get('nickname')
        admission_year = validated_data.get('admission_year')
        univ = validated_data.get('univ')
        profile_picture = validated_data.get('profile_picture')

        # password를 None으로 설정하면 set_password(None)이 쓰이는데,
        # set_password에 None을 전달하면 set_unusable_password()와 동일
        user = User.objects.create_user(username, email, password=None, nickname=nickname, admission_year=admission_year, univ=univ, profile_picture=profile_picture)
        SocialAccount.objects.create(social_id=username, provider=provider, user=user)
        jwt_token = jwt_token_of(user)
        return user, jwt_token

