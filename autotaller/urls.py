from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/core/", include("core.urls")),
    path("api/servicios/", include("servicios.urls")),
    path("api/solicitudes/", include("solicitudes.urls")),
]
