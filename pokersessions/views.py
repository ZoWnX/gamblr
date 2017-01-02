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
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory

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

        return redirect('pokersessions:edit', session_id=poker_session.id)

@login_required
def edit_poker_session(request, session_id):
    user = request.user

    # Create the formset, specifying the form and formset we want to use.
    UpdateFormSet = formset_factory(PokerSessionUpdateForm)
    poker_session = PokerSession.objects.get(pk=session_id)
    tz = timezone(poker_session.location.timezone)

    if(poker_session.user.id != user.id):
        messages.error(request, 'Not the owner of the poker session')
        return redirect('pokersession:index')

    if(request.method == "POST"):
        poker_session_form = PokerSessionForm(request.POST)
        update_formset = UpdateFormSet(request.POST)

        if(poker_session_form.is_valid() and update_formset.is_valid()):
            poker_session.location = poker_session_form.cleaned_data['location']
            poker_session.game = poker_session_form.cleaned_data['game']
            poker_session.public = poker_session_form.cleaned_data['public']

            poker_session.save()

            new_updates = []

            for update_form in update_formset:
                clean = update_form.cleaned_data
                time = clean.get('time')
                if time is None:
                    continue

                time = tz.localize(time.replace(tzinfo=None)).astimezone(pytz.utc)

                chip_stack = clean['chip_stack']
                buy_in = clean['buy_in']
                comment = clean['comment']
                if not (chip_stack is None and buy_in is None and comment is None):
                    new_updates.append(PokerSessionUpdate(
                            poker_session=poker_session,
                            time=time,
                            chip_stack=chip_stack,
                            buy_in=buy_in,
                            comment=comment
                        ))

            try:
                with transaction.atomic():
                    PokerSessionUpdate.objects.filter(poker_session=poker_session).delete()
                    PokerSessionUpdate.objects.bulk_create(new_updates)
                    messages.success(request, 'Poker Session Updated')

            except IntegrityError:
                messages.error(request, "There was an error with the update")

        else:
            context = {
                'poker_session_form': poker_session_form,
                'update_formset': update_formset,
                'poker_session': poker_session,
            }

            return render(request, 'pokersessions/edit_all.html', context)

    updates = poker_session.session_updates()
    update_info = []
    for update in updates:
        time = update.time.astimezone(tz)
        update_info.append({
            'time': time.strftime("%Y-%m-%d %H:%M"),
            'buy_in': update.buy_in,
            'chip_stack': update.chip_stack,
            'comment': update.comment
        })
    poker_session_form = PokerSessionForm(instance=poker_session)
    update_formset = UpdateFormSet(initial=update_info)

    context = {
        'poker_session_form': poker_session_form,
        'update_formset': update_formset,
        'poker_session': poker_session,
    }

    return render(request, 'pokersessions/edit.html', context)



class AddPokerSessionUpdateView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/update_add.html"
    form_class = PokerSessionUpdateForm
    success_url = reverse_lazy('pokersessions:index')
    poker_session = None

    def get(self, request, *args, **kwargs):
        session_id = self.kwargs['session_id']
        self.poker_session = PokerSession.objects.get(pk=session_id)

        return super(AddPokerSessionUpdateView, self).get(request, args, kwargs)

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

    def get_initial(self):
        session_id = self.kwargs['session_id']
        poker_session = PokerSession.objects.get(pk=session_id)
        return { "time": poker_session.end_time() }

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
