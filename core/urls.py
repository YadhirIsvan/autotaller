"""
CORE URLS (ACTUALIZADO CON AUTH)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TipoUsuarioViewSet, EstadoViewSet, UsuarioViewSet,
    MarcaViewSet, ModeloViewSet, VehiculoViewSet,
    TampBlockPrincipalViewSet, TampBlockTalleresViewSet
)
try:
    from .auth_views import login_view, logout_view, current_user_view, register_view
except ImportError:
    # Si no existe auth_views.py todavía, crear placeholder
    from rest_framework.decorators import api_view
    from rest_framework.response import Response
    
    @api_view(['POST'])
    def login_view(request):
        return Response({'error': 'Auth views not implemented yet'})
    
    @api_view(['POST'])
    def logout_view(request):
        return Response({'error': 'Auth views not implemented yet'})
    
    @api_view(['GET'])
    def current_user_view(request):
        return Response({'error': 'Auth views not implemented yet'})
    
    @api_view(['POST'])
    def register_view(request):
        return Response({'error': 'Auth views not implemented yet'})

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
    # Autenticación
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/current-user/', current_user_view, name='current-user'),
    path('auth/register/', register_view, name='register'),
    
    # Router URLs
    path('', include(router.urls)),
]