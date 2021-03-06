# Generated by Django 3.2.9 on 2022-01-05 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0008_auto_20220105_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grades',
            name='final_grading',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grades',
            name='first_grading',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grades',
            name='fourth_grading',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grades',
            name='second_grading',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grades',
            name='subject_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='student_management_app.subjects'),
        ),
        migrations.AlterField(
            model_name='grades',
            name='third_grading',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
