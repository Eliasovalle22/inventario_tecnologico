from django.db import models
from django.contrib.auth.models import User
from inventario.models import Activo
from django.utils import timezone

class Asignacion(models.Model):
    """
    Registro de asignaciones de activos a usuarios/empleados
    """
    activo = models.ForeignKey(Activo, on_delete=models.PROTECT, related_name='asignaciones')
    usuario_asignado = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='asignaciones_recibidas',
        verbose_name="Asignado a"
    )
    asignado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='asignaciones_realizadas'
    )
    
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    
    # Control
    activo_actual = models.BooleanField(default=True, help_text="Indica si esta es la asignación actual")
    
    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"{self.activo} asignado a {self.usuario_asignado} el {self.fecha_asignacion.date()}"
    
    def save(self, *args, **kwargs):
        # Si es una nueva asignación, marcar las anteriores como no activas
        if not self.pk:
            Asignacion.objects.filter(
                activo=self.activo, 
                activo_actual=True
            ).update(activo_actual=False)
            
            # Actualizar el responsable en el activo
            self.activo.responsable = self.usuario_asignado
            self.activo.save()
        
        super().save(*args, **kwargs)