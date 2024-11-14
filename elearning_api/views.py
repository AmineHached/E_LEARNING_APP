import datetime
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .soap_service import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def login_user(self, request):
        password = request.data.get('password')  # Adjust this based on your serializer and data structure
        username = request.data.get('username')
        user = User.objects.get(username=username)
        print("USER")
        if user is not None:
            # Log in the user
            login(request, user)
            # Redirect to the home page or any desired page
            return JsonResponse({'success': True, 'message': f'Welcome, {username}!', 'type': user.role})
        else:
            return JsonResponse({'error': True, 'message': 'Invalid username or password.'})

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        password = request.data.get('password')  # Adjust this based on your serializer and data structure
        username = request.data.get('username')
        email = request.data.get('email')
        role = request.data.get('role')
        date_joined = datetime.datetime.now()
        try:
            created = User.objects.create_user(username=username, email=email, password=password,
                                               date_joined=date_joined, role=role)
            print(created)
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'error': True})


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(methods=['POST'], detail=False)
    def create_courses(self, request):
        title = request.data.get("title")
        description = request.data.get("description")
        enrollment_capacity = request.data.get("enrollment_capacity")
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'tutor':
            return JsonResponse({"Error": "You need to be a tutor"})
        Course.objects.create(
            title=title,
            description=description,
            tutor=user,
            enrollment_capacity=enrollment_capacity
        )
        return JsonResponse({"Success": "Course created."})

    @action(methods=['POST'], detail=False)
    def delete_course(self, request):
        title = request.data.get("title")
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'tutor':
            return JsonResponse({"Error": "You need to be a tutor"})
        Course.objects.get(
            title=title,
            tutor=user.id
        ).delete()
        return JsonResponse({"Success": "Course deleted."})

    @action(methods=['GET'], detail=False)
    def get_courses(self, request):
        courses = Course.objects.all()
        data = CourseSerializer(courses, many=True).data
        
        i = 0
        for course in courses:
            data[i]["tutor_name"] = course.tutor.username
            data[i]["link"] = "/courses/course?id=" + str(CourseSerializer(course).data['id'])
            i+=1
        return JsonResponse(data, safe=False)

    @action(methods=['GET'], detail=True)
    def get_course(self, request, pk=None):
        course = self.get_object()
        course_data = CourseSerializer(course).data
        user = User.objects.get(username=request.GET['user'])
        try:
            enroll = Enrollment.objects.get(course=course, student=user)
            course_data['enrolled'] = True
        except:
            course_data['enrolled'] = False
        return JsonResponse(course_data, safe=False)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    @action(methods=['POST'], detail=False)
    def start_enroll(self, request):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        
        student = User.objects.get(username=request.data.get('username'))
        course_title = request.data.get("course_title")
        
        course = Course.objects.get(title=course_title)
        
        count = len(Enrollment.objects.filter(course=course))

        print(student.role)
        if not student.role == 'student':
            return JsonResponse({"Error": "You need to be a student"})
        if count == course.enrollment_capacity:
            return JsonResponse({"Error": "Course is already full"})
        
        Enrollment.objects.create(student=student, course=course, enrollment_date=datetime.datetime.now())
        return JsonResponse({"Succes": "Done"})

    @action(methods=['GET'], detail=False)
    def get_enroll(self, request):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'student':
            return JsonResponse({"Error": "You need to be a student"})
        enrollements = Enrollment.objects.filter(student_id=user.id)
        return JsonResponse(EnrollmentSerializer(enrollements, many=True).data, safe=False)

    @action(methods=['POST'], detail=False)
    def leave_enroll(self, request):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'student':
            return JsonResponse({"Error": "You need to be a student"})
        course = request.data.get("course")
        encrollement = Enrollment.objects.get(course_id=course, student_id=user.id).delete()
        return JsonResponse({"Success": "You have successfully left the course"})


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    @action(methods=['post'], detail=False)
    def create_material(self, request):
        title = request.data.get("title")
        content = request.data.get("content")
        course = Course.objects.get(id=request.data.get("id"))
        upload_date = datetime.datetime.now()
        document_type = request.data.get("document_type")
        print(course)
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'tutor':
            return JsonResponse({"Error": "You need to be a tutor"})
        Material.objects.create(
            title=title,
            content=content,
            course=course,
            upload_date=upload_date,
            document_type=document_type
        )
        return JsonResponse({"success": "Material added created."})

    @action(methods=['post'], detail=False)
    def delete_material(self, request):
        title = request.data.get("title")
        course = request.data.get("course")
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'tutor':
            return JsonResponse({"Error": "You need to be a tutor"})
        Material.objects.get(
            title=title,
            course=course
        ).delete()
        return JsonResponse({"Success": "You have successfully deleted the material"})

    @action(methods=['get'], detail=False)
    def check_materials(self, request):
        course = request.data.get("course")
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        material = Material.objects.filter(course=course)
        return JsonResponse(MaterialSerializer(material, many=True).data, safe=False)

    @action(methods=['post'], detail=False)
    def get_materials(self, request):
        try:
            course = Course.objects.get(title=request.data.get('title'))
            materials = Material.objects.filter(course=course)
            return JsonResponse(MaterialSerializer(materials, many=True).data, safe=False)
        except:
            return JsonResponse({}, safe=False)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    @action(methods=['POST'], detail=False)
    def create_assignement(self, request):
        title = request.data.get("title")
        description = request.data.get("description")
        course = Course.objects.get(id=request.data.get("course"))

        due_date = datetime.datetime.strptime(request.data.get("due_date"), "%d/%m/%y").date()
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        if not user.role == 'tutor':
            return JsonResponse({"Error": "You need to be a tutor"})
        Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            due_date=due_date
        )
        return JsonResponse({"success": "Assignement created."})

    @action(methods=['POST'], detail=False)
    def delete_assignement(self, request):
        id = request.data.get("aid")
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))

        if not user.role == 'tutor':
            return JsonResponse({"Error": "You need to be a tutor"})
        Assignment.objects.get(id=id).delete()
        return JsonResponse({"success": "Assignement Delete."})



    @action(methods=['POST'], detail=False)
    def get_assignements(self, request):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        try:
            if (user.role == 'tutor'):
                course = Course.objects.get(id=int(request.data.get("course_id")) + 1)
                assignment = Assignment.objects.filter(course_id=course)
                return JsonResponse(AssignmentSerializer(assignment, many=True).data, safe=False);
            else:
                enrollements = Enrollment.objects.filter(student=user)
                assignements = []
                for enroll in EnrollmentSerializer(enrollements, many=True).data:
                    print(enroll)
                    try:
                        assignement = Assignment.objects.filter(course=enroll['course'])
                        for ass in assignement:
                            assignements.append(AssignmentSerializer(ass).data)
                    except:
                        print("ERROR")
                    print(assignements)
                return JsonResponse( assignements, safe=False)
        except:
            print("EXCEPTION")
            return JsonResponse({})

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    @action(methods=['POST'], detail=False)
    def get_submission(self, request):
        user = User.objects.get(username=request.data.get('username'))
        assignment = Assignment.objects.get(id=request.data.get("assignment"))
        try:
            submission = Submission.objects.get(student=user, assignment=assignment)
            return JsonResponse({'exist': True})
        except:
            print("EROR")
            return JsonResponse({'exist': False})

    @action(methods=['POST'], detail=False)
    def get_submissions(self, request):
        user = User.objects.get(username=request.data.get('username'))
        submissions_thing = []
        try:
            courses = Course.objects.filter(tutor=user)

            for course in courses:
                try:
                    assignments = Assignment.objects.filter(course=course)
                    for assignment in assignments:
                        try:
                            submissions = Submission.objects.filter(assignment=assignment)
                            for submission in submissions:
                                try:
                                    grade = Grade.objects.get(assignment=assignment, student=submission.student)
                                except:
                                    submissions_thing.append(SubmissionSerializer(submission).data)
                        except:
                            pass
                except:
                    pass
            return JsonResponse(submissions_thing, safe=False)
        except:
            return JsonResponse(submissions_thing, safe=False)

    @action(methods=['POST'], detail=False)
    def submit_assignement(self, request):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        print(user)
        if not user.role == 'student':
            return JsonResponse({"Error": "You need to be a student"})
        assignment = Assignment.objects.get(id=request.data.get("assignment"))
        submission_content = request.data.get("submission_content")
        submission_date = datetime.datetime.now()
        Submission.objects.create(
            student=user,
            assignment=assignment,
            submission_content=submission_content,
            submission_date=submission_date
        )
        return JsonResponse({'success': 'done'})



class InteractionHistoryViewSet(viewsets.ModelViewSet):
    queryset = InteractionHistory.objects.all()
    serializer_class = InteractionHistorySerializer

    @action(detail=True, methods=['get'])
    def interaction_history(self, request, pk=None):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        interactions = InteractionHistory.objects.filter(student=user, material__course=course)
        serializer = InteractionHistorySerializer(interactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ReadingStateViewSet(viewsets.ModelViewSet):
    queryset = ReadingState.objects.all()
    serializer_class = ReadingStateSerializer

    @action(detail=True, methods=['post'])
    def save_reading_state(self, request, pk=None):
        if request.data.get('username') is None:
            return JsonResponse({"Error": "Need Authentification"})
        user = User.objects.get(username=request.data.get('username'))
        # Get the reading state data from the request
        data = request.data
        material_id = data.get('material_id', '')
        ReadingState.objects.update_or_create(student=user.id, material_id=material_id,
                                              defaults={'read_state': data.get('read_state', 0)})

        return Response({'detail': 'Reading state saved successfully.'}, status=status.HTTP_200_OK)

