from django.db import models


# Create your models here.
# AAA 교수의 BBB 강의 를 하나의 course로 본다.
class Course(models.Model):
    title = models.CharField(max_length=35)
    instructor = models.CharField(max_length=50, null=True)
    department = models.ForeignKey('lecture.Department', on_delete=models.SET_NULL, null=True)

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
    type = models.CharField(max_length=30, null=True)
    location = models.CharField(max_length=100, null=True)
    cart = models.IntegerField()
    quota = models.IntegerField()
    remark = models.TextField(null=True)
    language = models.CharField(max_length=4)
    semester = models.CharField(max_length=10)

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

class College(models.Model):
    name = models.CharField(max_length=30, unique=True)

class Department(models.Model):
    college = models.ForeignKey('lecture.College', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=30, unique=True)