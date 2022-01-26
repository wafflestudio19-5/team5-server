from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.conf import settings
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError

import requests
import json
import string
import urllib.parse
import random


from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from everytime import permissions
from everytime.exceptions import AlreadyLogin, SocialLoginError, DatabaseError, FieldError, DuplicationError
from everytime.utils import AccessToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from json.decoder import JSONDecodeError

from lecture.models import Point, Semester
from timetable.models import TimeTable
from .models import User, SocialAccount
from .serializers import UserCreateSerializer, UserLoginSerializer, SocialUserCreateSerializer, UserProfileSerializer, UserProfileUpdateSerializer, jwt_token_of, SchoolMailVerifyService
from .utils import email_verification_token, message

from post.serializers import PostSerializer
from post.models import Post


class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UserCreateSerializer, responses={201: 'user, token'})
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            raise DatabaseError()

        semesters = Semester.objects.all()
        for semester in semesters:
            TimeTable.objects.create(semester=semester, user=user, is_default=True, name='시간표 1')
        return Response({
            'user': user.username,
            'token': jwt_token
        }, status=status.HTTP_201_CREATED)

class UserDeleteAccountView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        serializer = UserLoginSerializer(data={
            "username": request.user.username,
            "password": request.data.get('password', None)
        })
        try:
            serializer.is_valid(raise_exception=True)
        except:
            raise FieldError("계정 비밀번호가 올바르지 않습니다.")
        else:
            refresh_token = RefreshToken(request.data.get('refresh'))
            access_token = AccessToken(request.META.get('HTTP_AUTHORIZATION').split()[1])
            refresh_token.blacklist()
            access_token.blacklist()
            request.user.delete()
            return Response("정상적으로 회원탈퇴가 완료되었습니다.")



class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UserLoginSerializer, responses={200: 'success, token'})
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)

class UserLogoutView(APIView):
    permission_classes(permissions.IsAuthenticated, )

    def post(self, request):
        refresh_token = RefreshToken(request.data.get('refresh'))
        access_token = AccessToken(request.META.get('HTTP_AUTHORIZATION').split()[1])
        refresh_token.blacklist()
        access_token.blacklist()
        return Response("Success")


class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response(UserProfileSerializer(user).data, status=200)

    def patch(self, request):
        user = request.user
        data = request.data
        serializer = UserProfileUpdateSerializer(user, data=data, context={'user':user})
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return DatabaseError()

        return Response(UserProfileSerializer(user).data, status=200)


class KaKaoLoginView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        REST_API_KEY = getattr(settings, 'SOCIAL_AUTH_KAKAO_SECRET')
        # BASE_URL = getattr(settings, 'BASE_URL')
        REDIRECT_URI = 'http://d2hw7p0vhygoha.cloudfront.net/social/kakao'

        API_HOST = f'https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code'
        if request.user.is_authenticated:
            raise AlreadyLogin()

        return redirect(API_HOST)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def kakao_callback(request):
    # return HttpResponse('로그인 실패')
    code = request.data.get("code")
    REST_API_KEY = getattr(settings, 'SOCIAL_AUTH_KAKAO_SECRET')
    # BASE_URL = getattr(settings, 'BASE_URL')
    REDIRECT_URI = 'http://d2hw7p0vhygoha.cloudfront.net/social/kakao'
    token_response = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&code={code}"
    )
    token_json = token_response.json()

    error = token_json.get("error", None)
    if error is not None:
        raise SocialLoginError(error)

    access_token = token_json.get("access_token")

    profile_req = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_req_status = profile_req.status_code
    if profile_req_status != 200:
        raise SocialLoginError('프로필 정보를 가져오는 데에 실패하였습니다.')
    profile_json = profile_req.json()
    email = profile_json.get("kakao_account").get("email")
    social_id = int(profile_json.get('id', -1))
    try:
        social_account = SocialAccount.objects.get(social_id=social_id, provider='kakao')
        user = social_account.user
        jwt_token = jwt_token_of(user)
        return JsonResponse({
            'login': True,
            'social_user': social_id, # -> username으로 사용
            'token': jwt_token
        })
    except SocialAccount.DoesNotExist:
        # 가입이 안 된 유저일 때 별도 가입페이지로 redirect하는 처리를 추가로 해줄 예정
        return JsonResponse({
            'login': False,
            'social_id': social_id,
            'email': email,
            'provider': 'kakao'
        })


      




