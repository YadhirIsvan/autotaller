# core/management/commands/crear_superusuario.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import TipoUsuario

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea un superusuario con tipo de usuario administrador'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nombre de usuario')
        parser.add_argument('--email', type=str, help='Email')
        parser.add_argument('--password', type=str, help='Contraseña')
        parser.add_argument('--nombre', type=str, help='Nombre completo')

    def handle(self, *args, **options):
        # Verificar que exista el tipo administrador
        try:
            tipo_admin = TipoUsuario.objects.get(cve='administrador')
        except TipoUsuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('No existe el tipo de usuario "administrador". Ejecuta las migraciones primero.')
            )
            return

        # Obtener datos
        username = options.get('username') or input('Nombre de usuario: ')
        email = options.get('email') or input('Email: ')
        password = options.get('password') or input('Contraseña: ')
        nombre = options.get('nombre') or input('Nombre completo: ')

        # Verificar si ya existe
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'Ya existe un usuario con username "{username}"')
            )
            return

        if Usuario.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Ya existe un usuario con email "{email}"')
            )
            return

        # Crear superusuario
        try:
            usuario = Usuario.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                nombre=nombre,
                id_tipo=tipo_admin,
                cve=f'ADM{username.upper()}',
                activo=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superusuario "{username}" creado exitosamente')
            )
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Tipo: {tipo_admin.descripcion}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear superusuario: {str(e)}')
            )
