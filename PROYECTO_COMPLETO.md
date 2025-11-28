# Proyecto Django Completo



---

## 📄 ./requirements.txt

```python
Django==5.0
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-decouple==3.8
psycopg2-binary==2.9.9
Pillow==10.2.0
python-decouple

```


---

## 📄 ./PROYECTO_COMPLETO.md

```python

```


---

## 📄 ./manage.py

```python
#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autotaller.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```


---

## 📄 ./exportar_proyecto.py

```python
import os

OUTPUT_FILE = "PROYECTO_COMPLETO.md"

# Carpetas y patrones que deben ignorarse
IGNORAR = [
    "venv", "__pycache__", "migrations",
    ".git", ".idea", ".vscode"
]

# Extensiones útiles para IA
EXTENSIONES = (
    ".py", ".html", ".css", ".js",
    ".json", ".md", ".txt", ".yaml", ".yml"
)


def debe_ignorar(path):
    return any(ignorar in path for ignorar in IGNORAR)


with open(OUTPUT_FILE, "w", encoding="utf-8") as salida:
    salida.write("# Proyecto Django Completo\n\n")

    for root, dirs, files in os.walk("."):
        if debe_ignorar(root):
            continue

        for file in files:
            if not file.endswith(EXTENSIONES):
                continue

            filepath = os.path.join(root, file)

            if debe_ignorar(filepath):
                continue

            salida.write(f"\n\n---\n\n")
            salida.write(f"## 📄 {filepath}\n\n")
            salida.write("```python\n")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    salida.write(f.read())
            except Exception as e:
                salida.write(f"[ERROR al leer archivo: {e}]")

            salida.write("\n```\n")

print(f"\n\n✅ Archivo generado exitosamente: {OUTPUT_FILE}\n")