class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        """
        Code Request
        """
        BASE_URL = getattr(settings, 'BASE_URL')
        GOOGLE_CALLBACK_URI = 'http://d2hw7p0vhygoha.cloudfront.net/social/google'
        scope = "https://www.googleapis.com/auth/userinfo.profile" + \
                " https://www.googleapis.com/auth/userinfo.email"
        client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        if request.user.is_authenticated:
            raise AlreadyLogin()

        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def google_callback(request):
    state = getattr(settings, 'STATE')
    BASE_URL = getattr(settings, 'BASE_URL')
    GOOGLE_CALLBACK_URI = 'http://d2hw7p0vhygoha.cloudfront.net/social/google'
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.data.get('code')
    """ 
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise SocialLoginError(error)
    access_token = token_req_json.get('access_token')
    """
    Profile Request
    """
    profile_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}")
    profile_req_status = profile_req.status_code
    if profile_req_status != 200:
        raise SocialLoginError('프로필 정보를 가져오는 데에 실패하였습니다.')
    profile_req_json = profile_req.json()
    social_id = profile_req_json.get('id')
    email = profile_req_json.get('email')

    """
    Signup or Signin Request
    """
    try:
        social_account = SocialAccount.objects.get(social_id=social_id, provider='google')
        user = social_account.user
        jwt_token = jwt_token_of(user)
        return JsonResponse({
            'login': True,
            'social_user': social_id, # -> username으로 사용
            'token': jwt_token
        })
    except SocialAccount.DoesNotExist:
        return JsonResponse({
            'login': False,
            'social_id': social_id,
            'email': email,
            'provider': 'google'
        })

      
# Code chunks below are mostly from https://medium.com/chanjongs-programming-diary/django-rest-framework로-소셜-로그인-api-구현해보기-google-kakao-github-2ccc4d49a781


class NaverLoginView(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        BASE_URL = getattr(settings, 'BASE_URL')
        NAVER_CALLBACK_URI = 'http://d2hw7p0vhygoha.cloudfront.net/social/naver'
        CLIENT_ID = getattr(settings, 'SOCIAL_AUTH_NAVER_CLIENT_ID')
        if request.user.is_authenticated:
            raise AlreadyLogin()
        # Create random state
        STATE = ''.join((random.choice(string.digits)) for x in range(15))
        request.session['original_state'] = STATE
        return redirect(
            f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={CLIENT_ID}&state={STATE}&redirect_uri={NAVER_CALLBACK_URI}"
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def naver_callback(request):
    CLIENT_ID = getattr(settings, 'SOCIAL_AUTH_NAVER_CLIENT_ID')
    CLIENT_SECRET = getattr(settings, 'SOCIAL_AUTH_NAVER_SECRET')
    code = request.data.get('code')
    state = request.data.get('state')
    # original_state = request.session.get('original_state')

    # state token 검증 - 수정필요
    # https://developers.naver.com/docs/login/web/web.md
    # if state != original_state:
    #     messages.error(request, '잘못된 경로로 로그인을 시도하셨습니다.', extra_tags='danger')
    #     return redirect('user:login') # 로그인하는 화면으로 redirect, 이후 수정

    # access token 받아오기
    token_req = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&state={state}"
    )
    token_req_json = token_req.json()

    # token을 제대로 받아오지 못했다면
    if not token_req.ok:
        raise SocialLoginError(token_req_json.get('error'))

    access_token = token_req_json.get('access_token')
    print(access_token)
    # access token 바탕으로 정보 가져오기
    access_token = urllib.parse.quote(access_token)
    profile_req = requests.get('https://openapi.naver.com/v1/nid/me', headers={'Authorization': '{} {}'.format('Bearer', access_token)})
    profile_req_status = profile_req.status_code
    if profile_req_status != 200:
        raise SocialLoginError('프로필 정보를 가져오는 데에 실패하였습니다.')

    profile_req_json = profile_req.json()['response']
    social_id = profile_req_json.get('id')
    email = profile_req_json.get('email')

    # Sign in 또는 Sign up
    try:
        social_account = SocialAccount.objects.get(social_id=social_id, provider='naver')
        user = social_account.user
        jwt_token = jwt_token_of(user)
        return JsonResponse({
            'login': True,
            'social_user': social_id, # -> username으로 사용
            'token': jwt_token
        })
    except SocialAccount.DoesNotExist:
        return JsonResponse({
            'login': False,
            'social_id': social_id,
            'email': email,
            'provider': 'naver'
        })


class SocialUserSignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # 해당 소셜 계정으로 이미 가입이 되어있는지 체크 - 사실 정상적인 경로를 통해 유입되었다면 이 signup이 아니라 login으로 연결되었을 것
        data = request.data
        social_id = data.get('social_id')
        provider = data.get('provider')
        if SocialAccount.objects.filter(social_id=social_id, provider=provider).exists():
            raise DuplicationError("이미 존재하는 소셜 계정 유저입니다.")

        # requests.data의 'email'에 대한 전제사항
        # 소셜로그인 callback 함수에서 JsonResponse로 반환된 email이 None이 아니라면, 그 값을 가짐 (사용자가 따로 입력할 수 없도록 프론트단에서 처리)
        # None이었다면 사용자에게 입력을 받은 이메일 값을 가짐

        # 이메일 중복 처리 - 소셜계정의 이메일로 이미 일반 회원가입을 한 상태일 때, 소셜 계정을 기존회원정보와 연동
        social_email = data.get('email')
        if not social_email:
            raise FieldError("이메일을 입력하세요.")
        if User.objects.filter(email=social_email).exists():
            user = User.objects.get(email=social_email)
            SocialAccount.objects.create(social_id=social_id, provider=provider, user=user)
            return Response({
                'notice': '동일한 이메일로 가입한 이력이 존재하여 기존 계정과 소셜 계정을 연동하였습니다. 기존 로그인과 소셜로그인을 모두 활용할 수 있습니다.',
                'user': user.username,
                'social_id': social_id,
                'token': jwt_token_of(user)
            }, status=status.HTTP_201_CREATED)

        # 이메일이 중복되지 않는 경우 (해당 이메일로 아예 처음 가입하는 경우)
        serializer = SocialUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['social_id'] = data.get('social_id')
        serializer.validated_data['provider'] = data.get('provider')
        serializer.validated_data['email'] = data.get('email')

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            raise DatabaseError()

        semesters = Semester.objects.all()
        for semester in semesters:
            TimeTable.objects.create(semester=semester, user=user, is_default=True, name='시간표 1')

        return Response({
            'social_user': user.username,   # social_id 값임
            'token': jwt_token
        }, status=status.HTTP_201_CREATED)


class VerifyingMailSendView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.school_email is not None:
            raise DuplicationError("이미 학교 인증을 마친 계정입니다.")

        data = request.data
        SchoolMailVerifyService(data=data).is_valid(raise_exception=True)
        email = data['email']
        if User.objects.filter(school_email=email).exists():
            raise FieldError('해당 메일로 인증된 계정이 이미 존재합니다. 다른 계정을 확인해주세요.')
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        emailb64 = urlsafe_base64_encode(force_bytes(email))
        token = email_verification_token.make_token(user)
        message_data = message(uidb64, token, emailb64)

        mail_title = "Team5_EveryTime 학교 인증 메일입니다."
        mail_to = email
        email = EmailMessage(mail_title, message_data, to=[mail_to])
        email.send()

        return JsonResponse({"message": "SUCCESS"}, status=200)


class VerifyingMailAcceptView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token, emailb64):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            email = force_text(urlsafe_base64_decode(emailb64))
            user = User.objects.get(pk=uid)
            if email_verification_token.check_token(user, token):
                user.school_email = email
                user.save()
                Point.objects.create(user=user.school_email, reason='기본 포인트 지급', point=20)
                return JsonResponse({"verify": "SUCCESS"}, status=200)

            raise FieldError("AUTH FAIL")

        except ValidationError:
            raise FieldError("TYPE_ERROR")
        except KeyError:
            raise FieldError("INVALID_KEY")


class UserScrapView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PostSerializer

    def get(self, request):
        user = request.user
        queryset = user.scrap_post.order_by('-id')
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)


class UserPostView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PostSerializer

    def get(self, request):
        user = request.user
        queryset = user.post_set.order_by('-id')
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)


class UserCommentView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PostSerializer

    def get(self, request):
        user = request.user
        queryset = Post.objects.filter(id__in=user.comment_set.values("post")).order_by('-id')
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)
