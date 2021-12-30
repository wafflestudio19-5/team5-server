import urllib.parse

from django.db import IntegrityError
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from django.shortcuts import redirect
from rest_auth.registration.views import SocialLoginView

from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserLoginSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import User
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import JsonResponse
import requests
from rest_framework import status
from json.decoder import JSONDecodeError


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

# Code chunks below are mostly from https://medium.com/chanjongs-programming-diary/django-rest-framework로-소셜-로그인-api-구현해보기-google-kakao-github-2ccc4d49a781
BASE_URL = 'http://127.0.0.1:8000/'
NAVER_CALLBACK_URI = BASE_URL + 'user/naver/callback/'
STATE = 'random_string'
CLIENT_ID = "qlDWX9G2YwKHuTKXttsR"
CLIENT_SECRET = "mRBFTWOJN2"

def naver_login(request):
    return redirect(f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={CLIENT_ID}&state={STATE}&redirect_uri={NAVER_CALLBACK_URI}")

def naver_callback(request):
    code = request.GET.get('code')
    # access token 받아오기
    token_req = requests.post(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&state={STATE}"
    )
    token_req_json = token_req.json()
    error = token_req_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    # access token 바탕으로 정보 가져오기
    # AccessToken 값은 일부 특수문자가 포함되어 있기 때문에 GET Parameter를 통하여 데이터를 전달하는 경우, AccessToken 값을 반드시 URL Encode 처리한 후에 전송하여야합니다.
    access_token = urllib.parse.quote(access_token)
    email_req = requests.get('https://openapi.naver.com/v1/nid/me', headers={'Authorization': '{} {}'.format('Bearer', access_token)})
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    # Sign in 또는 Sign up
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 naver가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
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
    except User.DoesNotExist:
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


# https://funncy.github.io/django/2020/04/24/django-jwt/
class NaverLogin(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/user/naver/callback/'
    client_class = OAuth2Client

# https://swarf00.github.io/2018/12/19/social-login.html
# class SocialLoginCallbackView(NaverLoginMixin, View):
#
#     success_url = settings.LOGIN_REDIRECT_URL
#     failure_url = settings.LOGIN_URL
#     required_profiles = ['email', 'name']
#     model = get_user_model()
#
#     def get(self, request, *args, **kwargs):
#
#         provider = kwargs.get('provider')
#
#         if provider == 'naver': # 프로바이더가 naver 일 경우
#             csrf_token = request.GET.get('state')
#             code = request.GET.get('code')
#             if not _compare_salted_tokens(csrf_token, request.COOKIES.get('csrftoken')): # state(csrf_token)이 잘못된 경우
#                 messages.error(request, '잘못된 경로로 로그인하셨습니다.', extra_tags='danger')
#                 return HttpResponseRedirect(self.failure_url)
#             is_success, error = self.login_with_naver(csrf_token, code)
#             if not is_success: # 로그인 실패할 경우
#                 messages.error(request, error, extra_tags='danger')
#             return HttpResponseRedirect(self.success_url if is_success else self.failure_url)
#
#         return HttpResponseRedirect(self.failure_url)
#
#     def set_session(self, **kwargs):
#         for key, value in kwargs.items():
#             self.request.session[key] = value
#
# class NaverLoginMixin:
#     naver_client = NaverClient()
#
#     def login_with_naver(self, state, code):
#
#         # 인증토근 발급
#         is_success, token_infos = self.naver_client.get_access_token(state, code)
#
#         if not is_success:
#             return False, '{} [{}]'.format(token_infos.get('error_desc'), token_infos.get('error'))
#
#         access_token = token_infos.get('access_token')
#         refresh_token = token_infos.get('refresh_token')
#         expires_in = token_infos.get('expires_in')
#         token_type = token_infos.get('token_type')
#
#         # 네이버 프로필 얻기
#         is_success, profiles = self.get_naver_profile(access_token, token_type)
#         if not is_success:
#             return False, profiles
#
#         # 사용자 생성 또는 업데이트
#         user, created = self.model.objects.get_or_create(email=profiles.get('email'))
#         if created:  # 사용자 생성할 경우
#             user.set_password(None)
#         user.name = profiles.get('name')
#         user.is_active = True
#         user.save()
#
#         # 로그인
#         login(self.request, user, 'user.oauth.backends.NaverBackend')  # NaverBackend 를 통한 인증 시도
#
#         # 세션데이터 추가
#         self.set_session(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in,
#                          token_type=token_type)
#
#         return True, user
#
#     def get_naver_profile(self, access_token, token_type):
#         is_success, profiles = self.naver_client.get_profile(access_token, token_type)
#
#         if not is_success:
#             return False, profiles
#
#         for profile in self.required_profiles:
#             if profile not in profiles:
#                 return False, '{}은 필수정보입니다. 정보제공에 동의해주세요.'.format(profile)
#
#         return True, profiles