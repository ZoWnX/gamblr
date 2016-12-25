from django.conf.urls import url
from django.contrib import admin

from .views import (ChipStackPokerUpdateJson)


urlpatterns = [
    url(r'^chipstack/(?P<session_id>\d+)/$', ChipStackPokerUpdateJson.as_view(), name='chipstack'),
]
