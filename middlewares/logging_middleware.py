"""
Middleware para logging de requests y responses
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware para registrar todas las peticiones HTTP"""
    
    def process_request(self, request):
        """Registra información del request"""
        request.start_time = time.time()
        
        logger.info(
            f"Request: {request.method} {request.path} "
            f"| User: {request.user if request.user.is_authenticated else 'Anonymous'} "
            f"| IP: {self.get_client_ip(request)}"
        )
        
        return None
    
    def process_response(self, request, response):
        """Registra información del response"""
        
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger.info(
                f"Response: {request.method} {request.path} "
                f"| Status: {response.status_code} "
                f"| Duration: {duration:.2f}s"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIErrorLoggingMiddleware(MiddlewareMixin):
    """Middleware para registrar errores de la API"""
    
    def process_exception(self, request, exception):
        """Registra excepciones no manejadas"""
        
        logger.error(
            f"Exception: {request.method} {request.path} "
            f"| User: {request.user if request.user.is_authenticated else 'Anonymous'} "
            f"| Error: {str(exception)}",
            exc_info=True
        )
        
        return None