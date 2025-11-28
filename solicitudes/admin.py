# solicitudes/admin.py
from django.contrib import admin
from .models import Solicitud, DetalleSolicitud, ReservacionTallerPrincipal

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_vehiculo', 'id_usuario', 'id_estado', 'fecha_creacion']
    list_filter = ['id_estado', 'fecha_creacion']
    search_fields = ['id_vehiculo__placa', 'id_usuario__nombre']

@admin.register(ReservacionTallerPrincipal)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_solicitud', 'id_estado', 'avance_global', 'creado_at']
    list_filter = ['id_estado', 'creado_at']