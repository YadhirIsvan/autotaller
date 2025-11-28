"""
SOLICITUDES SERIALIZERS
"""
from rest_framework import serializers
from .models import Solicitud, DetalleSolicitud, ReservacionTallerPrincipal
from core.serializers import VehiculoSerializer, UsuarioSerializer, EstadoSerializer


class DetalleSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleSolicitud
        fields = '__all__'
        read_only_fields = ['id', 'creado_at']


class SolicitudSerializer(serializers.ModelSerializer):
    vehiculo_info = serializers.SerializerMethodField()
    usuario_nombre = serializers.CharField(source='id_usuario.nombre', read_only=True)
    estado_descripcion = serializers.CharField(source='id_estado.descripcion', read_only=True)
    
    class Meta:
        model = Solicitud
        fields = [
            'id', 'id_vehiculo', 'vehiculo_info', 'id_usuario', 'usuario_nombre',
            'fecha_creacion', 'id_estado', 'estado_descripcion', 'descripcion',
            'motivo_rechazo', 'aprobado_por', 'fecha_respuesta', 'referencia_externa'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_respuesta']
    
    def get_vehiculo_info(self, obj):
        return f"{obj.id_vehiculo.placa} - {obj.id_vehiculo.id_modelo}"


class SolicitudDetailSerializer(serializers.ModelSerializer):
    vehiculo = VehiculoSerializer(source='id_vehiculo', read_only=True)
    usuario = UsuarioSerializer(source='id_usuario', read_only=True)
    estado = EstadoSerializer(source='id_estado', read_only=True)
    detalle = DetalleSolicitudSerializer(read_only=True)
    aprobado_por_info = UsuarioSerializer(source='aprobado_por', read_only=True)
    
    class Meta:
        model = Solicitud
        fields = '__all__'


class SolicitudCreateSerializer(serializers.ModelSerializer):
    observaciones = serializers.CharField(required=False, allow_blank=True)
    costo_estimado = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False
    )
    
    class Meta:
        model = Solicitud
        fields = ['id_vehiculo', 'id_usuario', 'descripcion', 'observaciones', 'costo_estimado']


class AprobarRechazarSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True)


class ReservacionTallerPrincipalSerializer(serializers.ModelSerializer):
    solicitud_info = serializers.SerializerMethodField()
    estado_descripcion = serializers.CharField(source='id_estado.descripcion', read_only=True)
    
    class Meta:
        model = ReservacionTallerPrincipal
        fields = [
            'id', 'id_solicitud', 'solicitud_info', 'id_tamp_block',
            'id_estado', 'estado_descripcion', 'fecha_evaluacion',
            'notas_evaluacion', 'avance_global', 'estado_global',
            'atendido_por', 'fecha_inicio', 'fecha_fin_estimada',
            'fecha_fin_real', 'creado_at'
        ]
        read_only_fields = ['id', 'creado_at', 'avance_global', 'estado_global']
    
    def get_solicitud_info(self, obj):
        return f"Solicitud #{obj.id_solicitud.id} - {obj.id_solicitud.id_vehiculo.placa}"


class ReservacionTallerPrincipalDetailSerializer(serializers.ModelSerializer):
    solicitud = SolicitudDetailSerializer(source='id_solicitud', read_only=True)
    estado = EstadoSerializer(source='id_estado', read_only=True)
    servicios = serializers.SerializerMethodField()
    
    class Meta:
        model = ReservacionTallerPrincipal
        fields = '__all__'
    
    def get_servicios(self, obj):
        from servicios.serializers import ReservacionServicioSerializer
        return ReservacionServicioSerializer(
            obj.servicios_asignados.all(),
            many=True
        ).data