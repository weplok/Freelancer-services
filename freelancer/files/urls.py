from django.urls import path
from .views import (
    homepage_view,
    test_ui_view,
    upload_file_view,
    get_upload_value_view,
)

urlpatterns = [
    path("", homepage_view, name="homepage"),
    path("homepage/", homepage_view, name="homepage"),
    path("upload/", upload_file_view, name="upload_file"),
    path("upload_status/<str:upload_id>/", get_upload_value_view, name="get_upload_value"),
    path("test_ui/", test_ui_view, name="test_ui"),
]
