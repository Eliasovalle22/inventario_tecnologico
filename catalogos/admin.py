from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Marca, Ubicacion, Estado

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion', 'fecha_creacion']
    list_display_links = ['nombre']
    search_fields = ['nombre']
    list_filter = ['fecha_creacion']
    ordering = ['nombre']

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion']
    list_display_links = ['nombre']
    search_fields = ['nombre']
    ordering = ['nombre']

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'direccion', 'descripcion']
    list_display_links = ['nombre']
    search_fields = ['nombre', 'direccion']
    ordering = ['nombre']

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'color', 'descripcion']
    list_display_links = ['nombre']
    search_fields = ['nombre']
    list_filter = ['nombre']
    ordering = ['nombre']
    
    def colored_name(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.nombre,
        )
    colored_name.short_description = 'Estado'
    colored_name.allow_tags = True