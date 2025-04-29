from django.urls import path
from . import views

urlpatterns = [
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('equipos/nuevo/', views.crear_equipo, name='crear_equipo'),
    path('equipos/editar/<int:equipo_id>/', views.editar_equipo, name='editar_equipo'),
    path('equipos/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),
    path('equipos/<int:equipo_id>/nuevo-cambio/', views.crear_cambio_parte, name='crear_cambio_parte'),

]
