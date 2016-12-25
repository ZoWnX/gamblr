from django.views.generic import TemplateView
from django.http import HttpResponse

import json

from pokersessions.models import PokerSession, PokerSessionUpdate


class ChipStackPokerUpdateJson(TemplateView):

   def get(self, request, *args, **kwargs):
      data = []

      session_id = self.kwargs['session_id']
      poker_session = PokerSession.objects.get(pk=session_id)

      if(poker_session.public):
         chip_stack_updates = poker_session.all_chip_stacks()
         for update in chip_stack_updates:
            data.append({'x':str(update.time), 'y':str(update.chip_stack)})
      return HttpResponse(json.dumps(data), content_type='application/json')
