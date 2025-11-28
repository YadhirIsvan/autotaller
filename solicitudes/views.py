"""
SOLICITUDES VIEWS
"""
from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Solicitud, ReservacionTallerPrincipal
from .serializers import (
    SolicitudSerializer, SolicitudDetailSerializer, SolicitudCreateSerializer,
    AprobarRechazarSerializer, ReservacionTallerPrincipalSerializer,
    ReservacionTallerPrincipalDetailSerializer
)
from .services.solicitud_service import SolicitudService
from .services.reservacion_service import ReservacionService


class SolicitudViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de solicitudes"""
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudCreateSerializer
        elif self.action == 'retrieve':
            return SolicitudDetailSerializer
        return SolicitudSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es cliente, solo ver sus solicitudes
        if user.id_tipo.cve == 'cliente':
            queryset = queryset.filter(id_usuario=user)
        
        return queryset
    
    def create(self, request):
        serializer = SolicitudCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            solicitud = SolicitudService().create_solicitud(serializer.validated_data)
            result_serializer = SolicitudDetailSerializer(solicitud)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        """Obtener solicitudes del usuario actual"""
        solicitudes = SolicitudService().get_solicitudes_by_usuario(request.user.id)
        serializer = self.get_serializer(solicitudes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtener solicitudes pendientes"""
        solicitudes = SolicitudService().get_solicitudes_pendientes()
        serializer = self.get_serializer(solicitudes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar una solicitud"""
        if request.user.id_tipo.cve not in ['administrador', 'agente']:
            return Response(
                {'error': 'No tiene permisos para aprobar solicitudes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            solicitud = SolicitudService().aprobar_solicitud(int(pk), request.user.id)
            serializer = self.get_serializer(solicitud)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechazar una solicitud"""
        if request.user.id_tipo.cve not in ['administrador', 'agente']:
            return Response(
                {'error': 'No tiene permisos para rechazar solicitudes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AprobarRechazarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        motivo = serializer.validated_data.get('motivo', '')
        if not motivo:
            return Response(
                {'error': 'Debe proporcionar un motivo de rechazo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            solicitud = SolicitudService().rechazar_solicitud(
                int(pk), motivo, request.user.id
            )
            result_serializer = self.get_serializer(solicitud)
            return Response(result_serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReservacionTallerPrincipalViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de reservaciones"""
    queryset = ReservacionTallerPrincipal.objects.all()
    serializer_class = ReservacionTallerPrincipalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReservacionTallerPrincipalDetailSerializer
        return ReservacionTallerPrincipalSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Si es cliente, solo ver sus reservaciones
        if user.id_tipo.cve == 'cliente':
            queryset = queryset.filter(id_solicitud__id_usuario=user)
        
        return queryset
    
    def create(self, request):
        try:
            reservacion = ReservacionService().create_reservacion(request.data)
            serializer = self.get_serializer(reservacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def mis_reservaciones(self, request):
        """Obtener reservaciones del usuario actual"""
        reservaciones = ReservacionService().get_reservaciones_by_cliente(request.user.id)
        serializer = self.get_serializer(reservaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def iniciar_evaluacion(self, request, pk=None):
        """Iniciar evaluación de una reservación"""
        if request.user.id_tipo.cve not in ['administrador', 'agente']:
            return Response(
                {'error': 'No tiene permisos para iniciar evaluaciones'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            reservacion = ReservacionService().iniciar_evaluacion(int(pk), request.user.id)
            serializer = self.get_serializer(reservacion)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)