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

    # sub_board 구현
    # head_board가 있으면(null이 아니면) 하위 게시판이 아닌 일반 게시판임
    # 일반 게시판이 사라지면 하위게시판도 삭제될 것이므로 on_delete는 CASCADE
    head_board = models.ForeignKey('self', related_name='sub_boards', on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return self.title

      
class HotBoard(models.Model):
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class BestBoard(models.Model):
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.SmallIntegerField(null=True)
    first_half = models.BooleanField(default=True)

    def get_post(self):
        return self.post

    
# <게시판 - 하위게시판>
# 새내기게시판 - 22학번, 21학번 이전 (해마다 교체)
# 장터 - 팝니다, 삽니다, 나눔, 원룸
# 동아리학회 - 교내, 연합
# 취업 진로 - 자유, 꿀팁, 후기
# 하드코딩으로 11개 넣어줘야할 듯
