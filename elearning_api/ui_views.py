import json

import requests
from django.shortcuts import render, redirect
from .forms import *
from zeep import Client
from zeep.transports import Transport


def check_authentification(session):
    if 'username' in session and 'role' in session:
        return {
            'username': session['username'],
            'is_authenticated': True,
            'role': session['role'] or None
        }
    else:
        return {
            'is_authenticated': False,
            'role': None,
            'username': None
        }


def home_view(request):
    context = {
        'user': check_authentification(request.session),
    }

    return render(request, 'home.html', context)


def assignment_view(request):
    if not 'username' in request.session:
        return redirect('login')
    data = {
        "username": request.session['username'],
    }
    res = requests.post("http://127.0.0.1:8000/assignments/get_assignements/", data=data)
    ajson = res.json()
    print(ajson)
    for assignement in ajson:
        assignement["link"] = "/assignment/submit?id=" + str(assignement['id'])
    context = {
        'user': check_authentification(request.session),
        'assignments': ajson
    }

    return render(request, 'assignment.html', context)


def manage_material_view(request):
    if not 'username' in request.session:
        if not request.session["role"] == 'tutor':
            return redirect('login')
    if request.method == 'POST':
        form = MaterialForm(request.POST or None)
        data = dict(form.data)
        data['id'] = request.GET['id']
        data['username'] = request.session['username']
        res = requests.post("http://127.0.0.1:8000/materials/create_material/", data=data)
        if 'success' in res.json():
            return redirect("/courses/manage/")

    course_id = int(request.GET['id']) - 1
    form = MaterialForm()
    context = {
        "user": check_authentification(request.session),
        'id': course_id,
        'form': form
    }

    return render(request, 'add-material.html', context)


def manage_course_view(request):
    if not 'username' in request.session:
        if not request.session["role"] == 'tutor':
            return redirect('login')
    if request.method == 'POST':
        form = CourseForm(request.POST or None)
        if form.is_valid():
            request.data = form.data
            data = dict(form.data)
            data["username"] = request.session["username"]
            res = requests.post("http://127.0.0.1:8000/courses/create_courses/", data=data)
            print(res.json())

    res = requests.get("http://127.0.0.1:8000/courses/get_courses")
    data = res.json()
    courses = []
    for course in data:
        if course["tutor_name"] == request.session['username']:
            course["link"] = "/courses/manage/material?id=" + course["link"].split("?id=")[1]
            course["link2"] = "/courses/manage/assignement?id=" + course["link"].split("?id=")[1]
            courses.append(course)

    form = CourseForm()
    context = {
        'form': form,
        'courses': courses
    }

    return render(request, 'create-course.html', context)


def delete_assignement_view(request):
    try:
        data = {}
        data['aid'] = request.GET['id']
        data['username'] = request.session['username']
        res = requests.post("http://127.0.0.1:8000/assignments/delete_assignement/", data=data)
        print(res)
        redirect("/courses/manage")
    except:
        print("ERROR")
        pass
    return redirect("/courses/manage")


def manage_assignement_view(request):
    if not 'username' in request.session:
        if not request.session["role"] == 'tutor':
            return redirect('login')
    if request.method == 'POST':
        form = AssignementAddForm(request.POST or None)
        data = dict(form.data)
        data['course'] = request.GET['id']
        data['username'] = request.session['username']
        res = requests.post("http://127.0.0.1:8000/assignments/create_assignement/", data=data)
        if 'success' in res.json():
            return redirect("/courses/manage/")

    course_id = int(request.GET['id']) - 1
    form = AssignementAddForm()
    data = {
        "username": request.session['username'],
        "course_id": course_id
    }
    res = requests.post("http://127.0.0.1:8000/assignments/get_assignements/", data=data)
    ajson = res.json()
    for assignement in ajson:
        assignement['link'] = "/courses/manage/delete-assignement?id=" + str(assignement["id"])

    context = {
        "user": check_authentification(request.session),
        'id': course_id,
        'form': form,
        "assignments": ajson
    }

    return render(request, 'add-assignment.html', context)


