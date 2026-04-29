from django.urls import path
from .views import (
    all_projects_view,
    project_create_view,
    upload_file_view,
    project_view,
    project_edit_view,
    project_delete_select_files_view,
    confirm_delete_select_files_view,
    project_delete_view,
    upload_to_project_view,
    get_upload_value_view,
    file_detail_view,
)

urlpatterns = [
    path("all/", all_projects_view, name="all_projects"),
    path("create/", project_create_view, name="project_create"),
    path("upload/", upload_file_view, name="upload_file"),
    path(
        "upload_status/<str:upload_id>/",
        get_upload_value_view,
        name="get_upload_value",
    ),
    path("project/<slug:project_slug>", project_view, name="project_detail"),
    path(
        "project/edit/<slug:project_slug>",
        project_edit_view,
        name="project_edit",
    ),
    path(
        "project/del_files/<slug:project_slug>",
        project_delete_select_files_view,
        name="project_files_delete_select",
    ),
    path(
        "project/confirm_del/<slug:project_slug>",
        confirm_delete_select_files_view,
        name="project_files_delete_confirm",
    ),
    path(
        "project/delete/<slug:project_slug>",
        project_delete_view,
        name="project_delete",
    ),
    path(
        "project/upload/<slug:project_slug>",
        upload_to_project_view,
        name="upload_file_to_project",
    ),
    path(
        "project/<slug:project_slug>/<slug:file_slug>",
        file_detail_view,
        name="file_detail",
    ),
]
