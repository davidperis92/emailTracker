from django.conf.urls import url
from . import views


app_name = 'emailTracker'

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^email/$', views.email, name='email'),
    url(r'^taiga_hook/$', views.taiga_hook, name='taiga_hook'),
    url(r'^results/', views.ResultsView.as_view(), name='results'),
    url(r'^details/(?P<email_id>[0-9]+)$', views.emailDetail, name='details'),
]
