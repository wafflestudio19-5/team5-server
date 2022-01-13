from django.db import models
from multiselectfield import MultiSelectField


# AAA 교수의 BBB 강의를 하나의 course로 본다.
class Course(models.Model):
    title = models.CharField(max_length=35)
    instructor = models.CharField(max_length=50, null=True)
    department = models.ForeignKey('lecture.Department', on_delete=models.SET_NULL, null=True)
    semester = models.CharField(max_length=255)  # 현재까지 개설학기, Lecture 모델에 semester 정보 저장할 필요는 없는가?


class College(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Department(models.Model):
    college = models.ForeignKey('lecture.College', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=30, unique=True)


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

    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    writer = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)

    # 성적반영관련 (grading)
    assignment = models.SmallIntegerField(default=1, choices=AMOUNT_CHOICES)
    team_project = models.SmallIntegerField(default=1, choices=AMOUNT_CHOICES)
    grade = models.SmallIntegerField(default=2, choices=GRADE_CHOICES)
    attendance = models.SmallIntegerField(default=3, choices=ATTENDANCE_CHOICES)
    exam = models.SmallIntegerField(default=2, choices=EXAM_FREQUENCY_CHOICES)

    # 총평 섹션
    rating = models.SmallIntegerField(default=3, choices=RATING_CHOICES)
    semester = models.CharField(max_length=10)

    # 평가내용
    content = models.TextField()

    # 추천
    num_of_likes = models.PositiveIntegerField(default=0, blank=True)
    like_users = models.ManyToManyField('user.User', related_name='like_evaluations')

    created_at = models.DateTimeField(auto_now_add=True)


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

    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    writer = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    # 강의평을 읽을 수 있는 유저
    readable_users = models.ManyToManyField('user.User', related_name='readable_evaluations')

    exam = models.SmallIntegerField(default=0, choices=EXAM_CHOICES)    # 응시한 시험 종류
    semester = models.CharField(max_length=10)
    strategy = models.TextField()
    type = MultiSelectField(choices=EXAM_TYPE_CHOICES, null=True)  # 문제유형, 필수 아님
    examples = models.TextField()   # tab으로 나뉘어지도록 할 수 있으면 좋을듯

    # 추천
    num_of_likes = models.PositiveIntegerField(default=0, blank=True)
    like_users = models.ManyToManyField('user.User', related_name='like_exam_info')

    created_at = models.DateTimeField(auto_now_add=True)


# 강의평가 서비스에서 사용되는 포인트
class Point(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    reason = models.CharField(max_length=30)
    point = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


# UserLecture Model
# class UserLecture(models.Model):
#     USER_LECTURE_CHOICES = [
#         ('2022-1', '2022년 1학기'),
#         ('2021-w', '2021년 겨울학기'),
#         ('2021-2', '2021년 2학기'),
#         ('2021-s', '2021년 여름학기'),
#         ('2021-1', '2021년 1학기'),
#         ('2020-w', '2020년 겨울학기'),
#         ('2020-2', '2020년 2학기'),
#         ('2020-s', '2020년 여름학기'),
#         ('2020-1', '2020년 1학기'),
#         ('2019-w', '2019년 겨울학기'),
#         ('2019-2', '2019년 2학기'),
#         ('2019-s', '2019년 여름학기'),
#         ('2019-1', '2019년 1학기'),
#         ('2018-w', '2018년 겨울학기'),
#         ('2018-2', '2018년 2학기'),
#         ('2018-s', '2018년 여름학기'),
#         ('2018-1', '2018년 1학기'),
#         ('2017-w', '2017년 겨울학기'),
#         ('2017-2', '2017년 2학기'),
#         ('2017-s', '2017년 여름학기'),
#         ('2017-1', '2017년 1학기'),
#         ('2016-w', '2016년 겨울학기'),
#         ('2016-2', '2016년 2학기'),
#         ('2016-s', '2016년 여름학기'),
#         ('2016-1', '2016년 1학기'),
#         ('2015-w', '2015년 겨울학기'),
#         ('2015-2', '2015년 2학기'),
#         ('2015-s', '2015년 여름학기'),
#         ('2015-1', '2015년 1학기'),
#         ('2014-w', '2014년 겨울학기'),
#         ('2014-2', '2014년 2학기'),
#         ('2014-s', '2014년 여름학기'),
#         ('2014-1', '2014년 1학기'),
#         ('2013-w', '2013년 겨울학기'),
#         ('2013-2', '2013년 2학기'),
#         ('2013-s', '2013년 여름학기'),
#         ('2013-1', '2013년 1학기'),
#         ('2012-w', '2012년 겨울학기'),
#         ('2012-2', '2012년 2학기'),
#         ('2012-s', '2012년 여름학기'),
#         ('2012-1', '2012년 1학기'),
#         ('2011-w', '2011년 겨울학기'),
#         ('2011-2', '2011년 2학기'),
#         ('2011-s', '2011년 여름학기'),
#         ('2011-1', '2011년 1학기'),
#         ('2010-w', '2010년 겨울학기'),
#         ('2010-2', '2010년 2학기'),
#         ('2010-s', '2010년 여름학기'),
#         ('2010-1', '2010년 1학기'),
#     ]
#
#     name = models.CharField(max_length=50, unique=True)
#     user = models.ForeignKey('user.User', on_delete=models.CASCADE)
#     lecture = models.ForeignKey('Lecture', on_delete=models.CASCADE)
#     # 2010년도 1학기부터 계절학기 포함해서 2022년도 1학기까지 존재
#     semester = models.CharField(max_length=5, choices=USER_LECTURE_CHOICES)
#     # 근데 이거 하다보니 timetable이랑 같아질 것 같아서 완성하지 않고 일단 그냥 놔둠
