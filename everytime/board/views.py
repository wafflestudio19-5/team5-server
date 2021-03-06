from django.shortcuts import render

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Board
from .serializers import BoardSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from everytime import permissions
from everytime.exceptions import NotAllowed
from everytime.utils import get_object_or_404, ViewSetActionPermissionMixin


class BoardViewSet(ViewSetActionPermissionMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    permission_action_classes = {
        'list': (permissions.IsLoggedIn, ),
    }

    def create(self, request):
        data = request.data
        user = request.user
        if user.is_staff is not True:
            raise NotAllowed(detail='staff만 Board를 생성할 수 있습니다.')
        serializer = BoardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(BoardSerializer(board).data, status.HTTP_201_CREATED)

    def list(self, request):
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
