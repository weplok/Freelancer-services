from django.urls import path
from .views import homepage_view, test_ui_view

urlpatterns = [
    path("", homepage_view, name="homepage"),
    path("test_ui/", test_ui_view, name="test_ui"),
]
