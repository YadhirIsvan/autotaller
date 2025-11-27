"""
SOLICITUDES MODELS: Solicitudes y Reservaciones Taller Principal
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Usuario, Estado, Vehiculo, TampBlockPrincipal


# =====================
# SOLICITUDES
# =====================

class Solicitud(models.Model):
    """Solicitudes de clientes para evaluación de vehículos"""
    id_vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_creadas',
        help_text='Cliente que solicita'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name='solicitudes'
    )
    descripcion = models.TextField(blank=True, null=True)
    motivo_rechazo = models.TextField(
        blank=True, 
        null=True,
        help_text='Si es rechazada, aquí va el motivo'
    )
    aprobado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas',
        help_text='Administrador/agente que aprobó'
    )
    fecha_respuesta = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Fecha de aprobación o rechazo'
    )
    referencia_externa = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'solicitudes'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Solicitud {self.id} - {self.id_vehiculo.placa}"


class DetalleSolicitud(models.Model):
    """Detalle de solicitud"""
    id_solicitud = models.OneToOneField(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='detalle'
    )
    observaciones = models.TextField(blank=True, null=True)
    costo_estimado = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,
        blank=True
    )
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'detalle_solicitud'
        verbose_name = 'Detalle de Solicitud'
        verbose_name_plural = 'Detalles de Solicitudes'
    
    def __str__(self):
        return f"Detalle de {self.id_solicitud}"


# =====================
# RESERVACIONES TALLER PRINCIPAL
# =====================

class ReservacionTallerPrincipal(models.Model):
    """Reservación de evaluación en taller principal"""
    id_solicitud = models.OneToOneField(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='reservacion',
        help_text='Una solicitud = una reservación'
    )
    id_tamp_block = models.ForeignKey(
        TampBlockPrincipal,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        help_text='Fecha/hora agendada'
    )
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name='reservaciones_principal'
    )
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)
    notas_evaluacion = models.TextField(blank=True, null=True)
    avance_global = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Progreso total 0-100%'
    )
    estado_global = models.CharField(max_length=100, default='pendiente')
    atendido_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_realizadas',
        help_text='Agente que realizó la evaluación'
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin_estimada = models.DateTimeField(null=True, blank=True)
    fecha_fin_real = models.DateTimeField(null=True, blank=True)
    creado_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reservaciones_taller_principal'
        verbose_name = 'Reservación Taller Principal'
        verbose_name_plural = 'Reservaciones Taller Principal'
        ordering = ['-creado_at']
    
    def __str__(self):
        return f"Reservación {self.id} - {self.id_solicitud.id_vehiculo.placa}"