"""
CORE URLS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TipoUsuarioViewSet, EstadoViewSet, UsuarioViewSet,
    MarcaViewSet, ModeloViewSet, VehiculoViewSet,
    TampBlockPrincipalViewSet, TampBlockTalleresViewSet
)

router = DefaultRouter()

# Catálogos
router.register(r'tipos-usuario', TipoUsuarioViewSet, basename='tipo-usuario')
router.register(r'estados', EstadoViewSet, basename='estado')

# Usuarios
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

# Vehículos
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'modelos', ModeloViewSet, basename='modelo')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')

# Calendarios
router.register(r'calendario-principal', TampBlockPrincipalViewSet, basename='calendario-principal')
router.register(r'calendario-talleres', TampBlockTalleresViewSet, basename='calendario-talleres')

urlpatterns = [
    path('', include(router.urls)),
]