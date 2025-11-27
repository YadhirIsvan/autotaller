"""
Service para lógica de negocio de Calendarios
"""
from typing import List, Dict
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from core.models import TampBlockPrincipal, TampBlockTalleres
from core.repositories.calendario_repository import (
    CalendarioPrincipalRepository,
    CalendarioTalleresRepository
)


class CalendarioPrincipalService:
    """Maneja la lógica de negocio para calendario del taller principal"""
    
    def __init__(self):
        self.repository = CalendarioPrincipalRepository()
    
    def get_all_bloques(self) -> List[TampBlockPrincipal]:
        """Obtiene todos los bloques del calendario"""
        return self.repository.get_all()
    
    def get_bloque_by_id(self, bloque_id: int) -> TampBlockPrincipal:
        """Obtiene un bloque por ID"""
        bloque = self.repository.get_by_id(bloque_id)
        
        if not bloque:
            raise ValidationError(f"Bloque con ID {bloque_id} no encontrado")
        
        return bloque
    
    def get_bloques_disponibles(self, fecha_inicio: date, fecha_fin: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques disponibles en un rango de fechas"""
        if fecha_inicio > fecha_fin:
            raise ValidationError("La fecha de inicio debe ser menor a la fecha fin")
        
        return self.repository.get_disponibles(fecha_inicio, fecha_fin)
    
    def get_bloques_by_fecha(self, fecha: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques de una fecha específica"""
        return self.repository.get_by_fecha(fecha)
    
    def create_bloque(self, data: Dict) -> TampBlockPrincipal:
        """Crea un nuevo bloque"""
        # Validar que hora_inicio < hora_fin
        if data.get('hora_inicio') >= data.get('hora_fin'):
            raise ValidationError("La hora de inicio debe ser menor a la hora fin")
        
        return self.repository.create(data)
    
    def update_bloque(self, bloque_id: int, data: Dict) -> TampBlockPrincipal:
        """Actualiza un bloque existente"""
        bloque = self.get_bloque_by_id(bloque_id)
        
        # Validar horas si se están actualizando
        hora_inicio = data.get('hora_inicio', bloque.hora_inicio)
        hora_fin = data.get('hora_fin', bloque.hora_fin)
        
        if hora_inicio >= hora_fin:
            raise ValidationError("La hora de inicio debe ser menor a la hora fin")
        
        return self.repository.update(bloque, data)
    
    def reservar_bloque(self, bloque_id: int) -> TampBlockPrincipal:
        """Reserva un espacio en el bloque"""
        bloque = self.get_bloque_by_id(bloque_id)
        
        if not bloque.disponible:
            raise ValidationError("El bloque no está disponible")
        
        if bloque.reservados >= bloque.capacidad:
            raise ValidationError("El bloque ya alcanzó su capacidad máxima")
        
        success = self.repository.incrementar_reservados(bloque_id)
        
        if not success:
            raise ValidationError("No se pudo reservar el bloque")
        
        return self.get_bloque_by_id(bloque_id)
    
    def liberar_bloque(self, bloque_id: int) -> TampBlockPrincipal:
        """Libera un espacio en el bloque"""
        self.repository.decrementar_reservados(bloque_id)
        return self.get_bloque_by_id(bloque_id)
    
    def generar_bloques_semana(self, fecha_inicio: date, horas: List[Dict]) -> List[TampBlockPrincipal]:
        """
        Genera bloques para una semana completa
        horas: [{'hora_inicio': '09:00', 'hora_fin': '10:00', 'capacidad': 2}, ...]
        """
        bloques_creados = []
        
        with transaction.atomic():
            for i in range(7):  # 7 días
                fecha = fecha_inicio + timedelta(days=i)
                
                for hora_config in horas:
                    bloque = self.repository.create({
                        'fecha': fecha,
                        'hora_inicio': hora_config['hora_inicio'],
                        'hora_fin': hora_config['hora_fin'],
                        'capacidad': hora_config.get('capacidad', 1),
                        'disponible': True,
                        'reservados': 0
                    })
                    bloques_creados.append(bloque)
        
        return bloques_creados


class CalendarioTalleresService:
    """Maneja la lógica de negocio para calendarios de talleres secundarios"""
    
    def __init__(self):
        self.repository = CalendarioTalleresRepository()
    
    def get_all_bloques(self) -> List[TampBlockTalleres]:
        """Obtiene todos los bloques de talleres"""
        return self.repository.get_all()
    
    def get_bloque_by_id(self, bloque_id: int) -> TampBlockTalleres:
        """Obtiene un bloque por ID"""
        bloque = self.repository.get_by_id(bloque_id)
        
        if not bloque:
            raise ValidationError(f"Bloque con ID {bloque_id} no encontrado")
        
        return bloque
    
    def get_bloques_by_taller(
        self,
        taller_id: int,
        fecha_inicio: date = None,
        fecha_fin: date = None
    ) -> List[TampBlockTalleres]:
        """Obtiene bloques de un taller específico"""
        return self.repository.get_by_taller(taller_id, fecha_inicio, fecha_fin)
    
    def get_bloques_disponibles_taller(
        self,
        taller_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[TampBlockTalleres]:
        """Obtiene bloques disponibles de un taller"""
        if fecha_inicio > fecha_fin:
            raise ValidationError("La fecha de inicio debe ser menor a la fecha fin")
        
        return self.repository.get_disponibles_taller(taller_id, fecha_inicio, fecha_fin)
    
    def create_bloque(self, data: Dict) -> TampBlockTalleres:
        """Crea un nuevo bloque de taller"""
        return self.repository.create(data)
    
    def update_bloque(self, bloque_id: int, data: Dict) -> TampBlockTalleres:
        """Actualiza un bloque existente"""
        bloque = self.get_bloque_by_id(bloque_id)
        return self.repository.update(bloque, data)
    
    def reservar_bloque(self, bloque_id: int) -> TampBlockTalleres:
        """Reserva un espacio en el bloque"""
        bloque = self.get_bloque_by_id(bloque_id)
        
        if not bloque.disponible:
            raise ValidationError("El bloque no está disponible")
        
        if bloque.reservados >= bloque.capacidad:
            raise ValidationError("El bloque ya alcanzó su capacidad máxima")
        
        success = self.repository.incrementar_reservados(bloque_id)
        
        if not success:
            raise ValidationError("No se pudo reservar el bloque")
        
        return self.get_bloque_by_id(bloque_id)
    
    def liberar_bloque(self, bloque_id: int) -> TampBlockTalleres:
        """Libera un espacio en el bloque"""
        self.repository.decrementar_reservados(bloque_id)
        return self.get_bloque_by_id(bloque_id)
    
    def generar_bloques_mes(self, taller_id: int, fecha_inicio: date) -> List[TampBlockTalleres]:
        """Genera bloques disponibles para un mes"""
        bloques_creados = []
        
        with transaction.atomic():
            for i in range(30):  # 30 días
                fecha = fecha_inicio + timedelta(days=i)
                
                # Evitar fines de semana (opcional)
                if fecha.weekday() >= 5:  # 5=Sábado, 6=Domingo
                    continue
                
                bloque = self.repository.create({
                    'id_usuario_taller_id': taller_id,
                    'fecha': fecha,
                    'disponible': True,
                    'capacidad': 1,
                    'reservados': 0
                })
                bloques_creados.append(bloque)
        
        return bloques_creados