from django.db import models

from board.models import Board
from everytime import settings

from django.contrib.auth import get_user_model



class Post(models.Model):
    # 게시판이 삭제되면 글도 삭제되어야하므로 cascade
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    # 작성자가 탈퇴해도 글은 남아있으므로 set_null, 작성자가 없으면 (알수없음)으로 뜸
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=100)    # 게시판에 따라 title 유무가 다름 --> 어떻게 구현?
    content = models.TextField()
    image = models.ImageField(upload_to='post/', null=True, blank=True)  # 사진은 필수가 아님, static/images/post에 저장됨
    # 게시판에 따라 image 첨부가능 여부가 다름 --> 어떻게 구현?

    # on_delete 옵션이 없으므로 view에서 구현
    tags = models.ManyToManyField('Tag', related_name='posts', null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_of_likes = models.PositiveIntegerField(default=0, blank=True)
    num_of_scrap = models.PositiveIntegerField(default=0, blank=True)
    is_anonymous = models.BooleanField(default=True, blank=True)
    is_question = models.BooleanField(default=False, blank=True)

class Tag(models.Model):
    tag = models.CharField(max_length=30, blank=False, primary_key=True)

# class Report(models.Model):
#     TYPE_CHOICES = (
#         ('게시판 성격에 부적절함', '게시판 성격에 부적절함'),
#         ('욕설/비하', '욕설/비하'),
#         ('음란물/불건전한 만남 및 대화', '음란물/불건전한 만남 및 대화'),
#         ('상업적 광고 및 판매', '상업적 광고 및 판매'),
#         ('유출/사칭/사기', '유출/사칭/사기'),
#         ('낚시/놀람/도배', '낚시/놀람/도배'),
#         ('정당/정치인 비하 및 선거운동', '정당/정치인 비하 및 선거운동')
#     )
#
#     is_user_reported = models.BooleanField()
#     reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='report', null=True)
#     reported_post = models.ForeignKey(Post, related_name='report', null=True)
#     # 위 둘 중 하나는 무조건 있어야 하는데 둘 다 null=True로 해둬서, 이후 validation 에서 둘 중 하나 값은 갖는지 따로 체크해줘야할듯
#     type = models.CharField(max_length=50, choices=TYPE_CHOICES)


