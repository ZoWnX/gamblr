from datetime import datetime, timedelta
from pytz import timezone
import pytz

import json

from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from accounts.models import User
from .models import PokerSession, PokerSessionUpdate
from .forms import (PokerSessionForm, PokerSessionUpdateForm, PokerSessionStartForm,
                    PokerSessionCreateForm, ActivePokerSessionUpdateForm)

# Create your views here.

class PokerSessionIndexView(LoginRequiredMixin, ListView):
    template_name = 'pokersessions/index.html'
    model = PokerSession

    def get_queryset(self):
        user = self.request.user
        object_list = self.model.objects.filter(user=user)
        return object_list

class PokerSessionUserView(ListView):
    template_name = 'pokersessions/view.html'
    model = PokerSession

    def get_queryset(self):
        user = User.objects.get(pk=self.kwargs['user_id'])
        object_list = self.model.objects.filter(user=user).exclude(public=False)
        return object_list

class CreatePokerSessionView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/create.html"
    form_class = PokerSessionCreateForm
    success_url = reverse_lazy('pokersessions:index')

    def form_valid(self, form):
        resp = super(CreatePokerSessionView, self).form_valid(form)
        clean = form.cleaned_data
        user = self.request.user
        location = clean['location']
        game = clean['game']
        public = clean['public']

        poker_session = PokerSession(user=user, location=location, game=game, active=False, public=public)
        poker_session.save()

        time = clean['time']
        buy_in = clean['buy_in']
        tzinfo = timezone(location.timezone)
        time = time.replace(tzinfo=tzinfo).astimezone(pytz.utc)

        update = PokerSessionUpdate(poker_session=poker_session, time=time,
                buy_in=buy_in, chip_stack=buy_in)
        update.save()

        messages.success(self.request, '{0} Created'.format(poker_session))

        return resp


class EditPokerSessionView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/edit.html"
    form_class = PokerSessionForm
    poker_session = None
    success_url = reverse_lazy('pokersessions:index')

    def get(self, request, *args, **kwargs):
        session_id = self.kwargs['session_id']
        self.poker_session = PokerSession.objects.get(pk=session_id)

        return super(EditPokerSessionView, self).get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        session_id = self.kwargs['session_id']
        self.poker_session = PokerSession.objects.get(pk=session_id)

        return super(EditPokerSessionView, self).post(request, args, kwargs)

    def get_initial(self):
        initial = {
            'location': self.poker_session.location,
            'game' : self.poker_session.game
        }
        return initial

    def form_valid(self, form):
        resp = super(EditPokerSessionView, self).form_valid(form)
        clean = form.cleaned_data
        location = clean['location']
        game = clean['game']
        public = clean['public']

        session_id = self.kwargs['session_id']
        poker_session = PokerSession.objects.get(pk=session_id)
        poker_session.location = location
        poker_session.game = game
        poker_session.public = public
        poker_session.save()

        messages.success(self.request, '{0} Updated'.format(poker_session))

        return self.render_to_response(self.get_context_data(form=form))

class AddPokerSessionUpdateView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/update_add.html"
    form_class = PokerSessionUpdateForm
    success_url = reverse_lazy('pokersessions:index')

    def form_valid(self, form):
        resp = super(AddPokerSessionUpdateView, self).form_valid(form)
        clean = form.cleaned_data
        time = clean['time']
        buy_in = clean['buy_in']
        chip_stack = clean['chip_stack']
        comment = clean['comment']


        session_id = self.kwargs['session_id']
        poker_session = PokerSession.objects.get(pk=session_id)

        tzinfo = timezone(poker_session.location.timezone)
        time = time.replace(tzinfo=tzinfo).astimezone(pytz.utc)

        update = PokerSessionUpdate(poker_session=poker_session, time=time,
                buy_in=buy_in, chip_stack=chip_stack, comment=comment)
        update.save()

        messages.success(self.request, '{0} added to {1}'.format(update, poker_session))

        if('add_return' in self.request.POST):
            return HttpResponseRedirect(reverse('pokersessions:edit', kwargs={'session_id':session_id}))

        return HttpResponseRedirect(reverse('pokersessions:add_update', kwargs={'session_id':session_id}))

