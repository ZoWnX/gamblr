from datetime import datetime, timedelta
from pytz import timezone
import pytz

from django.db import models

from accounts.models import User

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=256)
    address = models.TextField(blank=True)
    user = models.ForeignKey(User)
    public = models.BooleanField(default=False)
    #games = models.ManyToManyField(Game)

    TIMEZONE_CHOICES = [(x, x) for x in pytz.common_timezones]
    TIMEZONE_DEFAULT = ("UTC","UTC")

    timezone = models.CharField(
            max_length=80,
            choices=TIMEZONE_CHOICES,
            default=TIMEZONE_DEFAULT
        )

    def utc_to_local_time(self, utc_time):
        local_timezone = timezone(self.timezone)
        return utc_time.astimezone(local_timezone)

    def __str__(self):
        return self.name

