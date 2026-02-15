from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # Administración Django
    path('admin/', admin.site.urls),
    
    # Aplicaciones
    path('', include('core.urls')),
    
    # Cuentas y autenticación
    path('accounts/', include('accounts.urls')),
    
    # Módulos principales
    path('inventario/', include('inventario.urls')),
    
    # Módulos adicionales
    path('asignaciones/', include('asignaciones.urls')),
    
    # Módulos de gestión
    path('movimientos/', include('movimientos.urls')),
    
    # Módulos de catálogo
    path('catalogos/', include('catalogos.urls')),
    
    # Módulos de reportes
    path('reportes/', include('reportes.urls')),
]
# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)