from django.db import models
from django.contrib.auth.models import User
from inventario.models import Activo
from catalogos.models import Ubicacion, Estado
from django.utils import timezone

class Movimiento(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada a inventario'),
        ('SALIDA', 'Salida de inventario'),
        ('ASIGNACION', 'Asignación a usuario'),
        ('DEVOLUCION', 'Devolución'),
        ('TRASLADO', 'Traslado de ubicación'),
        ('REPARACION', 'Envío a reparación'),
        ('BAJA', 'Dar de baja'),
        ('CAMBIO_ESTADO', 'Cambio de estado'),
    ]
    
    activo = models.ForeignKey(Activo, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimientos_realizados')
    
    # Campos para tracking de cambios
    ubicacion_origen = models.ForeignKey(
        Ubicacion, 
        on_delete=models.PROTECT, 
        related_name='movimientos_origen',
        null=True, 
        blank=True
    )
    ubicacion_destino = models.ForeignKey(
        Ubicacion, 
        on_delete=models.PROTECT, 
        related_name='movimientos_destino',
        null=True, 
        blank=True
    )
    estado_origen = models.ForeignKey(
        Estado, 
        on_delete=models.PROTECT, 
        related_name='movimientos_estado_origen',
        null=True, 
        blank=True
    )
    estado_destino = models.ForeignKey(
        Estado, 
        on_delete=models.PROTECT, 
        related_name='movimientos_estado_destino',
        null=True, 
        blank=True
    )
    
    # Responsable involucrado (si aplica)
    responsable_anterior = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimientos_responsable_anterior'
    )
    responsable_nuevo = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimientos_responsable_nuevo'
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    # Referencia a asignación si aplica
    asignacion = models.ForeignKey(
        'asignaciones.Asignacion', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimientos'
    )
    
    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['activo', 'fecha']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.activo} - {self.fecha.date()}"