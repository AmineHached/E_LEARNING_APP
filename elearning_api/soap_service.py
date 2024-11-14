# soap_app/soap_service.py
from django.views.decorators.csrf import csrf_exempt
from spyne import Application, rpc, ServiceBase, Iterable, Unicode, Float
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication, DjangoView
from spyne.model.complex import ComplexModel
from .serializers import  *
import json

from .models import Grade, Assignment, User

class GradeService(ServiceBase):
    @rpc(Unicode, Unicode, Float, Unicode, _returns=Unicode)
    def create_grade(self, student_username, assignment_name, grade_value, feedback):
        print(student_username)
        try:
            student = User.objects.get(username=student_username)
            assignment = Assignment.objects.get(id=assignment_name)

            grade_instance = Grade.objects.create(
                student=student,
                assignment=assignment,
                grade=float(grade_value),
                feedback=feedback
            )
            grade_instance.save()

            return f"Grade created for {student_username} on {assignment_name}"
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"Error: {str(e)}"

    @rpc(Unicode, Float, Unicode, _returns=Unicode)
    def create_grade_from_submission(self, id_submission, grade, feedback):

        try:
            submission = Submission.objects.get(id=id_submission)
            print(submission)
            user = User.objects.get(id=submission.student.id)
            grade_instance = Grade.objects.create(
                student=submission.student,
                assignment=submission.assignment,
                grade=float(grade),
                feedback=feedback
            )
            grade_instance.save()

            return f"Grade created for {user.name} on {submission.assignment.title}"
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"Error: {str(e)}"





    @rpc(Unicode, Unicode, _returns=Unicode)
    def get_grade(self, student_username, assignment_name):
        try:
            student = User.objects.get(username=student_username)
            assignment = Assignment.objects.get(id=assignment_name)
            grade_instance = Grade.objects.get(student=student, assignment=assignment)
            return f"Grade for {student_username} on {assignment_name}: {grade_instance.grade}"
        except Grade.DoesNotExist:
            return f"Grade not found for {student_username} on {assignment_name}"
        except Exception as e:
            return f"Error: {str(e)}"

        return f"Grade created for {grade.student} on {grade.assignment.name}"
    @rpc(Unicode, _returns=Unicode)
    def get_grades(self, student_username):
        try:
            student = User.objects.get(username=student_username)
            
            grades = Grade.objects.filter(student=student)
            result = []
            for grade in GradeSerializer(grades, many=True).data:
                try:
                    grade_value = {}
                    grade_value['assigment'] = grade['assignment']
                    grade_value['grade'] = grade['grade']
                    grade_value['feedback'] = grade['feedback']
                    result.append(grade_value)
                except:
                    pass
            result_json = json.dumps(result)
            return str(result_json)
        except:
            pass


application = Application([GradeService],
                          'spyne.soap.django',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

soap_app = csrf_exempt(DjangoApplication(application))
