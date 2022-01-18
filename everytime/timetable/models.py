from django.db import models

# Create your models here.
class TimeTable(models.Model):
    PRIVATE_CHOICES=(
        ('전체공개', '전채공개'),
        ('친구공개', '친구공개'),
        ('비공개', '비공개')
    )
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=False)
    lecture = models.ManyToManyField('lecture.Lecture', blank=True)
    semester = models.ForeignKey('lecture.Semester', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)
    private = models.CharField(max_length=5, choices=PRIVATE_CHOICES, default='전체공개')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)