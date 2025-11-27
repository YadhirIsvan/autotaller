"""
Service para lógica de negocio de Progreso de Servicios
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from django.db import transaction
from servicios.models import ProgresoServicio
from servicios.repositories.progreso_repository import ProgresoServicioRepository
from servicios.repositories.servicio_repository import ReservacionServicioRepository
from solicitudes.repositories.reservacion_repository import ReservacionRepository


class ProgresoServicioService:
    """Maneja la lógica de negocio para progreso de servicios"""
    
    def __init__(self):
        self.repository = ProgresoServicioRepository()
        self.reservacion_servicio_repository = ReservacionServicioRepository()
        self.reservacion_principal_repository = ReservacionRepository()
    
    def get_historial_by_servicio(self, reservacion_servicio_id: int) -> List[ProgresoServicio]:
        """Obtiene el historial de progreso de un servicio"""
        return self.repository.get_by_reservacion_servicio(reservacion_servicio_id)
    
    def get_ultimo_progreso(self, reservacion_servicio_id: int) -> ProgresoServicio:
        """Obtiene el último progreso de un servicio"""
        return self.repository.get_ultimo_progreso(reservacion_servicio_id)
    
    def get_historial_completo(self, reservacion_principal_id: int) -> List[ProgresoServicio]:
        """Obtiene todo el historial de una reservación principal"""
        return self.repository.get_historial_completo(reservacion_principal_id)
    
    @transaction.atomic
    def actualizar_progreso(self, data: Dict) -> ProgresoServicio:
        """
        Actualiza el progreso de un servicio
        data: {
            'id_reservacion_servicio': int,
            'porcentaje_nuevo': int,
            'dias_estimados': int (opcional),
            'comentario': str (opcional),
            'evidencia_url': str (opcional),
            'actualizado_por': int
        }
        """
        reservacion_servicio_id = data.get('id_reservacion_servicio')
        porcentaje_nuevo = data.get('porcentaje_nuevo')
        
        # Validar porcentaje
        if porcentaje_nuevo < 0 or porcentaje_nuevo > 100:
            raise ValidationError("El porcentaje debe estar entre 0 y 100")
        
        # Obtener reservación de servicio
        reservacion_servicio = self.reservacion_servicio_repository.get_by_id(
            reservacion_servicio_id
        )
        
        if not reservacion_servicio:
            raise ValidationError("Reservación de servicio no encontrada")
        
        # Obtener porcentaje anterior
        porcentaje_anterior = reservacion_servicio.progreso
        
        # Crear registro de progreso
        progreso = self.repository.create({
            'id_reservacion_servicio_id': reservacion_servicio_id,
            'porcentaje_anterior': porcentaje_anterior,
            'porcentaje_nuevo': porcentaje_nuevo,
            'dias_estimados': data.get('dias_estimados'),
            'comentario': data.get('comentario'),
            'evidencia_url': data.get('evidencia_url'),
            'actualizado_por_id': data.get('actualizado_por')
        })
        
        # Actualizar progreso en reservación de servicio
        self.reservacion_servicio_repository.actualizar_progreso(
            reservacion_servicio_id,
            porcentaje_nuevo
        )
        
        # Actualizar días estimados si viene
        if data.get('dias_estimados'):
            self.reservacion_servicio_repository.update(reservacion_servicio, {
                'estado_dias': data['dias_estimados']
            })
        
        # Actualizar avance global de la reservación principal
        self.reservacion_principal_repository.actualizar_avance_global(
            reservacion_servicio.id_reservacion_taller_principal_id
        )
        
        return progreso
    
    def get_progreso_por_taller(self, taller_id: int) -> List[ProgresoServicio]:
        """Obtiene progreso actualizado por un taller"""
        return self.repository.get_by_taller(taller_id)
    
    def get_estadisticas_progreso(self, reservacion_principal_id: int) -> Dict:
        """Obtiene estadísticas de progreso de una reservación"""
        from django.db.models import Avg, Count
        
        servicios = self.reservacion_servicio_repository.get_by_reservacion_principal(
            reservacion_principal_id
        )
        
        total_servicios = servicios.count()
        servicios_completados = servicios.filter(progreso=100).count()
        servicios_en_proceso = servicios.filter(progreso__gt=0, progreso__lt=100).count()
        servicios_pendientes = servicios.filter(progreso=0).count()
        
        promedio_general = servicios.aggregate(
            promedio=Avg('progreso')
        )['promedio'] or 0
        
        return {
            'total_servicios': total_servicios,
            'completados': servicios_completados,
            'en_proceso': servicios_en_proceso,
            'pendientes': servicios_pendientes,
            'promedio_general': round(promedio_general, 2)
        }