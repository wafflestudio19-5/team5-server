import json
import string
import urllib.parse
import random
from django.contrib import messages

from django.db import IntegrityError
from django.shortcuts import redirect

from rest_framework import status, viewsets, permissions
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserLoginSerializer, SocialUserCreateSerializer
from drf_yasg.utils import swagger_auto_schema

from .models import User, SocialAccount
from django.http import JsonResponse
import requests
from rest_framework import status
from rest_framework_jwt.settings import api_settings

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


def jwt_token_of(user):
    payload = JWT_PAYLOAD_HANDLER(user)
    jwt_token = JWT_ENCODE_HANDLER(payload)
    return jwt_token


class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UserCreateSerializer, responses={201: 'user, token'})
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT, data='DATABASE ERROR : 서버 관리자에게 문의주세요.')

        return Response({
            'user': user.username,
            'token': jwt_token
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UserLoginSerializer, responses={200: 'success, token'})
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)


# Code chunks below are mostly from https://medium.com/chanjongs-programming-diary/django-rest-framework로-소셜-로그인-api-구현해보기-google-kakao-github-2ccc4d49a781
BASE_URL = 'http://127.0.0.1:8000/'
NAVER_CALLBACK_URI = BASE_URL + 'user/naver/login/callback/'
CLIENT_ID = "qlDWX9G2YwKHuTKXttsR"
CLIENT_SECRET = "mRBFTWOJN2"


def naver_login(request):
    if request.user.is_authenticated:
        messages.error(request, '이미 로그인된 유저입니다.')
        return redirect(BASE_URL)
    # Create random state
    STATE = ''.join((random.choice(string.digits)) for x in range(15))
    request.session['original_state'] = STATE
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={CLIENT_ID}&state={STATE}&redirect_uri={NAVER_CALLBACK_URI}"
    )


def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    original_state = request.session.get('original_state')

    # state token 검증
    # https://developers.naver.com/docs/login/web/web.md
    if state != original_state:
        messages.error(request, '잘못된 경로로 로그인을 시도하셨습니다.', extra_tags='danger')
        return redirect('user:login') # 로그인하는 화면으로 redirect, 이후 수정

    # access token 받아오기
    token_req = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&state={state}"
    )
    token_req_json = token_req.json()

    # token을 제대로 받아오지 못했다면
    if not token_req.ok:
        messages.error(request, token_req_json.get('error'), extra_tags='danger')
        return redirect('user:login')

    access_token = token_req_json.get('access_token')
    # access token 바탕으로 정보 가져오기
    access_token = urllib.parse.quote(access_token)
    profile_req = requests.get('https://openapi.naver.com/v1/nid/me', headers={'Authorization': '{} {}'.format('Bearer', access_token)})
    profile_req_status = profile_req.status_code
    if profile_req_status != 200:
        messages.error(request, '프로필 정보를 가져오는 데에 실패하였습니다.', extra_tags='danger')
        return redirect('user:login')

    profile_req_json = profile_req.json()['response']
    social_id = profile_req_json.get('id')
    email = profile_req_json.get('email')
    profile_pic = profile_req_json.get('profile_image', None)
    nickname = profile_req_json.get('nickname', None)

    # Sign in 또는 Sign up
    try:
        social_account = SocialAccount.objects.get(social_id=social_id, provider='naver')
        user = social_account.user
        jwt_token = jwt_token_of(user)
        return JsonResponse({
            'login': True,
            'social_user': social_id,
            'token': jwt_token
        })
    except SocialAccount.DoesNotExist:
        return JsonResponse({
            'login': False,
            'social_id': social_id,
            'email': email,
            'profile_pic': profile_pic,
            'nickname': nickname,
            'provider' : 'naver'
        })


class SocialUserSignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = SocialUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT, data='DATABASE ERROR : 서버 관리자에게 문의주세요.')

        return Response({
            'user': user.username,
            'token': jwt_token
        }, status=status.HTTP_201_CREATED)