from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from tablib import Dataset
from .resource import QuestionResource

import json


from student_management_app.models import *

def staff_home(request):
    staff = Staffs.objects.get(admin = request.user.id)
    assigned = AssignedModels.objects.filter(staff_id=staff.id)

    subject_count = assigned.count
    assigned_subject = []
    section_list = []

    for as_temp in assigned:
        subjects = Subjects.objects.get(id=as_temp.subject_id.id)
        section = Section.objects.get(id=as_temp.section_id.id)
        assigned_subject.append(subjects)
        section_list.append(section)

    attendance_count = Attendance.objects.filter(section_id__in=section_list).count()

    context={
        "assigned":assigned,
        "assigned_subject": assigned_subject,
        "subject_count":subject_count,
        "section_list":section_list,
        "staff":staff,
        "attendance_count": attendance_count
    }
    return render(request, "staff_template/staff_home_template.html", context)



def staff_take_attendance(request):
    staff = Staffs.objects.get(admin = request.user.id)
    assigned = AssignedModels.objects.filter(staff_id=staff.id)

    subject_count = assigned.count
    assigned_subject = []

    for subject in assigned:
        subjects = Subjects.objects.get(id=subject.subject_id.id)
        assigned_subject.append(subjects)
    context = {
        'assigned_subject':  assigned_subject,
    }
    return render(request, "staff_template/take_attendance_template.html", context)

def staff_view_subject(request):
    staff = Staffs.objects.get(admin = request.user.id)
    assigned = AssignedModels.objects.filter(staff_id=staff.id)

    subject_count = assigned.count
    assigned_subject = []

    for subject in assigned:
        subjects = Subjects.objects.get(id=subject.subject_id.id)
        assigned_subject.append(subjects)

    context = {
        'assigned_subject':  assigned_subject,
        'staff':staff,
        'assigned':assigned
    }
    return render(request, "staff_template/staff_view_subject_template.html", context)


