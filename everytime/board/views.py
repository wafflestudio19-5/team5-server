from django.shortcuts import render

from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Board
from .serializers import BoardSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class BoardView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        if user.is_staff is not True:
            raise exceptions.ValidationError(detail='staff만 Board를 생성할 수 있습니다.')
        serializer = BoardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(BoardSerializer(board).data, status.HTTP_201_CREATED)

    def get(self, request):
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
