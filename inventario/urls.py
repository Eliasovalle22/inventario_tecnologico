from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Activos
    path('', views.lista_activos, name='lista'),
    
    # Detalles, creación, edición y eliminación de activos
    path('nuevo/', views.crear_activo, name='crear'),
    
    # Detalles, edición y eliminación de activos
    path('<int:pk>/', views.detalle_activo, name='detalle'),
    
    # Edición y eliminación de activos
    path('<int:pk>/editar/', views.editar_activo, name='editar'),
    
    # Eliminación de activos
    path('<int:pk>/eliminar/', views.eliminar_activo, name='eliminar'),
    
    # Importación de activos
    path('descargar-plantilla/', views.descargar_plantilla_activos, name='descargar_plantilla'),
    path('importar/', views.importar_activos, name='importar'),
]