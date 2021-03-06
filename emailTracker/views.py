import requests
import json
import re
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from emailTracker.forms import LoginForm
from emailTracker.models import Email, UserStory, Task, LogTask, LogUserStory
from emailTracker import taiga_auth, validators



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
        # project_id = getProjectIdByName(project_name, request)

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

@csrf_exempt
def taiga_hook(request):

    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        signature = request.META['HTTP_X_TAIGA_WEBHOOK_SIGNATURE']
        taiga_json = json.loads(request.body.decode())
        if validators.verify_signature(settings.WEBHOOK_SECRET_KEY, request.body, signature):

            taiga_type = taiga_json['type']

            if   taiga_type == 'userstory':
                LogUserStory.create_from_json( taiga_json )
            elif taiga_type == 'task':
                LogTask.create_from_json( taiga_json )

            return HttpResponse()


class HomeView(LoginRequiredMixin, TemplateView):

    model = Email
    template_name = 'emailTracker/home.html'
    context_object_name = 'email_list'

    def get_context_data(self, **kwargs):
        context                 = super(HomeView, self).get_context_data(**kwargs)
        context['email_list']   = Email.objects.order_by('-date').all()
        return context



class ResultsView(LoginRequiredMixin, TemplateView):

    model = Email
    template_name = 'emailTracker/results.html'
    context_object_name = 'email_list'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)

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

def emailDetail(request, email_id):
    try:
        email = Email.objects.get(pk=email_id)
    except Email.DoesNotExist:
        raise Http404("Email does not exist")
    return render(request, 'emailTracker/email_details.html', {'email': email})


def login(request):

    if request.method == 'GET':
        form = LoginForm()
        form.helper.form_action = reverse('emailTracker:login')
    else:
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            taiga_auth_info = taiga_auth.authenticate(username, password)

            if taiga_auth_info.status_code == requests.codes.ok:
                user = auth.authenticate(remote_user=username)

                if user is not None:
                    auth.login(request, user)
                    request.session['taiga_user_data'] = taiga_auth_info.json()
                    return HttpResponseRedirect(reverse('emailTracker:home'))
            else:
                form.add_error(None, 'Usuario o contraseña incorrectos')

    return render(request, 'emailTracker/login.html', {
        'form': form,
    })


def logout(request):

    auth.logout(request)
    return HttpResponseRedirect(reverse('emailTracker:login'))


def getProjectIdByName(name, request):
    data = {
        "Content-Type": 'application/json',
        "Authorization": 'Bearer ' + request.session['taiga_user_data']['auth_token']
    }
    projects = requests.get('http://178.62.226.174:81/api/v1/projects/', data=data)
    for project in projects:
        if(project['name'] == name):
            return project['id']
    return None


def getTask(task_id):
    return requests.get('http://178.62.226.174:81/api/v1/tasks/' + task_id)


def get_emails_by_taskId(task_id):
    emails = Email.objects.order_by('-date').filter(task_id=task_id)
    return emails


def get_emails_by_subject(subject):
    emails = Email.objects.order_by('-date').filter(subject__icontains=subject)
    return emails


def get_emails_by_project_name(project_name):
    emails = Email.objects.order_by('-date').filter(project_name__icontains=project_name)
    return emails
