from django.db import models


# 신고당한 사람은 신고당한 글/댓글/...에서 가져오면 될 것 같고
# 신고한 사람은 글/댓글/...모델 필드에 reporting_users를 추가하면 어떨까싶음

class PostReport(models.Model):
    TYPE_CHOICES = (
        (0, '게시판 성격에 부적절함'),
        (1, '욕설/비하'),
        (2, '음란물/불건전한 만남 및 대화'),
        (3, '상업적 광고 및 판매'),
        (4, '유출/사칭/사기'),
        (5, '낚시/놀람/도배'),
        (6, '정당/정치인 비하 및 선거운동')
    )
    post = models.ForeignKey('post.Post', related_name='reports', on_delete=models.DO_NOTHING)
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class CommentReport(models.Model):
    TYPE_CHOICES = (
        (0, '게시판 성격에 부적절함'),
        (1, '욕설/비하'),
        (2, '음란물/불건전한 만남 및 대화'),
        (3, '상업적 광고 및 판매'),
        (4, '유출/사칭/사기'),
        (5, '낚시/놀람/도배'),
        (6, '정당/정치인 비하 및 선거운동')
    )
    comment = models.ForeignKey('comment.Comment', related_name='reports', on_delete=models.DO_NOTHING)
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class EvaluationReport(models.Model):
    eval = models.ForeignKey('lecture.LectureEvaluation', related_name='reports', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)


class ExamInfoReport(models.Model):
    examinfo = models.ForeignKey('lecture.ExamInfo', related_name='reports', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)


# 쪽지 신고
# class ChatReport(models.Model):
#     chatroom = models.ForeignKey(~~~)
#     created_at = models.DateTimeField(auto_now_add=True)


class ReportedUser(models.Model):
    school_email = models.CharField(max_length=255)
    # 몇 번 신고당했는지
    count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlockedUser(models.Model):
    pass