# Generated by Django 3.2.9 on 2022-01-15 01:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0017_alter_attendance_attendance_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students',
            name='admin',
            field=models.OneToOneField(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
