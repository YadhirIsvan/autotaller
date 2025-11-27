"""
Repository para operaciones de base de datos de Solicitudes
"""
from typing import List, Optional
from django.db.models import Q
from solicitudes.models import Solicitud, DetalleSolicitud
from core.models import Estado


class SolicitudRepository:
    """Maneja todas las operaciones de BD para solicitudes"""
    
    @staticmethod
    def get_all() -> List[Solicitud]:
        """Obtiene todas las solicitudes"""
        return Solicitud.objects.select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        ).all()
    
    @staticmethod
    def get_by_id(solicitud_id: int) -> Optional[Solicitud]:
        """Obtiene una solicitud por ID"""
        try:
            return Solicitud.objects.select_related(
                'id_vehiculo__id_modelo__id_marca',
                'id_usuario',
                'id_estado',
                'aprobado_por'
            ).get(id=solicitud_id)
        except Solicitud.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_usuario(usuario_id: int) -> List[Solicitud]:
        """Obtiene solicitudes de un usuario específico"""
        return Solicitud.objects.filter(
            id_usuario_id=usuario_id
        ).select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        ).order_by('-fecha_creacion')
    
    @staticmethod
    def get_by_estado(estado_clave: str) -> List[Solicitud]:
        """Obtiene solicitudes por estado"""
        return Solicitud.objects.filter(
            id_estado__clave=estado_clave
        ).select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        ).order_by('-fecha_creacion')
    
    @staticmethod
    def get_pendientes() -> List[Solicitud]:
        """Obtiene solicitudes pendientes"""
        return SolicitudRepository.get_by_estado('pendiente')
    
    @staticmethod
    def get_aprobadas() -> List[Solicitud]:
        """Obtiene solicitudes aprobadas"""
        return SolicitudRepository.get_by_estado('aprobada')
    
    @staticmethod
    def get_rechazadas() -> List[Solicitud]:
        """Obtiene solicitudes rechazadas"""
        return SolicitudRepository.get_by_estado('rechazada')
    
    @staticmethod
    def create(data: dict) -> Solicitud:
        """Crea una nueva solicitud"""
        return Solicitud.objects.create(**data)
    
    @staticmethod
    def update(solicitud: Solicitud, data: dict) -> Solicitud:
        """Actualiza una solicitud existente"""
        for key, value in data.items():
            setattr(solicitud, key, value)
        solicitud.save()
        return solicitud
    
    @staticmethod
    def aprobar(solicitud_id: int, aprobado_por_id: int, estado_aprobada: Estado) -> Solicitud:
        """Aprueba una solicitud"""
        from django.utils import timezone
        
        solicitud = Solicitud.objects.get(id=solicitud_id)
        solicitud.id_estado = estado_aprobada
        solicitud.aprobado_por_id = aprobado_por_id
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        return solicitud
    
    @staticmethod
    def rechazar(solicitud_id: int, motivo: str, rechazado_por_id: int, estado_rechazada: Estado) -> Solicitud:
        """Rechaza una solicitud"""
        from django.utils import timezone
        
        solicitud = Solicitud.objects.get(id=solicitud_id)
        solicitud.id_estado = estado_rechazada
        solicitud.motivo_rechazo = motivo
        solicitud.aprobado_por_id = rechazado_por_id
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        return solicitud
    
    @staticmethod
    def delete(solicitud: Solicitud) -> None:
        """Elimina una solicitud"""
        solicitud.delete()
    
    @staticmethod
    def search(query: str) -> List[Solicitud]:
        """Busca solicitudes por placa, cliente o referencia"""
        return Solicitud.objects.filter(
            Q(id_vehiculo__placa__icontains=query) |
            Q(id_usuario__nombre__icontains=query) |
            Q(referencia_externa__icontains=query)
        ).select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        )
    
    @staticmethod
    def tiene_solicitud_pendiente(vehiculo_id: int) -> bool:
        """Verifica si un vehículo tiene solicitudes pendientes"""
        return Solicitud.objects.filter(
            id_vehiculo_id=vehiculo_id,
            id_estado__clave='pendiente'
        ).exists()
    
    @staticmethod
    def tiene_solicitud_aprobada_sin_reserva(vehiculo_id: int) -> bool:
        """Verifica si un vehículo tiene solicitudes aprobadas sin reservación"""
        return Solicitud.objects.filter(
            id_vehiculo_id=vehiculo_id,
            id_estado__clave='aprobada',
            reservacion__isnull=True
        ).exists()


class DetalleSolicitudRepository:
    """Maneja operaciones de BD para detalles de solicitudes"""
    
    @staticmethod
    def get_by_solicitud(solicitud_id: int) -> Optional[DetalleSolicitud]:
        """Obtiene el detalle de una solicitud"""
        try:
            return DetalleSolicitud.objects.get(id_solicitud_id=solicitud_id)
        except DetalleSolicitud.DoesNotExist:
            return None
    
    @staticmethod
    def create(data: dict) -> DetalleSolicitud:
        """Crea un nuevo detalle de solicitud"""
        return DetalleSolicitud.objects.create(**data)
    
    @staticmethod
    def update(detalle: DetalleSolicitud, data: dict) -> DetalleSolicitud:
        """Actualiza un detalle existente"""
        for key, value in data.items():
            setattr(detalle, key, value)
        detalle.save()
        return detalle
    
    @staticmethod
    def delete(detalle: DetalleSolicitud) -> None:
        """Elimina un detalle"""
        detalle.delete()