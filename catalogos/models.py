from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text='Código hexadecimal para el color')
    
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        # Estados por defecto si no existen
        if not self.pk:
            estados_default = [
                ('Disponible', '#28a745'),
                ('Asignado', '#007bff'),
                ('En reparación', '#ffc107'),
                ('En bodega', '#17a2b8'),
                ('Dado de baja', '#dc3545'),
                ('Prestado', '#fd7e14'),
            ]
            for estado, color in estados_default:
                Estado.objects.get_or_create(nombre=estado, defaults={'color': color})
        super().save(*args, **kwargs)