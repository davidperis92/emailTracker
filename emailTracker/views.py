import requests
import json
import re
from django.shortcuts import render
from django.http import HttpResponseRedirect
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
        sender = re.search(email_address_matcher, email_data['headers']['From'])
        receivers = re.findall(email_address_matcher, email_data['headers']['To'])
        copy_receivers = re.findall(email_address_matcher, email_data['headers']['Cc'])
        Email.objects.create(
            subject=email_data['headers']['Subject'],
            text_html=email_data['html'],
            text_plain=email_data['plain']
        )


class HomeView(View):

    def get(self, request, *args, **kwargs):

        if request.session.get('taiga_user_data') is None:
            return HttpResponseRedirect(reverse('emailTracker:login'))
        else:
            return render(request, 'emailTracker/home.html')


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
                taiga_user_data = auth.json()
                request.session.flush()
                request.session['taiga_user_data'] = taiga_user_data
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