def login_view(request):
    form = LoginForm()
    context = {
        'form': form
    }
    if 'username' in request.session:
        return redirect('home')
    if request.method == 'POST':

        form = LoginForm(request.POST or None)
        if form.is_valid():
            request.data = form.data
            res = requests.post("http://127.0.0.1:8000/User/login_user/", data=form.data)
            try:
                json = res.json()
                if 'success' in json:
                    request.session['username'] = form.data.get('username')
                    request.session['role'] = json['type']
                    return render(request, 'login.html')
                else:
                    context['error'] = 'Wrong username or password'
            except:
                context['error'] = 'Wrong username or password'

    return render(request, 'login.html', context)


def logout_view(request):
    if 'username' in request.session:
        del request.session['username']
    else:
        return redirect("login")
    context = {
    }

    return render(request, 'logout.html', context)


def courses_view(request):
    if not 'username' in request.session:
        return redirect('login')

    res = requests.get("http://127.0.0.1:8000/courses/get_courses")
    context = {
        "user": check_authentification(request.session),
        "courses": res.json(),

    }

    return render(request, 'courses.html', context)


def course_view(request):
    if not 'username' in request.session:
        return redirect('login')

    if (request.method == 'POST'):
        res = requests.get("http://127.0.0.1:8000/courses/" + str(request.GET["id"]) + "/get_course" + str(
            '?user=' + request.session['username']))
        res = requests.post('http://127.0.0.1:8000/enrollments/start_enroll/', data={
            'username': request.session['username'],
            'course_title': res.json()['title']
        })
    res = requests.get("http://127.0.0.1:8000/courses/" + str(request.GET["id"]) + "/get_course" + str(
        '?user=' + request.session['username']))
    json_data = res.json()
    context = {
        "course": json_data,
        "user": check_authentification(request.session),

    }
    res = requests.post("http://127.0.0.1:8000/materials/get_materials/", data={"title": json_data['title']})
    context['materials'] = res.json()
    return render(request, 'course.html', context)


def profile_view(request):
    if not 'username' in request.session:
        return redirect('login')

    context = {
        "user": check_authentification(request.session),
    }

    return render(request, 'profile.html', context)


def register_view(request):
    form = RegisterForm()
    context = {
        "user": check_authentification(request.session),
        'form': form
    }
    if 'username' in request.session:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            request.data = form.data
            res = requests.post("http://127.0.0.1:8000/User/create_user/", data=form.data)
            res_data = res.json()
            if 'success' in res_data:
                request.session['username'] = form.data.get('username')
                request.session['role'] = form.data.get('role')
                return redirect("/")
            else:
                context['error'] = 'Unable to create your account'

    return render(request, 'register.html', context)


def submit_assignment_view(request):
    if not 'username' in request.session:
        if not request.session["role"] == 'student':
            return redirect('login')
    exist_query = requests.post("http://127.0.0.1:8000/submissions/get_submission/", data={
        'username': request.session['username'],
        'assignment': request.GET['id']
    })
    if exist_query.json()['exist']:
        return redirect("/assignment/")
    if request.method == 'POST':
        form = SubmissionForm(request.POST or None)
        data = dict(form.data)
        data['assignment'] = request.GET['id']
        data['username'] = request.session['username']
        res = requests.post("http://127.0.0.1:8000/submissions/submit_assignement/", data=data)
        print(res)
        if 'success' in res.json():
            return redirect("/assignment/")

    assignment_id = int(request.GET['id']) - 1
    form = SubmissionForm()

    context = {
        "user": check_authentification(request.session),
        'form': form,
        "id": assignment_id
    }

    return render(request, 'add-assignment.html', context)


def grades_view(request):
    context = {
        "user": check_authentification(request.session),
    }
    
    client = Client('http://localhost:8000/grades_soap/?wsdl', transport=Transport())

    result_get =client.service.get_grades(request.session['username'])
    
    context['grades'] = json.loads(result_get)

    return render(request, 'grades.html', context=context)


def submission_manage_view(request):
    if request.method == 'POST':
        grade = request.POST['Grade']
        id = request.POST['id_submission']
        feedback = request.POST['feedback']
        client = Client('http://localhost:8000/grades_soap/?wsdl', transport=Transport())
        result = client.service.create_grade_from_submission(id, grade, feedback)
        print(result)
    context = {
        'user': check_authentification(request.session)
    }
    data = {}
    data['username'] = request.session['username']
    res = requests.post("http://127.0.0.1:8000/submissions/get_submissions/", data=data)

    context['submissions'] = res.json()
    return render(request, 'manage-grades.html', context=context)