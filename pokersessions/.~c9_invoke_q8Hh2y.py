from datetime import datetime, timedelta
from pytz import timezone
import pytz

from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordResetForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from accounts.models import User
from .models import PokerSession, PokerSessionUpdate
from .forms import PokerSessionStartForm, PokerSessionForm

# Create your views here.

class PokerSessionIndexView(LoginRequiredMixin, ListView):
    template_name = 'pokersessions/index.html'
    model = PokerSession

    def get_queryset(self):
        user = self.request.user
        object_list = self.model.objects.filter(user=user)
        return object_list

class CreatePokerSessionView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/create.html"
    form_class = PokerSessionStartForm
    success_url = reverse_lazy('pokersessions:index')

    def form_valid(self, form):
        resp = super(CreatePokerSessionView, self).form_valid(form)
        clean = form.cleaned_data
        user = self.request.user
        location = clean['location']
        game = clean['game']

        poker_session = PokerSession(user=user, location=location, game=game, active=False)
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

        session_id = self.kwargs['session_id']
        poker_session = PokerSession.objects.get(pk=session_id)
        poker_session.location = location
        poker_session.game = game
        poker_session.save()

        messages.success(self.request, '{0} Updated'.format(poker_session))

        return self.render_to_response(self.get_context_data(form=form))

class AddPokerSessionUpdateView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/update.html"
    form_class = PokerSessionUpdateFOrm
    poker_session = None
    success_url = reverse_lazy('pokersessions:index')

