from django.contrib import admin
from .models import Asignacion

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = [
        'activo', 'usuario_asignado', 'fecha_asignacion', 
        'fecha_devolucion', 'activo_actual'
    ]
    list_filter = ['activo_actual', 'fecha_asignacion']
    search_fields = ['activo__codigo', 'usuario_asignado__username']
    readonly_fields = ['fecha_asignacion']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nueva asignación
            obj.asignado_por = request.user
        obj.save()