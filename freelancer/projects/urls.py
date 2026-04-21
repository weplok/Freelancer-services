from django.urls import path
from .views import (
    all_projects_view,
    upload_file_view,
    get_upload_value_view,
)

urlpatterns = [
    path("all/", all_projects_view, name="all_projects"),
    path("upload/", upload_file_view, name="upload_file"),
    path("upload_status/<str:upload_id>/", get_upload_value_view, name="get_upload_value"),
]