'''
class IndexView(TemplateView):
    template_name = "pokersessions/index.html"

    def poker_sessions(self):
        user = self.request.user
        poker_sessions = []
        if user.is_authenticated():
            poker_sessions = PokerSession.objects.filter(user=user)
        print(poker_sessions)
        return poker_sessions


class StartPokerSessionView(FormView):
    template_name = "pokersessions/start_session.html"
    form_class = StartPokerSessionForm
    success_url = reverse_lazy('pokersessions:current')

    def get(self, request, *args, **kwargs):
        user = request.user
        if(PokerSession.objects.user_active_session(user) is not None):
            return redirect("pokersessions:current")

        return super(StartPokerSessionView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated():
            started= datetime.utcnow()
            poker_session = PokerSession(
                    user=user,
                    location=form.cleaned_data['location'],
                    start_time=started,
                    active=True,
                    current_chip_stack=form.cleaned_data['buy_in'],
                    current_buy_in=form.cleaned_data['buy_in'],
                    current_game=form.cleaned_data['game']
                )
            poker_session.save()
            start_update = StartUpdate(
                    poker_session=poker_session,
                    time=started,
                    buy_in=form.cleaned_data['buy_in'],
                    game=form.cleaned_data['game']
                )
            start_update.save()
        return super(StartPokerSessionView, self).form_valid(form)


class UpdatePokerSessionView(FormView):
    template_name = "pokersessions/update_session.html"
    form_class = UpdatePokerSessionForm
    success_url = reverse_lazy('pokersessions:update')

    current_poker_session = None

    def current_poker_session(self):
        print("in current_poker_session()")
        return self.current_poker_session

    def get(self, request, *args, **kwargs):
        print("in get()")
        user = request.user
        if(user.is_authenticated()):
            print("user is_authenticated")
            self.current_poker_session = PokerSession.objects.user_active_session(user)
            print("current_poker_session")
            print(self.current_poker_session)
            if(self.current_poker_session is None):
                return redirect("pokersessions:start")

        return super(UpdatePokerSessionView, self).get(request, *args, **kwargs)

    def get_initial(self):
        user = self.request.user
        current_poker_session = PokerSession.objects.user_active_session(user)

        return {
            'game': current_poker_session.current_game,
            'buy_in': current_poker_session.current_buy_in,
            'chip_stack': current_poker_session.current_chip_stack
        }

class PokerSessionView(TemplateView):
    template_name = "pokersessions/view.html"

    def poker_session(self):
        ps_id = self.kwargs['id']
        print("ps_id = {0}".format(ps_id))
        ps_obj = PokerSession.objects.get(pk=ps_id)
        print("ps_obj = {0}".format(ps_obj))
        return ps_obj

    def poker_session_updates(self):
        ps = self.poker_session()
        print("ps = {0}".format(ps))
        return PokerSessionUpdate.objects.filter(poker_session=ps).order_by('time')

class PokerSessionEditView(LoginRequiredMixin, UpdateView):
    context_object_name = 'poker_session'
    template_name = "pokersessions/edit.html"
    form_class = PokerSessionForm
    model = PokerSession
    success_url = reverse_lazy('pokersessions:index')

    def get_object(self, queryset=None):
        obj = PokerSession.objects.get(id=self.kwargs['id'])
        if(obj.user.id == self.request.user.id):
            return obj
        else:
            return None


    def form_valid(self, form):
        resp = super(PokerSessionEditView, self).form_valid(form)
        clean = form.cleaned_data
        obj = self.get_object()
        start_time = clean['start_time']
        end_time = clean['end_time']
        location = clean['location']
        tzinfo = timezone(location.timezone)
        obj.start_time = start_time.replace(tzinfo=tzinfo).astimezone(pytz.utc)
        obj.end_time = end_time.replace(tzinfo=tzinfo).astimezone(pytz.utc)
        obj.location = location
        obj.save()
        return resp


    @property
    def get_session_updates(self):
        obj = self.get_object()
        if (obj is None):
            return None
        return PokerSessionUpdate.objects.filter(poker_session=obj)

class PokerSessionBatchLoadView(FormView):
    template_name = "pokersessions/batch_session.html"
    form_class = PokerSessionBatchLoadForm
    success_url = reverse_lazy('pokersessions:index')

class AddPokerSessionView(FormView):
    template_name = "pokersessions/add_session.html"
    form_class = AddPokerSessionForm
    success_url = reverse_lazy("pokersessions:index")


    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated():
            poker_session = PokerSession(
                    user=user,
                    location=form.cleaned_data['location'],
                    start_time=form.cleaned_data['start_time'].
                        replace(tzinfo=timezone(form.cleaned_data['location'].timezone)),
                    end_time=form.cleaned_data['end_time'].
                        replace(tzinfo=timezone(form.cleaned_data['location'].timezone)),
                    active=False,
                    current_chip_stack=form.cleaned_data['end_chip_stack'],
                    current_buy_in=form.cleaned_data['start_buy_in'],
                    current_game=form.cleaned_data['game']
                )
            poker_session.save()
            start_update = StartUpdate(
                    poker_session=poker_session,
                    time=poker_session.start_time,
                    buy_in=poker_session.current_buy_in,
                    game=poker_session.current_game
                )
            start_update.save()
            end_update = EndUpdate(
                    poker_session=poker_session,
                    time=poker_session.end_time,
                    chip_stack=poker_session.current_chip_stack
                )
            end_update.save()
        return super(AddPokerSessionView, self).form_valid(form)

class PokerSessionUpdateEditView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/update_edit.html"
    form_class = PokerSessionUpdateForm

    def get_context_data(self, **kwargs):
        context = super(PokerSessionUpdateEditView, self).get_context_data(**kwargs)
        context['poker_session'] = PokerSession.objects.get(pk=self.kwargs['session_id'])
        return context

    def get_initial(self):
        self.update_id = self.kwargs['update_id']

        update = PokerSessionUpdate.objects.get(pk=self.update_id)

        initial = { 'time': update.time }

        if(isinstance(update, ChipStackUpdate)):
            initial['chip_stack'] = update.chip_stack
            initial['chip_stack_update'] = True
        elif(isinstance(update, BuyinUpdate)):
            initial['buy_in'] = update.buy_in
            initial['buy_in_update'] = True
        elif(isinstance(update, GameUpdate)):
            initial['game'] = update.game
            initial['game_update'] = True

        print (initial)

        return initial

class PokerSessionUpdateAddView(LoginRequiredMixin, FormView):
    template_name = "pokersessions/update_add.html"
    form_class = PokerSessionUpdateForm

    def get_context_data(self, **kwargs):
        context = super(PokerSessionUpdateAddView, self).get_context_data(**kwargs)
        context['poker_session'] = PokerSession.objects.get(pk=self.kwargs['session_id'])
        return context

    def form_valid(self, form):
        cleaned = form.cleaned_data
        time = cleaned['time']
        poker_session = PokerSession.objects.get(pk=self.kwargs['session_id'])
        time=time.replace(tzinfo=timezone(poker_session.location.timezone))
        """
        figure out what type of update this is

        Get all updates first for this poker_session
        """
        updates = PokerSessionUpdate.objects.filter(poker_session=poker_session).order_by('time')


        return super(PokerSessionUpdateAddView, self).form_valid(form)

'''