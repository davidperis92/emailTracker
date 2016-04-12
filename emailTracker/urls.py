from django.conf.urls import url, include
from . import views


app_name = 'emailTracker'

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^email/$', views.email, name='email'),
    url(r'^results/', views.ResultsView.as_view(), name='results'),
]
