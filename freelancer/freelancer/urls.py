from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("projects/", include("projects.urls")),
    path("", include("homepage.urls")),
    path("accounts/", include("accounts.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (
        path("__debug__/", include(debug_toolbar.urls), name="debug_toolbar"),
    )
