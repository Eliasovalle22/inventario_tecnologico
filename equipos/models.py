from django.db import models

class Sede(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la sede")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ['nombre']

class Dependencia(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la dependencia")
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, verbose_name="Sede")

    def __str__(self):
        return f"{self.nombre} ({self.sede})"

    class Meta:
        verbose_name = "Dependencia"
        verbose_name_plural = "Dependencias"
        ordering = ['nombre']

class Salon(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del salón")
    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE, verbose_name="Dependencia")

    def __str__(self):
        return f"{self.nombre} ({self.dependencia})"

    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']

class Equipo(models.Model):
    TIPO_CHOICES = [
        ('Computador', 'Computador'),
        ('Impresora', 'Impresora'),
        ('Proyector', 'Proyector'),
        # Agrega más tipos según sea necesario
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de equipo")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    serial = models.CharField(max_length=100, unique=True, verbose_name="Número de serie")
    especificaciones = models.TextField(verbose_name="Especificaciones")
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Salón")
    asignado_a = models.CharField(max_length=100, blank=True, verbose_name="Asignado a")
    fecha_compra = models.DateField(null=True, blank=True, verbose_name="Fecha de compra")
    fecha_instalacion = models.DateField(null=True, blank=True, verbose_name="Fecha de instalación")

    def __str__(self):
        return f"{self.tipo} - {self.serial}"

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['tipo', 'marca', 'modelo']

class CambioParte(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='cambios', verbose_name="Equipo")
    componente = models.CharField(max_length=100, verbose_name="Componente")
    descripcion = models.TextField(verbose_name="Descripción")
    fecha_cambio = models.DateField(verbose_name="Fecha del cambio")

    def __str__(self):
        return f"{self.componente} cambiado en {self.equipo.serial}"

    class Meta:
        verbose_name = "Cambio de Parte"
        verbose_name_plural = "Cambios de Partes"
        ordering = ['-fecha_cambio']
