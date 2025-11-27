"""
Service para lógica de negocio de Usuarios
"""
from typing import List, Optional, Dict
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from core.models import Usuario, TipoUsuario
from core.repositories.usuario_repository import UsuarioRepository


class UsuarioService:
    """Maneja la lógica de negocio para usuarios"""
    
    def __init__(self):
        self.repository = UsuarioRepository()
    
    def get_all_usuarios(self, activo: Optional[bool] = None) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        return self.repository.get_all(activo=activo)
    
    def get_usuario_by_id(self, usuario_id: int) -> Usuario:
        """Obtiene un usuario por ID"""
        usuario = self.repository.get_by_id(usuario_id)
        
        if not usuario:
            raise ValidationError(f"Usuario con ID {usuario_id} no encontrado")
        
        return usuario
    
    def get_usuario_by_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email"""
        return self.repository.get_by_email(email)
    
    def get_usuarios_by_tipo(self, tipo_cve: str) -> List[Usuario]:
        """Obtiene usuarios por tipo"""
        return self.repository.get_by_tipo(tipo_cve)
    
    def get_talleres_activos(self) -> List[Usuario]:
        """Obtiene todos los talleres activos"""
        return self.repository.get_talleres_activos()
    
    def get_clientes_activos(self) -> List[Usuario]:
        """Obtiene todos los clientes activos"""
        return self.repository.get_clientes_activos()
    
    def create_usuario(self, data: Dict) -> Usuario:
        """Crea un nuevo usuario"""
        # Validar que el email no exista
        if self.repository.get_by_email(data.get('email')):
            raise ValidationError("El email ya está registrado")
        
        # Validar que el username no exista
        if data.get('username') and self.repository.get_by_username(data.get('username')):
            raise ValidationError("El username ya está registrado")
        
        # Encriptar password si viene
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        # Generar cve si no viene
        if not data.get('cve'):
            data['cve'] = self._generar_cve(data.get('id_tipo'))
        
        return self.repository.create(data)
    
    def update_usuario(self, usuario_id: int, data: Dict) -> Usuario:
        """Actualiza un usuario existente"""
        usuario = self.get_usuario_by_id(usuario_id)
        
        # Validar email si se está actualizando
        if 'email' in data and data['email'] != usuario.email:
            if self.repository.get_by_email(data['email']):
                raise ValidationError("El email ya está registrado")
        
        # Encriptar password si viene
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        return self.repository.update(usuario, data)
    
    def delete_usuario(self, usuario_id: int) -> None:
        """Elimina (desactiva) un usuario"""
        usuario = self.get_usuario_by_id(usuario_id)
        self.repository.delete(usuario)
    
    def search_usuarios(self, query: str) -> List[Usuario]:
        """Busca usuarios"""
        return self.repository.search(query)
    
    def validar_credenciales(self, email: str, password: str) -> Optional[Usuario]:
        """Valida credenciales de un usuario"""
        usuario = self.repository.get_by_email(email)
        
        if not usuario:
            return None
        
        if not usuario.check_password(password):
            return None
        
        if not usuario.activo:
            raise ValidationError("Usuario inactivo")
        
        return usuario
    
    def cambiar_password(self, usuario_id: int, password_actual: str, password_nueva: str) -> Usuario:
        """Cambia la contraseña de un usuario"""
        usuario = self.get_usuario_by_id(usuario_id)
        
        if not usuario.check_password(password_actual):
            raise ValidationError("Contraseña actual incorrecta")
        
        usuario.password = make_password(password_nueva)
        usuario.save()
        
        return usuario
    
    def activar_usuario(self, usuario_id: int) -> Usuario:
        """Activa un usuario"""
        usuario = self.get_usuario_by_id(usuario_id)
        usuario.activo = True
        usuario.save()
        return usuario
    
    def desactivar_usuario(self, usuario_id: int) -> Usuario:
        """Desactiva un usuario"""
        usuario = self.get_usuario_by_id(usuario_id)
        usuario.activo = False
        usuario.save()
        return usuario
    
    def _generar_cve(self, tipo_usuario_id: int) -> str:
        """Genera una clave única para el usuario"""
        from django.utils import timezone
        
        tipo = TipoUsuario.objects.get(id=tipo_usuario_id)
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        
        return f"{tipo.cve[:3].upper()}{timestamp}"
    
    def get_estadisticas_usuarios(self) -> Dict:
        """Obtiene estadísticas de usuarios"""
        total = Usuario.objects.count()
        activos = Usuario.objects.filter(activo=True).count()
        inactivos = total - activos
        
        por_tipo = {}
        for tipo in TipoUsuario.objects.all():
            por_tipo[tipo.cve] = Usuario.objects.filter(id_tipo=tipo).count()
        
        return {
            'total': total,
            'activos': activos,
            'inactivos': inactivos,
            'por_tipo': por_tipo
        }