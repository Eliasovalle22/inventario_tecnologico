from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),
    
    # Rutas de gestión de usuarios
    path('logout/', views.logout_view, name='logout'),
    
    # Rutas de administración de usuarios (solo para superuser o director)
    path('registro/', views.registro_view, name='registro'),
    
    # Rutas de perfil y lista de usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    
    # Ruta de perfil (accesible para todos los usuarios autenticados)
    path('perfil/', views.perfil_view, name='perfil'),
]