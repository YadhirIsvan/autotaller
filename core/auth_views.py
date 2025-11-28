"""
CORE AUTH VIEWS - Sistema de Autenticación
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .serializers import UsuarioSerializer, UsuarioCreateSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Endpoint de login"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email y contraseña son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Autenticar usuario
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.activo:
        return Response(
            {'error': 'Usuario inactivo'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Login
    login(request, user)
    
    serializer = UsuarioSerializer(user)
    return Response({
        'message': 'Login exitoso',
        'user': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Endpoint de logout"""
    logout(request)
    return Response({'message': 'Logout exitoso'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Obtener usuario actual"""
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registro de nuevo usuario"""
    serializer = UsuarioCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                'message': 'Usuario creado exitosamente',
                'user': UsuarioSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)