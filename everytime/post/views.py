import datetime

from django.shortcuts import render, get_object_or_404
# from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status, viewsets, permissions, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from comment.models import Comment
from comment.serializers import CommentSerializer
from .models import Post, Tag
from board.models import Board
from .serializers import PostSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import re

from everytime.utils import ViewSetActionPermissionMixin

# request.data안에 새로운 Tag를 찾아서 데이터베이스에 저장
def create_tag(data):
    if 'tags' in data:
        all_tag = Tag.objects.all()
        for tag_name in data.getlist('tags'):
            tag_name = tag_name.upper()
            if not all_tag.filter(name__iexact=tag_name).exists():
                Tag.objects.create(name=tag_name)

def delete_tag(tags):
    for tag in tags:
        if tag.posttag_set.count() == 0:
            tag.delete()


class PostViewSet(ViewSetActionPermissionMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    permission_action_classes = {
        'retrieve': (permissions.AllowAny, ),
        'list': (permissions.AllowAny, ),
        'comment': (permissions.AllowAny, ),
        'search': (permissions.AllowAny, )
    }
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def create(self, request):
        data = request.data.copy()

        create_tag(data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        return Response(self.get_serializer(post).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('board', openapi.IN_QUERY,description="게시판 ID",type=openapi.TYPE_STRING)])
    #swagger에 쿼리 파라미터는 자동으로 적용이 안되므로, 따로 추가하기.
    #파라미터 이름, 어떤 부분에 속하는지(QUERY, BODY, PATH 등), 파라미터 설명, 어떤 타입인지를 생성자에 제공
    def list(self, request):
        board = request.query_params.get('board')
        if board is None:
            return Response('board를 query parameter로 입력해주세요.', status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(board=board).all()
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        # 자신이 쓴 글이 아니면 프론트에서 수정 버튼이 존재하지 않을테지만,
        if post.writer != request.user:
            return JsonResponse({
                'is_success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        # 게시글이 질문 글이고 댓글이 존재한다면,
        # 수정 가능한 화면이 뜨고 글 내용을 수정할 수는 있지만 '수정'버튼을 누르면
        # '댓글이 달린 이후에는 글을 수정 및 삭제할 수 없습니다. 그래도 작성하시겠습니까?'라는 팝업메시지 이후
        # '질문 글은 댓글이 달린 이후에는 수정할 수 없습니다.'메시지가 뜸
        if post.is_question and post.comment_set.exists():
            return JsonResponse({
                'is_success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        tags = list(post.tags.all())
        data = request.data
        user = request.user

        create_tag(data)
        if post.writer_id is not user.id:
            raise exceptions.AuthenticationFailed('글 작성자가 아니므로 글을 수정할 수 없습니다.')

        serializer = self.get_serializer(post, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        delete_tag(tags)

        return JsonResponse({
            'is_success': True,
            'updated_post': self.get_serializer(post).data},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        # 자신이 쓴 글이 아니면 프론트에서 삭제 버튼이 존재하지 않을테지만,
        if post.writer != request.user:
            return JsonResponse({
                'is_success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        if post.is_question and post.comment_set.exists():  # 게시글이 질문 글이고 댓글이 존재한다면
            return JsonResponse({
                'is_success': False # '질문 글은 댓글이 달린 이후에는 삭제할 수 없습니다.' 팝업메시지
            }, status=status.HTTP_400_BAD_REQUEST )

        tags = list(post.tags.all())  # 이렇게 하지 않으면 post.delete() 이후에 tags도 비어있게 됨.
        for image in post.postimage_set.all():
            image.delete()
        post.delete()
        delete_tag(tags)
        return JsonResponse({
            'is_success': True  # 아무 팝업메시지없이 그냥 삭제되고 게시글 목록이 뜸
        })

    @action(
        detail=True,
        methods=['POST', 'GET'],
    )
    def comment(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        data = request.data
        if request.method == 'POST':
            serializer = CommentSerializer(data=data, context={'post': post, 'user': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True, context={'post': post, 'user': user}).data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            comments = Comment.objects.filter(post=post, head_comment=None).all()
            return Response(CommentSerializer(comments, many=True, context={'post': post, 'user': user}).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['DELETE'],
        url_path='comment/(?P<comment_id>[^/.]+)'
    )
    def destroy_comment(self, request, pk=None, comment_id=-1):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.writer != user:
            return JsonResponse({
                'is_success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        if comment.head_comment is not None:                # 지울려는 댓글이 대댓글인 경우 -> 댓글 삭제
            comment.delete()
            if not comment.head_comment.tail_comments.exists() \
                    and comment.head_comment.is_deleted:    # head comment가 삭제되었고 답글도 모두 지워진 경우 -> head comment 삭제
                comment.head_comment.delete()
        elif not comment.tail_comments.exists():            # 지울려는 댓글에 답글이 달리지 않은 경우 -> 댓글 삭제
            comment.delete()
        else:                                               # 지울려는 댓글이 대댓글이 아닌 경우 -> is_deleted = True
            comment.is_deleted = True
            comment.nickname = '(삭제)'
            comment.content = '삭제된 댓글입니다.'
            comment.save()
        comments = Comment.objects.filter(post=post, head_comment=None).all()
        return JsonResponse({
            'is_success': True,
            'comments': CommentSerializer(comments, many=True).data
        }, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET']
    )
    def search(self, request):
        board = request.query_params.get('board', '')
        search_set = request.query_params.get('query', '')
        search_set = search_set.split(' ')
        if len(search_set) == 0:
            return Response('검색어를 입력하십시오.', status.HTTP_400_BAD_REQUEST)
        if board == '':
            queryset = Post.objects.all()
            for query in search_set:
                queryset = queryset.filter(content__icontains=query) | \
                           queryset.filter(title__icontains=query)
        else:
            queryset = Post.objects.all()
            for query in search_set:
                queryset = queryset.filter(content__icontains=query, board_id=board) | \
                           queryset.filter(title__icontains=query, board_id=board)
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)

    @action(
        detail=True,
        methods=['POST']
    )
    def like(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = request.user

        if post in user.like_post.all(): # 이미 공감한 게시글입니다.
            return JsonResponse({
                'is_success': False,
                'error_code': 1
            })
        elif post.created_at < (timezone.now() - datetime.timedelta(days=365)): # 오래된 글은 공감할 수 없습니다.
            return JsonResponse({
                'is_success': False,
                'error_code': 2
            })
        else:
            post.num_of_likes += 1
            post.save()
            user.like_post.add(post)
            user.save()
            return JsonResponse({
                'is_success': True,
                'value': post.num_of_likes
            })

    @action(
        detail=True,
        methods=['POST', 'DELETE']
    )
    def scrap(self, request, pk):
        if request.method == 'POST':
            post = get_object_or_404(Post, pk=pk)
            user = request.user

            if post in user.scrap_post.all(): # 이미 스크랩한 글입니다.
                return JsonResponse({
                    'is_success': False,
                    'error_code': 1
                })
            else:
                post.num_of_scrap += 1
                user.scrap_post.add(post)
                post.save()
                user.save()
                return JsonResponse({
                    'is_success': True,
                    'value': post.num_of_scrap
                })
        else:
            user = request.user

            try:
                post = user.scrap_post.get(id=pk)
                post.num_of_scrap -= 1
                user.scrap_post.remove(post)
                post.save()
                user.save()
                return JsonResponse({
                    'is_success': True,
                    'value': post.num_of_scrap
                })
            except:
                raise exceptions.NotFound('게시글을 찾을 수 없습니다.')
