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

from .serializers import UserCreateSerializer, UserLoginSerializer
from drf_yasg.utils import swagger_auto_schema

from .models import User, SocialAccount
from django.http import JsonResponse
import requests
from rest_framework import status


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
NAVER_CALLBACK_URI = BASE_URL + 'user/naver/callback/'
CLIENT_ID = "qlDWX9G2YwKHuTKXttsR"
CLIENT_SECRET = "mRBFTWOJN2"


def naver_login(request):
    # Create random state
    STATE = ''.join((random.choice(string.digits)) for x in range(10))
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={CLIENT_ID}&state={STATE}&redirect_uri={NAVER_CALLBACK_URI}"
    )


def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    # access token 받아오기
    token_req = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&state={state}"
    )
    token_req_json = token_req.json()

    # token을 제대로 받아오지 못했다면
    if not token_req.ok:
        messages.error(request, token_req_json.get('error'), extra_tags='danger')
        return redirect('http://127.0.0.1:8000/user/naver/login/') # 로그인하는 화면으로 redirect, 주소는 달라져야할듯?

    access_token = token_req_json.get('access_token')
    refresh_token = token_req_json.get('refresh_token')

    # access token 바탕으로 정보 가져오기
    header = "Bearer " + access_token
    url = "https://openapi.naver.com/v1/nid/me"
    request = urllib.request.Request(url)
    request.add_header("Authorization", header)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if rescode != 200:
        messages.error(request, "Error Code:" + rescode, extra_tags='danger')
        return redirect('http://127.0.0.1:8000/user/naver/login/')  # 로그인하는 화면으로 redirect, 주소는 달라져야할듯?
    else:
        profile_req_json = json.loads(response.read().decode('utf-8'))

    id = profile_req_json.get('id')

    # Sign in 또는 Sign up
    try:
        social_account = SocialAccount.objects.get(id=id, provider='naver')
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'naver':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 naver로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}user/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except SocialAccount.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}user/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class SocialLoginException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'bad_request'
    default_detail = 'SocialLoginException'