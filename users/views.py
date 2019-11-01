from __future__ import print_function
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, UserRoles, Mentor, Worker
from django.http import HttpResponseRedirect
from django.contrib import messages
from .UserForms import ChangeRolesForm, ChangeMentorStatus

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
            if worker.role == UserRoles.NORMAL_WORKER.value:
                profile_val = userDetails(worker.user_id)
                dict_profile[profile_val['username']] = profile_val

            elif worker.role != UserRoles.ADMIN.value:
                work_val = userDetails(worker.user_id)
                emp_profile[work_val['username']] = work_val
        return render(request, 'admin_view.html', {'dict_profile': dict_profile, 'emp_profile': emp_profile})

    elif profile == UserRoles.NORMAL_WORKER.value:
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
        #print(posted_request)
        all_keys = list(posted_request.keys())
        usrname = all_keys[len(all_keys)-1]
        usr = User.objects.get(username=usrname)
        usr.profile.role = posted_request['role']
        usr.worker.salary = posted_request['salary']
        usr.worker.bonus = posted_request['bonus']
        usr.worker.fine = posted_request['fine']
        usr.worker.audit_prob_user = posted_request['audit_prob']
        usr.worker.save()
        usr.profile.save()

        # for user in users:
        #     id = user.id
        #     if 'Select' != request.POST.get('role_'+str(id)):
        #         user.profile.role = request.POST.get('role_'+str(id))
        #     user.worker.salary = request.POST.get('salary_' + str(id))
        #     user.worker.bonus = request.POST.get('bonus_' + str(id))
        #     user.worker.fine = request.POST.get('fine_' + str(id))
        #     user.worker.audit_prob_user = request.POST.get('audit_prob_' + str(id))
        #     #if request.POST.get('mantor_id_' + str(id)) is not 'None':
        #     #    user.profile.mentor_id = request.POST.get('mentor_id_' + str(id))
        #
        #     user.save()
    user_dict=dict()
    for usr in users:
        if (usr.profile.role == UserRoles.ADMIN.value):
            continue
        user_dict[usr.username] = ChangeRolesForm(value=usr.id)
        # prf = Profile.objects.get(user_id=usr.id)
        # user_dict[usr.id] = [0, usr.username, usr.email, prf.role, usr.worker.salary, usr.worker.bonus, usr.worker.fine,
        #                      usr.worker.audit_prob_user]
        # user_dict_html[usr.id] = [(prf.role==UserRoles.NORMAL_WORKER.value), usr.username, prf.role, i, i+1, i+2, i+3, i+4, i+5]

    #form = ChangeRolesForm(users=user_dict)
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
        worker.is_Mentor = value
        worker.save()

    worker_context = {}
    for profile in profiles:
        if profile.role == UserRoles.NORMAL_WORKER.value:
            worker_context[profile.user.username] = ChangeMentorStatus(value=profile.user.worker.is_Mentor)

    return render(request, 'mentorStatus.html', {'user_dict': worker_context})


