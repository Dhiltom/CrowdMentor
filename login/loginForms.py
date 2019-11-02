from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import UserRoles

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, help_text='Required')
    birth_date = forms.DateField(required=False)
    CHOICES = [
        (UserRoles.WORKER.value,'Worker'),
        (UserRoles.TASK_UPDATER.value, "Task Updater"),
        (UserRoles.AUDITOR.value, "Auditor")
    ]
    role = forms.ChoiceField(choices=CHOICES)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birth_date')
