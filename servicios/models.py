"""
SERVICIOS MODELS: Catálogo de servicios, asignaciones y progreso
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Usuario, Estado, TampBlockTalleres
from solicitudes.models import ReservacionTallerPrincipal


# =====================
# CATÁLOGO DE SERVICIOS
# =====================

class CategoriaServicio(models.Model):
    """Categorías de servicios"""
    nombre = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Pintura, Mecánica, Eléctrico, etc.'
    )
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categorias_servicios'
        verbose_name = 'Categoría de Servicio'
        verbose_name_plural = 'Categorías de Servicios'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    """Catálogo de servicios disponibles"""
    id_categoria = models.ForeignKey(
        CategoriaServicio,
        on_delete=models.CASCADE,
        related_name='servicios'
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    costo_base = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,
        blank=True
    )
    duracion_estimada_dias = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Días estimados para completar'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'servicios'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['id_categoria__nombre', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.id_categoria.nombre})"


class ServicioUsuarioTaller(models.Model):
    """Servicios que ofrece cada taller"""
    id_usuario_taller = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='servicios_ofrecidos',
        help_text='Taller que ofrece el servicio'
    )
    id_servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='talleres_ofrecen'
    )
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio que cobra este taller'
    )
    duracion_dias = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Días que tarda este taller específico'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'servicio_usuario_taller'
        verbose_name = 'Servicio de Taller'
        verbose_name_plural = 'Servicios de Talleres'
        unique_together = ['id_usuario_taller', 'id_servicio']
    
    def __str__(self):
        return f"{self.id_usuario_taller.nombre} - {self.id_servicio.nombre}"


# =====================
# RESERVACIONES DE SERVICIOS
# =====================

class ReservacionServicio(models.Model):
    """Servicios específicos asignados a una reservación"""
    id_reservacion_taller_principal = models.ForeignKey(
        ReservacionTallerPrincipal,
        on_delete=models.CASCADE,
        related_name='servicios_asignados',
        help_text='Reservación principal'
    )
    id_servicio_usuario_taller = models.ForeignKey(
        ServicioUsuarioTaller,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        help_text='Servicio y taller asignado'
    )
    estado_dias = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Días reales que tardó (actualizado por taller)'
    )
    progreso = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Porcentaje 0-100%'
    )
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name='reservaciones_servicios'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio_real = models.DateTimeField(null=True, blank=True)
    fecha_fin_estimada = models.DateTimeField(null=True, blank=True)
    fecha_fin_real = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'reservaciones_servicios'
        verbose_name = 'Reservación de Servicio'
        verbose_name_plural = 'Reservaciones de Servicios'
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"Servicio {self.id} - {self.id_servicio_usuario_taller.id_servicio.nombre}"


class ReservacionTampBlock(models.Model):
    """Vincula servicios con fechas del calendario del taller"""
    id_reservacion_servicio = models.ForeignKey(
        ReservacionServicio,
        on_delete=models.CASCADE,
        related_name='fechas_calendario'
    )
    id_tamp_block_taller = models.ForeignKey(
        TampBlockTalleres,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        help_text='Fecha en calendario del taller'
    )
    fecha_asignada = models.DateField()
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reservaciones_tamp_block'
        verbose_name = 'Reservación Calendario'
        verbose_name_plural = 'Reservaciones Calendario'
        ordering = ['fecha_asignada']
    
    def __str__(self):
        return f"Reserva {self.id_reservacion_servicio.id} - {self.fecha_asignada}"


class ProgresoServicio(models.Model):
    """Historial de actualizaciones de progreso"""
    id_reservacion_servicio = models.ForeignKey(
        ReservacionServicio,
        on_delete=models.CASCADE,
        related_name='historial_progreso'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    porcentaje_anterior = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    porcentaje_nuevo = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    dias_estimados = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Actualización de días estimados'
    )
    comentario = models.TextField(blank=True, null=True)
    evidencia_url = models.CharField(max_length=300, blank=True, null=True)
    actualizado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actualizaciones_progreso',
        help_text='Usuario taller que actualizó'
    )
    
    class Meta:
        db_table = 'progreso_servicio'
        verbose_name = 'Progreso de Servicio'
        verbose_name_plural = 'Progresos de Servicios'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Progreso {self.porcentaje_nuevo}% - {self.fecha.strftime('%Y-%m-%d %H:%M')}"