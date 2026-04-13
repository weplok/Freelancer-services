from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage),
    path("homepage/", views.homepage),
    path("upload/", views.upload_file),
    path("upload_status/<str:upload_id>/", views.get_upload_value),
    path("test_ui/", views.test_ui),
]
