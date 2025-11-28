"""
Middleware para deshabilitar CSRF en endpoints de API
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFMiddleware(MiddlewareMixin):
    """Deshabilita CSRF para rutas de API"""
    
    def process_request(self, request):
        # Deshabilitar CSRF para todas las rutas que empiecen con /api/
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
