from django.conf.urls import url, include
from django.views.generic import TemplateView


from . import views

app_name = 'emailTracker'
urlpatterns = [
    url(r'login', views.login),
    url(r"^$", TemplateView.as_view(template_name = app_name+"/index.html")),
    url(r'^(?P<pk>[0-9]+)/home/', include([
        url(r'^$', views.HomeView.as_view(), name='home'),
        url(r'^results/taiga_id/(?P<task_id>)$', views.ResultsView.get_emails_by_taskId),
        url(r'^results/subject/(?P<subject>)$', views.ResultsView.get_emails_by_subject),
        url(r'^results/sender/(?P<sender>)$', views.ResultsView.get_emails_by_sender),
    ])),
]
