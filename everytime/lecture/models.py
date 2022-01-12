from django.db import models


class Lecture(models.Model):
    pass


class UserLecture(models.Model):
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    lecture = models.ForeignKey('Lecture', on_delete=models.CASCADE)
    #2010년도 1학기부터 계절학기 포함해서 2022년도 1학기까지 존재
    semester =


# 개설학기 정보도 가져올 수 있으면 좋을텐데
class LectureEvaluation(models.Model):
    AMOUNT_CHOICES = [
        (2, '많음'),
        (1, '보통'),
        (0, '없음'),
    ]
    GRADE_CHOICES = [
        (2, '너그러움'),
        (1, '보통'),
        (0, '깐깐함'),
    ]
    ATTENDANCE_CHOICES = [
        (4, '혼용'),
        (3, '직접호명'),
        (2, '지정좌석'),
        (1, '전자출결'),
        (0, '반영안함'),
    ]
    EXAM_FREQUENCY_CHOICES = [
        (4, '네번이상'),
        (3, '세번'),
        (2, '두번'),
        (1, '한번'),
        (0, '없음'),
    ]
    RATING_CHOICES = [
        (1, '1점'),
        (2, '2점'),
        (3, '3점'),
        (4, '4점'),
        (5, '5점'),
    ]

    lecture = models.ForeignKey('Lecture', on_delete=models.CASCADE)
    writer = models.ForeignKey('user.User', on_delete=models.SET_NULL)

    # 성적반영관련 (grading)
    assignment = models.SmallIntegerField(default=1, choices=AMOUNT_CHOICES)
    team_project = models.SmallIntegerField(default=1, choices=AMOUNT_CHOICES)
    grade = models.SmallIntegerField(default=2, choices=GRADE_CHOICES)
    attendance = models.SmallIntegerField(default=3, choices=ATTENDANCE_CHOICES)
    exam = models.SmallIntegerField(default=2, choices=EXAM_FREQUENCY_CHOICES)

    # 총평 섹션
    rating = models.SmallIntegerField(default=3, choices=RATING_CHOICES)
    semester =

    # 평가내용
    content = models.TextField()

    # 추천
    num_of_likes = models.PositiveIntegerField(default=0, blank=True)
    like_users = models.ManyToManyField('user.User', related_name='like_evaluations')


class ExamInfo(models.Model):
    EXAM_CHOICES = [
        (0, '중간고사'),
        (1, '기말고사'),
        (2, '1차'),
        (3, '2차'),
        (4, '3차'),
        (5, '4차'),
        (6, '기타'),
    ]
    EXAM_TYPE_CHOICES = [
        (0, '객관식'),
        (1, '주관식'),
        (2, 'T/F형'),
        (3, '약술형'),
        (4, '논술형'),
        (5, '구술'),
        (6, '기타'),
    ]

    lecture = models.ForeignKey('Lecture', on_delete=models.CASCADE)
    writer = models.ForeignKey('user.User', on_delete=models.SET_NULL)

    exam =  models.SmallIntegerField(default=0, choices=EXAM_CHOICES) # 응시한 시험 종류
    semester =
    strategy = models.TextField()
    type = models.SmallIntegerField(choices=EXAM_TYPE_CHOICES)  # 문제유형, 필수 아님
    examples = models.TextField()

    # 추천
    num_of_likes = models.PositiveIntegerField(default=0, blank=True)
    like_users = models.ManyToManyField('user.User', related_name='like_evaluations')

