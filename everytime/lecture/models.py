from django.db import models
from multiselectfield import MultiSelectField


# AAA 교수의 BBB 강의를 하나의 course로 본다.
class Course(models.Model):
    title = models.CharField(max_length=35)
    instructor = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey('lecture.Department', on_delete=models.SET_NULL, null=True)
    self_made = models.BooleanField(default=False)


class Lecture(models.Model):
    course = models.ForeignKey('lecture.Course', on_delete=models.CASCADE)
    classification = models.CharField(max_length=3)
    degree = models.CharField(max_length=5)
    grade = models.SmallIntegerField(null=True)
    course_code = models.CharField(max_length=15)
    lecture_code = models.IntegerField()
    credits = models.SmallIntegerField()
    lecture = models.SmallIntegerField()  # 뭘 의미하는지 모르겠음
    laboratory = models.SmallIntegerField()
    type = models.CharField(max_length=30, blank=True)
    cart = models.IntegerField()
    quota = models.IntegerField()
    remark = models.TextField(null=True)
    language = models.CharField(max_length=4)
    semester = models.ForeignKey('lecture.Semester', on_delete=models.CASCADE)
    self_made = models.BooleanField(default=False)

class LectureTime(models.Model):
    DAY_CHOICES = (
        ('월', '월'),
        ('화', '화'),
        ('수', '수'),
        ('목', '목'),
        ('금', '금'),
        ('토', '토'),
    )
    lecture = models.ForeignKey('lecture.Lecture', on_delete=models.CASCADE)
    day = models.CharField(max_length=1, choices=DAY_CHOICES)
    start = models.IntegerField()
    end = models.IntegerField()
    location = models.CharField(max_length=30, blank=True)

class College(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Department(models.Model):
    college = models.ForeignKey('lecture.College', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=30)

class Semester(models.Model):
    SEMESTER_CHOICES = (
        ('2022년 1학기', '2022년 1학기'),
        ('2021년 겨울학기', '2021년 겨울학기'),
        ('2021년 2학기', '2021년 2학기'),
        ('2021년 여름학기', '2021년 여름학기'),
        ('2021년 1학기', '2021년 1학기'),
        ('2020년 겨울학기', '2020년 겨울학기'),
        ('2020년 2학기', '2020년 2학기'),
        ('2020년 여름학기', '2020년 여름학기'),
        ('2020년 1학기', '2020년 1학기')
    )
    name = models.CharField(max_length=12, choices=SEMESTER_CHOICES)

class TimeTable(models.Model):
    PRIVATE_CHOICES=(
        ('전체공개', '전채공개'),
        ('친구공개', '친구공개'),
        ('비공개', '비공개')
    )
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=False)
    lecture = models.ManyToManyField('lecture.Lecture', null=True)
    semester = models.ForeignKey('lecture.Semester', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)
    private = models.CharField(max_length=5, choices=PRIVATE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    semester = models.ForeignKey('lecture.Semester', on_delete=models.CASCADE)

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
    semester = models.ForeignKey('lecture.Semester', on_delete=models.CASCADE)
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