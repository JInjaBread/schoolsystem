from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.paginator import Paginator
from tablib import Dataset
from .resource import StaffResource, StudentResource
from django.db.models import Q
from .filter import StudentFilter
import json

from student_management_app.models import *


def admin_create_schoolyear(request):
    school_years = SchoolYearModel.objects.all()
    context = {
        "school_years": school_years
    }
    return render(request, "hod_template/add_school_year.html", context)

def add_school_year(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('admin_create_schoolyear')
    else:
        start = request.POST.get('school_year_start')
        end = request.POST.get('school_year_end')
        if end < start:
            messages.error(request, "Invalid Combination of Date! Please check if the end of school year is greater than the start of school year")
            return redirect('admin_create_schoolyear')
        else:
            try:
                sy = SchoolYearModel(school_year_start=start, school_year_end=end)
                sy.save()
                messages.success(request, "SY added Successfully!")
                return redirect("admin_create_schoolyear")
            except:
                messages.error(request, "Invalid Data! Make sure you input a valid data")
                return redirect("admin_create_schoolyear")

def admin_home(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    all_student_count = Students.objects.filter(sy_id=pk).count()
    staff_count = Staffs.objects.filter(sy_id=pk).count()
    grade_count = GradeLevelModel.objects.filter(sy_id=pk).count()
    subject_count = Subjects.objects.filter(sy_id=pk).count()
    # Total Subjects and students in Each Course
    grade_level = GradeLevelModel.objects.filter(sy_id=school_year.id)
    grade_level_name_list = []
    subject_count_list = []
    student_count_list_in_grade_level = []

    for grade in grade_level:
        subjects = Subjects.objects.filter(grade_level_id=grade.id).count()
        students = Students.objects.filter(grade_level_id=grade.id).count()
        grade_level_name_list.append(grade.grade_level_name)
        subject_count_list.append(subjects)
        student_count_list_in_grade_level.append(students)

    subject_all = Subjects.objects.filter(sy_id=school_year.id)
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        grade_level = GradeLevelModel.objects.get(id=subject.grade_level_id.id)
        student_count = Students.objects.filter(grade_level_id=grade_level.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    context={
        "school_year": school_year,
        "all_student_count": all_student_count,
        "grade_count": grade_count,
        "staff_count": staff_count,
        "subject_count":subject_count,
        "grade_level_name_list": grade_level_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_grade_level": student_count_list_in_grade_level,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)


    staffs = []

    if 'table_search' in request.GET:
        table_search = request.GET['table_search']
        multiple_q = Q(Q(first_name__icontains=table_search) | Q(last_name__icontains=table_search))
        custom_user = CustomUser.objects.filter(multiple_q)
        staffs_data = Staffs.objects.filter(sy_id=pk)
        for u in custom_user:
            st = staffs_data.filter(admin=u.id).exists()
            if st == True:
                staff = staffs_data.get(admin=u.id)
                staffs.append(staff)
            else:
                messages.error(request, "No Staff Found")
                break
    else:
        staffs_data = Staffs.objects.filter(sy_id=pk)
        for staff in staffs_data:
            staff = Staffs.objects.get(id=staff.id)
            staffs.append(staff)

    pages = Paginator(staffs, 10)
    page_number = request.GET.get('page')
    staffs = pages.get_page(page_number)
    context = {
        'pages':pages,
        'school_year':school_year,
        'staffs': staffs
    }
    return render(request, "hod_template/add_staff_template.html", context)


def add_staff_save(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.staffs.sy_id = school_year
            user.staffs.status = "new"
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('/add_staff/' + str(school_year.id))
        except Exception as e:
            messages.error(request, e)
            return redirect('/add_staff/' + str(school_year.id))

def add_staff_resource(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('/add_staff/', str(school_year.id))
    else:
        staff_resource = StaffResource()
        dataset = Dataset()
        list_of_staff = request.FILES["file"]

        if list_of_staff.name.endswith('xlsx'):
            try:
                imported_data = dataset.load(list_of_staff.read(), format='xlsx')
                for data in imported_data:
                    user = CustomUser.objects.create_user(username=data[0], password=data[1], email=data[2], first_name=data[3], last_name=data[4], user_type=2)
                    user.staffs.address = data[5]
                    user.staffs.sy_id = school_year
                    user.staffs.status = "new"
                    user.save()
                messages.success(request, "Staff Added Successfully!")
                return redirect('/add_staff/' + str(school_year.id))
            except Exception as e:
                messages.error(request, e)
                return redirect('/add_staff/' + str(school_year.id))



def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request, sy_id, staff_id):
    staff_data = Staffs.objects.get(admin=staff_id)
    school_year = SchoolYearModel.objects.get(id=sy_id)
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()
            messages.success(request, "Staff Updated Successfully.")
            return redirect('/add_staff/' + str(school_year.id))

        except Exception as e:
            messages.error(request,e)
            return redirect('/add_staff/' + str(school_year.id))



def delete_staff(request, sy_id, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    user = CustomUser.objects.get(id=staff_id)
    school_year = SchoolYearModel.objects.get(id=sy_id)
    try:
        staff.delete()
        user.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('/add_staff/' + str(school_year.id))
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('/add_staff/' + str(school_year.id))


def add_grade_level(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    gradelevels = GradeLevelModel.objects.filter(sy_id=pk)
    context = {
        "school_year":school_year,
        "gradelevels": gradelevels
    }
    return render(request, 'hod_template/add_grade_level.html', context)

def view_grade_level(request, pk, grade_level_id):
    school_year = SchoolYearModel.objects.get(id=pk)
    grade = GradeLevelModel.objects.get(id=grade_level_id)
    students = Students.objects.filter(grade_level_id = grade.id)
    sections = Section.objects.filter(grade_level_id=grade_level_id)
    context = {
        "students":students,
        "sections": sections,
        "school_year": school_year,
        "grade": grade
    }
    return render(request, 'hod_template/view_grade_level.html', context)


def add_grade_save(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('/add_grade_level/'+school_year.id)
    else:
        grade_level = request.POST.get("gradelevel")
        try:
            g = GradeLevelModel(grade_level_name=grade_level, sy_id = school_year)
            g.save()
            messages.success(request, "Grade Level Added Successfully!")
            return redirect('/add_grade_level/'+str(school_year.id))
        except:
            messages.error(request, "Failed to add Grade")
            return redirect('/add_grade_level/'+str(school_year.id))

def add_section(request, pk, grade_level_id):
    school_year = SchoolYearModel.objects.get(id=pk)
    grade = GradeLevelModel.objects.get(id=grade_level_id)

    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('/view_grade_level/'+str(school_year.id) + str(grade.id))
    else:
        section_name = request.POST.get("section")

        try:
            st_temp = Section(section_name = section_name, sy_id=school_year, grade_level_id=grade)
            st_temp.save()
            messages.success(request, "Section Added Successfully")
            return redirect('/view_grade_level/' + str(school_year.id) + '/' + str(grade.id))

        except Exception:
            messages.error(request, "Duplicated Section Name")
            return redirect('/view_grade_level/' + str(school_year.id) + '/' + str(grade.id))



def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')

def add_module(request):
    subject = Subjects.objects.all()
    form = AddModuleForm()
    context = {
        "subject": subject,
        "form": form
    }
    return render(request, 'hod_template/add_module_template.html', context)


def add_student(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    grade_levels = GradeLevelModel.objects.filter(sy_id=pk)

    students = []

    if 'table_search' in request.GET:
        table_search = request.GET['table_search']
        multiple_q = Q(Q(first_name__icontains=table_search) | Q(last_name__icontains=table_search))
        custom_user = CustomUser.objects.filter(multiple_q)
        students_data = Students.objects.filter(sy_id=pk)
        for u in custom_user:
            st = students_data.filter(admin=u.id).exists()
            if st == True:
                stud = students_data.get(admin=u.id)
                students.append(stud)
            else:
                messages.error(request, "No Student Found")
                break
    else:
        students_data = Students.objects.filter(sy_id=pk)
        for stu in students_data:
            stud = Students.objects.get(id=stu.id)
            students.append(stud)

    pages = Paginator(students, 10)
    page_number = request.GET.get('page')
    students = pages.get_page(page_number)
    context = {
        "pages":pages,
        "school_year":school_year,
        "students": students,
        "grade_levels":grade_levels
    }
    return render(request, 'hod_template/add_student_template.html', context)


def add_student_save(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        section = request.POST.get('section')
        grade_id = request.POST.get('grade_level')


        try:
            grade_level_data = GradeLevelModel.objects.get(id=grade_id)
            st_check_temp = Section.objects.filter(grade_level_id=grade_level_data.id)
            st_check = st_check_temp.filter(section_name = section).exists()
            st = st_check_temp.get(section_name=section)
            if st_check == True:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address
                user.students.sy_id = school_year
                user.students.grade_level_id = grade_level_data
                user.students.middle_name = middle_name
                user.students.gender = gender
                user.students.status = "new"
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('/add_student/' + str(school_year.id))
            else:
                messages.error(request, "Section Doesnt Exist!")
                return redirect('/add_student/' + str(school_year.id))
        except Exception as e:
            import traceback
            messages.error(request, e)
            return redirect('/add_student/' + str(school_year.id))

def add_student_resource(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('/add_student/', str(school_year.id))
    else:
        student_resource = StudentResource()
        dataset = Dataset()
        list_of_student = request.FILES["file"]
        g_list = GradeLevelModel.objects.filter(sy_id=school_year)
        if list_of_student.name.endswith('xlsx'):
            try:
                imported_data = dataset.load(list_of_student.read(), format='xlsx')
                for data in imported_data:
                    g = g_list.get(grade_level_name = data[7])
                    st_check_temp = Section.objects.filter(grade_level_id=g.id)
                    st_check = st_check_temp.filter(section_name=data[9]).exists()
                    st = st_check_temp.get(section_name=data[9])
                    if st_check == True:
                        user = CustomUser.objects.create_user(username=data[0], password=data[1], email=data[2], first_name=data[3], last_name=data[5], user_type=3)
                        user.students.grade_level_id = g
                        user.students.address = data[6]
                        user.students.sy_id = school_year
                        user.students.middle_name = data[4]
                        user.students.gender = data[8]
                        user.students.status = "new"
                        user.students.section_id = st
                        user.save()
                messages.success(request, "Data from files added Successfully")
                return redirect('/add_student/' + str(school_year.id))
            except Exception as e:
                messages.error(request, e)
                return redirect('/add_student/' + str(school_year.id))



def delete_student(request, sy_id, student_id):
    student = Students.objects.get(id=student_id)
    user = CustomUser.objects.get(id=student.admin.id)
    school_year = SchoolYearModel.objects.get(id=sy_id)
    try:
        student.delete()
        user.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('/add_student/' + str(school_year.id))
    except Exception as e:
        messages.error(request, e)
        return redirect('/add_student/' + str(school_year.id))


def view_subject(request, pk, subject_id):
    school_year = SchoolYearModel.objects.get(id=pk)
    staffs = Staffs.objects.filter(sy_id=pk)
    subject = Subjects.objects.get(id=subject_id)
    grade_obj = subject.grade_level_id
    sections = Section.objects.filter(grade_level_id=grade_obj.id)
    assign_list = AssignedModels.objects.filter(subject_id=subject_id)
    module_list = Modules.objects.filter(subject_id=subject.id)
    grading = GradingModel.objects.all()
    context = {
        "grading": grading,
        "module_list":module_list,
        "assign_list":assign_list,
        "sections":sections,
        "staffs": staffs,
        "school_year": school_year,
        "subject": subject
    }
    return render(request, 'hod_template/subject_view.html', context)

def assign_staff_subject(request, pk, subject_id):
    school_year = SchoolYearModel.objects.get(id=pk)
    subject_obj = Subjects.objects.get(id=subject_id)
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('/view_subject/' + str(school_year.id) + '/' + str(subject_id))
    else:
        staff = request.POST.get('staff_id')
        staff_obj = Staffs.objects.get(id=staff)

        section = request.POST.get('section_id')
        section_obj = Section.objects.get(id=section)

        try:
            as_temp = AssignedModels(subject_id = subject_obj, staff_id = staff_obj, section_id = section_obj)
            as_temp.save()
            messages.success(request, "Successfully Assigned")
            return redirect('/view_subject/' + str(school_year.id) + '/' + str(subject_id))
        except:
            messages.error(request, "Invalid!")
            return redirect('/view_subject/' + str(school_year.id) + '/' + str(subject_id))

def add_module_save(request, pk, subject_id):
    school_year = SchoolYearModel.objects.get(id=pk)
    subject_obj = Subjects.objects.get(id=subject_id)
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('/view_subject/' + str(school_year.id) + str(subject_obj.id))
    else:
        name = request.POST.get('name')
        grading = request.POST.get('grading_id')
        grading_obj = GradingModel.objects.get(id=grading)

        if len(request.FILES) != 0:
            module_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(module_file.name, module_file)
            module_file_url = fs.url(filename)
        else:
            module_file_url = None

        try:
            module = Modules(name=name, subject_id=subject_obj, grading_id=grading_obj, module_file=module_file_url, sy_id=school_year)
            module.save()
            messages.success(request, "Successfully Upload Module!")
            return redirect('/view_subject/' + str(school_year.id) + '/' + str(subject_obj.id))
        except:
            messages.error(request, "Failed to Upload Module")
            return redirect('/view_subject/' + str(school_year.id) + '/' + str(subject_obj.id))

def add_subject(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    staffs = Staffs.objects.filter(sy_id=pk)
    subjects = Subjects.objects.filter(sy_id=pk)
    gradelevel = GradeLevelModel.objects.filter(sy_id=school_year.id)
    staff = staffs.filter(sy_id=school_year.id)
    context = {
        "subjects":subjects,
        "school_year":school_year,
        "gradelevel": gradelevel,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request, pk):
    school_year = SchoolYearModel.objects.get(id=pk)
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject' + str(school_year.id))
    else:
        subject_name = request.POST.get('subject')

        grade_id = request.POST.get('grade_id')
        grade_level = GradeLevelModel.objects.get(id=grade_id)

        try:
            subject = Subjects(subject_name=subject_name,grade_level_id=grade_level, sy_id=school_year)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('/add_subject/' + str(school_year.id))
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject' + str(school_year.id))


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff

            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_student(request):
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


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')



def staff_profile(request):
    pass


def student_profile(requtest):
    pass