class DeletePokerSessionView(LoginRequiredMixin, DeleteView):

    def get_object(self):
        update_id = self.kwargs['session_id']
        obj = PokerSession.objects.get(pk=update_id)
        return obj

    def get(self, request, *args, **kwargs):
        return super(DeletePokerSessionView,self).post(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        poker_session = self.get_object()
        user = self.request.user
        if(poker_session.user.id == user.id):
            poker_session.delete()
            messages.success(request, 'Poker Session Deleted')
            return HttpResponseRedirect(reverse('pokersessions:index'))

        messages.error(request, 'Not the owner of the Poker Session')
        return HttpResponseRedirect(reverse('pokersession:index'))

class DeletePokerSessionUpdateView(LoginRequiredMixin, DeleteView):

    def get_object(self):
        update_id = self.kwargs['update_id']
        obj = PokerSessionUpdate.objects.get(pk=update_id)
        return obj

    def get(self, request, *args, **kwargs):
        return super(DeletePokerSessionUpdateView,self).post(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if(obj.poker_session.user.id == user.id):
            poker_session = obj.poker_session
            obj.delete()
            messages.success(request, 'Poker Session Update Deleted')
            return HttpResponseRedirect(reverse('pokersessions:edit', kwargs={'session_id':poker_session.id}))
        else:
            messages.error(request, 'Not the owner of the Poker Session Update')
            return HttpResponseRedirect(reverse('pokersession:index'))

class StartPokerSessionView( LoginRequiredMixin, FormView ):

    template_name = "pokersessions/start.html"
    form_class = PokerSessionStartForm
    success_url = reverse_lazy('pokersessions:active')

    def get(self, request, *args, **kwargs):
        #check if user has an active session already
        user = request.user
        poker_session_count = PokerSession.objects.filter(active=True).filter(user=user).count()
        if(poker_session_count > 0):
            messages.error(request, 'User already has an active session')
            return HttpResponseRedirect(reverse('pokersessions:active'))

        return super(StartPokerSessionView, self).get(request, args, kwargs)

    def form_valid(self, form):
        resp = super(StartPokerSessionView, self).form_valid(form)
        clean = form.cleaned_data
        user = self.request.user
        location = clean['location']
        game = clean['game']

        poker_session = PokerSession(user=user, location=location, game=game, active=True)
        poker_session.save()

        buy_in = clean['buy_in']
        time = datetime.now(pytz.utc)

        update = PokerSessionUpdate(poker_session=poker_session, time=time,
                buy_in=buy_in, chip_stack=buy_in)
        update.save()

        messages.success(self.request, 'Poker Session Started at {0}'.format(poker_session.location))

        return resp

class ActivePokerSessionView( LoginRequiredMixin, FormView ):

    template_name = "pokersessions/active.html"
    form_class = ActivePokerSessionUpdateForm
    success_url = reverse_lazy('pokersessions:active')

    def get(self, request, *args, **kwargs):
        #check if user has an active session already
        user = request.user
        poker_session_count = PokerSession.objects.filter(active=True).filter(user=user).count()
        if(poker_session_count > 1):
            messages.error(request, 'User has multiple active sessions')
            return HttpResponseRedirect(reverse('pokersessions:index'))
        elif(poker_session_count == 0):
            messages.error(request, 'User does not have an active session')
            return HttpResponseRedirect(reverse('pokersessions:start'))

        return super(ActivePokerSessionView, self).get(request, args, kwargs)

    def form_valid(self, form):
        clean = form.cleaned_data
        buy_in = clean['buy_in']
        chip_stack = clean['chip_stack']
        comment = clean['comment']

        time = datetime.now(pytz.utc)

        update = PokerSessionUpdate(poker_session=self.active_session(), time=time,
                buy_in=buy_in, chip_stack=chip_stack, comment=comment)
        update.save()

        if ( 'end_session' in self.request.POST ):
            session = self.active_session()
            session.active = False
            session.save()
            messages.success(self.request, 'The poker session has ended')
            return HttpResponseRedirect(reverse('pokersessions:index'))

        return super(ActivePokerSessionView, self).form_valid(form)


    def active_session(self):
        user = self.request.user
        return PokerSession.objects.get(active=True, user=user)

class PokerSessionDetailView(TemplateView):

    template_name = "pokersessions/detail.html"
    _poker_session = None

    def get(self, request, *args, **kwargs):
        resp = super(PokerSessionDetailView, self).get(request, args, kwargs)
        if(self.poker_session().public == False):
            messages.error(self.request, "Not a public poker session")
            return HttpResponseRedirect(reverse('pokersessions:view', kwargs={'user_id':self.poker_session().user.id}))
        elif(self.poker_session() == None):
            messages.error(self.request, "Poker Session Doesnt Exist")
            return HttpResponseRedirect(reverse('pokersessions:index'))

        return resp

    def poker_session(self):
        if (self._poker_session == None):
            self._poker_session = PokerSession.objects.get(pk=self.kwargs['session_id'])
        return self._poker_session

    def ChipStackUpdatesChartJson(self):
      data = []

      if(self.poker_session().public):
         chip_stack_updates = self.poker_session().all_chip_stacks()
         tzinfo = timezone(self.poker_session().location.timezone)
         for update in chip_stack_updates:
            time = update.time.astimezone(tzinfo)
            time = datetime.strftime(time, "%Y-%m-%d %H:%M")
            data.append({'x':time, 'y':str(update.chip_stack)})

      return json.dumps(data)

    def BuyInUpdatesChartJson(self):
      data = []

      if(self.poker_session().public):
         buy_in_updates = self.poker_session().all_buy_ins()
         tzinfo = timezone(self.poker_session().location.timezone)
         for update in buy_in_updates:
            time = update.time.astimezone(tzinfo)
            time = datetime.strftime(time, "%Y-%m-%d %H:%M")
            data.append({'x':time, 'y':str(update.buy_in)})

         last_update_time = self.poker_session().session_updates().latest('time').time
         last_buy_in = buy_in_updates.latest('time').buy_in
         time = last_update_time.astimezone(tzinfo)
         time = datetime.strftime(time, "%Y-%m-%d %H:%M")
         data.append({'x':time, 'y':str(last_buy_in)})
      return json.dumps(data)
