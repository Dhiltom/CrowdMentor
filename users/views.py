from __future__ import print_function
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, UserRoles, Mentor, Worker
from django.http import HttpResponseRedirect
from django.contrib import messages
from .UserForms import ChangeRolesForm, ChangeMentorStatus, AddMentor

def userDetails(user_id):
    dict_profile = {}
    user = User.objects.get(id=user_id)
    dict_profile['id'] = user.id
    dict_profile['fname'] = user.first_name
    dict_profile['lname'] = user.last_name
    dict_profile['username'] = user.username
    dict_profile['email'] = user.email
    dict_profile['role'] = user.profile.role
    dict_profile['bdate'] = user.profile.Birth_date
    dict_profile['salary'] = user.worker.salary
    dict_profile['bonus'] = user.worker.bonus
    dict_profile['fine'] = user.worker.fine
    dict_profile['total_salary'] = user.worker.total_salary
    dict_profile['claimed'] = user.worker.claimed_tasks
    dict_profile['finished'] = user.worker.completed_tasks
    dict_profile['worked'] = user.worker.open_tasks
    try:
        dict_profile['avgworked'] = (dict_profile['worked'] / dict_profile['finished'])
    except:
        dict_profile['avgworked'] = 0

    return dict_profile


@login_required
def profileview(request):
    user_id = User.objects.get(username=request.user.username).id
    dict_profile = {}
    profile = Profile.objects.get(user_id=user_id).role

    if profile == UserRoles.ADMIN.value:
        emp_profile = {}
        profiles = Profile.objects.all()
        for worker in profiles:
            if worker.role == UserRoles.WORKER.value:
                profile_val = userDetails(worker.user_id)
                dict_profile[profile_val['username']] = profile_val

            elif worker.role != UserRoles.ADMIN.value:
                work_val = userDetails(worker.user_id)
                emp_profile[work_val['username']] = work_val
        return render(request, 'admin_view.html', {'dict_profile': dict_profile, 'emp_profile': emp_profile})

    elif profile == UserRoles.WORKER.value:
        dict_profile[request.user.username] = userDetails(user_id)
        return render(request, 'home.html', {'dict_profile': dict_profile})

    elif profile == UserRoles.TASK_UPDATER.value:
        return  render(request, 'home.html', {'dict_profile': dict_profile})

@login_required
def change_roles(request):
    user = User.objects.get(username=request.user.username)
    profile = user.profile.role
    if profile != 'admin':
        messages.warning(request, 'Permission Denied!! You do not have permission to access this page')
        return HttpResponseRedirect('/')

    users = User.objects.all()
    if request.method == 'POST':
        posted_request = request.POST.dict()
        print(posted_request)
        all_keys = list(posted_request.keys())
        usrname = all_keys[len(all_keys)-1]
        usr = User.objects.get(username=usrname)
        previous_role = usr.profile.role
        usr.profile.role = posted_request['role']
        if (previous_role == UserRoles.WORKER.value) or (previous_role == UserRoles.AUDITOR.value):
            usr.worker.salary = posted_request['salary']
            usr.worker.bonus = posted_request['bonus']
            usr.worker.fine = posted_request['fine']
            usr.worker.audit_prob_user = posted_request['audit_prob']
        usr.worker.save()
        usr.profile.save()
    user_dict=dict()
    for usr in users:
        if (usr.profile.role == UserRoles.ADMIN.value):
            continue
        user_dict[usr.username] = ChangeRolesForm(value=usr.id)

    return render(request, 'changeRoles.html', {'user_dict':user_dict})


