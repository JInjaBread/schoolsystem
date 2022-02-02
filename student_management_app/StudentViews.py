from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object

from .models import *

def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()


    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(grade_level_id=student_obj.grade_level_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    context={
        "subject_data":subject_data,
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "student_template/student_home_template.html", context)

def student_view_subject(request):
    student_obj = Students.objects.get(admin=request.user.id)
    subject_data = Subjects.objects.filter(grade_level_id=student_obj.grade_level_id)

    context={
        "student_obj":student_obj,
        "subject_data": subject_data,
    }
    return render(request, "student_template/student_view_subject.html", context)


def student_view_attendance(request):
    student_data = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_data.id)
    context = {
        "student_data": student_data,
        "total_attendance": total_attendance
    }
    return render(request, "student_template/student_view_attendance.html", context)


def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')
    else:
        # Getting all the Input Data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        subject_obj = Subjects.objects.get(id=subject_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Student Data Based on Logged in Data
        stud_obj = Students.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'student_template/student_attendance_data.html', context)


def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'student_template/student_apply_leave.html', context)


def student_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        student_obj = Students.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStudent(student_id=student_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('student_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('student_apply_leave')


def student_feedback(request):
    student_obj = Students.objects.get(admin=request.user.id)
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'student_template/student_feedback.html', context)


def student_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('student_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        student_obj = Students.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStudent(student_id=student_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('student_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('student_feedback')


def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user)

    context={
        "user": user,
        "student": student
    }
    return render(request, 'student_template/student_profile.html', context)


def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            student = Students.objects.get(admin=customuser.id)
            student.address = address
            student.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('student_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('student_profile')


def student_view_result(request):
    student = Students.objects.get(admin=request.user.id)
    student_result = StudentResult.objects.filter(student_id=student.id)
    context = {
        "student_result": student_result,
    }
    return render(request, "student_template/student_view_result.html", context)

def view_single_subject(request, subject_id):
    student_data = Students.objects.get(admin=request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    module_list = Modules.objects.filter(subject_id=subject_data.id)

    context={
        "student_data": student_data,
        "subject_data": subject_data,
        "module_list": module_list,
    }
    return render(request, "student_template/view_single_subject.html", context)

def student_activities(request, activities_id):
    activities = Activities.objects.get(id=activities_id)
    context={
        "activities": activities,
    }
    return render(request, "student_template/student_activities.html", context)

def view_single_module(request, subject_id, module_id):
    student_data = Students.objects.get(admin=request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    module_data = Modules.objects.get(id=module_id)
    quiz = Quiz.objects.filter(subject_id=subject_data.id)
    quiz_d = quiz.filter(section_id = student_data.section_id.id)
    quiz_data = quiz_d.filter(module_id=module_data.id)
    task = Taskperformance.objects.filter(subject_id=subject_data.id)
    task_d = task.filter(section_id=student_data.section_id.id)
    task_data = task_d.filter(module_id=module_data.id)

    quiz_list = []


    for q in quiz_data:
        check = TakenQuiz.objects.filter(quiz_id=q.id).exists()
        if check == False:
            quiz_list.append(q)
    quiz_count = len(quiz_list)
    context={
        "student_data": student_data,
        "subject_data": subject_data,
        "module_data": module_data,
        "quiz_list": quiz_list,
        "quiz_count": quiz_count,
        "task_data": task_data
    }
    return render(request, "student_template/view_single_module.html", context)

def take_quiz(request, quiz_id):
    quiz_data = Quiz.objects.get(id=quiz_id)
    question = Question.objects.filter(quiz_id=quiz_data.id)

    context = {
        'question':question,
        'quiz_data': quiz_data
    }
    return render(request, "student_template/take_quiz.html", context)

def result(request, quiz_id):
    student_data = Students.objects.get(admin=request.user.id)
    if request.method == "POST":
        quiz_data = Quiz.objects.get(id=quiz_id)
        question = Question.objects.filter(quiz_id=quiz_data.id)
        score = 0
        total = 0
        for question in question:
            print(request.POST.get(question.question))
            total+=1
            if question.ans == request.POST.get(question.question):
                score+=1
        percentage = (score/total) * 100
        try:
            result = TakenQuiz(student_id=student_data, quiz_id=quiz_data, score=score, percentage=percentage)
            result.save()
            messages.success(request, "Result had been saved!")
        except:
            messages.error(request, "There must have been error, Try to contact admin!")
            return redirect('/take_quiz/' + str(quiz_data.id))
    context ={
        'score': score,
        'total': total,
        'percentage': percentage
    }
    return render(request, "student_template/result.html", context)

def submit_task(request, task_id):
    student_data = Students.objects.get(admin=request.user.id)
    task = Taskperformance.objects.get(id=task_id)
    context = {
        'task':task,
        'student_data': student_data
    }
    return render(request, "student_template/submit_task_performance.html", context)

def submit_task_save(request, task_id):
    student_data = Students.objects.get(admin=request.user.id)
    task_data = Taskperformance.objects.get(id=task_id)
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
    else:

        if len(request.FILES) != 0:
            work_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(work_file.name, work_file)
            work_file_url = fs.url(filename)
        else:
            work_file_url = None

        try:
            submit = SubmitedTaskperformance(student_id=student_data, task_id=task_data, work_file=work_file_url, score_result = 0)
            submit.save()
            messages.success(request, "File Successfully Submited!")
            return redirect('/submit_task/' + str(task_data.id))
        except Exception as e:
            messages.error(request, e)
            return redirect('/submit_task/' + str(task_data.id))

def view_result(request, subject_id, module_id):
    student_data = Students.objects.get(admin=request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    module_data = Modules.objects.get(id=module_id)
    quiz = Quiz.objects.filter(subject_id=subject_data.id)
    quiz_data = quiz.filter(section_id = student_data.section_id.id)
    task = Taskperformance.objects.filter(subject_id=subject_data.id)
    task_data = task.filter(section_id=student_data.section_id.id)

    task_temp = []

    quiz_list = []

    task_submited = SubmitedTaskperformance.objects.filter(student_id = student_data.id)
    quiz_taken = TakenQuiz.objects.filter(student_id = student_data.id)

    for sub in task_submited:
        for task in task_data:
            check = task_submited.filter(task_id=task.id).exists()
            if check == True:
                task_temp.append(sub)

    for qu in quiz_taken:
        for q in quiz_data:
            check = quiz_taken.filter(quiz_id=q.id).exists()
            if check == True:
                quiz_list.append(qu)

    context={
        "student_data": student_data,
        "subject_data": subject_data,
        "module_data": module_data,
        "task_data": task_data,
        "quiz_data": quiz_data,
        "task_temp": task_temp,
        "quiz_list": quiz_list
    }
    return render(request, "student_template/view_result.html", context)
