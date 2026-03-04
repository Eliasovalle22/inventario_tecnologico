from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from catalogos.models import Estado
from inventario.models import Activo
from asignaciones.models import Asignacion
from .models import Movimiento
from django.contrib.auth.models import User
import json

@receiver(post_save, sender=Activo)
def registrar_movimiento_activo(sender, instance, created, **kwargs):
    
    if created:
        # Movimiento de creación
        Movimiento.objects.create(
            activo=instance,
            tipo='ENTRADA',
            usuario=instance.creado_por or User.objects.first(),
            ubicacion_destino=instance.ubicacion,
            estado_destino=instance.estado,
            observaciones=f"Activo creado: {instance.codigo}",
            metadata={
                'accion': 'creacion',
                'valor_compra': str(instance.valor_compra) if instance.valor_compra else None,
                'garantia_meses': instance.garantia_meses,
            }
        )
    else:
        pass

@receiver(post_save, sender=Asignacion)
def registrar_movimiento_asignacion(sender, instance, created, **kwargs):
    
    
    if created:
        # Asignación
        Movimiento.objects.create(
            activo=instance.activo,
            tipo='ASIGNACION',
            usuario=instance.asignado_por,
            responsable_nuevo=instance.usuario_asignado,
            observaciones=f"Asignado a: {instance.usuario_asignado.get_full_name()}",
            asignacion=instance,
            metadata={
                'fecha_asignacion': instance.fecha_asignacion.isoformat(),
            }
        )
        
        # Actualizar el estado del activo
        activo = instance.activo
        estado_asignado = Estado.objects.filter(nombre='ASIGNADO').first()
        if estado_asignado:
            activo.estado = estado_asignado
            activo.responsable = instance.usuario_asignado
            activo.save()

@receiver(pre_delete, sender=Activo)
def registrar_movimiento_baja(sender, instance, **kwargs):
    
    
    Movimiento.objects.create(
        activo=instance,
        tipo='BAJA',
        usuario=None,
        observaciones=f"Activo dado de baja: {instance.codigo}",
        metadata={
            'motivo': 'eliminacion',
            'fecha_baja': instance.fecha_actualizacion.isoformat(),
        }
    )