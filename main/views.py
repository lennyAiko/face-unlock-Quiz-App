from http.client import HTTPResponse
from django.shortcuts import render, redirect
from .models import *
from .helper import get_image, get_verification, detectFace, create_image
import cv2
from . import forms
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
import numpy
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page

# Create your views here.

def home(request):
    return render(request, 'home.html')

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'studentclick.html')

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student-dashboard')
    else:
        return redirect('signup')

def signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict={'userForm': userForm, 'studentForm': studentForm}

    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            student = studentForm.save(commit=False)
            student.user = user
            image = create_image(request.FILES['profile_pic'])
            face = detectFace(image)
            if face:
                user.save()
                student.save()
                my_student_group = Group.objects.get_or_create(name='STUDENT')
                my_student_group[0].user_set.add(user)
                return HttpResponseRedirect('login')
            else:
                return HttpResponseRedirect('signup')
    return render(request, 'signup.html', context=mydict)

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user.id)
            compare = get_verification(student.profile_pic.path)
            if compare:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("student-dashboard")
                else:
                    messages.error(request,"Invalid username or password.")
            else:
                messages.error(request, "Face could not be recognised, try again or contact admin.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"form":form})

@login_required(login_url='login')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    'total_course':Course.objects.all().count(),
    'total_question':Question.objects.all().count(),
    }
    return render(request,'student_dashboard.html',context=dict)

@login_required(login_url='login')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=Course.objects.all()
    return render(request,'student_exam.html',{'courses':courses})

@login_required(login_url='login')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=Course.objects.get(id=pk)
    total_questions=Question.objects.all().filter(course=course).count()
    questions=Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

# @login_required(login_url='login')
# @user_passes_test(is_student)
# def start_exam_view(request,pk):
#     course=Course.objects.get(id=pk)
#     questions=Question.objects.all().filter(course=course)
#     if request.method=='POST':
#         total_marks=0
#         questions=Question.objects.all().filter(course=course)
#         for i in range(len(questions)):
            
#             selected_ans = request.POST.get(str(i+1))
#             actual_answer = questions[i].answer
#             if selected_ans == actual_answer:
#                 total_marks = total_marks + questions[i].marks
#         student = models.Student.objects.get(user_id=request.user.id)
#         result = Result()
#         result.marks=total_marks
#         result.exam=course
#         result.student=student
#         result.save()

#         return redirect("student-dashboard")
#     response= render(request,'start_exam.html',{'course':course,'questions':questions})
#     return response

@login_required(login_url='login')
@user_passes_test(is_student)
def exam_view_start(request,pk):
    course = Course.objects.get(id=pk)
    questions = Question.objects.all().filter(course=course)
    if request.method == "POST":
        total_marks=0
        questions=Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            selected_ans = request.POST.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = Student.objects.get(user_id=request.user.id)
        result = Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()
        return redirect("student-dashboard")
    return render(request, 'exam_start.html', {'course':course,'questions':questions})


# @login_required(login_url='login')
# @user_passes_test(is_student)
# def calculate_marks_view(request):
#     if request.COOKIES.get('course_id') is not None:
#         course_id = request.COOKIES.get('course_id')
#         course=Course.objects.get(id=course_id)
        
#         total_marks=0
#         questions=Question.objects.all().filter(course=course)
#         for i in range(len(questions)):
            
#             selected_ans = request.COOKIES.get(str(i+1))
#             actual_answer = questions[i].answer
#             if selected_ans == actual_answer:
#                 total_marks = total_marks + questions[i].marks
#         student = models.Student.objects.get(user_id=request.user.id)
#         result = Result()
#         result.marks=total_marks
#         result.exam=course
#         result.student=student
#         result.save()

#         return HttpResponseRedirect('view-result')



@login_required(login_url='login')
@user_passes_test(is_student)
def view_result_view(request):
    courses=Course.objects.all()
    return render(request,'view_result.html',{'courses':courses})
    

@login_required(login_url='login')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=Course.objects.get(id=pk)
    student = Student.objects.get(user_id=request.user.id)
    results= Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'check_marks.html',{'results':results})

@login_required(login_url='login')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=Course.objects.all()
    return render(request,'student_marks.html',{'courses':courses})
  