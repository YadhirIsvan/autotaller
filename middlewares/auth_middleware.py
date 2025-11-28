"""
Middleware de autenticación y permisos personalizados
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from core.models import TipoUsuario


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """Middleware para control de acceso basado en roles"""
    
    # Rutas públicas que no requieren autenticación
    PUBLIC_ROUTES = [
        '/admin/',
        '/api/core/auth/login/',
        '/api/core/auth/register/',
        '/api/core/auth/logout/',
        '/api/core/auth/current-user/',
    ]
    
    # Rutas por tipo de usuario
    ROLE_ROUTES = {
        TipoUsuario.ADMINISTRADOR: [
            '/api/core/',
            '/api/solicitudes/',
            '/api/servicios/',
        ],
        TipoUsuario.AGENTE: [
            '/api/solicitudes/',
            '/api/servicios/',
        ],
        TipoUsuario.TALLER: [
            '/api/servicios/mis-servicios/',
            '/api/servicios/actualizar-progreso/',
            '/api/servicios/calendario/',
        ],
        TipoUsuario.CLIENTE: [
            '/api/solicitudes/mis-solicitudes/',
            '/api/core/vehiculos/',
        ],
    }
    
    def process_request(self, request):
        """Procesa cada request verificando permisos"""
        
        # Permitir rutas públicas
        if any(request.path.startswith(route) for route in self.PUBLIC_ROUTES):
            return None
        
        # Verificar autenticación
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Autenticación requerida'},
                status=401
            )
        
        # Verificar si es superusuario
        if request.user.is_superuser:
            return None
        
        # Verificar permisos basados en rol
        user_role = request.user.id_tipo.cve
        allowed_routes = self.ROLE_ROUTES.get(user_role, [])
        
        # Verificar si la ruta está permitida para el rol
        if not any(request.path.startswith(route) for route in allowed_routes):
            return JsonResponse(
                {
                    'error': 'No tiene permisos para acceder a este recurso',
                    'role': user_role
                },
                status=403
            )
        
        return None


class UserActiveCheckMiddleware(MiddlewareMixin):
    """Middleware para verificar que el usuario esté activo"""
    
    # Rutas que no necesitan verificación de usuario activo
    SKIP_ROUTES = [
        '/admin/',
        '/api/core/auth/login/',
        '/api/core/auth/register/',
        '/api/core/auth/logout/',
    ]
    
    def process_request(self, request):
        """Verifica si el usuario está activo"""
        
        # Saltar verificación para rutas públicas
        if any(request.path.startswith(route) for route in self.SKIP_ROUTES):
            return None
        
        if request.user.is_authenticated:
            if hasattr(request.user, 'activo') and not request.user.activo:
                return JsonResponse(
                    {'error': 'Usuario inactivo. Contacte al administrador.'},
                    status=403
                )
        
        return None

