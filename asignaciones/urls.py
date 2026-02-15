from django.urls import path
from . import views

app_name = 'asignaciones'

urlpatterns = [
    # URLs para gestión de asignaciones
    path('', views.lista_asignaciones, name='lista'),
    
    path('dashboard/', views.dashboard_asignaciones, name='dashboard'),
    
]