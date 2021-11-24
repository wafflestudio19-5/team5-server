from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError

from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UserCreateSerializer, UserLoginSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(request_body=UserCreateSerializer,)
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, jwt_token = serializer.save()
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT, data='이미 존재하는 유저입니다.')

        return Response({
            'user' : user.username,
            'token' : jwt_token
        }, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny, )

    @swagger_auto_schema(request_body=UserLoginSerializer, responses={201:'success, token'})
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)
