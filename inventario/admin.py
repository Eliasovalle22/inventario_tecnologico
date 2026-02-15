from django.contrib import admin
from django.utils.html import format_html
from .models import Activo

@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'tipo', 'marca', 'modelo', 
        'estado_colored', 'ubicacion', 'responsable', 'fecha_compra'
    ]
    list_display_links = ['codigo']
    list_filter = ['tipo', 'estado', 'marca', 'categoria']
    search_fields = ['codigo', 'serial', 'modelo', 'observaciones']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'tipo', 'serial')
        }),
        ('Especificaciones', {
            'fields': ('categoria', 'marca', 'modelo', 'especificaciones')
        }),
        ('Estado y Ubicación', {
            'fields': ('estado', 'ubicacion', 'responsable')
        }),
        ('Información de Compra', {
            'fields': ('fecha_compra', 'valor_compra', 'garantia_meses', 'proveedor', 'factura')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Información de Control', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_colored(self, obj):
        if obj.estado:
            return format_html(
                '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white;">{}</span>',
                obj.estado.color,
                obj.estado.nombre,
            )
        return "-"
    estado_colored.short_description = 'Estado'
    estado_colored.admin_order_field = 'estado'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        obj.save()