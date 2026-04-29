from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from .models import CustomUser


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text="youremail@yandex.ru")
    name = forms.CharField(max_length=25, help_text="Имя")

    class Meta:
        model = CustomUser
        fields = ("username", "email", "name", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
