from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage),
    path("homepage/", views.homepage),
    path("upload/", views.upload_file),
    path("test_ui/", views.test_ui),
]
