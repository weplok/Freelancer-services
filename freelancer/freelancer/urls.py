from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("files/", include("files.urls")),
    path("", include("homepage.urls")),
    path("accounts/", include("accounts.urls")),
    path('django-rq/', include('django_rq.urls')),
]