@login_required
def mentor_status(request):
    user = User.objects.get(username=request.user.username)
    profile = user.profile.role
    if profile != 'admin':
        messages.warning(request, 'Permission Denied!! You do not have permission to access this page')
        return HttpResponseRedirect('/')

    profiles = Profile.objects.all()
    mentors = Mentor.objects.all()

    mentors_list = []

    for mentor in mentors:
        mentors_list.append(mentor.user.username)

    if request.method == 'POST':
        posted_request = request.POST.dict()
        all_keys = list(posted_request.keys())
        usrname = all_keys[len(all_keys)-1]
        usr_id = User.objects.get(username=usrname).id
        worker = Worker.objects.get(user_id=usr_id)
        value = request.POST.get("mentor_status")
        if value == 'True':
            value = True
        else:
            value = False
        worker.is_Mentor = value
        worker.save()
        try:
            if not (value==True):
                print('deleting')
                usr = User.objects.get(username=usrname)
                Mentor.objects.get(user_id=usr_id).delete()
                usr.save()
                mentors = Mentor.objects.all()
                mentors_list = []
                for mentor in mentors:
                    mentors_list.append(mentor.user.username)
        except:
            pass
        try:
            if (value==True):
                print('creating')
                usr = User.objects.get(username=usrname)
                Mentor.objects.create(user=usr)
                usr.mentor.save()
                mentors = Mentor.objects.all()
                mentors_list = []
                for mentor in mentors:
                    mentors_list.append(mentor.user.username)
        except:
            pass

    worker_context = {}
    for profile in profiles:
        if profile.role == UserRoles.WORKER.value:
            worker_context[profile.user.username] = ChangeMentorStatus(value=profile.user.worker.is_Mentor)

    return render(request, 'mentorStatus.html', {'user_dict': worker_context})




@login_required
def change_mentor(request, usrname):
    user = User.objects.get(username=request.user.username)
    profile = user.profile.role
    if profile != 'admin':
        messages.warning(request, 'Permission Denied!! You do not have permission to access this page')
        return HttpResponseRedirect('/')

    usr = User.objects.get(username=usrname)
    usr_mentors = user.sam.get_mentors()

    mentors = Mentor.objects.all()
    mentors_list = []

    for mentor in mentors:
        mentors_list.append(mentor.user.username)

    print(mentors_list)

    cur_mentor = usr.sam.get_mentors()
    new_form = AddMentor(mentor_choices=mentors_list,
                         pool=usr.worker.worker_pool, cur_mentor=cur_mentor,
                         set_mentor=None, set_pool=None, submitted= False)

    if request.method == 'POST':

        set_mentor = request.POST.get('mentor_ch')
        set_pool = request.POST.get('pool')
        form = AddMentor(mentor_choices=mentors_list,
                         pool=usr.worker.worker_pool, cur_mentor=cur_mentor,
                         set_mentor=set_mentor, set_pool=set_pool, submitted= True)
        if form.is_valid():
            print('form_valid')
            selected_pool = form.cleaned_data.get('pool')
            if usr.worker.worker_pool != selected_pool:
                for mentor in usr_mentors:
                    mentor_user = User.objects.get(username=mentor)
                    mentees_list = mentor_user.worker.get_mentees()
                    mentees_list.remove(usr)
                    mentor_user.worker.set_mentees(mentees_list)
                    mentor_user.worker.save()
                usr_mentors = [form.cleaned_data.get('mentor_ch')]
            else:
                new_mentor = form.cleaned_data.get('mentor_ch')
                usr_mentors.append(new_mentor)
                mentor_user = User.objects.get(username=new_mentor)
                mentees_list = mentor_user.worker.get_mentees()
                if usrname not in mentees_list:
                    mentees_list.append(usrname)
                mentor_user.worker.set_mentees(mentees_list)
                mentor_user.worker.save()
            usr.sam.set_mentors(usr_mentors)

    mentors = Mentor.objects.all()
    mentors_list = []

    for mentor in mentors:
        mentors_list.append(mentor.user.username)

    cur_mentor = usr.sam.get_mentors()
    new_form = AddMentor(mentor_choices=mentors_list,
                         pool=usr.worker.worker_pool, cur_mentor=cur_mentor,
                         set_mentor=None, set_pool=None, submitted= False)

    return render(request, 'changeMentor.html', {'username':usrname, 'cur_mentor': cur_mentor, 'form':new_form})
