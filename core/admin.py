"""
CORE ADMIN: Registro de modelos en Django Admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    TipoUsuario, Usuario, Estado, Marca, Modelo,
    Vehiculo, TampBlockPrincipal, TampBlockTalleres
)


@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['cve', 'descripcion']
    search_fields = ['cve', 'descripcion']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'nombre', 'id_tipo', 'activo', 'creado_at']
    list_filter = ['id_tipo', 'activo', 'creado_at']
    search_fields = ['username', 'email', 'nombre', 'cve']
    ordering = ['-creado_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('cve', 'id_tipo', 'nombre', 'telefono', 'activo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('cve', 'id_tipo', 'nombre', 'telefono', 'activo')
        }),
    )


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['clave', 'descripcion', 'tipo']
    list_filter = ['tipo']
    search_fields = ['clave', 'descripcion']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id_marca', 'atendible', 'ano_inicio', 'ano_fin', 'activo']
    list_filter = ['id_marca', 'atendible', 'activo']
    search_fields = ['nombre', 'id_marca__nombre']
    ordering = ['id_marca__nombre', 'nombre']


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'id_modelo', 'id_usuario_propietario', 'ano', 'color', 'creado_at']
    list_filter = ['id_modelo__id_marca', 'creado_at']
    search_fields = ['placa', 'vin', 'id_usuario_propietario__nombre']
    ordering = ['-creado_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('id_modelo__id_marca', 'id_usuario_propietario')


@admin.register(TampBlockPrincipal)
class TampBlockPrincipalAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'hora_inicio', 'hora_fin', 'disponible', 'capacidad', 'reservados', 'disponibles_display']
    list_filter = ['disponible', 'fecha']
    search_fields = ['fecha']
    ordering = ['fecha', 'hora_inicio']
    
    def disponibles_display(self, obj):
        return obj.disponibles
    disponibles_display.short_description = 'Disponibles'


@admin.register(TampBlockTalleres)
class TampBlockTalleresAdmin(admin.ModelAdmin):
    list_display = ['id_usuario_taller', 'fecha', 'disponible', 'capacidad', 'reservados', 'disponibles_display']
    list_filter = ['disponible', 'fecha', 'id_usuario_taller']
    search_fields = ['id_usuario_taller__nombre', 'fecha']
    ordering = ['fecha']
    
    def disponibles_display(self, obj):
        return obj.disponibles
    disponibles_display.short_description = 'Disponibles'