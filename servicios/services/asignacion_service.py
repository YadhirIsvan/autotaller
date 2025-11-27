"""
Service para lógica de negocio de Asignación de Servicios
"""
from typing import List, Dict
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from servicios.models import ReservacionServicio, ReservacionTampBlock
from servicios.repositories.servicio_repository import (
    ReservacionServicioRepository,
    ReservacionTampBlockRepository,
    ServicioUsuarioTallerRepository
)
from core.models import Estado
from core.services.calendario_service import CalendarioTalleresService


class AsignacionServicioService:
    """Maneja la lógica de asignación de servicios a talleres"""
    
    def __init__(self):
        self.repository = ReservacionServicioRepository()
        self.tamp_block_repository = ReservacionTampBlockRepository()
        self.servicio_taller_repository = ServicioUsuarioTallerRepository()
        self.calendario_service = CalendarioTalleresService()
    
    def get_all_reservaciones_servicios(self) -> List[ReservacionServicio]:
        """Obtiene todas las reservaciones de servicios"""
        return self.repository.get_all()
    
    def get_reservacion_servicio_by_id(self, reservacion_servicio_id: int) -> ReservacionServicio:
        """Obtiene una reservación de servicio por ID"""
        reservacion = self.repository.get_by_id(reservacion_servicio_id)
        
        if not reservacion:
            raise ValidationError(
                f"Reservación de servicio con ID {reservacion_servicio_id} no encontrada"
            )
        
        return reservacion
    
    def get_servicios_by_reservacion(self, reservacion_principal_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios de una reservación principal"""
        return self.repository.get_by_reservacion_principal(reservacion_principal_id)
    
    def get_servicios_by_taller(self, taller_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios asignados a un taller"""
        return self.repository.get_by_taller(taller_id)
    
    @transaction.atomic
    def asignar_servicio(self, data: Dict) -> ReservacionServicio:
        """
        Asigna un servicio a un taller
        data: {
            'id_reservacion_taller_principal': int,
            'id_servicio_usuario_taller': int,
            'fechas': [date1, date2, ...]  # Fechas en calendario del taller
        }
        """
        servicio_usuario_taller_id = data.get('id_servicio_usuario_taller')
        
        # Validar que el servicio-taller exista
        servicio_taller = self.servicio_taller_repository.get_by_id(servicio_usuario_taller_id)
        
        if not servicio_taller:
            raise ValidationError("Servicio de taller no encontrado")
        
        # Obtener estado pendiente
        estado_pendiente = Estado.objects.get(
            clave='pendiente',
            tipo=Estado.TIPO_SERVICIO
        )
        
        # Crear reservación de servicio
        reservacion_data = {
            'id_reservacion_taller_principal_id': data.get('id_reservacion_taller_principal'),
            'id_servicio_usuario_taller_id': servicio_usuario_taller_id,
            'id_estado': estado_pendiente,
            'progreso': 0
        }
        
        # Calcular fecha estimada de fin
        if servicio_taller.duracion_dias:
            fecha_inicio = timezone.now()
            reservacion_data['fecha_inicio_real'] = fecha_inicio
            reservacion_data['fecha_fin_estimada'] = fecha_inicio + timedelta(
                days=servicio_taller.duracion_dias
            )
        
        reservacion_servicio = self.repository.create(reservacion_data)
        
        # Asignar fechas en calendario del taller si vienen
        if data.get('fechas'):
            self._asignar_fechas_calendario(
                reservacion_servicio.id,
                servicio_taller.id_usuario_taller_id,
                data['fechas']
            )
        
        return reservacion_servicio
    
    @transaction.atomic
    def _asignar_fechas_calendario(
        self,
        reservacion_servicio_id: int,
        taller_id: int,
        fechas: List
    ) -> List[ReservacionTampBlock]:
        """Asigna fechas del calendario del taller al servicio"""
        asignaciones = []
        
        for fecha in fechas:
            # Buscar bloque disponible en esa fecha
            bloques = self.calendario_service.get_bloques_by_taller(
                taller_id,
                fecha,
                fecha
            )
            
            bloque_disponible = None
            for bloque in bloques:
                if bloque.disponible and bloque.reservados < bloque.capacidad:
                    bloque_disponible = bloque
                    break
            
            if not bloque_disponible:
                raise ValidationError(f"No hay disponibilidad en la fecha {fecha}")
            
            # Reservar el bloque
            self.calendario_service.reservar_bloque(bloque_disponible.id)
            
            # Crear asignación
            asignacion = self.tamp_block_repository.create({
                'id_reservacion_servicio_id': reservacion_servicio_id,
                'id_tamp_block_taller_id': bloque_disponible.id,
                'fecha_asignada': fecha
            })
            asignaciones.append(asignacion)
        
        return asignaciones
    
    def update_reservacion_servicio(
        self,
        reservacion_servicio_id: int,
        data: Dict
    ) -> ReservacionServicio:
        """Actualiza una reservación de servicio"""
        reservacion = self.get_reservacion_servicio_by_id(reservacion_servicio_id)
        return self.repository.update(reservacion, data)
    
    @transaction.atomic
    def iniciar_servicio(self, reservacion_servicio_id: int) -> ReservacionServicio:
        """Inicia un servicio"""
        reservacion = self.get_reservacion_servicio_by_id(reservacion_servicio_id)
        
        estado_en_proceso = Estado.objects.get(
            clave='en_proceso',
            tipo=Estado.TIPO_SERVICIO
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_en_proceso,
            'fecha_inicio_real': timezone.now()
        })
    
    @transaction.atomic
    def completar_servicio(self, reservacion_servicio_id: int) -> ReservacionServicio:
        """Completa un servicio"""
        reservacion = self.get_reservacion_servicio_by_id(reservacion_servicio_id)
        
        estado_completado = Estado.objects.get(
            clave='completada',
            tipo=Estado.TIPO_SERVICIO
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_completado,
            'progreso': 100,
            'fecha_fin_real': timezone.now()
        })