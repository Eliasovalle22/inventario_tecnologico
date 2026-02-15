from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Ruta principal del dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Rutas para dashboards específicos por rol
    path('dashboard/director/', views.dashboard_director, name='dashboard_director'),
    
    # Rutas para dashboards específicos por rol
    path('dashboard/asistente/', views.dashboard_asistente, name='dashboard_asistente'),
    
    # Rutas para dashboards específicos por rol
    path('dashboard/basico/', views.dashboard_basico, name='dashboard_basico'),
]