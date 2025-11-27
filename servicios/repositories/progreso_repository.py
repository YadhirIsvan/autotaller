"""
Repository para operaciones de base de datos de Progreso de Servicios
"""
from typing import List, Optional
from servicios.models import ProgresoServicio


class ProgresoServicioRepository:
    """Maneja operaciones de BD para progreso de servicios"""
    
    @staticmethod
    def get_all() -> List[ProgresoServicio]:
        """Obtiene todos los registros de progreso"""
        return ProgresoServicio.objects.select_related(
            'id_reservacion_servicio',
            'actualizado_por'
        ).all()
    
    @staticmethod
    def get_by_id(progreso_id: int) -> Optional[ProgresoServicio]:
        """Obtiene un registro de progreso por ID"""
        try:
            return ProgresoServicio.objects.select_related(
                'id_reservacion_servicio',
                'actualizado_por'
            ).get(id=progreso_id)
        except ProgresoServicio.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_reservacion_servicio(reservacion_servicio_id: int) -> List[ProgresoServicio]:
        """Obtiene el historial de progreso de una reservación de servicio"""
        return ProgresoServicio.objects.filter(
            id_reservacion_servicio_id=reservacion_servicio_id
        ).select_related(
            'id_reservacion_servicio',
            'actualizado_por'
        ).order_by('-fecha')
    
    @staticmethod
    def get_ultimo_progreso(reservacion_servicio_id: int) -> Optional[ProgresoServicio]:
        """Obtiene el último registro de progreso de una reservación"""
        try:
            return ProgresoServicio.objects.filter(
                id_reservacion_servicio_id=reservacion_servicio_id
            ).select_related(
                'id_reservacion_servicio',
                'actualizado_por'
            ).latest('fecha')
        except ProgresoServicio.DoesNotExist:
            return None
    
    @staticmethod
    def create(data: dict) -> ProgresoServicio:
        """Crea un nuevo registro de progreso"""
        return ProgresoServicio.objects.create(**data)
    
    @staticmethod
    def delete(progreso: ProgresoServicio) -> None:
        """Elimina un registro de progreso"""
        progreso.delete()
    
    @staticmethod
    def get_by_taller(taller_id: int) -> List[ProgresoServicio]:
        """Obtiene progreso de servicios actualizados por un taller"""
        return ProgresoServicio.objects.filter(
            actualizado_por_id=taller_id
        ).select_related(
            'id_reservacion_servicio',
            'actualizado_por'
        ).order_by('-fecha')
    
    @staticmethod
    def get_historial_completo(reservacion_principal_id: int) -> List[ProgresoServicio]:
        """Obtiene todo el historial de progreso de una reservación principal"""
        return ProgresoServicio.objects.filter(
            id_reservacion_servicio__id_reservacion_taller_principal_id=reservacion_principal_id
        ).select_related(
            'id_reservacion_servicio__id_servicio_usuario_taller__id_servicio',
            'id_reservacion_servicio__id_servicio_usuario_taller__id_usuario_taller',
            'actualizado_por'
        ).order_by('-fecha')