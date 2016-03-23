from django.conf.urls import url, include
from . import views


app_name = 'emailTracker'

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^email/$', views.email, name='email'),
    url(r'^results/', include([
        url(r'^taiga_id/(?P<task_id>)$', views.ResultsView.get_emails_by_taskId),
        url(r'^subject/(?P<subject>)$', views.ResultsView.get_emails_by_subject),
        url(r'^sender/(?P<sender>)$', views.ResultsView.get_emails_by_sender),
    ]), name='results'),
]
