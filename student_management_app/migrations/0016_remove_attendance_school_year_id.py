# Generated by Django 3.2.9 on 2022-01-13 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0015_auto_20220113_0753'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='school_year_id',
        ),
    ]