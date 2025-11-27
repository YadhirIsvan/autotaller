"""
SERVICIOS SERIALIZERS: Servicios, Asignaciones y Progreso
"""
from rest_framework import serializers
from .models import (
    CategoriaServicio, Servicio, ServicioUsuarioTaller,
    ReservacionServicio, ReservacionTampBlock, ProgresoServicio
)
from core.serializers import UsuarioSerializer, EstadoSerializer


# =====================
# CATÁLOGO DE SERVICIOS
# =====================

class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='id_categoria.nombre', read_only=True)
    
    class Meta:
        model = Servicio
        fields = [
            'id', 'id_categoria', 'categoria_nombre', 'nombre',
            'descripcion', 'costo_base', 'duracion_estimada_dias', 'activo'
        ]


class ServicioDetailSerializer(serializers.ModelSerializer):
    categoria = CategoriaServicioSerializer(source='id_categoria', read_only=True)
    talleres_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Servicio
        fields = '__all__'
    
    def get_talleres_disponibles(self, obj):
        return ServicioUsuarioTallerSerializer(
            obj.talleres_ofrecen.filter(activo=True),
            many=True
        ).data


class ServicioUsuarioTallerSerializer(serializers.ModelSerializer):
    taller_nombre = serializers.CharField(source='id_usuario_taller.nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='id_servicio.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='id_servicio.id_categoria.nombre', read_only=True)
    
    class Meta:
        model = ServicioUsuarioTaller
        fields = [
            'id', 'id_usuario_taller', 'taller_nombre',
            'id_servicio', 'servicio_nombre', 'categoria_nombre',
            'precio', 'duracion_dias', 'activo'
        ]


class ServicioUsuarioTallerDetailSerializer(serializers.ModelSerializer):
    taller = UsuarioSerializer(source='id_usuario_taller', read_only=True)
    servicio = ServicioDetailSerializer(source='id_servicio', read_only=True)
    
    class Meta:
        model = ServicioUsuarioTaller
        fields = '__all__'


# =====================
# RESERVACIONES DE SERVICIOS
# =====================

class ReservacionTampBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservacionTampBlock
        fields = '__all__'
        read_only_fields = ['id', 'creado_at']


class ProgresoServicioSerializer(serializers.ModelSerializer):
    actualizado_por_nombre = serializers.CharField(
        source='actualizado_por.nombre',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = ProgresoServicio
        fields = [
            'id', 'id_reservacion_servicio', 'fecha',
            'porcentaje_anterior', 'porcentaje_nuevo',
            'dias_estimados', 'comentario', 'evidencia_url',
            'actualizado_por', 'actualizado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha']


class ReservacionServicioSerializer(serializers.ModelSerializer):
    servicio_info = serializers.SerializerMethodField()
    taller_nombre = serializers.CharField(
        source='id_servicio_usuario_taller.id_usuario_taller.nombre',
        read_only=True
    )
    estado_descripcion = serializers.CharField(
        source='id_estado.descripcion',
        read_only=True
    )
    vehiculo_placa = serializers.CharField(
        source='id_reservacion_taller_principal.id_solicitud.id_vehiculo.placa',
        read_only=True
    )
    
    class Meta:
        model = ReservacionServicio
        fields = [
            'id', 'id_reservacion_taller_principal', 'vehiculo_placa',
            'id_servicio_usuario_taller', 'servicio_info', 'taller_nombre',
            'estado_dias', 'progreso', 'id_estado', 'estado_descripcion',
            'fecha_asignacion', 'fecha_inicio_real', 'fecha_fin_estimada',
            'fecha_fin_real', 'observaciones'
        ]
        read_only_fields = ['id', 'fecha_asignacion']
    
    def get_servicio_info(self, obj):
        servicio = obj.id_servicio_usuario_taller.id_servicio
        return f"{servicio.nombre} ({servicio.id_categoria.nombre})"


class ReservacionServicioDetailSerializer(serializers.ModelSerializer):
    servicio_taller = ServicioUsuarioTallerDetailSerializer(
        source='id_servicio_usuario_taller',
        read_only=True
    )
    estado = EstadoSerializer(source='id_estado', read_only=True)
    historial_progreso = ProgresoServicioSerializer(many=True, read_only=True)
    fechas_calendario = ReservacionTampBlockSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReservacionServicio
        fields = '__all__'


class ReservacionServicioCreateSerializer(serializers.ModelSerializer):
    fechas = serializers.ListField(
        child=serializers.DateField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ReservacionServicio
        fields = [
            'id_reservacion_taller_principal',
            'id_servicio_usuario_taller',
            'id_estado',
            'observaciones',
            'fechas'
        ]
    
    def create(self, validated_data):
        fechas = validated_data.pop('fechas', [])
        reservacion = ReservacionServicio.objects.create(**validated_data)
        
        # Crear las fechas en el calendario del taller
        taller = reservacion.id_servicio_usuario_taller.id_usuario_taller
        
        for fecha in fechas:
            from core.models import TampBlockTalleres
            tamp_block, created = TampBlockTalleres.objects.get_or_create(
                id_usuario_taller=taller,
                fecha=fecha,
                defaults={'disponible': True, 'capacidad': 1}
            )
            
            ReservacionTampBlock.objects.create(
                id_reservacion_servicio=reservacion,
                id_tamp_block_taller=tamp_block,
                fecha_asignada=fecha
            )
        
        return reservacion


class ActualizarProgresoSerializer(serializers.Serializer):
    """Para que el taller actualice el progreso"""
    porcentaje = serializers.IntegerField(min_value=0, max_value=100)
    dias_estimados = serializers.IntegerField(min_value=0, required=False)
    comentario = serializers.CharField(required=False, allow_blank=True)
    evidencia_url = serializers.CharField(required=False, allow_blank=True)