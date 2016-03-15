import requests
import django.db
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, TemplateView
from django.utils import timezone
from emailTracker.forms import LoginForm
from emailTracker.models import TaigaUser, Email

class HomeView(DetailView):
    model = TaigaUser
    template_name = 'emailTracker/home.html'
    context_object_name = 'taiga_user'


class ResultsView(TemplateView):
    model = Email
    template_name = 'emailTracker/results.html'
    context_object_name = 'email_list'

    def get_emails_by_taskId(request, task_id):
        emails = Email.objects.filter(task_id = task_id)
        return emails

    def get_emails_by_subject(request, subject):
        emails = Email.objects.filter(subject__icontains = subject)
        return emails

    def get_emails_by_sender(request, sender):
        emails = Email.objects.filter(sender__icontains = sender)
        return emails


def login(request):

    if request.method == 'GET':
        form = LoginForm()
    else:
        # A POST request: Handle Form Upload
        form = LoginForm(request.POST) # Bind data from request.POST into a PostForm
        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            auth = authentication(username, password)

            if(auth.status_code == requests.codes.ok):
                jsonObj = auth.json()
                user_id = jsonObj['id']
                if(not TaigaUser.objects.filter(user_id=user_id)):
                    token = jsonObj['auth_token']
                    email = jsonObj['email']
                    tUser = TaigaUser.objects.create_User(user_id, username, token, email)
                    tUser.save()

                request.session['user_id'] = user_id    # Initializes Session
                return HttpResponseRedirect(reverse('emailTracker:home', args=(user_id,)))

    return render(request, 'emailTracker/login.html', {
        'form': form,
    })

def authentication(user, password):
    info = {
        "type": "normal",
        "username": user,
        "password": password,
    }
    r = requests.post("https://api.taiga.io/api/v1/auth", data=info)
    return r

def getTask(task_id):
    r = requests.get("https://api.taiga.io/api/v1/tasks/" + task_id)
    return r