def staff_view_single_subject(request, subject_id, section_id):
    staff = Staffs.objects.get(admin = request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    assigned = AssignedModels.objects.get(staff_id=staff.id, subject_id=subject_data.id, section_id=section_id)
    section_data = Section.objects.get(id=section_id)
    students = Students.objects.filter(section_id=assigned.section_id)
    module_list = Modules.objects.filter(subject_id=subject_data.id)
    grade = Grades.objects.filter(subject_id=subject_data.id)

    stud_ungraded = []

    graded_data = []

    for student in students:
        g_check = grade.filter(student_id=student.id).exists()
        if g_check == True:
            stud = Grade.objects.get(student_id=student.id, subject_id=subject_data.id)
            graded_data.append(stud)
        else:
            stud_ungraded.append(student)

    context = {
        'staff': staff,
        'subject_data':  subject_data,
        'module_list': module_list,
        'assigned':assigned,
        'students':students,
        'section_data': section_data,
        'stud_ungraded': stud_ungraded,
        'graded_data': graded_data
        }
    return render(request, "staff_template/staff_view_single_subject_template.html", context)

def staff_view_single_modules(request, subject_id, module_id):
    staff = Staffs.objects.get(admin = request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    assigned = AssignedModels.objects.get(staff_id=staff.id, subject_id=subject_data.id)
    module_data = Modules.objects.get(id=module_id)
    quiz = Quiz.objects.filter(subject_id=subject_data.id)
    quiz_d = quiz.filter(section_id=assigned.section_id.id)
    quiz_data = quiz.filter(module_id=module_data.id)
    task = Taskperformance.objects.filter(subject_id=subject_data.id)
    task_d = task.filter(section_id=assigned.section_id.id)
    task_data = task.filter(module_id=module_data.id)
    context = {
        'quiz_data': quiz_data,
        'module_data':module_data,
        'subject_data': subject_data,
        'task_data': task_data
        }
    return render(request, "staff_template/staff_view_single_modules.html", context)

def staff_view_add_quiz(request, subject_id, module_id):
    staff = Staffs.objects.get(admin = request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    module_data = Modules.objects.get(id=module_id)
    assigned = AssignedModels.objects.get(staff_id=staff.id, subject_id=subject_data.id)

    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/staff_view_single_modules/'+str(subject_data.id)+ '/' + str(module_data.id))
    else:
        quiz_name = request.POST.get('quiz_name')
        deadline = request.POST.get('deadline_date')

        try:
            quiz = Quiz(staff_id=staff, section_id=assigned.section_id, name=quiz_name, subject_id=subject_data, module_id=module_data, grading_level=module_data.grading_id, deadline_date=deadline)
            quiz.save()
            messages.success(request, "Quiz Added Successfully! You can add questions now")
            return redirect('/staff_view_single_modules/'+str(subject_data.id)+ '/' + str(module_data.id))
        except Exception as e:
            messages.error(request, e)
            return redirect('/staff_view_single_modules/'+str(subject_data.id)+ '/' + str(module_data.id))

def add_question_to_quiz(request, quiz_id):
    quiz_data = Quiz.objects.get(id=quiz_id)
    question_data = Question.objects.filter(quiz_id=quiz_data.id)
    context = {
        'quiz_data': quiz_data,
        'question_data': question_data
    }
    return render(request, "staff_template/add_question_to_quiz.html", context)

def add_question_to_quiz_save(request, quiz_id):
    quiz_data = Quiz.objects.get(id=quiz_id)

    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/add_question_to_quiz/' + str(quiz_data.id))
    else:
        question = request.POST.get('question')
        a = request.POST.get('a')
        b = request.POST.get('b')
        c = request.POST.get('c')
        d = request.POST.get('d')
        ans = request.POST.get('ans')
        try:
            ques = Question(quiz_id=quiz_data,question=question, a=a, b=b, c=c, d=d, ans=ans)
            ques.save()
            messages.success(request, "Question Added Successfully!")
            return redirect('/add_question_to_quiz/' + str(quiz_data.id))
        except:
            messages.error(request, "Failed to add Question!")
            return redirect('/add_question_to_quiz/' + str(quiz_data.id))


def add_question_to_quiz_save_resource(request, quiz_id):
    quiz_data = Quiz.objects.get(id=quiz_id)

    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/add_question_to_quiz/' + str(quiz_data.id))
    else:
        question_resource = QuestionResource()
        dataset = Dataset()
        list_of_question = request.FILES['file']

        if list_of_question.name.endswith('xlsx'):
            try:
                imported_data = dataset.load(list_of_question.read(), format='xlsx')
                for data in imported_data:
                    ques = Question(quiz_id=quiz_data,question=data[0], a=data[1], b=data[2], c=data[3], d=data[4], ans=data[5])
                    ques.save()
                messages.success(request, "Question Added Successfully!")
                return redirect('/add_question_to_quiz/' + str(quiz_data.id))
            except Exception as e:
                messages.error(request, e)
                return redirect('/add_question_to_quiz/' + str(quiz_data.id))


def edit_question_to_quiz(request, question_id):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/add_question_to_quiz/' + str(quiz_data.id))
    else:
        question = request.POST.get('question')
        a = request.POST.get('a')
        b = request.POST.get('b')
        c = request.POST.get('c')
        d = request.POST.get('d')
        ans = request.POST.get('ans')

        try:
            ques = Question.objects.get(id=question_id)
            ques.question = question
            ques.a = a
            ques.b = b
            ques.c = c
            ques.d = d
            ques.ans = ans
            ques.save()
            messages.success(request, "Question Updated Successfully.")
            return redirect('/add_question_to_quiz/' + str(ques.quiz_id.id))
        except Exception as e:
            messages.error(request, e)
            return redirect('/add_question_to_quiz/' + str(ques.quiz_id.id))


def delete_question_to_quiz(request, question_id):
    question = Question.objects.get(id=question_id)

    try:
        question.delete()
        messages.success(request, "Question Deleted Successfully.")
        return redirect('/add_question_to_quiz/' + str(question.quiz_id.id))
    except:
        messages.error(request, "Failed to Delete Question.")
        return redirect('/add_question_to_quiz/' + str(question.quiz_id.id))

def staff_add_taskperformance(request, subject_id, module_id):
    staff = Staffs.objects.get(admin = request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    module_data = Modules.objects.get(id=module_id)
    assigned = AssignedModels.objects.get(staff_id=staff.id, subject_id=subject_data.id)

    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/staff_view_single_modules/'+str(subject_data.id)+ '/' + str(module_data.id))
    else:
        title = request.POST.get('title')
        instruction = request.POST.get('instruction')
        max_score = request.POST.get('max_score')
        try:
            task = Taskperformance(staff_id=staff, section_id=assigned.section_id, subject_id=subject_data, module_id=module_data, title=title, instruction=instruction, max_score=max_score)
            task.save()
            messages.success(request, "Task Performace Added Successfully!")
            return redirect('/staff_view_single_modules/'+str(subject_data.id)+ '/' + str(module_data.id))
        except Exception as e:
            messages.error(request, e)
            return redirect('/staff_view_single_modules/'+str(subject_data.id)+ '/' + str(module_data.id))

def staff_view_result_of_quiz(request, quiz_id):
    quiz_data = Quiz.objects.get(id=quiz_id)
    taken_quiz = TakenQuiz.objects.filter(quiz_id=quiz_data.id)
    context = {
        'quiz_data': quiz_data,
        'taken_quiz': taken_quiz
    }
    return render(request, "staff_template/staff_view_result_of_quiz.html", context)

def staff_view_submission(request, task_id):
    task_data = Taskperformance.objects.get(id=task_id)
    submited = SubmitedTaskperformance.objects.filter(task_id=task_data.id)
    context = {
        'task_data': task_data,
        'submited': submited
    }
    return render(request, "staff_template/staff_view_submision_of_task.html", context)

def staff_view_single_submission(request, task_id, submission_id):
    task_data = Taskperformance.objects.get(id=task_id)
    submited_data = SubmitedTaskperformance.objects.get(id=submission_id)

    context = {
        "task_data": task_data,
        "submited_data": submited_data
    }
    return render(request, "staff_template/staff_view_single_submission.html", context)

def staff_submit_score(request, task_id, submission_id):
    task_data = Taskperformance.objects.get(id=task_id)
    submited_data = SubmitedTaskperformance.objects.get(id=submission_id)
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/staff_view_single_submission/' + str(task_data.id) + '/' + str(submited_data.id))
    else:
        score_result = request.POST.get('score_result')

        try:
            submited_data.score_result = score_result
            submited_data.save()
            messages.success(request, "Score Successfully Submited!")
            return redirect('/staff_view_single_submission/' + str(task_data.id) + '/' + str(submited_data.id))
        except:
            messages.error(request, "Score Failed to Submit")
            return redirect('/staff_view_single_submission/' + str(task_data.id) + '/' + str(submited_data.id))


def add_activities_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('staff_view_single_subject')
    else:
        activities_name = request.POST.get('name')

        subject_id = request.POST.get('subject')
        subjects = Subjects.objects.get(id=subject_id)

        activities_link = request.POST.get('link')

        deadline_date = request.POST.get('dealine')

        try:
            activities = Activities(activities_name=activities_name, subject_id=subjects, activities_link=activities_link, deadline=deadline_date)
            activities.save()
            messages.success(request, "Activities Added Successfully!")
            return redirect("staff_view_subject")
        except Exception as e:
            messages.error(request,e)
            return redirect("staff_view_subject")

def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('staff_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('staff_apply_leave')


def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('staff_feedback')


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get("subject")
    section_id = request.POST.get("section")
    subject_model = Subjects.objects.get(id=subject_id)

    students = Students.objects.filter(section_id=section_id)

    list_data = []

    for student in students:
        data_small={"id":student.admin.id, "name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staf Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    section_id = request.POST.get("section_id")
    section_data = Section.objects.get(id=section_id)
    attendance_date = request.POST.get("attendance_date")

    subject_model = Subjects.objects.get(id=subject_id)
    json_student = json.loads(student_ids)

    print(student_ids)
    try:
        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(subject_id=subject_model, section_id=section_data)
        attendance.save()

        for stud in json_student:
            # Attendance of Individual Student saved on AttendanceReport Model
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(student_id=student, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except Exception as e:
        print(e)
        return HttpResponse(e)


def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)

@csrf_exempt
def get_attendance_dates(request):


    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:

        for stud in json_student:
            # Attendance of Individual Student saved on AttendanceReport Model
            student = Students.objects.get(admin=stud['id'])

            attendance_report = AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
            attendance_report.status=stud['status']

            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context={
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
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

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')
#Start QUIZ
def add_quiz(request, subject_id):
    staff = Staffs.objects.get(admin = request.user.id)
    subject_obj = Subjects.objects.get(id=subject_id)
    assign_temp = AssignedModels.objects.filter(staff_id=staff.id)
    assign = assign_temp.filter(subject_id=subject_obj.id)
    quiz = Quiz.objects.filter(section_id=assign[0].section_id.id)
    context = {
        "quiz":quiz
    }

    return render(request, 'staff_template/staff_profile.html', context)

def add_quiz_save(request, subject_id):
    staff = Staffs.objects.get(admin = request.user.id)
    subject_obj = Subjects.objects.get(id=subject_id)
    assign_temp = AssignedModels.objects.filter(staff_id=staff.id)
    assign = assign_temp.filter(subject_id=subject_obj.id)
    section = Section.obejecst.get(id=assign[0].section_id.id)

    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('/add_quiz/' + str(subject_obj.id))

    else:
        quiz_name = request.POST.get('quiz_name')
        grading = request.POST.get('grading')
        grading_obj = GradingLevel.objects.get(id=grading)
        try:
            quiz = Quiz(staff_id=staff, section_id=section, subject_id=subject_obj, grading_level=grading_obj)
            quiz.save()
            messages.success(request, "Quiz saved you can add question now.")
            return redirect('/add_quiz/' + str(subject_obj.id))
        except:
            messages.error(request, "Faile to add quiz!")
            return redirect('/add_quiz/' + str(subject_obj.id))

def add_question_save(request, subject_id):
    staff = Staff.objects.get(admin = request.user.id)
    subject_obj = Subjects.objects.get(id=subject_id)
    assign_temp = AssignedModels.objects.filter(staff_id=staff.id)
    assign = assign_temp.filter(subject_id=subject_obj.id)

    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('/add_quiz/' + str(subject_obj.id))

    else:
        question = request.POST.get('question')
        op1 = request.POST.get('op1')
        op2 = request.POST.get('op2')
        op3 = request.POST.get('op3')
        op4 = request.POST.get('op4')
        ans = request.POST.get('ans')

def staff_submit_grades(request, student_id, subject_id):
    staff_data = Staffs.objects.get(admin = request.user.id)
    subject_data = Subjects.objects.get(id=subject_id)
    student_data = Students.objects.get(id=student_id)

    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('/staff_view_single_subject/' + str(subject_data.id))

    else:
        first_grading = request.POST.get('first_grading')
        second_grading = request.POST.get('second_grading')
        third_grading = request.POST.get('third_grading')
        fourth_grading = request.POST.get('fourth_grading')

        try:
            grades = Grades.objects.create(school_year_id = staff_data.sy_id, subject_id=subject_data, student_id=student_data)
            grades.first_grading = first_grading
            grades.second_grading = second_grading
            grades.third_grading = third_grading
            grades.fourth_grading = fourth_grading
            grades.final_grading = 0
            grades.save()
            messages.success(request, "Grades Submited!")
            return redirect('/staff_view_single_subject/' + str(subject_data.id) + '/' + str(student_data.section_id.id))
        except Exception as e:
            messages.error(request,e)
            return redirect('/staff_view_single_subject/' + str(subject_data.id) + '/' + str(student_data.section_id.id))
