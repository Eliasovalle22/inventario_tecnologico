from django.urls import path
from . import views

app_name = 'movimientos'

urlpatterns = [
    # Listado de movimientos
    path('', views.lista_movimientos, name='lista'),
    
    # Dashboard de movimientos
    path('dashboard/', views.dashboard_movimientos, name='dashboard'),
    
    # Detalle de movimiento
    path('nuevo/', views.crear_movimiento, name='crear'),
    
    # Detalle de movimiento
    path('<int:pk>/', views.detalle_movimiento, name='detalle'),
    
    # Movimientos por activo
    path('activo/<int:activo_id>/', views.movimientos_por_activo, name='por_activo'),
]