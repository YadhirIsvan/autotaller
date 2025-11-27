"""
Middleware para manejo centralizado de errores
"""
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
from rest_framework.exceptions import APIException
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(MiddlewareMixin):
    """Middleware para manejo global de errores"""
    
    def process_exception(self, request, exception):
        """Maneja diferentes tipos de excepciones"""
        
        # Errores de validación
        if isinstance(exception, ValidationError):
            return JsonResponse(
                {
                    'error': 'Error de validación',
                    'details': exception.message_dict if hasattr(exception, 'message_dict') else str(exception)
                },
                status=400
            )
        
        # Errores de integridad de BD
        if isinstance(exception, IntegrityError):
            return JsonResponse(
                {
                    'error': 'Error de integridad de datos',
                    'message': 'El registro viola restricciones de la base de datos'
                },
                status=400
            )
        
        # Errores de permisos
        if isinstance(exception, PermissionDenied):
            return JsonResponse(
                {
                    'error': 'Permiso denegado',
                    'message': str(exception)
                },
                status=403
            )
        
        # Errores de DRF
        if isinstance(exception, APIException):
            return JsonResponse(
                {
                    'error': exception.default_detail,
                    'details': exception.detail if hasattr(exception, 'detail') else None
                },
                status=exception.status_code
            )
        
        # Errores genéricos
        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)
        
        return JsonResponse(
            {
                'error': 'Error interno del servidor',
                'message': 'Ha ocurrido un error inesperado'
            },
            status=500
        )