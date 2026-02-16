from django.contrib import admin
from .models import Asignacion

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'activo', 'usuario_asignado', 'asignado_por',
        'fecha_asignacion', 'activo_actual', 'fecha_devolucion'
    ]
    list_filter = ['activo_actual', 'fecha_asignacion']
    search_fields = ['activo__codigo', 'usuario_asignado__username', 'motivo']
    readonly_fields = ['fecha_asignacion']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('activo', 'usuario_asignado', 'asignado_por')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_estimada_devolucion', 'fecha_devolucion')
        }),
        ('Información', {
            'fields': ('motivo', 'observaciones')
        }),
        ('Estado', {
            'fields': ('activo_actual', 'activo_devuelto')
        }),
    )