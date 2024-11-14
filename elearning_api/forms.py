
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    email = forms.CharField(label='Email', widget=forms.EmailInput)

    role = forms.MultipleChoiceField(label='Role', choices=[('student', 'Student'), ('tutor', 'Tutor')])

class CourseForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    description = forms.CharField(label='Description', widget=forms.Textarea)
    enrollment_capacity = forms.CharField(label='Capacity', widget=forms.NumberInput)

class MaterialForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    content = forms.CharField(label='Content', widget=forms.Textarea)
    document_type = forms.MultipleChoiceField(label='Role', choices=[
        ('pdf', 'PDF'),
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ])

class AssignementAddForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    description = forms.CharField(label='Content', widget=forms.Textarea)
    due_date = forms.CharField(label='Due Date', widget=forms.DateTimeInput)


class SubmissionForm(forms.Form):
    submission_content = forms.CharField(label='Content', max_length=100, widget=forms.Textarea)