```


---

## 📄 ./servicios/serializers.py

```python
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
```


---

## 📄 ./servicios/views.py

```python
"""
SERVICIOS VIEWS: Catálogo, Asignaciones y Progreso
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    CategoriaServicio, Servicio, ServicioUsuarioTaller,
    ReservacionServicio, ReservacionTampBlock, ProgresoServicio
)
from .serializers import (
    CategoriaServicioSerializer, ServicioSerializer, ServicioDetailSerializer,
    ServicioUsuarioTallerSerializer, ServicioUsuarioTallerDetailSerializer,
    ReservacionServicioSerializer, ReservacionServicioDetailSerializer,
    ReservacionServicioCreateSerializer, ActualizarProgresoSerializer,
    ReservacionTampBlockSerializer, ProgresoServicioSerializer
)
from .services.servicio_service import ServicioService
from .services.asignacion_service import AsignacionService
from .services.progreso_service import ProgresoService


# =====================
# CATÁLOGO DE SERVICIOS
# =====================

class CategoriaServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para categorías de servicios
    """
    queryset = CategoriaServicio.objects.all()
    serializer_class = CategoriaServicioSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Solo categorías activas"""
        categorias = CategoriaServicio.objects.filter(activo=True)
        serializer = self.get_serializer(categorias, many=True)
        return Response(serializer.data)


class ServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para servicios
    """
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ServicioDetailSerializer
        return ServicioSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Solo servicios activos"""
        servicios = ServicioService.obtener_activos()
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Filtrar servicios por categoría"""
        categoria_id = request.query_params.get('categoria_id')
        if not categoria_id:
            return Response(
                {'error': 'Parámetro categoria_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servicios = ServicioService.obtener_por_categoria(int(categoria_id))
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def talleres_disponibles(self, request, pk=None):
        """Obtener talleres que ofrecen este servicio"""
        servicio = self.get_object()
        talleres = ServicioService.obtener_talleres_por_servicio(servicio.id)
        serializer = ServicioUsuarioTallerSerializer(talleres, many=True)
        return Response(serializer.data)


class ServicioUsuarioTallerViewSet(viewsets.ModelViewSet):
    """
    ViewSet para servicios ofrecidos por talleres
    """
    queryset = ServicioUsuarioTaller.objects.all()
    serializer_class = ServicioUsuarioTallerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ServicioUsuarioTallerDetailSerializer
        return ServicioUsuarioTallerSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es taller, solo ver sus servicios
        if user.id_tipo.cve == 'taller':
            queryset = queryset.filter(id_usuario_taller=user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def mis_servicios(self, request):
        """Obtener servicios del taller actual"""
        if request.user.id_tipo.cve != 'taller':
            return Response(
                {'error': 'Solo talleres pueden acceder a esta función'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        servicios = ServicioUsuarioTaller.objects.filter(
            id_usuario_taller=request.user,
            activo=True
        )
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_taller(self, request):
        """Obtener servicios de un taller específico"""
        taller_id = request.query_params.get('taller_id')
        if not taller_id:
            return Response(
                {'error': 'Parámetro taller_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servicios = ServicioService.obtener_servicios_taller(int(taller_id))
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)


# =====================
# RESERVACIONES DE SERVICIOS
# =====================

class ReservacionServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para reservaciones de servicios
    """
    queryset = ReservacionServicio.objects.all()
    serializer_class = ReservacionServicioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservacionServicioCreateSerializer
        elif self.action == 'retrieve':
            return ReservacionServicioDetailSerializer
        return ReservacionServicioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es taller, solo ver servicios asignados a él
        if user.id_tipo.cve == 'taller':
            queryset = queryset.filter(
                id_servicio_usuario_taller__id_usuario_taller=user
            )
        # Si es cliente, solo ver servicios de sus vehículos
        elif user.id_tipo.cve == 'cliente':
            queryset = queryset.filter(
                id_reservacion_taller_principal__id_solicitud__id_usuario=user
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def mis_servicios(self, request):
        """Obtener servicios del usuario actual"""
        if request.user.id_tipo.cve == 'taller':
            servicios = AsignacionService.obtener_por_taller(request.user.id)
        elif request.user.id_tipo.cve == 'cliente':
            # Obtener servicios de las reservaciones del cliente
            servicios = ReservacionServicio.objects.filter(
                id_reservacion_taller_principal__id_solicitud__id_usuario=request.user
            )
        else:
            servicios = self.get_queryset()
        
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def asignar_servicio(self, request):
        """Asignar un servicio a un taller"""
        # Verificar permisos
        if request.user.id_tipo.cve not in ['administrador', 'agente']:
            return Response(
                {'error': 'No tiene permisos para asignar servicios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReservacionServicioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            reservacion = AsignacionService.asignar_servicio(
                serializer.validated_data['id_reservacion_taller_principal'].id,
                serializer.validated_data['id_servicio_usuario_taller'].id,
                serializer.validated_data['id_estado'].id,
                serializer.validated_data.get('fechas', []),
                serializer.validated_data.get('observaciones', '')
            )
            
            result_serializer = ReservacionServicioDetailSerializer(reservacion)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def iniciar_servicio(self, request, pk=None):
        """Iniciar un servicio"""
        servicio = self.get_object()
        
        # Verificar permisos
        if request.user.id_tipo.cve == 'taller':
            if servicio.id_servicio_usuario_taller.id_usuario_taller != request.user:
                return Response(
                    {'error': 'No tiene permisos para este servicio'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            servicio_actualizado = AsignacionService.iniciar_servicio(servicio.id)
            serializer = self.get_serializer(servicio_actualizado)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def actualizar_progreso(self, request, pk=None):
        """Actualizar progreso del servicio"""
        servicio = self.get_object()
        
        # Verificar permisos
        if request.user.id_tipo.cve == 'taller':
            if servicio.id_servicio_usuario_taller.id_usuario_taller != request.user:
                return Response(
                    {'error': 'No tiene permisos para este servicio'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = ActualizarProgresoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            servicio_actualizado = ProgresoService.actualizar_progreso(
                servicio.id,
                serializer.validated_data['porcentaje'],
                request.user.id,
                serializer.validated_data.get('dias_estimados'),
                serializer.validated_data.get('comentario', ''),
                serializer.validated_data.get('evidencia_url', '')
            )
            
            result_serializer = ReservacionServicioDetailSerializer(servicio_actualizado)
            return Response(result_serializer.data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def finalizar_servicio(self, request, pk=None):
        """Finalizar un servicio"""
        servicio = self.get_object()
        
        # Verificar permisos
        if request.user.id_tipo.cve == 'taller':
            if servicio.id_servicio_usuario_taller.id_usuario_taller != request.user:
                return Response(
                    {'error': 'No tiene permisos para este servicio'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            servicio_actualizado = ProgresoService.finalizar_servicio(servicio.id)
            serializer = self.get_serializer(servicio_actualizado)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Obtener historial de progreso"""
        servicio = self.get_object()
        historial = ProgresoService.obtener_historial(servicio.id)
        serializer = ProgresoServicioSerializer(historial, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Filtrar servicios por estado"""
        estado = request.query_params.get('estado')
        if not estado:
            return Response(
                {'error': 'Parámetro estado requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servicios = AsignacionService.obtener_por_estado(estado)
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)


class ProgresoServicioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver historial de progreso
    """
    queryset = ProgresoServicio.objects.all()
    serializer_class = ProgresoServicioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es taller, solo ver progreso de sus servicios
        if user.id_tipo.cve == 'taller':
            queryset = queryset.filter(
                id_reservacion_servicio__id_servicio_usuario_taller__id_usuario_taller=user
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_servicio(self, request):
        """Obtener progreso de un servicio específico"""
        servicio_id = request.query_params.get('servicio_id')
        if not servicio_id:
            return Response(
                {'error': 'Parámetro servicio_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        progreso = ProgresoService.obtener_historial(int(servicio_id))
        serializer = self.get_serializer(progreso, many=True)
        return Response(serializer.data)
```


---

## 📄 ./servicios/models.py

```python
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
```


---

## 📄 ./servicios/admin.py

```python
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
```


---

## 📄 ./servicios/__init__.py

```python

```


---

## 📄 ./servicios/tests.py

```python
from django.test import TestCase

# Create your tests here.

```


---

## 📄 ./servicios/apps.py

```python
from django.apps import AppConfig


class ServiciosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'servicios'

```


---

## 📄 ./servicios/urls.py

```python
"""
SERVICIOS URLS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaServicioViewSet, ServicioViewSet,
    ServicioUsuarioTallerViewSet, ReservacionServicioViewSet,
    ProgresoServicioViewSet
)

router = DefaultRouter()

router.register(r'categorias', CategoriaServicioViewSet, basename='categoria-servicio')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'servicios-taller', ServicioUsuarioTallerViewSet, basename='servicio-taller')
router.register(r'reservaciones-servicio', ReservacionServicioViewSet, basename='reservacion-servicio')
router.register(r'progreso', ProgresoServicioViewSet, basename='progreso-servicio')

urlpatterns = [
    path('', include(router.urls)),
]
```


---

## 📄 ./servicios/repositories/servicio_repository.py

```python
"""
Repository para operaciones de base de datos de Servicios
"""
from typing import List, Optional
from django.db.models import Q
from servicios.models import (
    CategoriaServicio, Servicio, ServicioUsuarioTaller,
    ReservacionServicio, ReservacionTampBlock
)


class CategoriaServicioRepository:
    """Maneja operaciones de BD para categorías de servicios"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[CategoriaServicio]:
        """Obtiene todas las categorías"""
        queryset = CategoriaServicio.objects.all()
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(categoria_id: int) -> Optional[CategoriaServicio]:
        """Obtiene una categoría por ID"""
        try:
            return CategoriaServicio.objects.get(id=categoria_id)
        except CategoriaServicio.DoesNotExist:
            return None


class ServicioRepository:
    """Maneja operaciones de BD para servicios"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[Servicio]:
        """Obtiene todos los servicios"""
        queryset = Servicio.objects.select_related('id_categoria')
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(servicio_id: int) -> Optional[Servicio]:
        """Obtiene un servicio por ID"""
        try:
            return Servicio.objects.select_related('id_categoria').get(id=servicio_id)
        except Servicio.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_categoria(categoria_id: int) -> List[Servicio]:
        """Obtiene servicios de una categoría"""
        return Servicio.objects.filter(
            id_categoria_id=categoria_id,
            activo=True
        ).select_related('id_categoria')
    
    @staticmethod
    def create(data: dict) -> Servicio:
        """Crea un nuevo servicio"""
        return Servicio.objects.create(**data)
    
    @staticmethod
    def update(servicio: Servicio, data: dict) -> Servicio:
        """Actualiza un servicio existente"""
        for key, value in data.items():
            setattr(servicio, key, value)
        servicio.save()
        return servicio


class ServicioUsuarioTallerRepository:
    """Maneja operaciones de BD para servicios de talleres"""
    
    @staticmethod
    def get_all() -> List[ServicioUsuarioTaller]:
        """Obtiene todos los servicios de talleres"""
        return ServicioUsuarioTaller.objects.select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        ).all()
    
    @staticmethod
    def get_by_id(servicio_usuario_taller_id: int) -> Optional[ServicioUsuarioTaller]:
        """Obtiene un servicio de taller por ID"""
        try:
            return ServicioUsuarioTaller.objects.select_related(
                'id_usuario_taller',
                'id_servicio__id_categoria'
            ).get(id=servicio_usuario_taller_id)
        except ServicioUsuarioTaller.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_taller(taller_id: int, activo: bool = True) -> List[ServicioUsuarioTaller]:
        """Obtiene servicios que ofrece un taller"""
        queryset = ServicioUsuarioTaller.objects.filter(
            id_usuario_taller_id=taller_id
        ).select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        )
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_talleres_por_servicio(servicio_id: int) -> List[ServicioUsuarioTaller]:
        """Obtiene talleres que ofrecen un servicio específico"""
        return ServicioUsuarioTaller.objects.filter(
            id_servicio_id=servicio_id,
            activo=True
        ).select_related(
            'id_usuario_taller',
            'id_servicio__id_categoria'
        )
    
    @staticmethod
    def create(data: dict) -> ServicioUsuarioTaller:
        """Crea una nueva relación servicio-taller"""
        return ServicioUsuarioTaller.objects.create(**data)
    
    @staticmethod
    def update(servicio_taller: ServicioUsuarioTaller, data: dict) -> ServicioUsuarioTaller:
        """Actualiza una relación existente"""
        for key, value in data.items():
            setattr(servicio_taller, key, value)
        servicio_taller.save()
        return servicio_taller
    
    @staticmethod
    def delete(servicio_taller: ServicioUsuarioTaller) -> None:
        """Elimina una relación (soft delete)"""
        servicio_taller.activo = False
        servicio_taller.save()


class ReservacionServicioRepository:
    """Maneja operaciones de BD para reservaciones de servicios"""
    
    @staticmethod
    def get_all() -> List[ReservacionServicio]:
        """Obtiene todas las reservaciones de servicios"""
        return ReservacionServicio.objects.select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        ).all()
    
    @staticmethod
    def get_by_id(reservacion_servicio_id: int) -> Optional[ReservacionServicio]:
        """Obtiene una reservación de servicio por ID"""
        try:
            return ReservacionServicio.objects.select_related(
                'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
                'id_servicio_usuario_taller__id_servicio',
                'id_servicio_usuario_taller__id_usuario_taller',
                'id_estado'
            ).prefetch_related('historial_progreso').get(id=reservacion_servicio_id)
        except ReservacionServicio.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_reservacion_principal(reservacion_principal_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios de una reservación principal"""
        return ReservacionServicio.objects.filter(
            id_reservacion_taller_principal_id=reservacion_principal_id
        ).select_related(
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        )
    
    @staticmethod
    def get_by_taller(taller_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios asignados a un taller"""
        return ReservacionServicio.objects.filter(
            id_servicio_usuario_taller__id_usuario_taller_id=taller_id
        ).select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        ).order_by('-fecha_asignacion')
    
    @staticmethod
    def get_by_estado(estado_clave: str) -> List[ReservacionServicio]:
        """Obtiene reservaciones de servicios por estado"""
        return ReservacionServicio.objects.filter(
            id_estado__clave=estado_clave
        ).select_related(
            'id_reservacion_taller_principal__id_solicitud__id_vehiculo',
            'id_servicio_usuario_taller__id_servicio',
            'id_servicio_usuario_taller__id_usuario_taller',
            'id_estado'
        )
    
    @staticmethod
    def create(data: dict) -> ReservacionServicio:
        """Crea una nueva reservación de servicio"""
        return ReservacionServicio.objects.create(**data)
    
    @staticmethod
    def update(reservacion_servicio: ReservacionServicio, data: dict) -> ReservacionServicio:
        """Actualiza una reservación de servicio"""
        for key, value in data.items():
            setattr(reservacion_servicio, key, value)
        reservacion_servicio.save()
        return reservacion_servicio
    
    @staticmethod
    def actualizar_progreso(reservacion_servicio_id: int, nuevo_progreso: int) -> ReservacionServicio:
        """Actualiza el progreso de un servicio"""
        reservacion = ReservacionServicio.objects.get(id=reservacion_servicio_id)
        reservacion.progreso = nuevo_progreso
        reservacion.save()
        return reservacion
    
    @staticmethod
    def delete(reservacion_servicio: ReservacionServicio) -> None:
        """Elimina una reservación de servicio"""
        reservacion_servicio.delete()


class ReservacionTampBlockRepository:
    """Maneja operaciones de BD para reservaciones en calendarios de talleres"""
    
    @staticmethod
    def get_by_reservacion_servicio(reservacion_servicio_id: int) -> List[ReservacionTampBlock]:
        """Obtiene fechas asignadas a una reservación de servicio"""
        return ReservacionTampBlock.objects.filter(
            id_reservacion_servicio_id=reservacion_servicio_id
        ).select_related('id_tamp_block_taller').order_by('fecha_asignada')
    
    @staticmethod
    def create(data: dict) -> ReservacionTampBlock:
        """Crea una nueva asignación de fecha"""
        return ReservacionTampBlock.objects.create(**data)
    
    @staticmethod
    def delete(reservacion_tamp_block: ReservacionTampBlock) -> None:
        """Elimina una asignación de fecha"""
        reservacion_tamp_block.delete()
```


---

## 📄 ./servicios/repositories/progreso_repository.py

```python
"""
Repository para operaciones de base de datos de Progreso de Servicios
"""
from typing import List, Optional
from servicios.models import ProgresoServicio


class ProgresoServicioRepository:
    """Maneja operaciones de BD para progreso de servicios"""
    
    @staticmethod
    def get_all() -> List[ProgresoServicio]:
        """Obtiene todos los registros de progreso"""
        return ProgresoServicio.objects.select_related(
            'id_reservacion_servicio',
            'actualizado_por'
        ).all()
    
    @staticmethod
    def get_by_id(progreso_id: int) -> Optional[ProgresoServicio]:
        """Obtiene un registro de progreso por ID"""
        try:
            return ProgresoServicio.objects.select_related(
                'id_reservacion_servicio',
                'actualizado_por'
            ).get(id=progreso_id)
        except ProgresoServicio.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_reservacion_servicio(reservacion_servicio_id: int) -> List[ProgresoServicio]:
        """Obtiene el historial de progreso de una reservación de servicio"""
        return ProgresoServicio.objects.filter(
            id_reservacion_servicio_id=reservacion_servicio_id
        ).select_related(
            'id_reservacion_servicio',
            'actualizado_por'
        ).order_by('-fecha')
    
    @staticmethod
    def get_ultimo_progreso(reservacion_servicio_id: int) -> Optional[ProgresoServicio]:
        """Obtiene el último registro de progreso de una reservación"""
        try:
            return ProgresoServicio.objects.filter(
                id_reservacion_servicio_id=reservacion_servicio_id
            ).select_related(
                'id_reservacion_servicio',
                'actualizado_por'
            ).latest('fecha')
        except ProgresoServicio.DoesNotExist:
            return None
    
    @staticmethod
    def create(data: dict) -> ProgresoServicio:
        """Crea un nuevo registro de progreso"""
        return ProgresoServicio.objects.create(**data)
    
    @staticmethod
    def delete(progreso: ProgresoServicio) -> None:
        """Elimina un registro de progreso"""
        progreso.delete()
    
    @staticmethod
    def get_by_taller(taller_id: int) -> List[ProgresoServicio]:
        """Obtiene progreso de servicios actualizados por un taller"""
        return ProgresoServicio.objects.filter(
            actualizado_por_id=taller_id
        ).select_related(
            'id_reservacion_servicio',
            'actualizado_por'
        ).order_by('-fecha')
    
    @staticmethod
    def get_historial_completo(reservacion_principal_id: int) -> List[ProgresoServicio]:
        """Obtiene todo el historial de progreso de una reservación principal"""
        return ProgresoServicio.objects.filter(
            id_reservacion_servicio__id_reservacion_taller_principal_id=reservacion_principal_id
        ).select_related(
            'id_reservacion_servicio__id_servicio_usuario_taller__id_servicio',
            'id_reservacion_servicio__id_servicio_usuario_taller__id_usuario_taller',
            'actualizado_por'
        ).order_by('-fecha')
```


---

## 📄 ./servicios/repositories/__init__.py

```python

```


---

## 📄 ./servicios/services/asignacion_service.py

```python
"""
Service para lógica de negocio de Asignación de Servicios
"""
from typing import List, Dict
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from servicios.models import ReservacionServicio, ReservacionTampBlock
from servicios.repositories.servicio_repository import (
    ReservacionServicioRepository,
    ReservacionTampBlockRepository,
    ServicioUsuarioTallerRepository
)
from core.models import Estado
from core.services.calendario_service import CalendarioTalleresService


class AsignacionServicioService:
    """Maneja la lógica de asignación de servicios a talleres"""
    
    def __init__(self):
        self.repository = ReservacionServicioRepository()
        self.tamp_block_repository = ReservacionTampBlockRepository()
        self.servicio_taller_repository = ServicioUsuarioTallerRepository()
        self.calendario_service = CalendarioTalleresService()
    
    def get_all_reservaciones_servicios(self) -> List[ReservacionServicio]:
        """Obtiene todas las reservaciones de servicios"""
        return self.repository.get_all()
    
    def get_reservacion_servicio_by_id(self, reservacion_servicio_id: int) -> ReservacionServicio:
        """Obtiene una reservación de servicio por ID"""
        reservacion = self.repository.get_by_id(reservacion_servicio_id)
        
        if not reservacion:
            raise ValidationError(
                f"Reservación de servicio con ID {reservacion_servicio_id} no encontrada"
            )
        
        return reservacion
    
    def get_servicios_by_reservacion(self, reservacion_principal_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios de una reservación principal"""
        return self.repository.get_by_reservacion_principal(reservacion_principal_id)
    
    def get_servicios_by_taller(self, taller_id: int) -> List[ReservacionServicio]:
        """Obtiene servicios asignados a un taller"""
        return self.repository.get_by_taller(taller_id)
    
    @transaction.atomic
    def asignar_servicio(self, data: Dict) -> ReservacionServicio:
        """
        Asigna un servicio a un taller
        data: {
            'id_reservacion_taller_principal': int,
            'id_servicio_usuario_taller': int,
            'fechas': [date1, date2, ...]  # Fechas en calendario del taller
        }
        """
        servicio_usuario_taller_id = data.get('id_servicio_usuario_taller')
        
        # Validar que el servicio-taller exista
        servicio_taller = self.servicio_taller_repository.get_by_id(servicio_usuario_taller_id)
        
        if not servicio_taller:
            raise ValidationError("Servicio de taller no encontrado")
        
        # Obtener estado pendiente
        estado_pendiente = Estado.objects.get(
            clave='pendiente',
            tipo=Estado.TIPO_SERVICIO
        )
        
        # Crear reservación de servicio
        reservacion_data = {
            'id_reservacion_taller_principal_id': data.get('id_reservacion_taller_principal'),
            'id_servicio_usuario_taller_id': servicio_usuario_taller_id,
            'id_estado': estado_pendiente,
            'progreso': 0
        }
        
        # Calcular fecha estimada de fin
        if servicio_taller.duracion_dias:
            fecha_inicio = timezone.now()
            reservacion_data['fecha_inicio_real'] = fecha_inicio
            reservacion_data['fecha_fin_estimada'] = fecha_inicio + timedelta(
                days=servicio_taller.duracion_dias
            )
        
        reservacion_servicio = self.repository.create(reservacion_data)
        
        # Asignar fechas en calendario del taller si vienen
        if data.get('fechas'):
            self._asignar_fechas_calendario(
                reservacion_servicio.id,
                servicio_taller.id_usuario_taller_id,
                data['fechas']
            )
        
        return reservacion_servicio
    
    @transaction.atomic
    def _asignar_fechas_calendario(
        self,
        reservacion_servicio_id: int,
        taller_id: int,
        fechas: List
    ) -> List[ReservacionTampBlock]:
        """Asigna fechas del calendario del taller al servicio"""
        asignaciones = []
        
        for fecha in fechas:
            # Buscar bloque disponible en esa fecha
            bloques = self.calendario_service.get_bloques_by_taller(
                taller_id,
                fecha,
                fecha
            )
            
            bloque_disponible = None
            for bloque in bloques:
                if bloque.disponible and bloque.reservados < bloque.capacidad:
                    bloque_disponible = bloque
                    break
            
            if not bloque_disponible:
                raise ValidationError(f"No hay disponibilidad en la fecha {fecha}")
            
            # Reservar el bloque
            self.calendario_service.reservar_bloque(bloque_disponible.id)
            
            # Crear asignación
            asignacion = self.tamp_block_repository.create({
                'id_reservacion_servicio_id': reservacion_servicio_id,
                'id_tamp_block_taller_id': bloque_disponible.id,
                'fecha_asignada': fecha
            })
            asignaciones.append(asignacion)
        
        return asignaciones
    
    def update_reservacion_servicio(
        self,
        reservacion_servicio_id: int,
        data: Dict
    ) -> ReservacionServicio:
        """Actualiza una reservación de servicio"""
        reservacion = self.get_reservacion_servicio_by_id(reservacion_servicio_id)
        return self.repository.update(reservacion, data)
    
    @transaction.atomic
    def iniciar_servicio(self, reservacion_servicio_id: int) -> ReservacionServicio:
        """Inicia un servicio"""
        reservacion = self.get_reservacion_servicio_by_id(reservacion_servicio_id)
        
        estado_en_proceso = Estado.objects.get(
            clave='en_proceso',
            tipo=Estado.TIPO_SERVICIO
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_en_proceso,
            'fecha_inicio_real': timezone.now()
        })
    
    @transaction.atomic
    def completar_servicio(self, reservacion_servicio_id: int) -> ReservacionServicio:
        """Completa un servicio"""
        reservacion = self.get_reservacion_servicio_by_id(reservacion_servicio_id)
        
        estado_completado = Estado.objects.get(
            clave='completada',
            tipo=Estado.TIPO_SERVICIO
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_completado,
            'progreso': 100,
            'fecha_fin_real': timezone.now()
        })
```


---

## 📄 ./servicios/services/progreso_service.py

```python
"""
Service para lógica de negocio de Progreso de Servicios
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from django.db import transaction
from servicios.models import ProgresoServicio
from servicios.repositories.progreso_repository import ProgresoServicioRepository
from servicios.repositories.servicio_repository import ReservacionServicioRepository
from solicitudes.repositories.reservacion_repository import ReservacionRepository


class ProgresoServicioService:
    """Maneja la lógica de negocio para progreso de servicios"""
    
    def __init__(self):
        self.repository = ProgresoServicioRepository()
        self.reservacion_servicio_repository = ReservacionServicioRepository()
        self.reservacion_principal_repository = ReservacionRepository()
    
    def get_historial_by_servicio(self, reservacion_servicio_id: int) -> List[ProgresoServicio]:
        """Obtiene el historial de progreso de un servicio"""
        return self.repository.get_by_reservacion_servicio(reservacion_servicio_id)
    
    def get_ultimo_progreso(self, reservacion_servicio_id: int) -> ProgresoServicio:
        """Obtiene el último progreso de un servicio"""
        return self.repository.get_ultimo_progreso(reservacion_servicio_id)
    
    def get_historial_completo(self, reservacion_principal_id: int) -> List[ProgresoServicio]:
        """Obtiene todo el historial de una reservación principal"""
        return self.repository.get_historial_completo(reservacion_principal_id)
    
    @transaction.atomic
    def actualizar_progreso(self, data: Dict) -> ProgresoServicio:
        """
        Actualiza el progreso de un servicio
        data: {
            'id_reservacion_servicio': int,
            'porcentaje_nuevo': int,
            'dias_estimados': int (opcional),
            'comentario': str (opcional),
            'evidencia_url': str (opcional),
            'actualizado_por': int
        }
        """
        reservacion_servicio_id = data.get('id_reservacion_servicio')
        porcentaje_nuevo = data.get('porcentaje_nuevo')
        
        # Validar porcentaje
        if porcentaje_nuevo < 0 or porcentaje_nuevo > 100:
            raise ValidationError("El porcentaje debe estar entre 0 y 100")
        
        # Obtener reservación de servicio
        reservacion_servicio = self.reservacion_servicio_repository.get_by_id(
            reservacion_servicio_id
        )
        
        if not reservacion_servicio:
            raise ValidationError("Reservación de servicio no encontrada")
        
        # Obtener porcentaje anterior
        porcentaje_anterior = reservacion_servicio.progreso
        
        # Crear registro de progreso
        progreso = self.repository.create({
            'id_reservacion_servicio_id': reservacion_servicio_id,
            'porcentaje_anterior': porcentaje_anterior,
            'porcentaje_nuevo': porcentaje_nuevo,
            'dias_estimados': data.get('dias_estimados'),
            'comentario': data.get('comentario'),
            'evidencia_url': data.get('evidencia_url'),
            'actualizado_por_id': data.get('actualizado_por')
        })
        
        # Actualizar progreso en reservación de servicio
        self.reservacion_servicio_repository.actualizar_progreso(
            reservacion_servicio_id,
            porcentaje_nuevo
        )
        
        # Actualizar días estimados si viene
        if data.get('dias_estimados'):
            self.reservacion_servicio_repository.update(reservacion_servicio, {
                'estado_dias': data['dias_estimados']
            })
        
        # Actualizar avance global de la reservación principal
        self.reservacion_principal_repository.actualizar_avance_global(
            reservacion_servicio.id_reservacion_taller_principal_id
        )
        
        return progreso
    
    def get_progreso_por_taller(self, taller_id: int) -> List[ProgresoServicio]:
        """Obtiene progreso actualizado por un taller"""
        return self.repository.get_by_taller(taller_id)
    
    def get_estadisticas_progreso(self, reservacion_principal_id: int) -> Dict:
        """Obtiene estadísticas de progreso de una reservación"""
        from django.db.models import Avg, Count
        
        servicios = self.reservacion_servicio_repository.get_by_reservacion_principal(
            reservacion_principal_id
        )
        
        total_servicios = servicios.count()
        servicios_completados = servicios.filter(progreso=100).count()
        servicios_en_proceso = servicios.filter(progreso__gt=0, progreso__lt=100).count()
        servicios_pendientes = servicios.filter(progreso=0).count()
        
        promedio_general = servicios.aggregate(
            promedio=Avg('progreso')
        )['promedio'] or 0
        
        return {
            'total_servicios': total_servicios,
            'completados': servicios_completados,
            'en_proceso': servicios_en_proceso,
            'pendientes': servicios_pendientes,
            'promedio_general': round(promedio_general, 2)
        }
```


---

## 📄 ./servicios/services/__init__.py

```python

```


---

## 📄 ./servicios/services/servicio_service.py

```python
"""
Service para lógica de negocio de Servicios
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from servicios.models import Servicio, ServicioUsuarioTaller
from servicios.repositories.servicio_repository import (
    ServicioRepository,
    ServicioUsuarioTallerRepository
)


class ServicioService:
    """Maneja la lógica de negocio para servicios"""
    
    def __init__(self):
        self.repository = ServicioRepository()
    
    def get_all_servicios(self, activo: bool = True) -> List[Servicio]:
        """Obtiene todos los servicios"""
        return self.repository.get_all(activo=activo)
    
    def get_servicio_by_id(self, servicio_id: int) -> Servicio:
        """Obtiene un servicio por ID"""
        servicio = self.repository.get_by_id(servicio_id)
        
        if not servicio:
            raise ValidationError(f"Servicio con ID {servicio_id} no encontrado")
        
        return servicio
    
    def get_servicios_by_categoria(self, categoria_id: int) -> List[Servicio]:
        """Obtiene servicios de una categoría"""
        return self.repository.get_by_categoria(categoria_id)
    
    def create_servicio(self, data: Dict) -> Servicio:
        """Crea un nuevo servicio"""
        return self.repository.create(data)
    
    def update_servicio(self, servicio_id: int, data: Dict) -> Servicio:
        """Actualiza un servicio"""
        servicio = self.get_servicio_by_id(servicio_id)
        return self.repository.update(servicio, data)


class ServicioTallerService:
    """Maneja la lógica de negocio para servicios de talleres"""
    
    def __init__(self):
        self.repository = ServicioUsuarioTallerRepository()
    
    def get_all_servicios_talleres(self) -> List[ServicioUsuarioTaller]:
        """Obtiene todos los servicios de talleres"""
        return self.repository.get_all()
    
    def get_servicio_taller_by_id(self, servicio_taller_id: int) -> ServicioUsuarioTaller:
        """Obtiene un servicio de taller por ID"""
        servicio_taller = self.repository.get_by_id(servicio_taller_id)
        
        if not servicio_taller:
            raise ValidationError(f"Servicio de taller con ID {servicio_taller_id} no encontrado")
        
        return servicio_taller
    
    def get_servicios_by_taller(self, taller_id: int) -> List[ServicioUsuarioTaller]:
        """Obtiene servicios que ofrece un taller"""
        return self.repository.get_by_taller(taller_id)
    
    def get_talleres_por_servicio(self, servicio_id: int) -> List[ServicioUsuarioTaller]:
        """Obtiene talleres que ofrecen un servicio"""
        return self.repository.get_talleres_por_servicio(servicio_id)
    
    def asignar_servicio_a_taller(self, data: Dict) -> ServicioUsuarioTaller:
        """Asigna un servicio a un taller"""
        # Validar que no exista ya
        taller_id = data.get('id_usuario_taller')
        servicio_id = data.get('id_servicio')
        
        existente = ServicioUsuarioTaller.objects.filter(
            id_usuario_taller_id=taller_id,
            id_servicio_id=servicio_id
        ).first()
        
        if existente:
            raise ValidationError("El servicio ya está asignado a este taller")
        
        return self.repository.create(data)
    
    def update_servicio_taller(
        self,
        servicio_taller_id: int,
        data: Dict
    ) -> ServicioUsuarioTaller:
        """Actualiza un servicio de taller"""
        servicio_taller = self.get_servicio_taller_by_id(servicio_taller_id)
        return self.repository.update(servicio_taller, data)
    
    def desactivar_servicio_taller(self, servicio_taller_id: int) -> None:
        """Desactiva un servicio de taller"""
        servicio_taller = self.get_servicio_taller_by_id(servicio_taller_id)
        self.repository.delete(servicio_taller)
```


---

## 📄 ./core/serializers.py

```python
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
```


---

## 📄 ./core/views.py

```python
"""
CORE VIEWS: Usuarios, Vehículos, Calendarios
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import (
    TipoUsuario, Usuario, Estado, Marca, Modelo,
    Vehiculo, TampBlockPrincipal, TampBlockTalleres
)
from .serializers import (
    TipoUsuarioSerializer, UsuarioSerializer, UsuarioCreateSerializer,
    EstadoSerializer, MarcaSerializer, ModeloSerializer, ModeloDetailSerializer,
    VehiculoSerializer, VehiculoDetailSerializer,
    TampBlockPrincipalSerializer, TampBlockTalleresSerializer
)
from .services.usuario_service import UsuarioService
from .services.vehiculo_service import VehiculoService
from .services.calendario_service import CalendarioService


# =====================
# TIPOS Y ESTADOS
# =====================

class TipoUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver tipos de usuario
    """
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer
    permission_classes = [AllowAny]


class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver estados del sistema
    """
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener estados por tipo (solicitud, reservacion, servicio)"""
        tipo = request.query_params.get('tipo')
        if not tipo:
            return Response(
                {'error': 'Parámetro tipo requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estados = Estado.objects.filter(tipo=tipo)
        serializer = self.get_serializer(estados, many=True)
        return Response(serializer.data)


# =====================
# USUARIOS
# =====================

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Filtrar usuarios por tipo"""
        tipo = request.query_params.get('tipo')
        if not tipo:
            return Response(
                {'error': 'Parámetro tipo requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuarios = UsuarioService.obtener_por_tipo(tipo)
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def talleres(self, request):
        """Obtener solo talleres"""
        talleres = UsuarioService.obtener_talleres()
        serializer = self.get_serializer(talleres, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def clientes(self, request):
        """Obtener solo clientes"""
        clientes = UsuarioService.obtener_clientes()
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Activar/desactivar usuario"""
        usuario = self.get_object()
        activo = request.data.get('activo')
        
        if activo is None:
            return Response(
                {'error': 'Campo activo requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario = UsuarioService.cambiar_estado(usuario.id, activo)
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)


# =====================
# VEHÍCULOS
# =====================

class MarcaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de marcas
    """
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Solo marcas activas"""
        marcas = Marca.objects.filter(activo=True)
        serializer = self.get_serializer(marcas, many=True)
        return Response(serializer.data)


class ModeloViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de modelos
    """
    queryset = Modelo.objects.all()
    serializer_class = ModeloSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModeloDetailSerializer
        return ModeloSerializer
    
    @action(detail=False, methods=['get'])
    def por_marca(self, request):
        """Filtrar modelos por marca"""
        marca_id = request.query_params.get('marca_id')
        if not marca_id:
            return Response(
                {'error': 'Parámetro marca_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        modelos = Modelo.objects.filter(id_marca_id=marca_id, activo=True)
        serializer = self.get_serializer(modelos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def atendibles(self, request):
        """Solo modelos atendibles"""
        modelos = Modelo.objects.filter(atendible=True, activo=True)
        serializer = self.get_serializer(modelos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def verificar_atendible(self, request, pk=None):
        """Verificar si un modelo es atendible"""
        modelo = self.get_object()
        ano = request.query_params.get('ano')
        
        if not ano:
            return Response({'atendible': modelo.atendible})
        
        try:
            ano = int(ano)
            atendible = VehiculoService.validar_modelo_atendible(modelo.id, ano)
            return Response({'atendible': atendible})
        except ValueError:
            return Response(
                {'error': 'Año inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )


class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de vehículos
    """
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VehiculoDetailSerializer
        return VehiculoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es cliente, solo ver sus vehículos
        if user.id_tipo.cve == 'cliente':
            queryset = queryset.filter(id_usuario_propietario=user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def mis_vehiculos(self, request):
        """Obtener vehículos del usuario actual"""
        vehiculos = VehiculoService.obtener_por_propietario(request.user.id)
        serializer = self.get_serializer(vehiculos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def validar(self, request, pk=None):
        """Validar si un vehículo puede ser atendido"""
        vehiculo = self.get_object()
        puede_atender, mensaje = VehiculoService.puede_ser_atendido(vehiculo.id)
        
        return Response({
            'puede_atender': puede_atender,
            'mensaje': mensaje
        })


# =====================
# CALENDARIOS
# =====================

class TampBlockPrincipalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para calendario del taller principal
    """
    queryset = TampBlockPrincipal.objects.all()
    serializer_class = TampBlockPrincipalSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Obtener fechas disponibles"""
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio:
            fecha_inicio = datetime.now().date()
        else:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        
        if not fecha_fin:
            fecha_fin = fecha_inicio + timedelta(days=30)
        else:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        fechas = CalendarioService.obtener_fechas_disponibles_principal(
            fecha_inicio, fecha_fin
        )
        serializer = self.get_serializer(fechas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reservar(self, request, pk=None):
        """Reservar un espacio"""
        tamp_block = self.get_object()
        exito = CalendarioService.reservar_espacio_principal(tamp_block.id)
        
        if exito:
            serializer = self.get_serializer(
                TampBlockPrincipal.objects.get(id=tamp_block.id)
            )
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'No hay espacios disponibles'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TampBlockTalleresViewSet(viewsets.ModelViewSet):
    """
    ViewSet para calendario de talleres secundarios
    """
    queryset = TampBlockTalleres.objects.all()
    serializer_class = TampBlockTalleresSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es taller, solo ver su propio calendario
        if user.id_tipo.cve == 'taller':
            queryset = queryset.filter(id_usuario_taller=user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_taller(self, request):
        """Obtener calendario de un taller específico"""
        taller_id = request.query_params.get('taller_id')
        if not taller_id:
            return Response(
                {'error': 'Parámetro taller_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio:
            fecha_inicio = datetime.now().date()
        else:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        
        if not fecha_fin:
            fecha_fin = fecha_inicio + timedelta(days=30)
        else:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        fechas = CalendarioService.obtener_fechas_disponibles_taller(
            int(taller_id), fecha_inicio, fecha_fin
        )
        serializer = self.get_serializer(fechas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mi_calendario(self, request):
        """Obtener calendario del taller actual"""
        if request.user.id_tipo.cve != 'taller':
            return Response(
                {'error': 'Solo talleres pueden acceder a esta función'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        fechas = TampBlockTalleres.objects.filter(
            id_usuario_taller=request.user
        ).order_by('fecha')
        
        serializer = self.get_serializer(fechas, many=True)
        return Response(serializer.data)
```


---

## 📄 ./core/models.py

```python
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
```


---

## 📄 ./core/admin.py

```python
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
```


---

## 📄 ./core/__init__.py

```python

```


---

## 📄 ./core/tests.py

```python
from django.test import TestCase

# Create your tests here.

```


---

## 📄 ./core/apps.py

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

```


---

## 📄 ./core/urls.py

```python
"""
CORE URLS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TipoUsuarioViewSet, EstadoViewSet, UsuarioViewSet,
    MarcaViewSet, ModeloViewSet, VehiculoViewSet,
    TampBlockPrincipalViewSet, TampBlockTalleresViewSet
)

router = DefaultRouter()

# Catálogos
router.register(r'tipos-usuario', TipoUsuarioViewSet, basename='tipo-usuario')
router.register(r'estados', EstadoViewSet, basename='estado')

# Usuarios
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

# Vehículos
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'modelos', ModeloViewSet, basename='modelo')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')

# Calendarios
router.register(r'calendario-principal', TampBlockPrincipalViewSet, basename='calendario-principal')
router.register(r'calendario-talleres', TampBlockTalleresViewSet, basename='calendario-talleres')

urlpatterns = [
    path('', include(router.urls)),
]
```


---

## 📄 ./core/repositories/vehiculo_repository.py

```python
"""
Repository para operaciones de base de datos de Vehículos
"""
from typing import List, Optional
from django.db.models import Q
from core.models import Vehiculo, Marca, Modelo


class VehiculoRepository:
    """Maneja todas las operaciones de BD para vehículos"""
    
    @staticmethod
    def get_all() -> List[Vehiculo]:
        """Obtiene todos los vehículos"""
        return Vehiculo.objects.select_related(
            'id_modelo__id_marca',
            'id_usuario_propietario'
        ).all()
    
    @staticmethod
    def get_by_id(vehiculo_id: int) -> Optional[Vehiculo]:
        """Obtiene un vehículo por ID"""
        try:
            return Vehiculo.objects.select_related(
                'id_modelo__id_marca',
                'id_usuario_propietario'
            ).get(id=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_placa(placa: str) -> Optional[Vehiculo]:
        """Obtiene un vehículo por placa"""
        try:
            return Vehiculo.objects.select_related(
                'id_modelo__id_marca',
                'id_usuario_propietario'
            ).get(placa=placa)
        except Vehiculo.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_propietario(propietario_id: int) -> List[Vehiculo]:
        """Obtiene vehículos de un propietario"""
        return Vehiculo.objects.filter(
            id_usuario_propietario_id=propietario_id
        ).select_related(
            'id_modelo__id_marca',
            'id_usuario_propietario'
        )
    
    @staticmethod
    def create(data: dict) -> Vehiculo:
        """Crea un nuevo vehículo"""
        return Vehiculo.objects.create(**data)
    
    @staticmethod
    def update(vehiculo: Vehiculo, data: dict) -> Vehiculo:
        """Actualiza un vehículo existente"""
        for key, value in data.items():
            setattr(vehiculo, key, value)
        vehiculo.save()
        return vehiculo
    
    @staticmethod
    def delete(vehiculo: Vehiculo) -> None:
        """Elimina un vehículo"""
        vehiculo.delete()
    
    @staticmethod
    def search(query: str) -> List[Vehiculo]:
        """Busca vehículos por placa, VIN o propietario"""
        return Vehiculo.objects.filter(
            Q(placa__icontains=query) |
            Q(vin__icontains=query) |
            Q(id_usuario_propietario__nombre__icontains=query)
        ).select_related(
            'id_modelo__id_marca',
            'id_usuario_propietario'
        )


class ModeloRepository:
    """Maneja operaciones de BD para modelos de vehículos"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[Modelo]:
        """Obtiene todos los modelos"""
        queryset = Modelo.objects.select_related('id_marca')
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(modelo_id: int) -> Optional[Modelo]:
        """Obtiene un modelo por ID"""
        try:
            return Modelo.objects.select_related('id_marca').get(id=modelo_id)
        except Modelo.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_marca(marca_id: int) -> List[Modelo]:
        """Obtiene modelos de una marca"""
        return Modelo.objects.filter(
            id_marca_id=marca_id,
            activo=True
        ).select_related('id_marca')
    
    @staticmethod
    def get_atendibles() -> List[Modelo]:
        """Obtiene modelos atendibles"""
        return Modelo.objects.filter(
            atendible=True,
            activo=True
        ).select_related('id_marca')
    
    @staticmethod
    def is_modelo_atendible(modelo_id: int, ano: int) -> bool:
        """Verifica si un modelo es atendible para un año específico"""
        try:
            modelo = Modelo.objects.get(id=modelo_id)
            
            if not modelo.atendible:
                return False
            
            if modelo.ano_inicio and ano < modelo.ano_inicio:
                return False
            
            if modelo.ano_fin and ano > modelo.ano_fin:
                return False
            
            return True
        except Modelo.DoesNotExist:
            return False


class MarcaRepository:
    """Maneja operaciones de BD para marcas"""
    
    @staticmethod
    def get_all(activo: bool = True) -> List[Marca]:
        """Obtiene todas las marcas"""
        queryset = Marca.objects.all()
        
        if activo:
            queryset = queryset.filter(activo=True)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(marca_id: int) -> Optional[Marca]:
        """Obtiene una marca por ID"""
        try:
            return Marca.objects.get(id=marca_id)
        except Marca.DoesNotExist:
            return None
```


---

## 📄 ./core/repositories/__init__.py

```python

```


---

## 📄 ./core/repositories/usuario_repository.py

```python
"""
Repository para operaciones de base de datos de Usuarios
"""
from typing import List, Optional
from django.db.models import Q
from core.models import Usuario, TipoUsuario


class UsuarioRepository:
    """Maneja todas las operaciones de BD para usuarios"""
    
    @staticmethod
    def get_all(activo: Optional[bool] = None) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        queryset = Usuario.objects.select_related('id_tipo')
        
        if activo is not None:
            queryset = queryset.filter(activo=activo)
        
        return queryset.all()
    
    @staticmethod
    def get_by_id(usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        try:
            return Usuario.objects.select_related('id_tipo').get(id=usuario_id)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email"""
        try:
            return Usuario.objects.select_related('id_tipo').get(email=email)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Usuario]:
        """Obtiene un usuario por username"""
        try:
            return Usuario.objects.select_related('id_tipo').get(username=username)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_tipo(tipo_cve: str) -> List[Usuario]:
        """Obtiene usuarios por tipo"""
        return Usuario.objects.filter(
            id_tipo__cve=tipo_cve,
            activo=True
        ).select_related('id_tipo')
    
    @staticmethod
    def create(data: dict) -> Usuario:
        """Crea un nuevo usuario"""
        return Usuario.objects.create(**data)
    
    @staticmethod
    def update(usuario: Usuario, data: dict) -> Usuario:
        """Actualiza un usuario existente"""
        for key, value in data.items():
            setattr(usuario, key, value)
        usuario.save()
        return usuario
    
    @staticmethod
    def delete(usuario: Usuario) -> None:
        """Elimina un usuario (soft delete)"""
        usuario.activo = False
        usuario.save()
    
    @staticmethod
    def search(query: str) -> List[Usuario]:
        """Busca usuarios por nombre, email o username"""
        return Usuario.objects.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        ).select_related('id_tipo')
    
    @staticmethod
    def get_talleres_activos() -> List[Usuario]:
        """Obtiene todos los talleres activos"""
        return Usuario.objects.filter(
            id_tipo__cve=TipoUsuario.TALLER,
            activo=True
        ).select_related('id_tipo')
    
    @staticmethod
    def get_clientes_activos() -> List[Usuario]:
        """Obtiene todos los clientes activos"""
        return Usuario.objects.filter(
            id_tipo__cve=TipoUsuario.CLIENTE,
            activo=True
        ).select_related('id_tipo')
```


---

## 📄 ./core/repositories/calendario_repository.py

```python
"""
Repository para operaciones de base de datos de Calendarios
"""
from typing import List, Optional
from datetime import date, time
from django.db.models import F, Q
from core.models import TampBlockPrincipal, TampBlockTalleres


class CalendarioPrincipalRepository:
    """Maneja operaciones de BD para calendario del taller principal"""
    
    @staticmethod
    def get_all() -> List[TampBlockPrincipal]:
        """Obtiene todos los bloques del calendario"""
        return TampBlockPrincipal.objects.all()
    
    @staticmethod
    def get_by_id(block_id: int) -> Optional[TampBlockPrincipal]:
        """Obtiene un bloque por ID"""
        try:
            return TampBlockPrincipal.objects.get(id=block_id)
        except TampBlockPrincipal.DoesNotExist:
            return None
    
    @staticmethod
    def get_disponibles(fecha_inicio: date, fecha_fin: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques disponibles en un rango de fechas"""
        return TampBlockPrincipal.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            disponible=True,
            reservados__lt=F('capacidad')
        ).order_by('fecha', 'hora_inicio')
    
    @staticmethod
    def get_by_fecha(fecha: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques de una fecha específica"""
        return TampBlockPrincipal.objects.filter(
            fecha=fecha
        ).order_by('hora_inicio')
    
    @staticmethod
    def create(data: dict) -> TampBlockPrincipal:
        """Crea un nuevo bloque"""
        return TampBlockPrincipal.objects.create(**data)
    
    @staticmethod
    def update(block: TampBlockPrincipal, data: dict) -> TampBlockPrincipal:
        """Actualiza un bloque existente"""
        for key, value in data.items():
            setattr(block, key, value)
        block.save()
        return block
    
    @staticmethod
    def incrementar_reservados(block_id: int) -> bool:
        """Incrementa el contador de reservados"""
        block = TampBlockPrincipal.objects.get(id=block_id)
        
        if block.reservados < block.capacidad:
            block.reservados += 1
            block.save()
            return True
        
        return False
    
    @staticmethod
    def decrementar_reservados(block_id: int) -> None:
        """Decrementa el contador de reservados"""
        block = TampBlockPrincipal.objects.get(id=block_id)
        
        if block.reservados > 0:
            block.reservados -= 1
            block.save()
    
    @staticmethod
    def tiene_disponibilidad(block_id: int) -> bool:
        """Verifica si un bloque tiene disponibilidad"""
        try:
            block = TampBlockPrincipal.objects.get(id=block_id)
            return block.disponible and block.reservados < block.capacidad
        except TampBlockPrincipal.DoesNotExist:
            return False


class CalendarioTalleresRepository:
    """Maneja operaciones de BD para calendarios de talleres secundarios"""
    
    @staticmethod
    def get_all() -> List[TampBlockTalleres]:
        """Obtiene todos los bloques de talleres"""
        return TampBlockTalleres.objects.select_related('id_usuario_taller').all()
    
    @staticmethod
    def get_by_id(block_id: int) -> Optional[TampBlockTalleres]:
        """Obtiene un bloque por ID"""
        try:
            return TampBlockTalleres.objects.select_related('id_usuario_taller').get(id=block_id)
        except TampBlockTalleres.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_taller(taller_id: int, fecha_inicio: date = None, fecha_fin: date = None) -> List[TampBlockTalleres]:
        """Obtiene bloques de un taller específico"""
        queryset = TampBlockTalleres.objects.filter(id_usuario_taller_id=taller_id)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        return queryset.order_by('fecha')
    
    @staticmethod
    def get_disponibles_taller(taller_id: int, fecha_inicio: date, fecha_fin: date) -> List[TampBlockTalleres]:
        """Obtiene bloques disponibles de un taller"""
        return TampBlockTalleres.objects.filter(
            id_usuario_taller_id=taller_id,
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            disponible=True,
            reservados__lt=F('capacidad')
        ).order_by('fecha')
    
    @staticmethod
    def create(data: dict) -> TampBlockTalleres:
        """Crea un nuevo bloque de taller"""
        return TampBlockTalleres.objects.create(**data)
    
    @staticmethod
    def update(block: TampBlockTalleres, data: dict) -> TampBlockTalleres:
        """Actualiza un bloque existente"""
        for key, value in data.items():
            setattr(block, key, value)
        block.save()
        return block
    
    @staticmethod
    def incrementar_reservados(block_id: int) -> bool:
        """Incrementa el contador de reservados"""
        block = TampBlockTalleres.objects.get(id=block_id)
        
        if block.reservados < block.capacidad:
            block.reservados += 1
            block.save()
            return True
        
        return False
    
    @staticmethod
    def decrementar_reservados(block_id: int) -> None:
        """Decrementa el contador de reservados"""
        block = TampBlockTalleres.objects.get(id=block_id)
        
        if block.reservados > 0:
            block.reservados -= 1
            block.save()
    
    @staticmethod
    def tiene_disponibilidad(block_id: int) -> bool:
        """Verifica si un bloque tiene disponibilidad"""
        try:
            block = TampBlockTalleres.objects.get(id=block_id)
            return block.disponible and block.reservados < block.capacidad
        except TampBlockTalleres.DoesNotExist:
            return False
```


---

## 📄 ./core/services/vehiculo_service.py

```python
"""
Service para lógica de negocio de Vehículos
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from core.models import Vehiculo, Modelo, Marca
from core.repositories.vehiculo_repository import (
    VehiculoRepository, ModeloRepository, MarcaRepository
)


class VehiculoService:
    """Maneja la lógica de negocio para vehículos"""
    
    def __init__(self):
        self.repository = VehiculoRepository()
        self.modelo_repository = ModeloRepository()
    
    def get_all_vehiculos(self) -> List[Vehiculo]:
        """Obtiene todos los vehículos"""
        return self.repository.get_all()
    
    def get_vehiculo_by_id(self, vehiculo_id: int) -> Vehiculo:
        """Obtiene un vehículo por ID"""
        vehiculo = self.repository.get_by_id(vehiculo_id)
        
        if not vehiculo:
            raise ValidationError(f"Vehículo con ID {vehiculo_id} no encontrado")
        
        return vehiculo
    
    def get_vehiculo_by_placa(self, placa: str) -> Vehiculo:
        """Obtiene un vehículo por placa"""
        vehiculo = self.repository.get_by_placa(placa)
        
        if not vehiculo:
            raise ValidationError(f"Vehículo con placa {placa} no encontrado")
        
        return vehiculo
    
    def get_vehiculos_by_propietario(self, propietario_id: int) -> List[Vehiculo]:
        """Obtiene vehículos de un propietario"""
        return self.repository.get_by_propietario(propietario_id)
    
    def create_vehiculo(self, data: Dict) -> Vehiculo:
        """Crea un nuevo vehículo"""
        # Validar que la placa no exista
        if self.repository.get_by_placa(data.get('placa')):
            raise ValidationError("La placa ya está registrada")
        
        # Validar que el modelo sea atendible
        modelo_id = data.get('id_modelo')
        ano = data.get('ano')
        
        if modelo_id and ano:
            if not self.modelo_repository.is_modelo_atendible(modelo_id, ano):
                raise ValidationError(
                    "El modelo y año del vehículo no pueden ser atendidos en el taller"
                )
        
        return self.repository.create(data)
    
    def update_vehiculo(self, vehiculo_id: int, data: Dict) -> Vehiculo:
        """Actualiza un vehículo existente"""
        vehiculo = self.get_vehiculo_by_id(vehiculo_id)
        
        # Validar placa si se está actualizando
        if 'placa' in data and data['placa'] != vehiculo.placa:
            if self.repository.get_by_placa(data['placa']):
                raise ValidationError("La placa ya está registrada")
        
        # Validar modelo atendible si se actualiza
        if 'id_modelo' in data or 'ano' in data:
            modelo_id = data.get('id_modelo', vehiculo.id_modelo_id)
            ano = data.get('ano', vehiculo.ano)
            
            if modelo_id and ano:
                if not self.modelo_repository.is_modelo_atendible(modelo_id, ano):
                    raise ValidationError(
                        "El modelo y año del vehículo no pueden ser atendidos en el taller"
                    )
        
        return self.repository.update(vehiculo, data)
    
    def delete_vehiculo(self, vehiculo_id: int) -> None:
        """Elimina un vehículo"""
        vehiculo = self.get_vehiculo_by_id(vehiculo_id)
        self.repository.delete(vehiculo)
    
    def search_vehiculos(self, query: str) -> List[Vehiculo]:
        """Busca vehículos"""
        return self.repository.search(query)
    
    def validar_vehiculo_atendible(self, vehiculo_id: int) -> bool:
        """Valida si un vehículo puede ser atendido"""
        vehiculo = self.get_vehiculo_by_id(vehiculo_id)
        
        return self.modelo_repository.is_modelo_atendible(
            vehiculo.id_modelo_id,
            vehiculo.ano
        )
    
    def get_estadisticas_vehiculos(self) -> Dict:
        """Obtiene estadísticas de vehículos"""
        from django.db.models import Count
        
        total = Vehiculo.objects.count()
        
        por_marca = Vehiculo.objects.values(
            'id_modelo__id_marca__nombre'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        return {
            'total': total,
            'por_marca': list(por_marca)
        }


class ModeloService:
    """Maneja la lógica de negocio para modelos"""
    
    def __init__(self):
        self.repository = ModeloRepository()
    
    def get_all_modelos(self, activo: bool = True) -> List[Modelo]:
        """Obtiene todos los modelos"""
        return self.repository.get_all(activo=activo)
    
    def get_modelo_by_id(self, modelo_id: int) -> Modelo:
        """Obtiene un modelo por ID"""
        modelo = self.repository.get_by_id(modelo_id)
        
        if not modelo:
            raise ValidationError(f"Modelo con ID {modelo_id} no encontrado")
        
        return modelo
    
    def get_modelos_by_marca(self, marca_id: int) -> List[Modelo]:
        """Obtiene modelos de una marca"""
        return self.repository.get_by_marca(marca_id)
    
    def get_modelos_atendibles(self) -> List[Modelo]:
        """Obtiene modelos atendibles"""
        return self.repository.get_atendibles()


class MarcaService:
    """Maneja la lógica de negocio para marcas"""
    
    def __init__(self):
        self.repository = MarcaRepository()
    
    def get_all_marcas(self, activo: bool = True) -> List[Marca]:
        """Obtiene todas las marcas"""
        return self.repository.get_all(activo=activo)
    
    def get_marca_by_id(self, marca_id: int) -> Marca:
        """Obtiene una marca por ID"""
        marca = self.repository.get_by_id(marca_id)
        
        if not marca:
            raise ValidationError(f"Marca con ID {marca_id} no encontrada")
        
        return marca
```


---

## 📄 ./core/services/__init__.py

```python

```


---

## 📄 ./core/services/calendario_service.py

```python
"""
Service para lógica de negocio de Calendarios
"""
from typing import List, Dict
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from core.models import TampBlockPrincipal, TampBlockTalleres
from core.repositories.calendario_repository import (
    CalendarioPrincipalRepository,
    CalendarioTalleresRepository
)


class CalendarioPrincipalService:
    """Maneja la lógica de negocio para calendario del taller principal"""
    
    def __init__(self):
        self.repository = CalendarioPrincipalRepository()
    
    def get_all_bloques(self) -> List[TampBlockPrincipal]:
        """Obtiene todos los bloques del calendario"""
        return self.repository.get_all()
    
    def get_bloque_by_id(self, bloque_id: int) -> TampBlockPrincipal:
        """Obtiene un bloque por ID"""
        bloque = self.repository.get_by_id(bloque_id)
        
        if not bloque:
            raise ValidationError(f"Bloque con ID {bloque_id} no encontrado")
        
        return bloque
    
    def get_bloques_disponibles(self, fecha_inicio: date, fecha_fin: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques disponibles en un rango de fechas"""
        if fecha_inicio > fecha_fin:
            raise ValidationError("La fecha de inicio debe ser menor a la fecha fin")
        
        return self.repository.get_disponibles(fecha_inicio, fecha_fin)
    
    def get_bloques_by_fecha(self, fecha: date) -> List[TampBlockPrincipal]:
        """Obtiene bloques de una fecha específica"""
        return self.repository.get_by_fecha(fecha)
    
    def create_bloque(self, data: Dict) -> TampBlockPrincipal:
        """Crea un nuevo bloque"""
        # Validar que hora_inicio < hora_fin
        if data.get('hora_inicio') >= data.get('hora_fin'):
            raise ValidationError("La hora de inicio debe ser menor a la hora fin")
        
        return self.repository.create(data)
    
    def update_bloque(self, bloque_id: int, data: Dict) -> TampBlockPrincipal:
        """Actualiza un bloque existente"""
        bloque = self.get_bloque_by_id(bloque_id)
        
        # Validar horas si se están actualizando
        hora_inicio = data.get('hora_inicio', bloque.hora_inicio)
        hora_fin = data.get('hora_fin', bloque.hora_fin)
        
        if hora_inicio >= hora_fin:
            raise ValidationError("La hora de inicio debe ser menor a la hora fin")
        
        return self.repository.update(bloque, data)
    
    def reservar_bloque(self, bloque_id: int) -> TampBlockPrincipal:
        """Reserva un espacio en el bloque"""
        bloque = self.get_bloque_by_id(bloque_id)
        
        if not bloque.disponible:
            raise ValidationError("El bloque no está disponible")
        
        if bloque.reservados >= bloque.capacidad:
            raise ValidationError("El bloque ya alcanzó su capacidad máxima")
        
        success = self.repository.incrementar_reservados(bloque_id)
        
        if not success:
            raise ValidationError("No se pudo reservar el bloque")
        
        return self.get_bloque_by_id(bloque_id)
    
    def liberar_bloque(self, bloque_id: int) -> TampBlockPrincipal:
        """Libera un espacio en el bloque"""
        self.repository.decrementar_reservados(bloque_id)
        return self.get_bloque_by_id(bloque_id)
    
    def generar_bloques_semana(self, fecha_inicio: date, horas: List[Dict]) -> List[TampBlockPrincipal]:
        """
        Genera bloques para una semana completa
        horas: [{'hora_inicio': '09:00', 'hora_fin': '10:00', 'capacidad': 2}, ...]
        """
        bloques_creados = []
        
        with transaction.atomic():
            for i in range(7):  # 7 días
                fecha = fecha_inicio + timedelta(days=i)
                
                for hora_config in horas:
                    bloque = self.repository.create({
                        'fecha': fecha,
                        'hora_inicio': hora_config['hora_inicio'],
                        'hora_fin': hora_config['hora_fin'],
                        'capacidad': hora_config.get('capacidad', 1),
                        'disponible': True,
                        'reservados': 0
                    })
                    bloques_creados.append(bloque)
        
        return bloques_creados


class CalendarioTalleresService:
    """Maneja la lógica de negocio para calendarios de talleres secundarios"""
    
    def __init__(self):
        self.repository = CalendarioTalleresRepository()
    
    def get_all_bloques(self) -> List[TampBlockTalleres]:
        """Obtiene todos los bloques de talleres"""
        return self.repository.get_all()
    
    def get_bloque_by_id(self, bloque_id: int) -> TampBlockTalleres:
        """Obtiene un bloque por ID"""
        bloque = self.repository.get_by_id(bloque_id)
        
        if not bloque:
            raise ValidationError(f"Bloque con ID {bloque_id} no encontrado")
        
        return bloque
    
    def get_bloques_by_taller(
        self,
        taller_id: int,
        fecha_inicio: date = None,
        fecha_fin: date = None
    ) -> List[TampBlockTalleres]:
        """Obtiene bloques de un taller específico"""
        return self.repository.get_by_taller(taller_id, fecha_inicio, fecha_fin)
    
    def get_bloques_disponibles_taller(
        self,
        taller_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[TampBlockTalleres]:
        """Obtiene bloques disponibles de un taller"""
        if fecha_inicio > fecha_fin:
            raise ValidationError("La fecha de inicio debe ser menor a la fecha fin")
        
        return self.repository.get_disponibles_taller(taller_id, fecha_inicio, fecha_fin)
    
    def create_bloque(self, data: Dict) -> TampBlockTalleres:
        """Crea un nuevo bloque de taller"""
        return self.repository.create(data)
    
    def update_bloque(self, bloque_id: int, data: Dict) -> TampBlockTalleres:
        """Actualiza un bloque existente"""
        bloque = self.get_bloque_by_id(bloque_id)
        return self.repository.update(bloque, data)
    
    def reservar_bloque(self, bloque_id: int) -> TampBlockTalleres:
        """Reserva un espacio en el bloque"""
        bloque = self.get_bloque_by_id(bloque_id)
        
        if not bloque.disponible:
            raise ValidationError("El bloque no está disponible")
        
        if bloque.reservados >= bloque.capacidad:
            raise ValidationError("El bloque ya alcanzó su capacidad máxima")
        
        success = self.repository.incrementar_reservados(bloque_id)
        
        if not success:
            raise ValidationError("No se pudo reservar el bloque")
        
        return self.get_bloque_by_id(bloque_id)
    
    def liberar_bloque(self, bloque_id: int) -> TampBlockTalleres:
        """Libera un espacio en el bloque"""
        self.repository.decrementar_reservados(bloque_id)
        return self.get_bloque_by_id(bloque_id)
    
    def generar_bloques_mes(self, taller_id: int, fecha_inicio: date) -> List[TampBlockTalleres]:
        """Genera bloques disponibles para un mes"""
        bloques_creados = []
        
        with transaction.atomic():
            for i in range(30):  # 30 días
                fecha = fecha_inicio + timedelta(days=i)
                
                # Evitar fines de semana (opcional)
                if fecha.weekday() >= 5:  # 5=Sábado, 6=Domingo
                    continue
                
                bloque = self.repository.create({
                    'id_usuario_taller_id': taller_id,
                    'fecha': fecha,
                    'disponible': True,
                    'capacidad': 1,
                    'reservados': 0
                })
                bloques_creados.append(bloque)
        
        return bloques_creados
```


---

## 📄 ./core/services/usuario_service.py

```python
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
```


---

## 📄 ./middlewares/error_handler_middleware.py

```python
"""
Middleware para manejo centralizado de errores
"""
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
from rest_framework.exceptions import APIException
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(MiddlewareMixin):
    """Middleware para manejo global de errores"""
    
    def process_exception(self, request, exception):
        """Maneja diferentes tipos de excepciones"""
        
        # Errores de validación
        if isinstance(exception, ValidationError):
            return JsonResponse(
                {
                    'error': 'Error de validación',
                    'details': exception.message_dict if hasattr(exception, 'message_dict') else str(exception)
                },
                status=400
            )
        
        # Errores de integridad de BD
        if isinstance(exception, IntegrityError):
            return JsonResponse(
                {
                    'error': 'Error de integridad de datos',
                    'message': 'El registro viola restricciones de la base de datos'
                },
                status=400
            )
        
        # Errores de permisos
        if isinstance(exception, PermissionDenied):
            return JsonResponse(
                {
                    'error': 'Permiso denegado',
                    'message': str(exception)
                },
                status=403
            )
        
        # Errores de DRF
        if isinstance(exception, APIException):
            return JsonResponse(
                {
                    'error': exception.default_detail,
                    'details': exception.detail if hasattr(exception, 'detail') else None
                },
                status=exception.status_code
            )
        
        # Errores genéricos
        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)
        
        return JsonResponse(
            {
                'error': 'Error interno del servidor',
                'message': 'Ha ocurrido un error inesperado'
            },
            status=500
        )
```


---

## 📄 ./middlewares/logging_middleware.py

```python
"""
Middleware para logging de requests y responses
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware para registrar todas las peticiones HTTP"""
    
    def process_request(self, request):
        """Registra información del request"""
        request.start_time = time.time()
        
        logger.info(
            f"Request: {request.method} {request.path} "
            f"| User: {request.user if request.user.is_authenticated else 'Anonymous'} "
            f"| IP: {self.get_client_ip(request)}"
        )
        
        return None
    
    def process_response(self, request, response):
        """Registra información del response"""
        
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger.info(
                f"Response: {request.method} {request.path} "
                f"| Status: {response.status_code} "
                f"| Duration: {duration:.2f}s"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIErrorLoggingMiddleware(MiddlewareMixin):
    """Middleware para registrar errores de la API"""
    
    def process_exception(self, request, exception):
        """Registra excepciones no manejadas"""
        
        logger.error(
            f"Exception: {request.method} {request.path} "
            f"| User: {request.user if request.user.is_authenticated else 'Anonymous'} "
            f"| Error: {str(exception)}",
            exc_info=True
        )
        
        return None
```


---

## 📄 ./middlewares/auth_middleware.py

```python
"""
Middleware de autenticación y permisos personalizados
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from core.models import TipoUsuario


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """Middleware para control de acceso basado en roles"""
    
    # Rutas públicas que no requieren autenticación
    PUBLIC_ROUTES = [
        '/admin/',
        '/api/core/auth/login/',
        '/api/core/auth/register/',
    ]
    
    # Rutas por tipo de usuario
    ROLE_ROUTES = {
        TipoUsuario.ADMINISTRADOR: [
            '/api/core/',
            '/api/solicitudes/',
            '/api/servicios/',
        ],
        TipoUsuario.AGENTE: [
            '/api/solicitudes/',
            '/api/servicios/',
        ],
        TipoUsuario.TALLER: [
            '/api/servicios/mis-servicios/',
            '/api/servicios/actualizar-progreso/',
            '/api/servicios/calendario/',
        ],
        TipoUsuario.CLIENTE: [
            '/api/solicitudes/mis-solicitudes/',
            '/api/core/vehiculos/',
        ],
    }
    
    def process_request(self, request):
        """Procesa cada request verificando permisos"""
        
        # Permitir rutas públicas
        if any(request.path.startswith(route) for route in self.PUBLIC_ROUTES):
            return None
        
        # Verificar autenticación
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Autenticación requerida'},
                status=401
            )
        
        # Verificar si es superusuario
        if request.user.is_superuser:
            return None
        
        # Verificar permisos basados en rol
        user_role = request.user.id_tipo.cve
        allowed_routes = self.ROLE_ROUTES.get(user_role, [])
        
        # Verificar si la ruta está permitida para el rol
        if not any(request.path.startswith(route) for route in allowed_routes):
            return JsonResponse(
                {
                    'error': 'No tiene permisos para acceder a este recurso',
                    'role': user_role
                },
                status=403
            )
        
        return None


class UserActiveCheckMiddleware(MiddlewareMixin):
    """Middleware para verificar que el usuario esté activo"""
    
    def process_request(self, request):
        """Verifica si el usuario está activo"""
        
        if request.user.is_authenticated:
            if hasattr(request.user, 'activo') and not request.user.activo:
                return JsonResponse(
                    {'error': 'Usuario inactivo. Contacte al administrador.'},
                    status=403
                )
        
        return None
```


---

## 📄 ./solicitudes/serializers.py

```python

```


---

## 📄 ./solicitudes/views.py

```python
from django.shortcuts import render

# Create your views here.

```


---

## 📄 ./solicitudes/models.py

```python
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
```


---

## 📄 ./solicitudes/admin.py

```python
from django.contrib import admin

# Register your models here.

```


---

## 📄 ./solicitudes/__init__.py

```python

```


---

## 📄 ./solicitudes/tests.py

```python
from django.test import TestCase

# Create your tests here.

```


---

## 📄 ./solicitudes/apps.py

```python
from django.apps import AppConfig


class SolicitudesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solicitudes'

```


---

## 📄 ./solicitudes/repositories/solicitud_repository.py

```python
"""
Repository para operaciones de base de datos de Solicitudes
"""
from typing import List, Optional
from django.db.models import Q
from solicitudes.models import Solicitud, DetalleSolicitud
from core.models import Estado


class SolicitudRepository:
    """Maneja todas las operaciones de BD para solicitudes"""
    
    @staticmethod
    def get_all() -> List[Solicitud]:
        """Obtiene todas las solicitudes"""
        return Solicitud.objects.select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        ).all()
    
    @staticmethod
    def get_by_id(solicitud_id: int) -> Optional[Solicitud]:
        """Obtiene una solicitud por ID"""
        try:
            return Solicitud.objects.select_related(
                'id_vehiculo__id_modelo__id_marca',
                'id_usuario',
                'id_estado',
                'aprobado_por'
            ).get(id=solicitud_id)
        except Solicitud.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_usuario(usuario_id: int) -> List[Solicitud]:
        """Obtiene solicitudes de un usuario específico"""
        return Solicitud.objects.filter(
            id_usuario_id=usuario_id
        ).select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        ).order_by('-fecha_creacion')
    
    @staticmethod
    def get_by_estado(estado_clave: str) -> List[Solicitud]:
        """Obtiene solicitudes por estado"""
        return Solicitud.objects.filter(
            id_estado__clave=estado_clave
        ).select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        ).order_by('-fecha_creacion')
    
    @staticmethod
    def get_pendientes() -> List[Solicitud]:
        """Obtiene solicitudes pendientes"""
        return SolicitudRepository.get_by_estado('pendiente')
    
    @staticmethod
    def get_aprobadas() -> List[Solicitud]:
        """Obtiene solicitudes aprobadas"""
        return SolicitudRepository.get_by_estado('aprobada')
    
    @staticmethod
    def get_rechazadas() -> List[Solicitud]:
        """Obtiene solicitudes rechazadas"""
        return SolicitudRepository.get_by_estado('rechazada')
    
    @staticmethod
    def create(data: dict) -> Solicitud:
        """Crea una nueva solicitud"""
        return Solicitud.objects.create(**data)
    
    @staticmethod
    def update(solicitud: Solicitud, data: dict) -> Solicitud:
        """Actualiza una solicitud existente"""
        for key, value in data.items():
            setattr(solicitud, key, value)
        solicitud.save()
        return solicitud
    
    @staticmethod
    def aprobar(solicitud_id: int, aprobado_por_id: int, estado_aprobada: Estado) -> Solicitud:
        """Aprueba una solicitud"""
        from django.utils import timezone
        
        solicitud = Solicitud.objects.get(id=solicitud_id)
        solicitud.id_estado = estado_aprobada
        solicitud.aprobado_por_id = aprobado_por_id
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        return solicitud
    
    @staticmethod
    def rechazar(solicitud_id: int, motivo: str, rechazado_por_id: int, estado_rechazada: Estado) -> Solicitud:
        """Rechaza una solicitud"""
        from django.utils import timezone
        
        solicitud = Solicitud.objects.get(id=solicitud_id)
        solicitud.id_estado = estado_rechazada
        solicitud.motivo_rechazo = motivo
        solicitud.aprobado_por_id = rechazado_por_id
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        return solicitud
    
    @staticmethod
    def delete(solicitud: Solicitud) -> None:
        """Elimina una solicitud"""
        solicitud.delete()
    
    @staticmethod
    def search(query: str) -> List[Solicitud]:
        """Busca solicitudes por placa, cliente o referencia"""
        return Solicitud.objects.filter(
            Q(id_vehiculo__placa__icontains=query) |
            Q(id_usuario__nombre__icontains=query) |
            Q(referencia_externa__icontains=query)
        ).select_related(
            'id_vehiculo__id_modelo__id_marca',
            'id_usuario',
            'id_estado',
            'aprobado_por'
        )
    
    @staticmethod
    def tiene_solicitud_pendiente(vehiculo_id: int) -> bool:
        """Verifica si un vehículo tiene solicitudes pendientes"""
        return Solicitud.objects.filter(
            id_vehiculo_id=vehiculo_id,
            id_estado__clave='pendiente'
        ).exists()
    
    @staticmethod
    def tiene_solicitud_aprobada_sin_reserva(vehiculo_id: int) -> bool:
        """Verifica si un vehículo tiene solicitudes aprobadas sin reservación"""
        return Solicitud.objects.filter(
            id_vehiculo_id=vehiculo_id,
            id_estado__clave='aprobada',
            reservacion__isnull=True
        ).exists()


class DetalleSolicitudRepository:
    """Maneja operaciones de BD para detalles de solicitudes"""
    
    @staticmethod
    def get_by_solicitud(solicitud_id: int) -> Optional[DetalleSolicitud]:
        """Obtiene el detalle de una solicitud"""
        try:
            return DetalleSolicitud.objects.get(id_solicitud_id=solicitud_id)
        except DetalleSolicitud.DoesNotExist:
            return None
    
    @staticmethod
    def create(data: dict) -> DetalleSolicitud:
        """Crea un nuevo detalle de solicitud"""
        return DetalleSolicitud.objects.create(**data)
    
    @staticmethod
    def update(detalle: DetalleSolicitud, data: dict) -> DetalleSolicitud:
        """Actualiza un detalle existente"""
        for key, value in data.items():
            setattr(detalle, key, value)
        detalle.save()
        return detalle
    
    @staticmethod
    def delete(detalle: DetalleSolicitud) -> None:
        """Elimina un detalle"""
        detalle.delete()
```


---

## 📄 ./solicitudes/repositories/__init__.py

```python

```


---

## 📄 ./solicitudes/repositories/reservacion_repository.py

```python
"""
Repository para operaciones de base de datos de Reservaciones
"""
from typing import List, Optional
from datetime import date
from django.db.models import Q, Prefetch
from solicitudes.models import ReservacionTallerPrincipal


class ReservacionRepository:
    """Maneja todas las operaciones de BD para reservaciones"""
    
    @staticmethod
    def get_all() -> List[ReservacionTallerPrincipal]:
        """Obtiene todas las reservaciones"""
        return ReservacionTallerPrincipal.objects.select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).all()
    
    @staticmethod
    def get_by_id(reservacion_id: int) -> Optional[ReservacionTallerPrincipal]:
        """Obtiene una reservación por ID"""
        try:
            return ReservacionTallerPrincipal.objects.select_related(
                'id_solicitud__id_vehiculo__id_modelo__id_marca',
                'id_solicitud__id_usuario',
                'id_tamp_block',
                'id_estado',
                'atendido_por'
            ).prefetch_related('servicios_asignados').get(id=reservacion_id)
        except ReservacionTallerPrincipal.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_solicitud(solicitud_id: int) -> Optional[ReservacionTallerPrincipal]:
        """Obtiene reservación por solicitud"""
        try:
            return ReservacionTallerPrincipal.objects.select_related(
                'id_solicitud__id_vehiculo__id_modelo__id_marca',
                'id_solicitud__id_usuario',
                'id_tamp_block',
                'id_estado',
                'atendido_por'
            ).get(id_solicitud_id=solicitud_id)
        except ReservacionTallerPrincipal.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_cliente(cliente_id: int) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de un cliente"""
        return ReservacionTallerPrincipal.objects.filter(
            id_solicitud__id_usuario_id=cliente_id
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('-creado_at')
    
    @staticmethod
    def get_by_fecha(fecha: date) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de una fecha específica"""
        return ReservacionTallerPrincipal.objects.filter(
            id_tamp_block__fecha=fecha
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('id_tamp_block__hora_inicio')
    
    @staticmethod
    def get_by_estado(estado_clave: str) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones por estado"""
        return ReservacionTallerPrincipal.objects.filter(
            id_estado__clave=estado_clave
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('-creado_at')
    
    @staticmethod
    def get_pendientes() -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones pendientes"""
        return ReservacionRepository.get_by_estado('pendiente')
    
    @staticmethod
    def get_en_proceso() -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones en proceso"""
        return ReservacionRepository.get_by_estado('en_proceso')
    
    @staticmethod
    def get_completadas() -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones completadas"""
        return ReservacionRepository.get_by_estado('completada')
    
    @staticmethod
    def create(data: dict) -> ReservacionTallerPrincipal:
        """Crea una nueva reservación"""
        return ReservacionTallerPrincipal.objects.create(**data)
    
    @staticmethod
    def update(reservacion: ReservacionTallerPrincipal, data: dict) -> ReservacionTallerPrincipal:
        """Actualiza una reservación existente"""
        for key, value in data.items():
            setattr(reservacion, key, value)
        reservacion.save()
        return reservacion
    
    @staticmethod
    def actualizar_avance_global(reservacion_id: int) -> ReservacionTallerPrincipal:
        """Actualiza el avance global basado en los servicios asignados"""
        from django.db.models import Avg
        
        reservacion = ReservacionTallerPrincipal.objects.get(id=reservacion_id)
        
        # Calcular promedio de progreso de todos los servicios
        promedio = reservacion.servicios_asignados.aggregate(
            promedio=Avg('progreso')
        )['promedio'] or 0
        
        reservacion.avance_global = int(promedio)
        
        # Actualizar estado global
        if promedio == 0:
            reservacion.estado_global = 'pendiente'
        elif promedio < 100:
            reservacion.estado_global = 'en_proceso'
        else:
            reservacion.estado_global = 'completado'
        
        reservacion.save()
        return reservacion
    
    @staticmethod
    def delete(reservacion: ReservacionTallerPrincipal) -> None:
        """Elimina una reservación"""
        reservacion.delete()
    
    @staticmethod
    def search(query: str) -> List[ReservacionTallerPrincipal]:
        """Busca reservaciones por placa o cliente"""
        return ReservacionTallerPrincipal.objects.filter(
            Q(id_solicitud__id_vehiculo__placa__icontains=query) |
            Q(id_solicitud__id_usuario__nombre__icontains=query)
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        )
    
    @staticmethod
    def get_proximas(dias: int = 7) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones próximas en X días"""
        from django.utils import timezone
        from datetime import timedelta
        
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        
        return ReservacionTallerPrincipal.objects.filter(
            id_tamp_block__fecha__lte=fecha_limite,
            id_tamp_block__fecha__gte=timezone.now().date()
        ).select_related(
            'id_solicitud__id_vehiculo__id_modelo__id_marca',
            'id_solicitud__id_usuario',
            'id_tamp_block',
            'id_estado',
            'atendido_por'
        ).order_by('id_tamp_block__fecha', 'id_tamp_block__hora_inicio')
```


---

## 📄 ./solicitudes/services/solicitud_service.py

```python
"""
Service para lógica de negocio de Solicitudes
"""
from typing import List, Dict
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from solicitudes.models import Solicitud, DetalleSolicitud
from solicitudes.repositories.solicitud_repository import (
    SolicitudRepository, DetalleSolicitudRepository
)
from core.models import Estado
from core.repositories.vehiculo_repository import ModeloRepository


class SolicitudService:
    """Maneja la lógica de negocio para solicitudes"""
    
    def __init__(self):
        self.repository = SolicitudRepository()
        self.detalle_repository = DetalleSolicitudRepository()
        self.modelo_repository = ModeloRepository()
    
    def get_all_solicitudes(self) -> List[Solicitud]:
        """Obtiene todas las solicitudes"""
        return self.repository.get_all()
    
    def get_solicitud_by_id(self, solicitud_id: int) -> Solicitud:
        """Obtiene una solicitud por ID"""
        solicitud = self.repository.get_by_id(solicitud_id)
        
        if not solicitud:
            raise ValidationError(f"Solicitud con ID {solicitud_id} no encontrada")
        
        return solicitud
    
    def get_solicitudes_by_usuario(self, usuario_id: int) -> List[Solicitud]:
        """Obtiene solicitudes de un usuario"""
        return self.repository.get_by_usuario(usuario_id)
    
    def get_solicitudes_pendientes(self) -> List[Solicitud]:
        """Obtiene solicitudes pendientes"""
        return self.repository.get_pendientes()
    
    def get_solicitudes_aprobadas(self) -> List[Solicitud]:
        """Obtiene solicitudes aprobadas"""
        return self.repository.get_aprobadas()
    
    def get_solicitudes_rechazadas(self) -> List[Solicitud]:
        """Obtiene solicitudes rechazadas"""
        return self.repository.get_rechazadas()
    
    @transaction.atomic
    def create_solicitud(self, data: Dict) -> Solicitud:
        """Crea una nueva solicitud"""
        vehiculo_id = data.get('id_vehiculo')
        
        # Validar que el vehículo pueda ser atendido
        from core.services.vehiculo_service import VehiculoService
        vehiculo_service = VehiculoService()
        
        if not vehiculo_service.validar_vehiculo_atendible(vehiculo_id):
            raise ValidationError(
                "El modelo y año del vehículo no pueden ser atendidos en el taller"
            )
        
        # Validar que no tenga solicitudes pendientes
        if self.repository.tiene_solicitud_pendiente(vehiculo_id):
            raise ValidationError(
                "El vehículo ya tiene una solicitud pendiente"
            )
        
        # Obtener estado pendiente
        estado_pendiente = Estado.objects.get(
            clave='pendiente',
            tipo=Estado.TIPO_SOLICITUD
        )
        
        data['id_estado'] = estado_pendiente
        
        # Crear solicitud
        solicitud = self.repository.create(data)
        
        # Crear detalle si viene información
        if data.get('observaciones') or data.get('costo_estimado'):
            self.detalle_repository.create({
                'id_solicitud': solicitud,
                'observaciones': data.get('observaciones'),
                'costo_estimado': data.get('costo_estimado')
            })
        
        return solicitud
    
    @transaction.atomic
    def aprobar_solicitud(self, solicitud_id: int, aprobado_por_id: int) -> Solicitud:
        """Aprueba una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        
        # Validar que esté pendiente
        if solicitud.id_estado.clave != 'pendiente':
            raise ValidationError("Solo se pueden aprobar solicitudes pendientes")
        
        # Obtener estado aprobada
        estado_aprobada = Estado.objects.get(
            clave='aprobada',
            tipo=Estado.TIPO_SOLICITUD
        )
        
        return self.repository.aprobar(solicitud_id, aprobado_por_id, estado_aprobada)
    
    @transaction.atomic
    def rechazar_solicitud(
        self,
        solicitud_id: int,
        motivo: str,
        rechazado_por_id: int
    ) -> Solicitud:
        """Rechaza una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        
        # Validar que esté pendiente
        if solicitud.id_estado.clave != 'pendiente':
            raise ValidationError("Solo se pueden rechazar solicitudes pendientes")
        
        if not motivo:
            raise ValidationError("Debe proporcionar un motivo de rechazo")
        
        # Obtener estado rechazada
        estado_rechazada = Estado.objects.get(
            clave='rechazada',
            tipo=Estado.TIPO_SOLICITUD
        )
        
        return self.repository.rechazar(
            solicitud_id,
            motivo,
            rechazado_por_id,
            estado_rechazada
        )
    
    def update_solicitud(self, solicitud_id: int, data: Dict) -> Solicitud:
        """Actualiza una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        return self.repository.update(solicitud, data)
    
    def delete_solicitud(self, solicitud_id: int) -> None:
        """Elimina una solicitud"""
        solicitud = self.get_solicitud_by_id(solicitud_id)
        
        # Validar que no tenga reservación
        if hasattr(solicitud, 'reservacion'):
            raise ValidationError("No se puede eliminar una solicitud con reservación")
        
        self.repository.delete(solicitud)
    
    def search_solicitudes(self, query: str) -> List[Solicitud]:
        """Busca solicitudes"""
        return self.repository.search(query)
    
    def get_estadisticas_solicitudes(self) -> Dict:
        """Obtiene estadísticas de solicitudes"""
        from django.db.models import Count
        
        total = Solicitud.objects.count()
        
        por_estado = Solicitud.objects.values(
            'id_estado__clave',
            'id_estado__descripcion'
        ).annotate(
            total=Count('id')
        )
        
        return {
            'total': total,
            'por_estado': list(por_estado),
            'pendientes': self.repository.get_pendientes().count(),
            'aprobadas': self.repository.get_aprobadas().count(),
            'rechazadas': self.repository.get_rechazadas().count()
        }
```


---

## 📄 ./solicitudes/services/reservacion_service.py

```python
"""
Service para lógica de negocio de Reservaciones
"""
from typing import List, Dict
from datetime import date
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from solicitudes.models import ReservacionTallerPrincipal
from solicitudes.repositories.reservacion_repository import ReservacionRepository
from core.models import Estado
from core.services.calendario_service import CalendarioPrincipalService


class ReservacionService:
    """Maneja la lógica de negocio para reservaciones"""
    
    def __init__(self):
        self.repository = ReservacionRepository()
        self.calendario_service = CalendarioPrincipalService()
    
    def get_all_reservaciones(self) -> List[ReservacionTallerPrincipal]:
        """Obtiene todas las reservaciones"""
        return self.repository.get_all()
    
    def get_reservacion_by_id(self, reservacion_id: int) -> ReservacionTallerPrincipal:
        """Obtiene una reservación por ID"""
        reservacion = self.repository.get_by_id(reservacion_id)
        
        if not reservacion:
            raise ValidationError(f"Reservación con ID {reservacion_id} no encontrada")
        
        return reservacion
    
    def get_reservaciones_by_cliente(self, cliente_id: int) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de un cliente"""
        return self.repository.get_by_cliente(cliente_id)
    
    def get_reservaciones_by_fecha(self, fecha: date) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones de una fecha"""
        return self.repository.get_by_fecha(fecha)
    
    def get_reservaciones_pendientes(self) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones pendientes"""
        return self.repository.get_pendientes()
    
    def get_reservaciones_proximas(self, dias: int = 7) -> List[ReservacionTallerPrincipal]:
        """Obtiene reservaciones próximas"""
        return self.repository.get_proximas(dias)
    
    @transaction.atomic
    def create_reservacion(self, data: Dict) -> ReservacionTallerPrincipal:
        """Crea una nueva reservación"""
        from solicitudes.services.solicitud_service import SolicitudService
        
        solicitud_id = data.get('id_solicitud')
        tamp_block_id = data.get('id_tamp_block')
        
        # Validar que la solicitud exista y esté aprobada
        solicitud_service = SolicitudService()
        solicitud = solicitud_service.get_solicitud_by_id(solicitud_id)
        
        if solicitud.id_estado.clave != 'aprobada':
            raise ValidationError("Solo se pueden crear reservaciones de solicitudes aprobadas")
        
        # Validar que no tenga reservación
        if hasattr(solicitud, 'reservacion'):
            raise ValidationError("La solicitud ya tiene una reservación")
        
        # Validar y reservar el bloque
        bloque = self.calendario_service.reservar_bloque(tamp_block_id)
        
        # Obtener estado pendiente
        estado_pendiente = Estado.objects.get(
            clave='pendiente',
            tipo=Estado.TIPO_RESERVACION
        )
        
        data['id_estado'] = estado_pendiente
        
        try:
            reservacion = self.repository.create(data)
            return reservacion
        except Exception as e:
            # Si falla, liberar el bloque
            self.calendario_service.liberar_bloque(tamp_block_id)
            raise e
    
    def update_reservacion(self, reservacion_id: int, data: Dict) -> ReservacionTallerPrincipal:
        """Actualiza una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        return self.repository.update(reservacion, data)
    
    @transaction.atomic
    def iniciar_evaluacion(
        self,
        reservacion_id: int,
        atendido_por_id: int
    ) -> ReservacionTallerPrincipal:
        """Inicia la evaluación de una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        
        estado_en_proceso = Estado.objects.get(
            clave='en_proceso',
            tipo=Estado.TIPO_RESERVACION
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_en_proceso,
            'atendido_por_id': atendido_por_id,
            'fecha_evaluacion': timezone.now(),
            'fecha_inicio': timezone.now()
        })
    
    @transaction.atomic
    def completar_evaluacion(
        self,
        reservacion_id: int,
        notas: str
    ) -> ReservacionTallerPrincipal:
        """Completa la evaluación de una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        
        return self.repository.update(reservacion, {
            'notas_evaluacion': notas,
            'fecha_fin_real': timezone.now()
        })
    
    def actualizar_avance_global(self, reservacion_id: int) -> ReservacionTallerPrincipal:
        """Actualiza el avance global de la reservación"""
        return self.repository.actualizar_avance_global(reservacion_id)
    
    @transaction.atomic
    def cancelar_reservacion(self, reservacion_id: int) -> ReservacionTallerPrincipal:
        """Cancela una reservación"""
        reservacion = self.get_reservacion_by_id(reservacion_id)
        
        # Liberar el bloque
        self.calendario_service.liberar_bloque(reservacion.id_tamp_block_id)
        
        estado_cancelada = Estado.objects.get(
            clave='cancelada',
            tipo=Estado.TIPO_RESERVACION
        )
        
        return self.repository.update(reservacion, {
            'id_estado': estado_cancelada
        })
    
    def search_reservaciones(self, query: str) -> List[ReservacionTallerPrincipal]:
        """Busca reservaciones"""
        return self.repository.search(query)
```


---

## 📄 ./solicitudes/services/__init__.py

```python

```


---

## 📄 ./autotaller/wsgi.py

```python
"""
WSGI config for autotaller project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autotaller.settings')

application = get_wsgi_application()

```


---

## 📄 ./autotaller/asgi.py

```python
"""
ASGI config for autotaller project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autotaller.settings')

application = get_asgi_application()

```


---

## 📄 ./autotaller/__init__.py

```python

```


---

## 📄 ./autotaller/settings.py

```python
"""
Django settings for taller_automotriz project.
Arquitectura: Monolítica
"""

from pathlib import Path
from decouple import config

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'core',
    'solicitudes',
    'servicios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='taller_automotriz'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'core.Usuario'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

CORS_ALLOW_CREDENTIALS = True
```


---

## 📄 ./autotaller/urls.py

```python
"""
URL configuration for autotaller project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# autotaller/autotaller/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Incluye las urls de cada app
    path("", include("core.urls")),             # home / endpoints del core
    path("servicios/", include("servicios.urls")),
    path("solicitudes/", include("solicitudes.urls")),
]

```
