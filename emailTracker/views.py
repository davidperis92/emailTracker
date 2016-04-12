import requests
import json
import re
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from emailTracker.forms import LoginForm
from emailTracker.models import Email


@csrf_exempt
def email(request):

    if request.method == 'POST':
        email_data = json.loads(request.body.decode())
        email_address_matcher = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
        sender = re.search(email_address_matcher, email_data['headers']['From']).group()
        if 'To' in email_data['headers']:
            receivers = re.findall(email_address_matcher, email_data['headers']['To'])
        else:
            receivers = []

        if 'Cc' in email_data['headers']:
            copy_receivers = re.findall(email_address_matcher, email_data['headers']['Cc'])
        else:
            copy_receivers = []

        project_name_matcher = re.compile(r'\[[\[a-zA-Z0-9\s\]._%+-]+\]')
        project_name = re.findall(project_name_matcher, email_data['headers']['Subject'])[0]
        project_name = project_name[1:len(project_name)-1]

        task_id_matcher = re.compile(r'\#[0-9]+\b')
        task_id = re.findall(task_id_matcher, email_data['headers']['Subject'])[0]
        task_id = task_id[1:len(task_id)]
        #project_id = getProjectIdByName(project_name, request)
        #import pdb; pdb.set_trace()
        text_html = text_plain = ''
        if email_data['html'] is not None:
            text_html = email_data['html']
        if email_data['plain'] is not None:
            text_plain = email_data['plain']

        date = datetime.strptime(email_data['headers']['Date'], '%a, %d %b %Y %H:%M:%S %z')

        Email.objects.create(
            project_name=project_name,
            task_id=task_id,
            sender=sender,
            receivers=receivers,
            copy_receivers=copy_receivers,
            subject=email_data['headers']['Subject'],
            text_html=text_html,
            text_plain=text_plain,
            date=date
        )

        return HttpResponse()


class HomeView(View):

    def get(self, request, *args, **kwargs):

        if request.session.get('taiga_user_data') is None:
            return HttpResponseRedirect(reverse('emailTracker:login'))
        else:
            return render(request, 'emailTracker/home.html', {
                'user_logged': True
            })


class ResultsView(TemplateView):
    model = Email
    template_name = 'emailTracker/results.html'
    context_object_name = 'email_list'


    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        if self.request.session.get('taiga_user_data') is None:
            return HttpResponseRedirect(reverse('emailTracker:login'))
        else:
            parameter = self.request.GET.get('task_id', '')
            if parameter != '':
                context['email_list'] = get_emails_by_taskId(parameter)
                return context

            parameter = self.request.GET.get('subject', '')
            if parameter != '':
                context['email_list'] = get_emails_by_subject(parameter)
                return context

            parameter = self.request.GET.get('project_name', '')
            if parameter != '':
                context['email_list'] = get_emails_by_project_name(parameter)
                return context



def login(request):

    authentication_error = False

    if request.method == 'GET':
        form = LoginForm()
        form.helper.form_action = reverse('emailTracker:login')
    else:
        # A POST request: Handle Form Upload
        form = LoginForm(request.POST)  # Bind data from request.POST into a PostForm
        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            auth = authentication(username, password)
            if auth.status_code == requests.codes.ok:
                taiga_user_data = auth.json()
                request.session.flush()
                request.session['taiga_user_data'] = taiga_user_data
                return HttpResponseRedirect(reverse('emailTracker:home'))
            else:
                authentication_error = True

    return render(request, 'emailTracker/login.html', {
        'form': form,
        'authentication_error': authentication_error,
        'user_logged': request.session.get('taiga_user_data') is not None
    })


def logout(request):

    request.session.flush()

    return HttpResponseRedirect(reverse('emailTracker:login'))


def authentication(user, password):

    data = {
        "type": "normal",
        "username": user,
        "password": password
    }

    return requests.post('http://178.62.226.174:81/api/v1/auth', data=data)

def getProjectIdByName(name, request):
    data = {
        "Content-Type": 'application/json',
        "Authorization": 'Bearer '+ request.session['taiga_user_data']['auth_token']
    }
    projects = requests.get('http://178.62.226.174:81/api/v1/projects/', data=data)
    for project in projects:
        if(project['name'] == name):
            return project['id']
    return null

def getTask(task_id):
    return requests.get('http://178.62.226.174:81/api/v1/tasks/' + task_id)

def get_emails_by_taskId(task_id):
    emails = Email.objects.filter(task_id=task_id)
    return emails

def get_emails_by_subject(subject):
    emails = Email.objects.filter(subject__icontains=subject)
    return emails

def get_emails_by_project_name(project_name):
    emails = Email.objects.filter(project_name__icontains=project_name)
    return emails
