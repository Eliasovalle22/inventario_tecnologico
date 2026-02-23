from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Activo(models.Model):
    TIPO_ACTIVO = [
        ('LAPTOP', 'Laptop'),
        ('PC', 'Computador de escritorio'),
        ('MONITOR', 'Monitor'),
        ('IMPRESORA', 'Impresora'),
        ('SWITCH', 'Switch'),
        ('ROUTER', 'Router'),
        ('SERVER', 'Servidor'),
        ('CELULAR', 'Celular'),
        ('OTRO', 'Otro'),
    ]
    
    # Identificación
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código/Inventario")
    tipo = models.CharField(max_length=20, choices=TIPO_ACTIVO, default='OTRO')
    serial = models.CharField(max_length=100, blank=True, null=True)
    
    # Especificaciones
    categoria = models.ForeignKey('catalogos.Categoria', on_delete=models.PROTECT)
    marca = models.ForeignKey('catalogos.Marca', on_delete=models.PROTECT)
    modelo = models.CharField(max_length=100)
    
    # Estado y ubicación
    estado = models.ForeignKey('catalogos.Estado', on_delete=models.PROTECT)
    ubicacion = models.ForeignKey('catalogos.Ubicacion', on_delete=models.PROTECT)
    
    # Información de compra
    fecha_compra = models.DateField(blank=True, null=True)
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    garantia_meses = models.IntegerField(default=12)
    proveedor = models.CharField(max_length=200, blank=True, null=True)
    factura = models.CharField(max_length=100, blank=True, null=True, verbose_name="N° Factura")
    
    # Responsable actual (puede ser None si está en bodega)
    responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activos_asignados',
        verbose_name="Responsable actual"
    )
    
    # Especificaciones técnicas
    especificaciones = models.TextField(blank=True, null=True)
    
    # Control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='activos_creados'
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Activo"
        verbose_name_plural = "Activos"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['serial']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.marca} {self.modelo}"
    
    @property
    def garantia_valida_hasta(self):
        if self.fecha_compra and self.garantia_meses:
            return self.fecha_compra + timezone.timedelta(days=30 * self.garantia_meses)
        return None
    
    @property
    def esta_en_garantia(self):
        if self.garantia_valida_hasta:
            return self.garantia_valida_hasta >= timezone.now().date()
        return False