"""
Service para lógica de negocio de Vehículos
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from core.models import Vehiculo, Modelo, Marca
from core.repositories.vehiculo_repository import (
    VehiculoRepository, ModeloRepository, MarcaRepository
)


class VehiculoService:
    """Maneja la lógica de negocio para vehículos"""
    
    def __init__(self):
        self.repository = VehiculoRepository()
        self.modelo_repository = ModeloRepository()
    
    def get_all_vehiculos(self) -> List[Vehiculo]:
        """Obtiene todos los vehículos"""
        return self.repository.get_all()
    
    def get_vehiculo_by_id(self, vehiculo_id: int) -> Vehiculo:
        """Obtiene un vehículo por ID"""
        vehiculo = self.repository.get_by_id(vehiculo_id)
        
        if not vehiculo:
            raise ValidationError(f"Vehículo con ID {vehiculo_id} no encontrado")
        
        return vehiculo
    
    def get_vehiculo_by_placa(self, placa: str) -> Vehiculo:
        """Obtiene un vehículo por placa"""
        vehiculo = self.repository.get_by_placa(placa)
        
        if not vehiculo:
            raise ValidationError(f"Vehículo con placa {placa} no encontrado")
        
        return vehiculo
    
    def get_vehiculos_by_propietario(self, propietario_id: int) -> List[Vehiculo]:
        """Obtiene vehículos de un propietario"""
        return self.repository.get_by_propietario(propietario_id)
    
    def create_vehiculo(self, data: Dict) -> Vehiculo:
        """Crea un nuevo vehículo"""
        # Validar que la placa no exista
        if self.repository.get_by_placa(data.get('placa')):
            raise ValidationError("La placa ya está registrada")
        
        # Validar que el modelo sea atendible
        modelo_id = data.get('id_modelo')
        ano = data.get('ano')
        
        if modelo_id and ano:
            if not self.modelo_repository.is_modelo_atendible(modelo_id, ano):
                raise ValidationError(
                    "El modelo y año del vehículo no pueden ser atendidos en el taller"
                )
        
        return self.repository.create(data)
    
    def update_vehiculo(self, vehiculo_id: int, data: Dict) -> Vehiculo:
        """Actualiza un vehículo existente"""
        vehiculo = self.get_vehiculo_by_id(vehiculo_id)
        
        # Validar placa si se está actualizando
        if 'placa' in data and data['placa'] != vehiculo.placa:
            if self.repository.get_by_placa(data['placa']):
                raise ValidationError("La placa ya está registrada")
        
        # Validar modelo atendible si se actualiza
        if 'id_modelo' in data or 'ano' in data:
            modelo_id = data.get('id_modelo', vehiculo.id_modelo_id)
            ano = data.get('ano', vehiculo.ano)
            
            if modelo_id and ano:
                if not self.modelo_repository.is_modelo_atendible(modelo_id, ano):
                    raise ValidationError(
                        "El modelo y año del vehículo no pueden ser atendidos en el taller"
                    )
        
        return self.repository.update(vehiculo, data)
    
    def delete_vehiculo(self, vehiculo_id: int) -> None:
        """Elimina un vehículo"""
        vehiculo = self.get_vehiculo_by_id(vehiculo_id)
        self.repository.delete(vehiculo)
    
    def search_vehiculos(self, query: str) -> List[Vehiculo]:
        """Busca vehículos"""
        return self.repository.search(query)
    
    def validar_vehiculo_atendible(self, vehiculo_id: int) -> bool:
        """Valida si un vehículo puede ser atendido"""
        vehiculo = self.get_vehiculo_by_id(vehiculo_id)
        
        return self.modelo_repository.is_modelo_atendible(
            vehiculo.id_modelo_id,
            vehiculo.ano
        )
    
    def get_estadisticas_vehiculos(self) -> Dict:
        """Obtiene estadísticas de vehículos"""
        from django.db.models import Count
        
        total = Vehiculo.objects.count()
        
        por_marca = Vehiculo.objects.values(
            'id_modelo__id_marca__nombre'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        return {
            'total': total,
            'por_marca': list(por_marca)
        }


class ModeloService:
    """Maneja la lógica de negocio para modelos"""
    
    def __init__(self):
        self.repository = ModeloRepository()
    
    def get_all_modelos(self, activo: bool = True) -> List[Modelo]:
        """Obtiene todos los modelos"""
        return self.repository.get_all(activo=activo)
    
    def get_modelo_by_id(self, modelo_id: int) -> Modelo:
        """Obtiene un modelo por ID"""
        modelo = self.repository.get_by_id(modelo_id)
        
        if not modelo:
            raise ValidationError(f"Modelo con ID {modelo_id} no encontrado")
        
        return modelo
    
    def get_modelos_by_marca(self, marca_id: int) -> List[Modelo]:
        """Obtiene modelos de una marca"""
        return self.repository.get_by_marca(marca_id)
    
    def get_modelos_atendibles(self) -> List[Modelo]:
        """Obtiene modelos atendibles"""
        return self.repository.get_atendibles()


class MarcaService:
    """Maneja la lógica de negocio para marcas"""
    
    def __init__(self):
        self.repository = MarcaRepository()
    
    def get_all_marcas(self, activo: bool = True) -> List[Marca]:
        """Obtiene todas las marcas"""
        return self.repository.get_all(activo=activo)
    
    def get_marca_by_id(self, marca_id: int) -> Marca:
        """Obtiene una marca por ID"""
        marca = self.repository.get_by_id(marca_id)
        
        if not marca:
            raise ValidationError(f"Marca con ID {marca_id} no encontrada")
        
        return marca