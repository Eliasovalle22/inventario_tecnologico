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
        related_name='asignaciones_realizadas',
        verbose_name="Asignado por"
    )
    
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    fecha_estimada_devolucion = models.DateTimeField(null=True, blank=True, 
                                                      help_text="Fecha estimada de devolución")
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    motivo = models.CharField(max_length=200, blank=True, null=True, 
                              help_text="Motivo de la asignación")
    
    # Control
    activo_actual = models.BooleanField(default=True, 
                                        help_text="Indica si esta es la asignación actual")
    activo_devuelto = models.BooleanField(default=False)
    
    # Metadatos
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        ordering = ['-fecha_asignacion']
        indexes = [
            models.Index(fields=['activo', 'activo_actual']),
            models.Index(fields=['usuario_asignado', 'activo_actual']),
            models.Index(fields=['fecha_asignacion']),
        ]
    
    def __str__(self):
        estado = "Activa" if self.activo_actual else "Devuelta"
        return f"{self.activo.codigo} → {self.usuario_asignado.get_full_name()} ({estado})"
    
    def save(self, *args, **kwargs):
        # Si es una nueva asignación, marcar las anteriores como no activas
        if not self.pk:
            # Marcar asignaciones anteriores como no activas
            Asignacion.objects.filter(
                activo=self.activo, 
                activo_actual=True
            ).update(activo_actual=False, activo_devuelto=True)
            
            # Actualizar el responsable en el activo
            self.activo.responsable = self.usuario_asignado
            self.activo.save()
        
        super().save(*args, **kwargs)
    
    def devolver(self, fecha_devolucion=None, observaciones=""):
        """Método para devolver un activo"""
        self.fecha_devolucion = fecha_devolucion or timezone.now()
        self.activo_actual = False
        self.activo_devuelto = True
        if observaciones:
            self.observaciones = (self.observaciones or "") + f"\nDevolución: {observaciones}"
        self.save()
        
        # Actualizar el activo
        self.activo.responsable = None
        self.activo.save()
        
        # Registrar movimiento
        from movimientos.models import Movimiento
        Movimiento.objects.create(
            activo=self.activo,
            tipo='DEVOLUCION',
            usuario=self.asignado_por,
            responsable_anterior=self.usuario_asignado,
            observaciones=f"Devolución de asignación #{self.id}. {observaciones}",
            asignacion=self
        )
    
    @property
    def dias_transcurridos(self):
        """Días desde la asignación"""
        delta = timezone.now() - self.fecha_asignacion
        return delta.days
    
    @property
    def dias_para_devolucion(self):
        """Días restantes para la devolución estimada"""
        if self.fecha_estimada_devolucion:
            delta = self.fecha_estimada_devolucion - timezone.now()
            return delta.days
        return None