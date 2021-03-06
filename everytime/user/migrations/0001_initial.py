# Generated by Django 3.2.6 on 2022-01-08 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('school_email', models.EmailField(max_length=255, null=True, unique=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('nickname', models.CharField(max_length=30, unique=True)),
                ('univ', models.CharField(max_length=50)),
                ('admission_year', models.CharField(choices=[('22학번', '22학번'), ('21학번', '21학번'), ('20학번', '20학번'), ('19학번', '19학번'), ('18학번', '18학번'), ('17학번', '17학번'), ('16학번', '16학번'), ('15학번', '15학번'), ('14학번', '14학번'), ('13학번', '13학번'), ('12학번', '12학번'), ('11학번', '11학번'), ('10학번', '10학번'), ('그 외 학번', '그 외 학번'), ('졸업생', '졸업생')], max_length=10)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_deleted', models.BooleanField(default=False)),
                ('profile_picture', models.ImageField(blank=True, default='images/profile/default.png', upload_to=user.models.profile_upload_func)),
                ('reported_cnt', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('last_nickname_update', models.DateField(default=None, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('like_post', models.ManyToManyField(related_name='like_user', to='post.Post')),
                ('scrap_post', models.ManyToManyField(related_name='scrap_user', to='post.Post')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', user.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=10, null=True)),
                ('social_id', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='socialaccount', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
