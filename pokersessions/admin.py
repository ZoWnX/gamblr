from django.contrib import admin

# Register your models here.
from . import models
admin.site.register(models.PokerSession)
admin.site.register(models.PokerSessionUpdate)

