from decimal import *

from django.db import models

from datetime import datetime, timedelta
from pytz import timezone
import pytz

from accounts.models import User
from locations.models import Location
from games.models import Game


class PokerSessionManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super(PokerSessionManager, self).__init__(*args, **kwargs)


# Create your models here.
class PokerSession(models.Model):
    user = models.ForeignKey(User)
    location = models.ForeignKey(Location)
    active = models.BooleanField(default=False)
    game = models.ForeignKey(Game)
    public = models.BooleanField(default=False)
    get_latest_by = 'time'
    deleted = models.BooleanField(default=False)

    def session_updates(self):
        sessions = PokerSessionUpdate.objects.filter(poker_session=self).order_by('time')
        return sessions

    def start_time(self):
        try:
            start_time = self.session_updates()[0].time
        except IndexError:
            start_time = None
        return start_time

    def end_time(self):
        try:
            end_time = self.session_updates().latest('time').time
        except IndexError:
            end_time = None
        return end_time

    def total_mins_played(self):
        return self.end_time() - self.start_time()

    def all_buy_ins(self):
        return self.session_updates().exclude(buy_in__isnull=True)

    def all_chip_stacks(self):
        return self.session_updates().exclude(chip_stack__isnull=True)

    def net(self):
        return self.all_chip_stacks().latest('time').chip_stack - self.all_buy_ins().latest('time').buy_in

    def short_title(self):
        return '{0} @ {1}'.format(self.game.short_str(), self.location)

    def __str__(self):
        return self.short_title()


class PokerSessionUpdate(models.Model):
    poker_session = models.ForeignKey(PokerSession)
    time = models.DateTimeField(
        blank=False
    )
    chip_stack = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    buy_in = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    comment = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return "Poker Session Update - poker_session.id = {0}".format(self.poker_session.id)

    def all_str(self):
        s = "poker_session = {0} | time = {1} | chip_stack = {2} | buy_in = {3} | comment = {4}".format(
                self.poker_session, self.time, self.chip_stack, self.buy_in, self.comment,
            )
        return s

    def chip_stack_pretty(self):
        if (self.chip_stack == None):
            return ""
        return "{0}{1:,}".format(
            self.poker_session.game.currency.symbol,
            float(str(self.chip_stack))
        )

    def buy_in_pretty(self):
        if (self.buy_in == None):
            return ""
        return "{0}{1:,}".format(
            self.poker_session.game.currency.symbol,
            float(str(self.buy_in))
        )

