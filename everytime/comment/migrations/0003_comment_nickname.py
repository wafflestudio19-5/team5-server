# Generated by Django 3.2.6 on 2022-01-03 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0002_auto_20211224_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='nickname',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
