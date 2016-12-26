from django.db import models

from accounts.models import User
from locations.models import Location

# Create your models here.

class Currency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=5)
    code = models.CharField(max_length=3)

    def __str__(self):
        return 'Currency: {0} - {1} - {2}'.format(self.name, self.code, self.symbol)

    def short_str(self):
        return '{0} ({1})'.format(self.name, self.symbol)


    class Meta:
        verbose_name_plural = "currencies"

class Game(models.Model):

    title = models.CharField(max_length=256)
    user = models.ForeignKey(User)
    public = models.BooleanField(default=False)
    tournament = models.BooleanField(default=False)
    min_buy_in = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_buy_in = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey(
        'Currency',
        default=1
    )

    def short_str(self):
        return '{1} ({0})'.format(self.title, self.currency.symbol)

    def __str__(self):
        return '{0} min:{1} max:{2} currency:{3}'.format(self.title, self.min_buy_in, self.max_buy_in, self.currency.symbol)

    class Meta:
        ordering = ('title',)
