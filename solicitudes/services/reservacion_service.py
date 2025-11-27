"""
Service para lógica de negocio de Reservaciones
"""
from typing import List, Dict
from datetime import date
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from solicitudes.models import ReservacionTallerPrincipal
from solicitudes.repositories.reservacion_repository import ReservacionRepository
from core.models import Estado
from core.services.calendario_service import CalendarioPrincipalService


class ReservacionService:
    """Maneja la lógica de negocio para reservaciones"""
    
    def __init__(self):
        self.repository = ReservacionRepository()
        self.calendario_service = CalendarioPrincipalService()
    
    def get_all_reservaciones(self) -> List[ReservacionTallerPrincipal]:
        """Obtiene todas las reservaciones"""
        return self.repository.get_all()
    
    def get_reservacion_by_id(self, reservacion_id: int) -> ReservacionTallerPrincipal:
        """Obtiene una reservación por ID"""
        reservacion = self.repository.get_by_id(reservacion_id)
        
        if not reservacion:
            raise ValidationError(f"Reservación con ID {reservacion_id} no encontrada")
        
        return reservacion
    
    def get_reservaciones_by_cliente(self, cliente_id: int) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de un cliente"""
        return self.repository.get_by_cliente(cliente_id)
    
    def get_reservaciones_by_fecha(self, fecha: date) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de una fecha"""
        return self.repository.get_by_fecha(fecha)
    
    def get_reservaciones_pendientes(self) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones pendientes"""
        return self.repository.get_pendientes()
    
    def get_reservaciones_proximas(self, dias: int = 7) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones próximas"""
        return self.repository.get_proximas(dias)
    
    @transaction.atomic
    def create_reservacion(self, data: Dict) -> ReservacionTallerPrincipal:
        """Crea una nueva reservación"""
        from solicitudes.services.solicitud_service import SolicitudService
        
        solicitud_id = data.get('id_solicitud')
        tamp_block_id = data.get('id_tamp_block')
        
        # Validar que la solicitud exista y esté aprobada
        solicitud_service = SolicitudService()
        solicitud = solicitud_service.get_solicitud_by_id(solicitud_id)
        
        if solicitud.id_estado.clave != 'aprobada':
            raise ValidationError("Solo se pueden crear reservaciones de solicitudes aprobadas")
        
        # Validar que no tenga reservación
        if hasattr(solicitud, 'reservacion'):
            raise ValidationError("La solicitud ya tiene una reservación")
        
        # Validar y reservar el bloque
        bloque = self.calendario_service.reservar_bloque(tamp_block_id)
        
        # Obtener estado pendiente
        estado_pendiente = Estado.objects.get(
            clave='pendiente',
            tipo=Estado.TIPO_RESERVACION
        )
        
        data['id_estado'] = estado_pendiente
        
        try:
            reservacion = self.repository.create(data)
            return reservacion
        except Exception as e:
            # Si falla, liberar el bloque
            self.calendario_service.liberar_bloque(tamp_block_id)
            raise e
    
    def update_reservacion(self, reservacion_id: int, data: Dict) -> ReservacionTallerPrincipal:
        """Actualiza una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        return self.repository.update(reservacion, data)
    
    @transaction.atomic
    def iniciar_evaluacion(
        self,
        reservacion_id: int,
        atendido_por_id: int
    ) -> ReservacionTallerPrincipal:
        """Inicia la evaluación de una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        
        estado_en_proceso = Estado.objects.get(
            clave='en_proceso',
            tipo=Estado.TIPO_RESERVACION
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_en_proceso,
            'atendido_por_id': atendido_por_id,
            'fecha_evaluacion': timezone.now(),
            'fecha_inicio': timezone.now()
        })
    
    @transaction.atomic
    def completar_evaluacion(
        self,
        reservacion_id: int,
        notas: str
    ) -> ReservacionTallerPrincipal:
        """Completa la evaluación de una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        
        return self.repository.update(reservacion, {
            'notas_evaluacion': notas,
            'fecha_fin_real': timezone.now()
        })
    
    def actualizar_avance_global(self, reservacion_id: int) -> ReservacionTallerPrincipal:
        """Actualiza el avance global de la reservación"""
        return self.repository.actualizar_avance_global(reservacion_id)
    
    @transaction.atomic
    def cancelar_reservacion(self, reservacion_id: int) -> ReservacionTallerPrincipal:
        """Cancela una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        
        # Liberar el bloque
        self.calendario_service.liberar_bloque(reservacion.id_tamp_block_id)
        
        estado_cancelada = Estado.objects.get(
            clave='cancelada',
            tipo=Estado.TIPO_RESERVACION
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_cancelada
        })
    
    def search_reservaciones(self, query: str) -> List[ReservacionTallerPrincipal]:
        """Busca reservaciones"""
        return self.repository.search(query)