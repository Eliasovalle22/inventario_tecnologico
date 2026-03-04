from django.db import models
from django.contrib.auth.models import User
from inventario.models import Activo
from django.utils import timezone
from catalogos.models import Estado, Ubicacion

class Asignacion(models.Model):

    activo = models.ForeignKey(Activo, on_delete=models.PROTECT, related_name='asignaciones')
    usuario_asignado = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='asignaciones_recibidas',
        verbose_name="Asignado a"
    )
    sede = models.ForeignKey(
        'catalogos.Sede',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Sede"
    )
    ubicacion = models.ForeignKey(
        'catalogos.Ubicacion',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Ubicación"
    )
    asignado_por = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='asignaciones_realizadas',
        verbose_name="Asignado por"
    )
    
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    fecha_estimada_devolucion = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    motivo = models.CharField(max_length=200, blank=True, null=True)
    evidencias = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name="Evidencias",
        help_text="URL de evidencia fotográfica o documental"
    )
    
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
            
            # Cambiar estado del activo a "Asignado"
            estado_asignado = Estado.objects.filter(nombre='Asignado').first()
            if estado_asignado:
                self.activo.estado = estado_asignado
            
            # Actualizar ubicación del activo si se indicó en la asignación
            if self.ubicacion:
                self.activo.ubicacion = self.ubicacion
            
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
        
        # Restaurar estado del activo a "En bodega"
        estado_bodega = Estado.objects.filter(nombre='En bodega').first()
        if estado_bodega:
            self.activo.estado = estado_bodega
        
        # Restaurar ubicación del activo a "En bodega"
        ubicacion_bodega = Ubicacion.objects.filter(nombre='En bodega').first()
        if ubicacion_bodega:
            self.activo.ubicacion = ubicacion_bodega
        
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