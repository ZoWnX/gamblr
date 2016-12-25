from django import forms

from .models import ( PokerSession, PokerSessionUpdate)
from locations.models import Location
from games.models import Game

class PokerSessionForm(forms.ModelForm):
   class Meta:
      model = PokerSession
      fields = ['location', 'game', 'public']

class PokerSessionUpdateForm(forms.Form):
   time = forms.DateTimeField(
         label="YYYY-MM-DD HH:mm",
      )
   buy_in = forms.DecimalField(
         max_digits=15,
         decimal_places=2,
         required=False,
         label="Total Buy in",
      )
   chip_stack = forms.DecimalField(
         max_digits=15,
         decimal_places=2,
         required=False,
         label="Current Chip Stack",
      )
   comment = forms.CharField(
         required = False,
         widget=forms.Textarea
      )

class PokerSessionCreateForm(forms.Form):
   time = forms.DateTimeField(
         label="YYYY-MM-DD HH:mm"
      )
   location = forms.ModelChoiceField(
         queryset=Location.objects.all(),
         empty_label=None,
         required=True,
         label="Location"
      )
   game = forms.ModelChoiceField(
         queryset=Game.objects.all(),
         empty_label=None,
         required=True,
         label="Game"
      )
   buy_in = forms.DecimalField(
         max_digits=15,
         decimal_places=2,
         required=True,
         label="Total Buy in"
      )

class PokerSessionStartForm(forms.Form):
   location = forms.ModelChoiceField(
         queryset=Location.objects.all(),
         empty_label=None,
         required=True,
         label="Location"
      )
   game = forms.ModelChoiceField(
         queryset=Game.objects.all(),
         empty_label=None,
         required=True,
         label="Game"
      )
   buy_in = forms.DecimalField(
         max_digits=15,
         decimal_places=2,
         required=True,
         label="Buy in"
      )

class ActivePokerSessionUpdateForm(forms.Form):
   buy_in = forms.DecimalField(
         max_digits=15,
         decimal_places=2,
         required=False,
         label="Total Buy in",
      )
   chip_stack = forms.DecimalField(
         max_digits=15,
         decimal_places=2,
         required=False,
         label="Current Chip Stack",
      )
   comment = forms.CharField(
         required = False,
         widget=forms.Textarea
      )