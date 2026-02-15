from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventario.models import Activo
from asignaciones.models import Asignacion
from movimientos.models import Movimiento
from catalogos.models import Categoria, Marca, Ubicacion, Estado

class Command(BaseCommand):
    help = 'Crea grupos y permisos para el sistema de inventario'
    
    def handle(self, *args, **kwargs):
        # Crear grupos
        grupo_director, created = Group.objects.get_or_create(name='DirectorTI')
        grupo_asistente, created = Group.objects.get_or_create(name='Asistente')
        
        # Obtener todos los content types de los modelos principales
        modelos = [Activo, Asignacion, Movimiento, Categoria, Marca, Ubicacion, Estado]
        
        # Permisos para Director TI (todos los permisos)
        for modelo in modelos:
            content_type = ContentType.objects.get_for_model(modelo)
            permisos = Permission.objects.filter(content_type=content_type)
            grupo_director.permissions.add(*permisos)
        
        # Permisos para Asistente (limitados)
        # Activos: puede ver, agregar y cambiar, pero no eliminar
        content_activo = ContentType.objects.get_for_model(Activo)
        permisos_activo = Permission.objects.filter(
            content_type=content_activo,
            codename__in=['view_activo', 'add_activo', 'change_activo']
        )
        grupo_asistente.permissions.add(*permisos_activo)
        
        # Asignaciones: puede ver y agregar
        content_asignacion = ContentType.objects.get_for_model(Asignacion)
        permisos_asignacion = Permission.objects.filter(
            content_type=content_asignacion,
            codename__in=['view_asignacion', 'add_asignacion']
        )
        grupo_asistente.permissions.add(*permisos_asignacion)
        
        # Movimientos: puede ver y agregar
        content_movimiento = ContentType.objects.get_for_model(Movimiento)
        permisos_movimiento = Permission.objects.filter(
            content_type=content_movimiento,
            codename__in=['view_movimiento', 'add_movimiento']
        )
        grupo_asistente.permissions.add(*permisos_movimiento)
        
        # Catálogos: solo puede ver (no modificar)
        catalogos = [Categoria, Marca, Ubicacion, Estado]
        for catalogo in catalogos:
            content = ContentType.objects.get_for_model(catalogo)
            permiso_view = Permission.objects.get(
                content_type=content,
                codename=f'view_{catalogo.__name__.lower()}'
            )
            grupo_asistente.permissions.add(permiso_view)
        
        self.stdout.write(
            self.style.SUCCESS('Grupos y permisos creados exitosamente')
        )