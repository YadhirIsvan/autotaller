"""
SERVICIOS ADMIN: Registro de modelos en Django Admin
"""
from django.contrib import admin
from .models import (
    CategoriaServicio, Servicio, ServicioUsuarioTaller,
    ReservacionServicio, ReservacionTampBlock, ProgresoServicio
)


@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'id_categoria', 'costo_base',
        'duracion_estimada_dias', 'activo'
    ]
    list_filter = ['id_categoria', 'activo']
    search_fields = ['nombre', 'id_categoria__nombre']
    ordering = ['id_categoria__nombre', 'nombre']


@admin.register(ServicioUsuarioTaller)
class ServicioUsuarioTallerAdmin(admin.ModelAdmin):
    list_display = [
        'id_usuario_taller', 'id_servicio',
        'precio', 'duracion_dias', 'activo'
    ]
    list_filter = ['id_usuario_taller', 'id_servicio__id_categoria', 'activo']
    search_fields = [
        'id_usuario_taller__nombre',
        'id_servicio__nombre'
    ]
    ordering = ['id_usuario_taller__nombre', 'id_servicio__nombre']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        )


class ProgresoServicioInline(admin.TabularInline):
    model = ProgresoServicio
    extra = 0
    can_delete = False
    readonly_fields = ['fecha']
    ordering = ['-fecha']


@admin.register(ReservacionServicio)
class ReservacionServicioAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_vehiculo', 'get_servicio', 'get_taller',
        'progreso', 'id_estado', 'fecha_asignacion'
    ]
    list_filter = [
        'id_estado',
        'id_servicio_usuario_taller__id_usuario_taller',
        'fecha_asignacion'
    ]
    search_fields = [
        'id_reservacion_taller_principal__id_solicitud__id_vehiculo__placa',
        'id_servicio_usuario_taller__id_servicio__nombre',
        'id_servicio_usuario_taller__id_usuario_taller__nombre'
    ]
    ordering = ['-fecha_asignacion']
    inlines = [ProgresoServicioInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': (
                'id_reservacion_taller_principal',
                'id_servicio_usuario_taller',
                'id_estado'
            )
        }),
        ('Progreso', {
            'fields': (
                'progreso', 'estado_dias',
                'fecha_inicio_real', 'fecha_fin_estimada', 'fecha_fin_real'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )
    
    readonly_fields = ['fecha_asignacion']
    
    def get_vehiculo(self, obj):
        return obj.id_reservacion_taller_principal.id_solicitud.id_vehiculo.placa
    get_vehiculo.short_description = 'Vehículo'
    
    def get_servicio(self, obj):
        return obj.id_servicio_usuario_taller.id_servicio.nombre
    get_servicio.short_description = 'Servicio'
    
    def get_taller(self, obj):
        return obj.id_servicio_usuario_taller.id_usuario_taller.nombre
    get_taller.short_description = 'Taller'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        )


@admin.register(ReservacionTampBlock)
class ReservacionTampBlockAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_servicio', 'get_taller',
        'fecha_asignada', 'creado_at'
    ]
    list_filter = ['fecha_asignada', 'creado_at']
    search_fields = [
        'id_reservacion_servicio__id_servicio_usuario_taller__id_servicio__nombre'
    ]
    ordering = ['fecha_asignada']
    
    def get_servicio(self, obj):
        return obj.id_reservacion_servicio.id_servicio_usuario_taller.id_servicio.nombre
    get_servicio.short_description = 'Servicio'
    
    def get_taller(self, obj):
        return obj.id_reservacion_servicio.id_servicio_usuario_taller.id_usuario_taller.nombre
    get_taller.short_description = 'Taller'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'id_reservacion_servicio__id_servicio_usuario_taller__id_servicio',
            'id_reservacion_servicio__id_servicio_usuario_taller__id_usuario_taller'
        )


@admin.register(ProgresoServicio)
class ProgresoServicioAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_servicio', 'fecha',
        'porcentaje_anterior', 'porcentaje_nuevo',
        'dias_estimados', 'actualizado_por'
    ]
    list_filter = ['fecha', 'actualizado_por']
    search_fields = [
        'id_reservacion_servicio__id_servicio_usuario_taller__id_servicio__nombre'
    ]
    ordering = ['-fecha']
    readonly_fields = ['fecha']
    
    def get_servicio(self, obj):
        return obj.id_reservacion_servicio.id_servicio_usuario_taller.id_servicio.nombre
    get_servicio.short_description = 'Servicio'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'id_reservacion_servicio__id_servicio_usuario_taller__id_servicio',
            'actualizado_por'
        )