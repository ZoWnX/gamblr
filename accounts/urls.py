from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView

from .views import RegisterView, IndexView, LoginView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^register/$', RegisterView.as_view() , name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/accounts/'}, name='logout'),
]
