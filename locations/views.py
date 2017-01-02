from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import LocationForm
from .models import Location
# Create your views here.
@login_required
def locations_list_view(request):
   user = request.user
   form = LocationForm(request.POST or None)

   if(request.method == "POST"):
      if(form.is_valid()):
         cleaned = form.cleaned_data
         location = Location(
               name=cleaned['name'],
               timezone=cleaned['timezone'],
               user=user
            )

         location.save()
         form = LocationForm()


   locations = Location.objects.filter(public=True) | Location.objects.filter(user=user)
   context = {
      'locations': locations,
      'form': form,
   }
   return render(request, 'locations/list.html', context)