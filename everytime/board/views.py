from django.shortcuts import render, get_object_or_404

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
        # 하위 게시판이 아닌 일반 게시판만 불러옴
        boards = Board.objects.filter(head_board=None)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class SubBoardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # 특정 게시판의 하위 게시판들을 불러옴
    def get(self, request, pk=None):
        board = get_object_or_404(Board, pk=pk)
        sub_boards = board.sub_boards.all()
        serializer = BoardSerializer(sub_boards, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
