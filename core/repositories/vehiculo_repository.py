"""
Repository para operaciones de base de datos de Vehículos
"""
from typing import List, Optional
from django.db.models import Q
from core.models import Vehiculo, Marca, Modelo


class VehiculoRepository:
    """Maneja todas las operaciones de BD para vehículos"""
    
    @staticmethod
    def get_all() -> List[Vehiculo]:
        """Obtiene todos los vehículos"""
        return Vehiculo.objects.select_related(
            'id_modelo__id_marca',
            'id_usuario_propietario'
        ).all()
    
    @staticmethod
    def get_by_id(vehiculo_id: int) -> Optional[Vehiculo]:
        """Obtiene un vehículo por ID"""
        try:
            return Vehiculo.objects.select_related(
                'id_modelo__id_marca',
                'id_usuario_propietario'
            ).get(id=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_placa(placa: str) -> Optional[Vehiculo]:
        """Obtiene un vehículo por placa"""
        try:
            return Vehiculo.objects.select_related(
                'id_modelo__id_marca',
                'id_usuario_propietario'
            ).get(placa=placa)
        except Vehiculo.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_propietario(propietario_id: int) -> List[Vehiculo]:
        """Obtiene vehículos de un propietario"""
        return Vehiculo.objects.filter(
            id_usuario_propietario_id=propietario_id
        ).select_related(
            'id_modelo__id_marca',
            'id_usuario_propietario'
        )
    
    @staticmethod
    def create(data: dict) -> Vehiculo:
        """Crea un nuevo vehículo"""
        return Vehiculo.objects.create(**data)
    
    @staticmethod
    def update(vehiculo: Vehiculo, data: dict) -> Vehiculo:
        """Actualiza un vehículo existente"""
        for key, value in data.items():
            setattr(vehiculo, key, value)
        vehiculo.save()
        return vehiculo
    
    @staticmethod
    def delete(vehiculo: Vehiculo) -> None:
        """Elimina un vehículo"""
        vehiculo.delete()
    
    @staticmethod
    def search(query: str) -> List[Vehiculo]:
        """Busca vehículos por placa, VIN o propietario"""
        return Vehiculo.objects.filter(
            Q(placa__icontains=query) |
            Q(vin__icontains=query) |
            Q(id_usuario_propietario__nombre__icontains=query)
        ).select_related(
            'id_modelo__id_marca',
            'id_usuario_propietario'
        )


class ModeloRepository:
    """Maneja operaciones de BD para modelos de vehículos"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[Modelo]:
        """Obtiene todos los modelos"""
        queryset = Modelo.objects.select_related('id_marca')
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(modelo_id: int) -> Optional[Modelo]:
        """Obtiene un modelo por ID"""
        try:
            return Modelo.objects.select_related('id_marca').get(id=modelo_id)
        except Modelo.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_marca(marca_id: int) -> List[Modelo]:
        """Obtiene modelos de una marca"""
        return Modelo.objects.filter(
            id_marca_id=marca_id,
            activo=True
        ).select_related('id_marca')
    
    @staticmethod
    def get_atendibles() -> List[Modelo]:
        """Obtiene modelos atendibles"""
        return Modelo.objects.filter(
            atendible=True,
            activo=True
        ).select_related('id_marca')
    
    @staticmethod
    def is_modelo_atendible(modelo_id: int, ano: int) -> bool:
        """Verifica si un modelo es atendible para un año específico"""
        try:
            modelo = Modelo.objects.get(id=modelo_id)
            
            if not modelo.atendible:
                return False
            
            if modelo.ano_inicio and ano < modelo.ano_inicio:
                return False
            
            if modelo.ano_fin and ano > modelo.ano_fin:
                return False
            
            return True
        except Modelo.DoesNotExist:
            return False


class MarcaRepository:
    """Maneja operaciones de BD para marcas"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[Marca]:
        """Obtiene todas las marcas"""
        queryset = Marca.objects.all()
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(marca_id: int) -> Optional[Marca]:
        """Obtiene una marca por ID"""
        try:
            return Marca.objects.get(id=marca_id)
        except Marca.DoesNotExist:
            return None