"""
CORE SERIALIZERS: Usuarios, Vehículos, Calendarios
"""
from rest_framework import serializers
from .models import (
    TipoUsuario, Usuario, Estado, Marca, Modelo, 
    Vehiculo, TampBlockPrincipal, TampBlockTalleres
)
from django.contrib.auth.password_validation import validate_password


# =====================
# TIPOS Y ESTADOS
# =====================

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'


# =====================
# USUARIOS
# =====================

class UsuarioSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField(source='id_tipo.descripcion', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password', 'cve', 
            'id_tipo', 'tipo_usuario', 'nombre', 'telefono', 
            'activo', 'creado_at'
        ]
        read_only_fields = ['id', 'creado_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario.objects.create(**validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'cve', 'id_tipo', 'nombre', 'telefono'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


# =====================
# VEHÍCULOS
# =====================

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'


class ModeloSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='id_marca.nombre', read_only=True)
    
    class Meta:
        model = Modelo
        fields = [
            'id', 'id_marca', 'marca_nombre', 'nombre', 
            'atendible', 'ano_inicio', 'ano_fin', 'activo'
        ]


class ModeloDetailSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer(source='id_marca', read_only=True)
    
    class Meta:
        model = Modelo
        fields = '__all__'


class VehiculoSerializer(serializers.ModelSerializer):
    modelo_info = serializers.SerializerMethodField()
    propietario_nombre = serializers.CharField(source='id_usuario_propietario.nombre', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = [
            'id', 'placa', 'id_modelo', 'modelo_info',
            'id_usuario_propietario', 'propietario_nombre',
            'ano', 'color', 'vin', 'creado_at'
        ]
        read_only_fields = ['id', 'creado_at']
    
    def get_modelo_info(self, obj):
        return f"{obj.id_modelo.id_marca.nombre} {obj.id_modelo.nombre}"


class VehiculoDetailSerializer(serializers.ModelSerializer):
    modelo = ModeloDetailSerializer(source='id_modelo', read_only=True)
    propietario = UsuarioSerializer(source='id_usuario_propietario', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = '__all__'


# =====================
# CALENDARIOS
# =====================

class TampBlockPrincipalSerializer(serializers.ModelSerializer):
    disponibles = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TampBlockPrincipal
        fields = [
            'id', 'fecha', 'hora_inicio', 'hora_fin',
            'disponible', 'capacidad', 'reservados', 
            'disponibles', 'creado_at'
        ]
        read_only_fields = ['id', 'reservados', 'creado_at']


class TampBlockTalleresSerializer(serializers.ModelSerializer):
    taller_nombre = serializers.CharField(source='id_usuario_taller.nombre', read_only=True)
    disponibles = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TampBlockTalleres
        fields = [
            'id', 'id_usuario_taller', 'taller_nombre', 'fecha',
            'disponible', 'capacidad', 'reservados', 'disponibles',
            'notas', 'creado_at'
        ]
        read_only_fields = ['id', 'reservados', 'creado_at']