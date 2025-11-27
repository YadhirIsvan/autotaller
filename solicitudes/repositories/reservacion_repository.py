"""
Repository para operaciones de base de datos de Reservaciones
"""
from typing import List, Optional
from datetime import date
from django.db.models import Q, Prefetch
from solicitudes.models import ReservacionTallerPrincipal


class ReservacionRepository:
    """Maneja todas las operaciones de BD para reservaciones"""
    
    @staticmethod
    def get_all() -> List[ReservacionTallerPrincipal]:
        """Obtiene todas las reservaciones"""
        return ReservacionTallerPrincipal.objects.select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).all()
    
    @staticmethod
    def get_by_id(reservacion_id: int) -> Optional[ReservacionTallerPrincipal]:
        """Obtiene una reservación por ID"""
        try:
            return ReservacionTallerPrincipal.objects.select_related(
                'id_solicitud__id_vehiculo__id_modelo__id_marca',
                'id_solicitud__id_usuario',
                'id_tamp_block',
                'id_estado',
                'atendido_por'
            ).prefetch_related('servicios_asignados').get(id=reservacion_id)
        except ReservacionTallerPrincipal.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_solicitud(solicitud_id: int) -> Optional[ReservacionTallerPrincipal]:
        """Obtiene reservación por solicitud"""
        try:
            return ReservacionTallerPrincipal.objects.select_related(
                'id_solicitud__id_vehiculo__id_modelo__id_marca',
                'id_solicitud__id_usuario',
                'id_tamp_block',
                'id_estado',
                'atendido_por'
            ).get(id_solicitud_id=solicitud_id)
        except ReservacionTallerPrincipal.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_cliente(cliente_id: int) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de un cliente"""
        return ReservacionTallerPrincipal.objects.filter(
            id_solicitud__id_usuario_id=cliente_id
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('-creado_at')
    
    @staticmethod
    def get_by_fecha(fecha: date) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de una fecha específica"""
        return ReservacionTallerPrincipal.objects.filter(
            id_tamp_block__fecha=fecha
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('id_tamp_block__hora_inicio')
    
    @staticmethod
    def get_by_estado(estado_clave: str) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones por estado"""
        return ReservacionTallerPrincipal.objects.filter(
            id_estado__clave=estado_clave
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('-creado_at')
    
    @staticmethod
    def get_pendientes() -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones pendientes"""
        return ReservacionRepository.get_by_estado('pendiente')
    
    @staticmethod
    def get_en_proceso() -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones en proceso"""
        return ReservacionRepository.get_by_estado('en_proceso')
    
    @staticmethod
    def get_completadas() -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones completadas"""
        return ReservacionRepository.get_by_estado('completada')
    
    @staticmethod
    def create(data: dict) -> ReservacionTallerPrincipal:
        """Crea una nueva reservación"""
        return ReservacionTallerPrincipal.objects.create(**data)
    
    @staticmethod
    def update(reservacion: ReservacionTallerPrincipal, data: dict) -> ReservacionTallerPrincipal:
        """Actualiza una reservación existente"""
        for key, value in data.items():
            setattr(reservacion, key, value)
        reservacion.save()
        return reservacion
    
    @staticmethod
    def actualizar_avance_global(reservacion_id: int) -> ReservacionTallerPrincipal:
        """Actualiza el avance global basado en los servicios asignados"""
        from django.db.models import Avg
        
        reservacion = ReservacionTallerPrincipal.objects.get(id=reservacion_id)
        
        # Calcular promedio de progreso de todos los servicios
        promedio = reservacion.servicios_asignados.aggregate(
            promedio=Avg('progreso')
        )['promedio'] or 0
        
        reservacion.avance_global = int(promedio)
        
        # Actualizar estado global
        if promedio == 0:
            reservacion.estado_global = 'pendiente'
        elif promedio < 100:
            reservacion.estado_global = 'en_proceso'
        else:
            reservacion.estado_global = 'completado'
        
        reservacion.save()
        return reservacion
    
    @staticmethod
    def delete(reservacion: ReservacionTallerPrincipal) -> None:
        """Elimina una reservación"""
        reservacion.delete()
    
    @staticmethod
    def search(query: str) -> List[ReservacionTallerPrincipal]:
        """Busca reservaciones por placa o cliente"""
        return ReservacionTallerPrincipal.objects.filter(
            Q(id_solicitud__id_vehiculo__placa__icontains=query) |
            Q(id_solicitud__id_usuario__nombre__icontains=query)
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        )
    
    @staticmethod
    def get_proximas(dias: int = 7) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones próximas en X días"""
        from django.utils import timezone
        from datetime import timedelta
        
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        
        return ReservacionTallerPrincipal.objects.filter(
            id_tamp_block__fecha__lte=fecha_limite,
            id_tamp_block__fecha__gte=timezone.now().date()
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('id_tamp_block__fecha', 'id_tamp_block__hora_inicio')