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
# ✅ CORREGIDO: Importar las clases correctas
from .services.calendario_service import CalendarioPrincipalService, CalendarioTalleresService


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
        
        usuarios = UsuarioService().get_usuarios_by_tipo(tipo)
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def talleres(self, request):
        """Obtener solo talleres"""
        talleres = UsuarioService().get_talleres_activos()
        serializer = self.get_serializer(talleres, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def clientes(self, request):
        """Obtener solo clientes"""
        clientes = UsuarioService().get_clientes_activos()
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
        
        if activo:
            usuario = UsuarioService().activar_usuario(usuario.id)
        else:
            usuario = UsuarioService().desactivar_usuario(usuario.id)
        
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
            from .repositories.vehiculo_repository import ModeloRepository
            ano = int(ano)
            atendible = ModeloRepository.is_modelo_atendible(modelo.id, ano)
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
        vehiculos = VehiculoService().get_vehiculos_by_propietario(request.user.id)
        serializer = self.get_serializer(vehiculos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def validar(self, request, pk=None):
        """Validar si un vehículo puede ser atendido"""
        vehiculo = self.get_object()
        puede_atender = VehiculoService().validar_vehiculo_atendible(vehiculo.id)
        
        return Response({
            'puede_atender': puede_atender,
            'mensaje': 'El vehículo puede ser atendido' if puede_atender else 'El modelo/año no es atendible'
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
        
        # ✅ CORREGIDO: Usar CalendarioPrincipalService
        fechas = CalendarioPrincipalService().get_bloques_disponibles(
            fecha_inicio, fecha_fin
        )
        serializer = self.get_serializer(fechas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reservar(self, request, pk=None):
        """Reservar un espacio"""
        tamp_block = self.get_object()
        
        # ✅ CORREGIDO: Usar CalendarioPrincipalService
        try:
            bloque = CalendarioPrincipalService().reservar_bloque(tamp_block.id)
            serializer = self.get_serializer(bloque)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
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
        
        # ✅ CORREGIDO: Usar CalendarioTalleresService
        fechas = CalendarioTalleresService().get_bloques_disponibles_taller(
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