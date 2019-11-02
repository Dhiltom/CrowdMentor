from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.models import Profile
from users.models import UserRoles

def view(request):
    dict_functs = {}
    broadcast_count = ''
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        user_id = user.id
        profile = Profile.objects.get(user_id=user_id).role
        #broadcast_messages_count = BroadcastMessages.objects.filter(group_role=profile, claim=False).count()
        #broadcast_count = 'Broadcast(' + str(broadcast_messages_count) + ')'
        if profile == UserRoles.TASK_UPDATER.value:
            dict_functs['/tasks/add_tasks']= 'Add task'
            dict_functs['/tasks/'] = 'View task'
            dict_functs['/help/'] = 'Help'

        if profile == UserRoles.ADMIN.value:
            dict_functs['/change_roles'] = 'Update Worker'
            dict_functs['/mentor_status'] = 'Mentor Status'
            dict_functs['/help/'] = 'Help'

        if profile == UserRoles.WORKER.value:
            dict_functs['/tasks/claimed/'] = 'Claimed tasks'
            dict_functs['/tasks/'] = 'Open tasks'
            dict_functs['/messages/'] = 'Messages'
            dict_functs['/help/'] = 'Help'

        if profile == UserRoles.AUDITOR.value:
            dict_functs['/tasks/open_audits/'] = 'Open Audits'
            dict_functs['/tasks/audits/'] = 'Claimed Audits'
            dict_functs['/help/'] = 'Help'

        # if profile == UserRoles.MENTOR.value:
        #     dict_functs['/messages/'] = 'Messages'
        #     dict_functs['/tasks/task_status/'+str(user_id)+'/'] = 'Task Status'
        #     dict_functs['/help/'] = 'Help'
    else:
        dict_functs['/accounts/login'] = 'Login'
        dict_functs['/signup'] = 'Signup'

    return {"dict_functs" : dict_functs}

