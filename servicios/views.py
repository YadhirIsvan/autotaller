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
# ✅ CORREGIDO: Importar las clases correctas
from .services.servicio_service import ServicioService, ServicioTallerService
from .services.asignacion_service import AsignacionServicioService
from .services.progreso_service import ProgresoServicioService


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
        servicios = ServicioService().get_all_servicios(activo=True)
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
        
        servicios = ServicioService().get_servicios_by_categoria(int(categoria_id))
        serializer = self.get_serializer(servicios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def talleres_disponibles(self, request, pk=None):
        """Obtener talleres que ofrecen este servicio"""
        talleres = ServicioTallerService().get_talleres_por_servicio(int(pk))
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
        
        servicios = ServicioTallerService().get_servicios_by_taller(request.user.id)
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
        
        servicios = ServicioTallerService().get_servicios_by_taller(int(taller_id))
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
        service = AsignacionServicioService()
        
        if request.user.id_tipo.cve == 'taller':
            servicios = service.get_servicios_by_taller(request.user.id)
        elif request.user.id_tipo.cve == 'cliente':
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
        if request.user.id_tipo.cve not in ['administrador', 'agente']:
            return Response(
                {'error': 'No tiene permisos para asignar servicios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReservacionServicioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = AsignacionServicioService()
            reservacion = service.asignar_servicio(serializer.validated_data)
            
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
            service = AsignacionServicioService()
            servicio_actualizado = service.iniciar_servicio(servicio.id)
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
            data = {
                'id_reservacion_servicio': servicio.id,
                'porcentaje_nuevo': serializer.validated_data['porcentaje'],
                'dias_estimados': serializer.validated_data.get('dias_estimados'),
                'comentario': serializer.validated_data.get('comentario', ''),
                'evidencia_url': serializer.validated_data.get('evidencia_url', ''),
                'actualizado_por': request.user.id
            }
            
            service = ProgresoServicioService()
            service.actualizar_progreso(data)
            
            # Obtener servicio actualizado
            servicio.refresh_from_db()
            result_serializer = ReservacionServicioDetailSerializer(servicio)
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
            service = AsignacionServicioService()
            servicio_actualizado = service.completar_servicio(servicio.id)
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
        service = ProgresoServicioService()
        historial = service.get_historial_by_servicio(servicio.id)
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
        
        servicios = ReservacionServicio.objects.filter(id_estado__clave=estado)
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
        
        service = ProgresoServicioService()
        progreso = service.get_historial_by_servicio(int(servicio_id))
        serializer = self.get_serializer(progreso, many=True)
        return Response(serializer.data)