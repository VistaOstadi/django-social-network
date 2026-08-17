from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class" : "form-control",
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class" : "form-control",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class" :"form-control",
        })
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            raise ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        username_exists = User.objects.filter(username=username).exists()
        if username_exists:
            raise ValidationError("This username is already registered.")
        return username


