import random

import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SignUpForm, LoginForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not user.avatar_url:
                avatar_response = requests.get(
                    url=f"https://picsum.photos/seed/{random.randint(1, 999999)}/200",
                )
                user.avatar_url = avatar_response.url
                user.save()
            login(request, user)
            return redirect("profile")
    else:
        form = SignUpForm()

    context = {
        "form": form,
        "page_title": "Регистрация",
    }

    return render(request, "accounts/signup.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")
    form = LoginForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("profile")

    context = {
        "form": form,
        "page_title": "Аутентификация",
    }

    return render(request, "accounts/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def personal_view(request):
    context = {"page_title": f"Кабинет {request.user.username}"}
    return render(request, "accounts/profile.html", context)
