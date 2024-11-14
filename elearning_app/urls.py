"""
URL configuration for elearning_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import routers
from django.contrib import admin
from django.urls import path
from elearning_api.views import *
from elearning_api.ui_views import *

router = routers.DefaultRouter()

router.register(r'User', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', SubmissionViewSet)
router.register(r'interaction-history', InteractionHistoryViewSet)
router.register(r'reading-states', ReadingStateViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('assignment/', assignment_view, name='assignment'),
    path('submission/manage', submission_manage_view, name='submissionmanage'),
    path('grades/', grades_view, name='grades'),
    path('assignment/submit', submit_assignment_view, name='assignmentsubmit'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('courses/', courses_view, name='courses'),
    path('courses/course/', course_view, name='course'),
    path('courses/manage/', manage_course_view, name='managecourse'),
    path('courses/manage/assignement', manage_assignement_view, name='addassignement'),
    path('courses/manage/material', manage_material_view, name='addmaterial'),
    path('profile/', profile_view, name='profile'),
    path('register/', register_view, name='register'),
    path('courses/manage/delete-assignement', delete_assignement_view, name='deleteassignemet'),
    path('grades_soap/', soap_app, name='grades_soap'),
]

urlpatterns += router.urls;