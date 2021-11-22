from django.db import models

# Create your models here.
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('아이디를 설정해주세요.')
        email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    studentid_validator = RegexValidator(regex=r'^\d\d\d\d-\d\d\d\d\d$')

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150, # 아이디 길이 제한
        validators=[username_validator],
        unique=True
    )
    nickname = models.CharField(max_length=20, blank=True)
    university = models.CharField(max_length=20,blank=True)
    studentid = models.CharField(
        max_length=10,
        validators=[studentid_validator]
    )
    is_staff = models.BooleanField(
        default=False
    )
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'