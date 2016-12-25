from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import PasswordResetForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login

from .forms import RegistrationForm, LoginForm
from .models import User

class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:register')

    def form_valid(self, form):
        print("RegisterView.form_valid() - Registering user {0}"
                .format(form.cleaned_data['email']))
        email = form.cleaned_data['email']
        password = form.cleaned_datua['password']
        u = User.objects.create_user(email,password)
        u.save()
        return super(RegisterView, self).form_valid(form)

class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy('accounts:index')

    def form_valid(self, form):
        print("LoginView.form_valid() - Authenticating User {0}"
                .format(form.cleaned_data['email']))
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            # A backend authenticated the credentials
            print("User is authenticated")
            login(self.request, user)
        else:
            # No backend authenticated the credentials
            print("User is not authenticated")

        return super(LoginView, self).form_valid(form)

class IndexView(TemplateView):
    template_name = "accounts/index.html"
