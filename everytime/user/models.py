
from django.db import models

# Create your models here.
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone

from post.models import Post
from uuid import uuid4
import os


def profile_upload_func(instance, filename):
    prefix = 'images/profile/user_{}'.format(instance.username)
    file_name = uuid4().hex
    extension = os.path.splitext(filename)[-1].lower()  # 확장자 추출
    return "/".join(
        [prefix, file_name+extension,]
    )

# 이메일 기반으로 인증 방식을 변경하기 위한 구현
# CustomUserManager는 과제 assignment2와 동일
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('아이디를 설정해주세요.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(force_insert=True, using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        # setdefault -> 딕셔너리에 key가 없을 경우 default로 값 설정
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('권한 설정이 잘못되었습니다.')

        return self._create_user(username, email, password, **extra_fields)


# 이메일 기반으로 인증하여 가입한다고 가정하였을 때
class User(AbstractBaseUser, PermissionsMixin):

    objects = CustomUserManager()

    # 학번 선택을 위한 choice 목록, 일단은 10학번까지
    YEAR_CHOICES = (
        ('22학번', '22학번'),
        ('21학번', '21학번'),
        ('20학번', '20학번'),
        ('19학번', '19학번'),
        ('18학번', '18학번'),
        ('17학번', '17학번'),
        ('16학번', '16학번'),
        ('15학번', '15학번'),
        ('14학번', '14학번'),
        ('13학번', '13학번'),
        ('12학번', '12학번'),
        ('11학번', '11학번'),
        ('10학번', '10학번'),
        ('그 외 학번', '그 외 학번'),
        ('졸업생', '졸업생')
    )

    email = models.EmailField(max_length=255, unique=True)
    school_email = models.EmailField(max_length=255, unique=True, null=True)
    username = models.CharField(max_length=100, unique=True)                 # id
    nickname = models.CharField(max_length=30, unique=True)                  # 닉네임
    univ = models.CharField(max_length=50)                                   # 학교
    admission_year = models.CharField(max_length=10, choices=YEAR_CHOICES)   # 학번
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)                  # 혹시 필요할까 해서
    is_deleted = models.BooleanField(default=False)

    # 프로필 사진, default.png = static/images/default.png 의미
    # path 관련해서는 settings.py의 MEDIA 관련 부분 참조
    # 프로필 사진은 media/images/profile 에 저장됨
    # 참고 자료 : https://www.youtube.com/watch?v=aNk2CAkHvlE
    profile_picture = models.ImageField(default='images/profile/default.png', upload_to=profile_upload_func, blank=True)   # 프로필 사진

    # 한 사람도 여러개의 게시물을 좋아할 수 있고, 한 게시물에도 그것을 좋아해준 사람이 여러명일 수 있으므로 many to many 관계
    like_post = models.ManyToManyField('post.Post', related_name='like_user')      # 좋아한 게시물
    scrap_post = models.ManyToManyField('post.Post', related_name='scrap_user')    # 스크랩한 게시물
    reported_cnt = models.PositiveSmallIntegerField(default=0, blank=True)  # 신고당한 횟수

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    # python manage.py createsuperuser로 사용자를 만들 때 필수로 입력하게 되는 필드 리스트
    # USERNAME_FIELD와 password는 항상 입력이 요구됨
    REQUIRED_FIELDS = ['email', 'nickname']


    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.email

class SocialAccount(models.Model):
    provider = models.CharField(max_length=10, null=True)
    social_id = models.CharField(max_length=100)
    user = models.ForeignKey('user.User', related_name='socialaccount', on_delete=models.CASCADE)