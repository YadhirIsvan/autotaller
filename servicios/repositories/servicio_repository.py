"""
Repository para operaciones de base de datos de Servicios
"""
from typing import List, Optional
from django.db.models import Q
from servicios.models import (
    CategoriaServicio, Servicio, ServicioUsuarioTaller,
    ReservacionServicio, ReservacionTampBlock
)


class CategoriaServicioRepository:
    """Maneja operaciones de BD para categorías de servicios"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[CategoriaServicio]:
        """Obtiene todas las categorías"""
        queryset = CategoriaServicio.objects.all()
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(categoria_id: int) -> Optional[CategoriaServicio]:
        """Obtiene una categoría por ID"""
        try:
            return CategoriaServicio.objects.get(id=categoria_id)
        except CategoriaServicio.DoesNotExist:
            return None


class ServicioRepository:
    """Maneja operaciones de BD para servicios"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[Servicio]:
        """Obtiene todos los servicios"""
        queryset = Servicio.objects.select_related('id_categoria')
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(servicio_id: int) -> Optional[Servicio]:
        """Obtiene un servicio por ID"""
        try:
            return Servicio.objects.select_related('id_categoria').get(id=servicio_id)
        except Servicio.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_categoria(categoria_id: int) -> List[Servicio]:
        """Obtiene servicios de una categoría"""
        return Servicio.objects.filter(
            id_categoria_id=categoria_id,
            activo=True
        ).select_related('id_categoria')
    
    @staticmethod
    def create(data: dict) -> Servicio:
        """Crea un nuevo servicio"""
        return Servicio.objects.create(**data)
    
    @staticmethod
    def update(servicio: Servicio, data: dict) -> Servicio:
        """Actualiza un servicio existente"""
        for key, value in data.items():
            setattr(servicio, key, value)
        servicio.save()
        return servicio


class ServicioUsuarioTallerRepository:
    """Maneja operaciones de BD para servicios de talleres"""
    
    @staticmethod
    def get_all() -> List[ServicioUsuarioTaller]:
        """Obtiene todos los servicios de talleres"""
        return ServicioUsuarioTaller.objects.select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        ).all()
    
    @staticmethod
    def get_by_id(servicio_usuario_taller_id: int) -> Optional[ServicioUsuarioTaller]:
        """Obtiene un servicio de taller por ID"""
        try:
            return ServicioUsuarioTaller.objects.select_related(
                'id_usuario_taller',
                'id_servicio__id_categoria'
            ).get(id=servicio_usuario_taller_id)
        except ServicioUsuarioTaller.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_taller(taller_id: int, activo: bool = True) -> List[ServicioUsuarioTaller]:
        """Obtiene servicios que ofrece un taller"""
        queryset = ServicioUsuarioTaller.objects.filter(
            id_usuario_taller_id=taller_id
        ).select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        )
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_talleres_por_servicio(servicio_id: int) -> List[ServicioUsuarioTaller]:
        """Obtiene talleres que ofrecen un servicio específico"""
        return ServicioUsuarioTaller.objects.filter(
            id_servicio_id=servicio_id,
            activo=True
        ).select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        )
    
    @staticmethod
    def create(data: dict) -> ServicioUsuarioTaller:
        """Crea una nueva relación servicio-taller"""
        return ServicioUsuarioTaller.objects.create(**data)
    
    @staticmethod
    def update(servicio_taller: ServicioUsuarioTaller, data: dict) -> ServicioUsuarioTaller:
        """Actualiza una relación existente"""
        for key, value in data.items():
            setattr(servicio_taller, key, value)
        servicio_taller.save()
        return servicio_taller
    
    @staticmethod
    def delete(servicio_taller: ServicioUsuarioTaller) -> None:
        """Elimina una relación (soft delete)"""
        servicio_taller.activo = False
        servicio_taller.save()


class ReservacionServicioRepository:
    """Maneja operaciones de BD para reservaciones de servicios"""
    
    @staticmethod
    def get_all() -> List[ReservacionServicio]:
        """Obtiene todas las reservaciones de servicios"""
        return ReservacionServicio.objects.select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        ).all()
    
    @staticmethod
    def get_by_id(reservacion_servicio_id: int) -> Optional[ReservacionServicio]:
        """Obtiene una reservación de servicio por ID"""
        try:
            return ReservacionServicio.objects.select_related(
                'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
                'id_servicio_usuario_taller__id_servicio',
                'id_servicio_usuario_taller__id_usuario_taller',
                'id_estado'
            ).prefetch_related('historial_progreso').get(id=reservacion_servicio_id)
        except ReservacionServicio.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_reservacion_principal(reservacion_principal_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios de una reservación principal"""
        return ReservacionServicio.objects.filter(
            id_reservacion_taller_principal_id=reservacion_principal_id
        ).select_related(
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        )
    
    @staticmethod
    def get_by_taller(taller_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios asignados a un taller"""
        return ReservacionServicio.objects.filter(
            id_servicio_usuario_taller__id_usuario_taller_id=taller_id
        ).select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        ).order_by('-fecha_asignacion')
    
    @staticmethod
    def get_by_estado(estado_clave: str) -> List[ReservacionServicio]:
        """Obtiene reservaciones de servicios por estado"""
        return ReservacionServicio.objects.filter(
            id_estado__clave=estado_clave
        ).select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        )
    
    @staticmethod
    def create(data: dict) -> ReservacionServicio:
        """Crea una nueva reservación de servicio"""
        return ReservacionServicio.objects.create(**data)
    
    @staticmethod
    def update(reservacion_servicio: ReservacionServicio, data: dict) -> ReservacionServicio:
        """Actualiza una reservación de servicio"""
        for key, value in data.items():
            setattr(reservacion_servicio, key, value)
        reservacion_servicio.save()
        return reservacion_servicio
    
    @staticmethod
    def actualizar_progreso(reservacion_servicio_id: int, nuevo_progreso: int) -> ReservacionServicio:
        """Actualiza el progreso de un servicio"""
        reservacion = ReservacionServicio.objects.get(id=reservacion_servicio_id)
        reservacion.progreso = nuevo_progreso
        reservacion.save()
        return reservacion
    
    @staticmethod
    def delete(reservacion_servicio: ReservacionServicio) -> None:
        """Elimina una reservación de servicio"""
        reservacion_servicio.delete()


class ReservacionTampBlockRepository:
    """Maneja operaciones de BD para reservaciones en calendarios de talleres"""
    
    @staticmethod
    def get_by_reservacion_servicio(reservacion_servicio_id: int) -> List[ReservacionTampBlock]:
        """Obtiene fechas asignadas a una reservación de servicio"""
        return ReservacionTampBlock.objects.filter(
            id_reservacion_servicio_id=reservacion_servicio_id
        ).select_related('id_tamp_block_taller').order_by('fecha_asignada')
    
    @staticmethod
    def create(data: dict) -> ReservacionTampBlock:
        """Crea una nueva asignación de fecha"""
        return ReservacionTampBlock.objects.create(**data)
    
    @staticmethod
    def delete(reservacion_tamp_block: ReservacionTampBlock) -> None:
        """Elimina una asignación de fecha"""
        reservacion_tamp_block.delete()