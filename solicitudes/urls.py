"""
SOLICITUDES URLS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudViewSet, ReservacionTallerPrincipalViewSet

router = DefaultRouter()

router.register(r'solicitudes', SolicitudViewSet, basename='solicitud')
router.register(r'reservaciones', ReservacionTallerPrincipalViewSet, basename='reservacion')

urlpatterns = [
    path('', include(router.urls)),
]