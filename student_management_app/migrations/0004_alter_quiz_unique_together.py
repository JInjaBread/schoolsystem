# Generated by Django 3.2.9 on 2022-01-04 02:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0003_alter_question_question'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='quiz',
            unique_together={('name', 'section_id')},
        ),
    ]