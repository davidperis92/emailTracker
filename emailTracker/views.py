import requests
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView
from emailTracker.forms import LoginForm
from emailTracker.models import TaigaUser, Email


class HomeView(TemplateView):
    model = TaigaUser
    template_name = 'emailTracker/home.html'
    context_object_name = 'taiga_user'

    # return TaigaUser.objects.filter(user_id=request.session('user_id'))


class ResultsView(TemplateView):
    model = Email
    template_name = 'emailTracker/results.html'
    context_object_name = 'email_list'

    def get_emails_by_taskId(request, task_id):
        emails = Email.objects.filter(task_id=task_id)
        return emails

    def get_emails_by_subject(request, subject):
        emails = Email.objects.filter(subject__icontains=subject)
        return emails

    def get_emails_by_sender(request, sender):
        emails = Email.objects.filter(sender__icontains=sender)
        return emails


def login(request):

    if request.method == 'GET':
        form = LoginForm()
    else:
        # A POST request: Handle Form Upload
        form = LoginForm(request.POST)  # Bind data from request.POST into a PostForm
        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            auth = authentication(username, password)

            if auth.status_code == requests.codes.ok:
                jsonObj = auth.json()
                user_id = jsonObj['id']
                if not TaigaUser.objects.filter(user_id=user_id):
                    token = jsonObj['auth_token']
                    email = jsonObj['email']
                    TaigaUser.objects.create(user_id=user_id, username=username, token=token, email=email)

                request.session['user_id'] = user_id    # Initializes Session
                return HttpResponseRedirect(reverse('emailTracker:home'))

    return render(request, 'emailTracker/login.html', {
        'form': form,
    })


def authentication(user, password):

    data = {
        "type": "normal",
        "username": user,
        "password": password
    }

    return requests.post('http://178.62.226.174:81/api/v1/auth', data=data)


def getTask(task_id):
    return requests.get('http://178.62.226.174:81/api/v1/tasks/' + task_id)
