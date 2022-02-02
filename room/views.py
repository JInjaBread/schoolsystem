from django.views import View
from django.shortcuts import render
from student_management_app.models import Students, Section, Subjects, Staffs, CustomUser

from .utils import get_turn_info

def RoomView(request):
    return render(request, 'room/whiteboard.html')

def peer1(request):
    # get numb turn info
    context = get_turn_info()

    return render(request, 'room/peer1.html', context=context)

def peer2(request):
    # get numb turn info
    context = get_turn_info()

    return render(request, 'room/peer2.html', context=context)

def peer(request, subject_id, section_id):
    # get numb turn info
    user = CustomUser.objects.get(id=request.user.id)

    if user.user_type == "2":
        user_data = Staffs.objects.get(admin=request.user.id)
        students_data = Students.objects.filter(section_id=section_id)
        section_data = Section.objects.get(id=section_id)
        subject_data = Subjects.objects.get(id=subject_id)

        context = {
        'get_turn_info()': get_turn_info(),
        'user_data': user_data,
        'students_data':students_data,
        'section_data': section_data,
        'subject_data': subject_data,
        'user':user
        }

        return render(request, 'room/peer.html', context=context )
    elif user.user_type == "3":
        user_data = Students.objects.get(admin=request.user.id)

        context = {
        'get_turn_info()': get_turn_info(),
        'user_data': user_data,
        'user':user
        }

        return render(request, 'room/peer.html', context=context )
