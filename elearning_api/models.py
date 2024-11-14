from datetime import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, unique=True)
    name = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    role_choices = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('administrator', 'Administrator'),
    ]
    role = models.CharField(max_length=15, choices=role_choices)
    date_joined = models.DateTimeField()


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    enrollment_capacity = models.PositiveIntegerField()
    class Meta:
        db_table="Course"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField()
    class Meta:
        db_table="Enrollment"


class Material(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    upload_date = models.DateField()
    document_type_choices = [
        ('pdf', 'PDF'),
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    document_type = models.CharField(max_length=10, choices=document_type_choices)
    class Meta:
        db_table="Material"
    def __str__(self):
        return self.title 

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    due_date = models.DateField()

    class Meta:
        db_table="Assignment"
    def __str__(self):
        return self.title

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submission_content = models.TextField()
    submission_date = models.DateField()
    class Meta:
        db_table="Submission"
  

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.FloatField()
    feedback = models.TextField()
    class Meta:
        db_table="Grade"
  

class InteractionHistory(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    interaction_type_choices = [
        ('upload', 'Upload'),
        ('read', 'Read'),
    ]
    interaction_type = models.CharField(max_length=10, choices=interaction_type_choices)
    interaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table="InteractionHistory"
    

class ReadingState(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    read_state = models.FloatField()  # e.g., percentage completed
    last_read_date = models.DateField()
    class Meta:
        db_table="ReadingState"
  


# Create your models here.
