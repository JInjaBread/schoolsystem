# Generated by Django 3.2.9 on 2022-01-04 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0005_submitedtaskperformance_takenquiz_taskperformance'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='takenquiz',
            unique_together={('student_id', 'quiz_id')},
        ),
    ]
