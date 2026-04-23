from django.urls import path
from .views import (
    all_projects_view,
    project_create_view,
    upload_file_view,
    project_view,
    get_upload_value_view,
)

urlpatterns = [
    path("all/", all_projects_view, name="all_projects"),
    path("create/", project_create_view, name="project_create"),
    path("upload/", upload_file_view, name="upload_file"),
    path("project/<slug:project_slug>", project_view, name="project"),
    path("upload_status/<str:upload_id>/", get_upload_value_view, name="get_upload_value"),
]
