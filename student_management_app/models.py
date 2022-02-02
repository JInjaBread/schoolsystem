from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_file_extension_pdf

hide_or_show = (
    ('Hide','Hide'),
    ('Show','Show')
)

old_new = (
    ('New', 'New'),
    ('Old', 'Old')
)

class GradingModel(models.Model):
    id = models.AutoField(primary_key=True)
    grading_name = models.CharField(max_length=255)

class SchoolYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    school_year_start = models.DateField()
    school_year_end = models.DateField()
    objects = models.Manager()

    def __str__(self):
        return str(self.school_year_start.year) + "-" + str(self.school_year_end.year)

# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)



class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=50)
    address = models.TextField()
    sy_id = models.ForeignKey(SchoolYearModel, on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(max_length=20, choices=old_new)
    objects = models.Manager()

    def __str__(self):
        return self.admin.first_name

class GradeLevelModel(models.Model):
    id = models.AutoField(primary_key=True)
    grade_level_name = models.CharField(max_length=255)
    sy_id = models.ForeignKey(SchoolYearModel, on_delete = models.DO_NOTHING)
    objects = models.Manager()

    class Meta:
        unique_together = ('sy_id', 'grade_level_name',)

    def __str__(self):
	     return self.grade_level_name

class Section(models.Model):
    id = models.AutoField(primary_key=True)
    section_name = models.CharField(max_length=255)
    grade_level_id = models.ForeignKey(GradeLevelModel, on_delete=models.CASCADE, related_name='section')
    sy_id = models.ForeignKey(SchoolYearModel, on_delete=models.DO_NOTHING, null=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('section_name', 'grade_level_id',)

    def __str__(self):
        return str(self.id)

class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    grade_level_id = models.ForeignKey(GradeLevelModel, on_delete=models.CASCADE, related_name='subject')
    sy_id = models.ForeignKey(SchoolYearModel, on_delete = models.DO_NOTHING)
    objects = models.Manager()

class AssignedModels(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING, related_name='subjects')
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE)
    objects = models.Manager()

    class Meta:
        unique_together = ('subject_id', 'section_id',)
        ordering = ('section_id',)

    def __str__(self):
        return self.section_id


class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE, db_constraint=False)
    middle_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    address = models.TextField()
    grade_level_id = models.ForeignKey(GradeLevelModel, on_delete=models.DO_NOTHING, related_name='student', null=True)
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students', null=True)
    sy_id = models.ForeignKey(SchoolYearModel, on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(max_length=20, choices=old_new)
    objects = models.Manager()

class Modules(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING, related_name="sj")
    grading_id = models.ForeignKey(GradingModel, on_delete=models.DO_NOTHING)
    module_file = models.FileField(validators=[validate_file_extension_pdf])
    sy_id = models.ForeignKey(SchoolYearModel, on_delete = models.DO_NOTHING)
    objects = models.Manager()

    class Meta:
        unique_together = ('name', 'subject_id',)

class Quiz(models.Model):
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE, related_name='staff')
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section')
    name = models.CharField(max_length=255)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    module_id = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='quizzes')
    grading_level = models.ForeignKey(GradingModel, on_delete=models.CASCADE)
    deadline_date = models.DateTimeField()

    class Meta:
        unique_together = ('name', 'section_id',)

    def __str__(self):
        return self.name

class Question(models.Model):
    quiz_id = models.ForeignKey(Quiz, on_delete = models.CASCADE)
    question = models.CharField(max_length=200)
    a = models.CharField(max_length=200,null=True)
    b = models.CharField(max_length=200,null=True)
    c = models.CharField(max_length=200,null=True)
    d = models.CharField(max_length=200,null=True)
    ans = models.CharField(max_length=200)

    def __str__(self):
        return self.question

class TakenQuiz(models.Model):
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.IntegerField()
    percentage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student_id', 'quiz_id',)

class Taskperformance(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    section_id = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    module_id = models.ForeignKey(Modules, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    instruction = models.CharField(max_length=200)
    max_score = models.IntegerField()
    objects = models.Manager()

    def __str__(self):
        return self.title

class SubmitedTaskperformance(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='submited_task')
    task_id = models.ForeignKey(Taskperformance, on_delete=models.CASCADE, related_name='submited_task')
    work_file = models.FileField()
    score_result = models.IntegerField()
    objects = models.Manager()

    def __str__(self):
        return str(self.id)

class Grades(models.Model):
    id = models.AutoField(primary_key=True)
    school_year_id = models.ForeignKey(SchoolYearModel, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='grades')
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='stud_grades')
    first_grading = models.IntegerField(blank=True, default=0)
    second_grading = models.IntegerField(blank=True, default=0)
    third_grading = models.IntegerField(blank=True, default=0)
    fourth_grading = models.IntegerField(blank=True, default=0)
    final_grading = models.IntegerField(blank=True, default=0)

    class Meta:
        unique_together = ('student_id', 'subject_id',)

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING)
    section_id = models.ForeignKey(Section, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

#Creating Django Signals

# It's like trigger in database. It will run only when Data is Added in CustomUser model

@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Student
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
    if instance.user_type == 3:
        instance.students.save()
