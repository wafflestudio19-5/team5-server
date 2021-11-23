from django.db import models

from board.models import Board
from everytime import settings


class Post(models.Model):
    pass
#     # 게시판이 삭제되면 글도 삭제되어야하므로 cascade
#     board = models.ForeignKey(Board, on_delete=models.CASCADE)
#     # 작성자가 탈퇴해도 글은 남아있으므로 set_null, 작성자가 없으면 (알수없음)으로 뜸
#     writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#
#     title = models.CharField(max_length=100)    # 게시판에 따라 title 유무가 다름 --> 어떻게 구현?
#     content = models.TextField()
#     image = models.ImageField(upload_to='post/', null=True, blank=True)  # 사진은 필수가 아님, static/images/post에 저장됨
#     # 게시판에 따라 image 첨부가능 여부가 다름 --> 어떻게 구현?
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     num_of_likes = models.PositiveIntegerField(default=0, blank=True)
#     num_of_scrap = models.PositiveIntegerField(default=0, blank=True)
#     is_anonymous = models.BooleanField(default=True, blank=True)
#     is_question = models.BooleanField(default=False, blank=True)
#
