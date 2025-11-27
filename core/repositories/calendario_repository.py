"""
Repository para operaciones de base de datos de Calendarios
"""
from typing import List, Optional
from datetime import date, time
from django.db.models import F, Q
from core.models import TampBlockPrincipal, TampBlockTalleres


class CalendarioPrincipalRepository:
    """Maneja operaciones de BD para calendario del taller principal"""
    
    @staticmethod
    def get_all() -> List[TampBlockPrincipal]:
        """Obtiene todos los bloques del calendario"""
        return TampBlockPrincipal.objects.all()
    
    @staticmethod
    def get_by_id(block_id: int) -> Optional[TampBlockPrincipal]:
        """Obtiene un bloque por ID"""
        try:
            return TampBlockPrincipal.objects.get(id=block_id)
        except TampBlockPrincipal.DoesNotExist:
            return None
    
    @staticmethod
    def get_disponibles(fecha_inicio: date, fecha_fin: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques disponibles en un rango de fechas"""
        return TampBlockPrincipal.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            disponible=True,
            reservados__lt=F('capacidad')
        ).order_by('fecha', 'hora_inicio')
    
    @staticmethod
    def get_by_fecha(fecha: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques de una fecha específica"""
        return TampBlockPrincipal.objects.filter(
            fecha=fecha
        ).order_by('hora_inicio')
    
    @staticmethod
    def create(data: dict) -> TampBlockPrincipal:
        """Crea un nuevo bloque"""
        return TampBlockPrincipal.objects.create(**data)
    
    @staticmethod
    def update(block: TampBlockPrincipal, data: dict) -> TampBlockPrincipal:
        """Actualiza un bloque existente"""
        for key, value in data.items():
            setattr(block, key, value)
        block.save()
        return block
    
    @staticmethod
    def incrementar_reservados(block_id: int) -> bool:
        """Incrementa el contador de reservados"""
        block = TampBlockPrincipal.objects.get(id=block_id)
        
        if block.reservados < block.capacidad:
            block.reservados += 1
            block.save()
            return True
        
        return False
    
    @staticmethod
    def decrementar_reservados(block_id: int) -> None:
        """Decrementa el contador de reservados"""
        block = TampBlockPrincipal.objects.get(id=block_id)
        
        if block.reservados > 0:
            block.reservados -= 1
            block.save()
    
    @staticmethod
    def tiene_disponibilidad(block_id: int) -> bool:
        """Verifica si un bloque tiene disponibilidad"""
        try:
            block = TampBlockPrincipal.objects.get(id=block_id)
            return block.disponible and block.reservados < block.capacidad
        except TampBlockPrincipal.DoesNotExist:
            return False


class CalendarioTalleresRepository:
    """Maneja operaciones de BD para calendarios de talleres secundarios"""
    
    @staticmethod
    def get_all() -> List[TampBlockTalleres]:
        """Obtiene todos los bloques de talleres"""
        return TampBlockTalleres.objects.select_related('id_usuario_taller').all()
    
    @staticmethod
    def get_by_id(block_id: int) -> Optional[TampBlockTalleres]:
        """Obtiene un bloque por ID"""
        try:
            return TampBlockTalleres.objects.select_related('id_usuario_taller').get(id=block_id)
        except TampBlockTalleres.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_taller(taller_id: int, fecha_inicio: date = None, fecha_fin: date = None) -> List[TampBlockTalleres]:
        """Obtiene bloques de un taller específico"""
        queryset = TampBlockTalleres.objects.filter(id_usuario_taller_id=taller_id)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        return queryset.order_by('fecha')
    
    @staticmethod
    def get_disponibles_taller(taller_id: int, fecha_inicio: date, fecha_fin: date) -> List[TampBlockTalleres]:
        """Obtiene bloques disponibles de un taller"""
        return TampBlockTalleres.objects.filter(
            id_usuario_taller_id=taller_id,
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            disponible=True,
            reservados__lt=F('capacidad')
        ).order_by('fecha')
    
    @staticmethod
    def create(data: dict) -> TampBlockTalleres:
        """Crea un nuevo bloque de taller"""
        return TampBlockTalleres.objects.create(**data)
    
    @staticmethod
    def update(block: TampBlockTalleres, data: dict) -> TampBlockTalleres:
        """Actualiza un bloque existente"""
        for key, value in data.items():
            setattr(block, key, value)
        block.save()
        return block
    
    @staticmethod
    def incrementar_reservados(block_id: int) -> bool:
        """Incrementa el contador de reservados"""
        block = TampBlockTalleres.objects.get(id=block_id)
        
        if block.reservados < block.capacidad:
            block.reservados += 1
            block.save()
            return True
        
        return False
    
    @staticmethod
    def decrementar_reservados(block_id: int) -> None:
        """Decrementa el contador de reservados"""
        block = TampBlockTalleres.objects.get(id=block_id)
        
        if block.reservados > 0:
            block.reservados -= 1
            block.save()
    
    @staticmethod
    def tiene_disponibilidad(block_id: int) -> bool:
        """Verifica si un bloque tiene disponibilidad"""
        try:
            block = TampBlockTalleres.objects.get(id=block_id)
            return block.disponible and block.reservados < block.capacidad
        except TampBlockTalleres.DoesNotExist:
            return False