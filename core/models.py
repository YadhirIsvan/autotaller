"""
CORE MODELS: Usuarios, Estados, Vehículos, Calendarios
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


# =====================
# TIPOS DE USUARIO
# =====================

class TipoUsuario(models.Model):
    """Tipos de usuario: administrador, agente, taller, cliente"""
    ADMINISTRADOR = 'administrador'
    AGENTE = 'agente'
    TALLER = 'taller'
    CLIENTE = 'cliente'
    
    TIPOS_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (AGENTE, 'Agente'),
        (TALLER, 'Taller'),
        (CLIENTE, 'Cliente'),
    ]
    
    cve = models.CharField(max_length=20, unique=True, choices=TIPOS_CHOICES)
    descripcion = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'tipos_usuarios'
        verbose_name = 'Tipo de Usuario'
        verbose_name_plural = 'Tipos de Usuarios'
    
    def __str__(self):
        return self.descripcion


# =====================
# USUARIO PERSONALIZADO
# =====================

class Usuario(AbstractUser):
    """Usuario extendido del sistema"""
    cve = models.CharField(max_length=50, unique=True, blank=True, null=True)
    id_tipo = models.ForeignKey(
        TipoUsuario, 
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name='Tipo de Usuario'
    )
    nombre = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre or self.username} ({self.id_tipo.cve})"


# =====================
# ESTADOS
# =====================

class Estado(models.Model):
    """Estados para diferentes procesos del sistema"""
    TIPO_SOLICITUD = 'solicitud'
    TIPO_RESERVACION = 'reservacion'
    TIPO_SERVICIO = 'servicio'
    
    TIPO_CHOICES = [
        (TIPO_SOLICITUD, 'Solicitud'),
        (TIPO_RESERVACION, 'Reservación'),
        (TIPO_SERVICIO, 'Servicio'),
    ]
    
    clave = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    
    class Meta:
        db_table = 'estados'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
    
    def __str__(self):
        return f"{self.descripcion} ({self.tipo})"


# =====================
# VEHÍCULOS
# =====================

class Marca(models.Model):
    """Marcas de vehículos"""
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'marcas'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Modelo(models.Model):
    """Modelos de vehículos"""
    id_marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        related_name='modelos'
    )
    nombre = models.CharField(max_length=100)
    atendible = models.BooleanField(
        default=True,
        help_text='Define si el modelo puede ser atendido'
    )
    ano_inicio = models.IntegerField(
        null=True, 
        blank=True,
        help_text='Año desde el cual se atiende'
    )
    ano_fin = models.IntegerField(
        null=True, 
        blank=True,
        help_text='Año hasta el cual se atiende'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'modelos'
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        ordering = ['id_marca__nombre', 'nombre']
    
    def __str__(self):
        return f"{self.id_marca.nombre} {self.nombre}"


class Vehiculo(models.Model):
    """Vehículos de los clientes"""
    placa = models.CharField(max_length=50, unique=True)
    id_modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        related_name='vehiculos'
    )
    id_usuario_propietario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='vehiculos',
        help_text='Cliente propietario del vehículo'
    )
    ano = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    vin = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True, 
        null=True,
        help_text='Número de identificación vehicular'
    )
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-creado_at']
    
    def __str__(self):
        return f"{self.placa} - {self.id_modelo}"


# =====================
# CALENDARIOS (TAMP BLOCK)
# =====================

class TampBlockPrincipal(models.Model):
    """Calendario de disponibilidad del taller principal"""
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponible = models.BooleanField(default=True)
    capacidad = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Cuántos vehículos puede atender'
    )
    reservados = models.IntegerField(default=0)
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tamp_block_principal'
        verbose_name = 'Calendario Taller Principal'
        verbose_name_plural = 'Calendarios Taller Principal'
        unique_together = ['fecha', 'hora_inicio']
        ordering = ['fecha', 'hora_inicio']
    
    def __str__(self):
        return f"{self.fecha} {self.hora_inicio}-{self.hora_fin}"
    
    @property
    def disponibles(self):
        """Retorna cuántos espacios quedan disponibles"""
        return self.capacidad - self.reservados


class TampBlockTalleres(models.Model):
    """Calendario de disponibilidad de talleres secundarios"""
    id_usuario_taller = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='calendario',
        help_text='Taller secundario'
    )
    fecha = models.DateField()
    disponible = models.BooleanField(default=True)
    capacidad = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    reservados = models.IntegerField(default=0)
    notas = models.TextField(blank=True, null=True)
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tamp_block_talleres'
        verbose_name = 'Calendario Taller Secundario'
        verbose_name_plural = 'Calendarios Talleres Secundarios'
        unique_together = ['id_usuario_taller', 'fecha']
        ordering = ['fecha']
    
    def __str__(self):
        return f"{self.id_usuario_taller.nombre} - {self.fecha}"
    
    @property
    def disponibles(self):
        """Retorna cuántos espacios quedan disponibles"""
        return self.capacidad - self.reservados