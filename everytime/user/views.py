from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError

from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from .models import User
from .serializers import UserCreateSerializer, UserLoginSerializer, jwt_token_of
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import requests

class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(request_body=UserCreateSerializer, responses={201: 'user, token'})
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT, data='DATABASE ERROR : 서버 관리자에게 문의주세요.')

        return Response({
            'user' : user.username,
            'token' : jwt_token
        }, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(request_body=UserLoginSerializer, responses={200: 'success, token'})
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)

class KaKaoLoginView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        REST_API_KEY = '4c3c166a3ec7e5a2da86cb7f358a1a17'
        REDIRECT_URI = 'http://localhost:8000/user/kakao/callback/'

        API_HOST = f'https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code'
        try:
            if request.user.is_authenticated:
                raise SocialLoginException("User already logged in")

            return redirect(API_HOST)
        except KakaoException as error:
            messages.error(request, error)
            return redirect("user:login")
        except SocialLoginException as error:
            messages.error(request, error)
            return redirect("user:login")


def kakao_callback(request):
    # return HttpResponse('로그인 실패')
    try:
        code = request.GET.get("code")
        REST_API_KEY = '4c3c166a3ec7e5a2da86cb7f358a1a17'
        REDIRECT_URI = 'http://localhost:8000/user/kakao/callback/'
        token_response = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&code={code}"
        )
        token_json = token_response.json()

        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException()

        access_token = token_json.get("access_token")

        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        email = profile_json.get("kakao_account", None).get("email")
        if email is None:
            raise KakaoException()
        # properties = profile_json.get("properties")
        # nickname = properties.get("nickname")
        # profile_image = properties.get("profile_image")

        try:
            user = User.objects.get(email=email)
            # if user.login_method != User.LOGIN_KAKAO:
            #     raise KakaoException()
        except User.DoesNotExist:
            return HttpResponse('소셜 로그인용 가입 페이지')
            # user = User.objects.create(
            #     email=email,
            #     username=email,
            #     first_name=nickname,
            #     login_method=User.LOGIN_KAKAO,
            #     email_verified=True,
            # )
            # user.set_unusable_password()
            # user.save()
        return JsonResponse({
            'username' : user.username,
            'token' : jwt_token_of(user)
        })
    except KakaoException:
        return HttpResponse('Login failed')


class KakaoException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'bad_request'
    default_detail = 'KakaoException'

class SocialLoginException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'bad_request'
    default_detail = 'SocialLoginException'

