from django.shortcuts import render

def homepage_view(request):
    return render(request, "homepage/homepage.html")


def test_ui_view(request):
    return render(request, "homepage/test_ui.html")
