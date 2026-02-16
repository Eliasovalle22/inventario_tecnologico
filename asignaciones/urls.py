from django.urls import path
from . import views

app_name = 'asignaciones'

urlpatterns = [
    # URLs para gestión de asignaciones
    path('', views.lista_asignaciones, name='lista'),
    path('dashboard/', views.dashboard_asignaciones, name='dashboard'),
    # URLs para asignar y devolver activos
    path('mis-asignaciones/', views.mis_asignaciones, name='mis_asignaciones'),
    
    # CRUD
    path('nueva/', views.crear_asignacion, name='crear'),
    path('<int:pk>/', views.detalle_asignacion, name='detalle'),
    path('<int:pk>/devolver/', views.devolver_asignacion, name='devolver'),
    path('<int:pk>/eliminar/', views.eliminar_asignacion, name='eliminar'),
]