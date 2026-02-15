from django.urls import path
from . import views

app_name = 'catalogos'

urlpatterns = [
    # Categorías
    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Marcas
    path('marcas/', views.lista_marcas, name='marcas'),
    path('marcas/crear/', views.crear_marca, name='crear_marca'),
    path('marcas/<int:pk>/editar/', views.editar_marca, name='editar_marca'),
    path('marcas/<int:pk>/eliminar/', views.eliminar_marca, name='eliminar_marca'),
    
    # Ubicaciones
    path('ubicaciones/', views.lista_ubicaciones, name='ubicaciones'),
    path('ubicaciones/crear/', views.crear_ubicacion, name='crear_ubicacion'),
    path('ubicaciones/<int:pk>/editar/', views.editar_ubicacion, name='editar_ubicacion'),
    path('ubicaciones/<int:pk>/eliminar/', views.eliminar_ubicacion, name='eliminar_ubicacion'),
    
    # Estados
    path('estados/', views.lista_estados, name='estados'),
    path('estados/crear/', views.crear_estado, name='crear_estado'),
    path('estados/<int:pk>/editar/', views.editar_estado, name='editar_estado'),
    path('estados/<int:pk>/eliminar/', views.eliminar_estado, name='eliminar_estado'),
]