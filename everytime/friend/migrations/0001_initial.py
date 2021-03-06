# Generated by Django 3.2.6 on 2022-01-19 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_to_set', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reqeust_from_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends2', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='friendrequest',
            constraint=models.UniqueConstraint(fields=('sender', 'receiver'), name='friend request'),
        ),
        migrations.AddConstraint(
            model_name='friend',
            constraint=models.UniqueConstraint(fields=('user', 'friend'), name='friend relation'),
        ),
    ]
