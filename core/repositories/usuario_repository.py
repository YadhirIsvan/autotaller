"""
Repository para operaciones de base de datos de Usuarios
"""
from typing import List, Optional
from django.db.models import Q
from core.models import Usuario, TipoUsuario


class UsuarioRepository:
    """Maneja todas las operaciones de BD para usuarios"""
    
    @staticmethod
    def get_all(activo: Optional[bool] = None) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        queryset = Usuario.objects.select_related('id_tipo')
        
        if activo is not None:
            queryset = queryset.filter(activo=activo)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        try:
            return Usuario.objects.select_related('id_tipo').get(id=usuario_id)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email"""
        try:
            return Usuario.objects.select_related('id_tipo').get(email=email)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Usuario]:
        """Obtiene un usuario por username"""
        try:
            return Usuario.objects.select_related('id_tipo').get(username=username)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_tipo(tipo_cve: str) -> List[Usuario]:
        """Obtiene usuarios por tipo"""
        return Usuario.objects.filter(
            id_tipo__cve=tipo_cve,
            activo=True
        ).select_related('id_tipo')
    
    @staticmethod
    def create(data: dict) -> Usuario:
        """Crea un nuevo usuario"""
        return Usuario.objects.create(**data)
    
    @staticmethod
    def update(usuario: Usuario, data: dict) -> Usuario:
        """Actualiza un usuario existente"""
        for key, value in data.items():
            setattr(usuario, key, value)
        usuario.save()
        return usuario
    
    @staticmethod
    def delete(usuario: Usuario) -> None:
        """Elimina un usuario (soft delete)"""
        usuario.activo = False
        usuario.save()
    
    @staticmethod
    def search(query: str) -> List[Usuario]:
        """Busca usuarios por nombre, email o username"""
        return Usuario.objects.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        ).select_related('id_tipo')
    
    @staticmethod
    def get_talleres_activos() -> List[Usuario]:
        """Obtiene todos los talleres activos"""
        return Usuario.objects.filter(
            id_tipo__cve=TipoUsuario.TALLER,
            activo=True
        ).select_related('id_tipo')
    
    @staticmethod
    def get_clientes_activos() -> List[Usuario]:
        """Obtiene todos los clientes activos"""
        return Usuario.objects.filter(
            id_tipo__cve=TipoUsuario.CLIENTE,
            activo=True
        ).select_related('id_tipo')