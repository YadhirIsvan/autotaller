"""
SERVICIOS URLS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaServicioViewSet, ServicioViewSet,
    ServicioUsuarioTallerViewSet, ReservacionServicioViewSet,
    ProgresoServicioViewSet
)

router = DefaultRouter()

router.register(r'categorias', CategoriaServicioViewSet, basename='categoria-servicio')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'servicios-taller', ServicioUsuarioTallerViewSet, basename='servicio-taller')
router.register(r'reservaciones-servicio', ReservacionServicioViewSet, basename='reservacion-servicio')
router.register(r'progreso', ProgresoServicioViewSet, basename='progreso-servicio')

urlpatterns = [
    path('', include(router.urls)),
]