from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    path("", include("reserve.urls")),
    path("auth/", include("users.urls")),
    path("admin/", admin.site.urls),
]
