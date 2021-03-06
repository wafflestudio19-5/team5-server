# Generated by Django 3.2.6 on 2022-01-14 23:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lecture', '0002_alter_department_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examinfo',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lecture.semester'),
        ),
        migrations.AlterField(
            model_name='lectureevaluation',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lecture.semester'),
        ),
    ]
