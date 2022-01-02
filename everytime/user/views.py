import requests
from django.http import HttpResponse, JsonResponse
from django.core.validators import validate_email
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError

from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from json.decoder import JSONDecodeError
from django.shortcuts import redirect
from rest_framework_jwt.settings import api_settings
from .models import User, SocialAccount
from .serializers import UserCreateSerializer, UserLoginSerializer
from .utils import email_verification_token, message



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


def ping(request):
    return HttpResponse('pong')


state = getattr(settings, 'STATE')
BASE_URL = 'http://127.0.0.1:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'user/google/login/callback/'

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


def jwt_token_of(user):
    payload = JWT_PAYLOAD_HANDLER(user)
    jwt_token = JWT_ENCODE_HANDLER(payload)
    return jwt_token


def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.profile" + \
            " https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):

    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')
    """ 
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    """
    Profile Request
    """
    profile_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}")
    profile_req_status = profile_req.status_code
    if profile_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get profile'}, status=status.HTTP_400_BAD_REQUEST)
    profile_req_json = profile_req.json()
    social_id = profile_req_json.get('id')
    email = profile_req_json.get('email')
    name = profile_req_json.get('name')
    """
    Signup or Signin Request
    """
    try:
        social_account = SocialAccount.objects.get(social_id=social_id, provider='google')
        user = social_account.user
        jwt_token = jwt_token_of(user)
        return JsonResponse({
            'login': True,
            'user': user.username,
            'token': jwt_token
        },json_dumps_params={'ensure_ascii': False})

    except SocialAccount.DoesNotExist:
        return JsonResponse({
            'login': False,
            'social_id': social_id,
            'email': email,
            'name': name
        },json_dumps_params={'ensure_ascii': False})


class VerifyingMailSendView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = request.user
        data = request.data
        email = data['email']
        current_site = get_current_site(request)
        domain = current_site.domain
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        emailb64 = urlsafe_base64_encode(force_bytes(email))
        token = email_verification_token.make_token(user)
        message_data = message(domain, uidb64, token, emailb64)

        mail_title = "Team5_EveryTime 학교 인증 메일입니다."
        mail_to = email
        email = EmailMessage(mail_title, message_data, to=[mail_to])
        email.send()

        return JsonResponse({"message": "SUCCESS"}, status=200)


class VerifyingMailAcceptView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, uidb64, token, emailb64):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            email = force_text(urlsafe_base64_decode(emailb64))
            user = User.objects.get(pk=uid)
            if email_verification_token.check_token(user, token):
                user.school_email = email
                user.save()
                return JsonResponse({"verify": "SUCCESS"}, status=200)

            return JsonResponse({"message":"AUTH FAIL"}, status=400)

        except ValidationError:
            return JsonResponse({"message": "TYPE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({"message": "INVALID_KEY"}, status=400)
