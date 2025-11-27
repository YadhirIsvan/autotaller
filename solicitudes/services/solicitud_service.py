"""
Service para lógica de negocio de Solicitudes
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from solicitudes.models import Solicitud, DetalleSolicitud
from solicitudes.repositories.solicitud_repository import (
    SolicitudRepository, DetalleSolicitudRepository
)
from core.models import Estado
from core.repositories.vehiculo_repository import ModeloRepository


class SolicitudService:
    """Maneja la lógica de negocio para solicitudes"""
    
    def __init__(self):
        self.repository = SolicitudRepository()
        self.detalle_repository = DetalleSolicitudRepository()
        self.modelo_repository = ModeloRepository()
    
    def get_all_solicitudes(self) -> List[Solicitud]:
        """Obtiene todas las solicitudes"""
        return self.repository.get_all()
    
    def get_solicitud_by_id(self, solicitud_id: int) -> Solicitud:
        """Obtiene una solicitud por ID"""
        solicitud = self.repository.get_by_id(solicitud_id)
        
        if not solicitud:
            raise ValidationError(f"Solicitud con ID {solicitud_id} no encontrada")
        
        return solicitud
    
    def get_solicitudes_by_usuario(self, usuario_id: int) -> List[Solicitud]:
        """Obtiene solicitudes de un usuario"""
        return self.repository.get_by_usuario(usuario_id)
    
    def get_solicitudes_pendientes(self) -> List[Solicitud]:
        """Obtiene solicitudes pendientes"""
        return self.repository.get_pendientes()
    
    def get_solicitudes_aprobadas(self) -> List[Solicitud]:
        """Obtiene solicitudes aprobadas"""
        return self.repository.get_aprobadas()
    
    def get_solicitudes_rechazadas(self) -> List[Solicitud]:
        """Obtiene solicitudes rechazadas"""
        return self.repository.get_rechazadas()
    
    @transaction.atomic
    def create_solicitud(self, data: Dict) -> Solicitud:
        """Crea una nueva solicitud"""
        vehiculo_id = data.get('id_vehiculo')
        
        # Validar que el vehículo pueda ser atendido
        from core.services.vehiculo_service import VehiculoService
        vehiculo_service = VehiculoService()
        
        if not vehiculo_service.validar_vehiculo_atendible(vehiculo_id):
            raise ValidationError(
                "El modelo y año del vehículo no pueden ser atendidos en el taller"
            )
        
        # Validar que no tenga solicitudes pendientes
        if self.repository.tiene_solicitud_pendiente(vehiculo_id):
            raise ValidationError(
                "El vehículo ya tiene una solicitud pendiente"
            )
        
        # Obtener estado pendiente
        estado_pendiente = Estado.objects.get(
            clave='pendiente',
            tipo=Estado.TIPO_SOLICITUD
        )
        
        data['id_estado'] = estado_pendiente
        
        # Crear solicitud
        solicitud = self.repository.create(data)
        
        # Crear detalle si viene información
        if data.get('observaciones') or data.get('costo_estimado'):
            self.detalle_repository.create({
                'id_solicitud': solicitud,
                'observaciones': data.get('observaciones'),
                'costo_estimado': data.get('costo_estimado')
            })
        
        return solicitud
    
    @transaction.atomic
    def aprobar_solicitud(self, solicitud_id: int, aprobado_por_id: int) -> Solicitud:
        """Aprueba una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        
        # Validar que esté pendiente
        if solicitud.id_estado.clave != 'pendiente':
            raise ValidationError("Solo se pueden aprobar solicitudes pendientes")
        
        # Obtener estado aprobada
        estado_aprobada = Estado.objects.get(
            clave='aprobada',
            tipo=Estado.TIPO_SOLICITUD
        )
        
        return self.repository.aprobar(solicitud_id, aprobado_por_id, estado_aprobada)
    
    @transaction.atomic
    def rechazar_solicitud(
        self,
        solicitud_id: int,
        motivo: str,
        rechazado_por_id: int
    ) -> Solicitud:
        """Rechaza una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        
        # Validar que esté pendiente
        if solicitud.id_estado.clave != 'pendiente':
            raise ValidationError("Solo se pueden rechazar solicitudes pendientes")
        
        if not motivo:
            raise ValidationError("Debe proporcionar un motivo de rechazo")
        
        # Obtener estado rechazada
        estado_rechazada = Estado.objects.get(
            clave='rechazada',
            tipo=Estado.TIPO_SOLICITUD
        )
        
        return self.repository.rechazar(
            solicitud_id,
            motivo,
            rechazado_por_id,
            estado_rechazada
        )
    
    def update_solicitud(self, solicitud_id: int, data: Dict) -> Solicitud:
        """Actualiza una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        return self.repository.update(solicitud, data)
    
    def delete_solicitud(self, solicitud_id: int) -> None:
        """Elimina una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        
        # Validar que no tenga reservación
        if hasattr(solicitud, 'reservacion'):
            raise ValidationError("No se puede eliminar una solicitud con reservación")
        
        self.repository.delete(solicitud)
    
    def search_solicitudes(self, query: str) -> List[Solicitud]:
        """Busca solicitudes"""
        return self.repository.search(query)
    
    def get_estadisticas_solicitudes(self) -> Dict:
        """Obtiene estadísticas de solicitudes"""
        from django.db.models import Count
        
        total = Solicitud.objects.count()
        
        por_estado = Solicitud.objects.values(
            'id_estado__clave',
            'id_estado__descripcion'
        ).annotate(
            total=Count('id')
        )
        
        return {
            'total': total,
            'por_estado': list(por_estado),
            'pendientes': self.repository.get_pendientes().count(),
            'aprobadas': self.repository.get_aprobadas().count(),
            'rechazadas': self.repository.get_rechazadas().count()
        }