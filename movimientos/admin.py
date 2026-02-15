from django.contrib import admin
from .models import Movimiento

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = [
        'fecha', 'activo', 'tipo', 'usuario', 
        'ubicacion_destino', 'estado_destino'
    ]
    list_filter = ['tipo', 'fecha']
    search_fields = ['activo__codigo', 'observaciones']
    readonly_fields = ['fecha']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('activo', 'tipo', 'fecha', 'usuario')
        }),
        ('Cambios de Ubicación', {
            'fields': ('ubicacion_origen', 'ubicacion_destino')
        }),
        ('Cambios de Estado', {
            'fields': ('estado_origen', 'estado_destino')
        }),
        ('Cambios de Responsable', {
            'fields': ('responsable_anterior', 'responsable_nuevo')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'asignacion')
        }),
    )