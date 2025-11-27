"""
Service para lógica de negocio de Servicios
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from servicios.models import Servicio, ServicioUsuarioTaller
from servicios.repositories.servicio_repository import (
    ServicioRepository,
    ServicioUsuarioTallerRepository
)


class ServicioService:
    """Maneja la lógica de negocio para servicios"""
    
    def __init__(self):
        self.repository = ServicioRepository()
    
    def get_all_servicios(self, activo: bool = True) -> List[Servicio]:
        """Obtiene todos los servicios"""
        return self.repository.get_all(activo=activo)
    
    def get_servicio_by_id(self, servicio_id: int) -> Servicio:
        """Obtiene un servicio por ID"""
        servicio = self.repository.get_by_id(servicio_id)
        
        if not servicio:
            raise ValidationError(f"Servicio con ID {servicio_id} no encontrado")
        
        return servicio
    
    def get_servicios_by_categoria(self, categoria_id: int) -> List[Servicio]:
        """Obtiene servicios de una categoría"""
        return self.repository.get_by_categoria(categoria_id)
    
    def create_servicio(self, data: Dict) -> Servicio:
        """Crea un nuevo servicio"""
        return self.repository.create(data)
    
    def update_servicio(self, servicio_id: int, data: Dict) -> Servicio:
        """Actualiza un servicio"""
        servicio = self.get_servicio_by_id(servicio_id)
        return self.repository.update(servicio, data)


class ServicioTallerService:
    """Maneja la lógica de negocio para servicios de talleres"""
    
    def __init__(self):
        self.repository = ServicioUsuarioTallerRepository()
    
    def get_all_servicios_talleres(self) -> List[ServicioUsuarioTaller]:
        """Obtiene todos los servicios de talleres"""
        return self.repository.get_all()
    
    def get_servicio_taller_by_id(self, servicio_taller_id: int) -> ServicioUsuarioTaller:
        """Obtiene un servicio de taller por ID"""
        servicio_taller = self.repository.get_by_id(servicio_taller_id)
        
        if not servicio_taller:
            raise ValidationError(f"Servicio de taller con ID {servicio_taller_id} no encontrado")
        
        return servicio_taller
    
    def get_servicios_by_taller(self, taller_id: int) -> List[ServicioUsuarioTaller]:
        """Obtiene servicios que ofrece un taller"""
        return self.repository.get_by_taller(taller_id)
    
    def get_talleres_por_servicio(self, servicio_id: int) -> List[ServicioUsuarioTaller]:
        """Obtiene talleres que ofrecen un servicio"""
        return self.repository.get_talleres_por_servicio(servicio_id)
    
    def asignar_servicio_a_taller(self, data: Dict) -> ServicioUsuarioTaller:
        """Asigna un servicio a un taller"""
        # Validar que no exista ya
        taller_id = data.get('id_usuario_taller')
        servicio_id = data.get('id_servicio')
        
        existente = ServicioUsuarioTaller.objects.filter(
            id_usuario_taller_id=taller_id,
            id_servicio_id=servicio_id
        ).first()
        
        if existente:
            raise ValidationError("El servicio ya está asignado a este taller")
        
        return self.repository.create(data)
    
    def update_servicio_taller(
        self,
        servicio_taller_id: int,
        data: Dict
    ) -> ServicioUsuarioTaller:
        """Actualiza un servicio de taller"""
        servicio_taller = self.get_servicio_taller_by_id(servicio_taller_id)
        return self.repository.update(servicio_taller, data)
    
    def desactivar_servicio_taller(self, servicio_taller_id: int) -> None:
        """Desactiva un servicio de taller"""
        servicio_taller = self.get_servicio_taller_by_id(servicio_taller_id)
        self.repository.delete(servicio_taller)