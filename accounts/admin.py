from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Perfil

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    extra = 0
    min_num = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def has_add_permission(self, request, obj=None):
        # No permitir agregar inline si el perfil ya existe (lo crea el signal)
        if obj and Perfil.objects.filter(usuario=obj).exists():
            return False
        return False  # Nunca agregar desde inline, el signal se encarga

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Grupos'

# Reemplazar el UserAdmin original
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'departamento', 'cargo']
    search_fields = ['usuario__username', 'usuario__email']