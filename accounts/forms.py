from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_again = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['email',]

    #called on validation of the form
    def clean(self):
        #run the standard clean method first
        cleaned_data=super(RegistrationForm, self).clean()

        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")
            #check if passwords are entered and match
        if password and password_again and password==password_again:
            print("RegistrationForm.clean() -- Passwords Match")
        else:
            raise forms.ValidationError("Passwords do not match!")
            #always return the cleaned data
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())