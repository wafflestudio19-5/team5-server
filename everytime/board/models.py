from django.db import models
from everytime import settings

class Board(models.Model):
    # 게시판 관리자가 탈퇴했다고 게시판이 사라지면 안되므로 set_null
    manager = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    # 게시판 생성자가 아래 사항을 모두 정하도록 함
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    # 에타에서 실제로 게시판을 만들 때는 이름, 설명, 기본형/사진형, 익명허용, 이 네 가지만 고름
    anonym_enabled = models.BooleanField(default=True, blank=True)

    # 실제 에타에서 아래 필드들은 게시판 생성시 고려되진 않고,
    # 이미 생성되어있는 몇몇 게시판의 특징값으로 볼 수 있음 --> 따라서 일단은 blank=True 처리
    is_market = models.BooleanField(default=False, blank=True)
    title_enabled = models.BooleanField(default=True, blank=True)
    question_enabled = models.BooleanField(default=False, blank=True)
    notice_enabled = models.BooleanField(default=False, blank=True)

    # 게시판 타입
    board_type = models.IntegerField(default=1)

    def __str__(self):
        return self.title