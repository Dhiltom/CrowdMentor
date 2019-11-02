from django import forms
from .models import UserRoles, TRUE_OR_FALSE, pool_choices
from django.contrib.auth.models import User

class ChangeRolesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        value = kwargs.pop('value')
        usr = User.objects.get(id=value)
        super(ChangeRolesForm, self).__init__(*args, **kwargs)

        choices = [(tag.value, tag.value) for tag in UserRoles]
        self.is_worker = (usr.profile.role == UserRoles.WORKER.value) or (usr.profile.role == UserRoles.AUDITOR.value)
        self.fields['existing_role'] = forms.CharField(initial=usr.profile.role,
                                                       widget=forms.TextInput(attrs={'readonly':'readonly'}))
        self.fields['role'] = forms.ChoiceField(choices=choices, initial=usr.profile.role, required=False)
        self.fields['salary'] = forms.FloatField(label='Salary', initial=usr.worker.salary, required=False)
        self.fields['bonus'] = forms.FloatField(label='Bonus', initial=usr.worker.bonus, required=False)
        self.fields['fine'] = forms.FloatField(label='Fine', initial=usr.worker.fine, required=False)
        self.fields['audit_prob'] = forms.FloatField(label='Audit Probability', initial=usr.worker.audit_prob_user, required=False)


class ChangeMentorStatus(forms.Form):
    def __init__(self, *args, **kwargs):
        value = kwargs.pop('value')
        super(ChangeMentorStatus, self).__init__(*args, **kwargs)

        self.fields["mentor_status"] = forms.ChoiceField(choices=TRUE_OR_FALSE, initial=value)


class AddMentor(forms.Form):
    def __init__(self, *args, **kwargs):
        mentor_choices = kwargs.pop('mentor_choices')
        self.pool = kwargs.pop('pool')
        self.cur_mentor = kwargs.pop('cur_mentor')
        self.set_mentor = kwargs.pop('set_mentor')
        self.set_pool = kwargs.pop('set_pool')
        submitted = kwargs.pop('submitted')
        super(AddMentor, self).__init__(*args, **kwargs)

        CHOICES = [('Select','Select')]
        for choice in mentor_choices:
            CHOICES.append((choice,choice))
        self.fields['pool'] = forms.ChoiceField(choices=pool_choices,initial=self.pool,label='Worker Pool')
        self.fields['mentor_ch'] = forms.ChoiceField(choices=CHOICES, label='Select New mentor')
        if self.pool == 'A':
            try:
                self.fields['mentor_ch'].initial = self.cur_mentor[0]
            except:
                pass

        if submitted:
            self.fields['mentor_ch'].initial = self.set_mentor
            self.fields['pool'].initial = self.set_pool

    def clean(self, *args, **kwargs):

        if self.set_mentor == 'Select':
            raise forms.ValidationError('This is not a valid choice')
        elif (self.set_pool != self.pool):
            if (self.set_mentor in self.cur_mentor):
                raise forms.ValidationError('Already a mentor for current user')
