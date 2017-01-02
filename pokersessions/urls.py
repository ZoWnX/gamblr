from django.conf.urls import url
from django.contrib import admin

from .views import (PokerSessionIndexView, CreatePokerSessionView,
                    AddPokerSessionUpdateView, DeletePokerSessionUpdateView,
                    StartPokerSessionView, ActivePokerSessionView, PokerSessionUserView,
                    PokerSessionDetailView, DeletePokerSessionView)

import pokersessions


urlpatterns = [
    url(r'^$', PokerSessionIndexView.as_view(), name='index'),
    url(r'^(?P<user_id>\d+)/$', PokerSessionUserView.as_view(), name='view'),
    url(r'^create/$', CreatePokerSessionView.as_view(), name='create'),
    url(r'^edit/(?P<session_id>\d+)/add/$', AddPokerSessionUpdateView.as_view(), name='add_update'),
    url(r'^edit/delete/(?P<update_id>\d+)/$', DeletePokerSessionUpdateView.as_view(), name='delete_update'),
    url(r'^start/$', StartPokerSessionView.as_view(), name='start'),
    url(r'^active/$', ActivePokerSessionView.as_view(), name='active'),
    url(r'^(?P<session_id>\d+)/detail/$', PokerSessionDetailView.as_view(), name='detail'),
    url(r'^(?P<session_id>\d+)/delete/$', DeletePokerSessionView.as_view(), name='delete'),
    url(r'^(?P<session_id>\d+)/edit/$', pokersessions.views.edit_poker_session, name='edit'),
]
