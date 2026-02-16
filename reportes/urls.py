from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Dashboard de reportes
    path('', views.dashboard_reportes, name='dashboard'),
    
    # Reportes de inventario
    path('inventario/', views.reporte_inventario, name='inventario'),
    path('inventario/excel/', views.exportar_inventario_excel, name='inventario_excel'),
    path('inventario/pdf/', views.exportar_inventario_pdf, name='inventario_pdf'),
    
    # Reportes por categoría
    path('categorias/', views.reporte_categorias, name='categorias'),
    path('categorias/excel/', views.exportar_categorias_excel, name='categorias_excel'),
    
    # Reportes de asignaciones
    path('asignaciones/', views.reporte_asignaciones, name='asignaciones'),
    path('asignaciones/excel/', views.exportar_asignaciones_excel, name='asignaciones_excel'),
    path('asignaciones/pdf/', views.exportar_asignaciones_pdf, name='asignaciones_pdf'),
    
    # Reportes de movimientos
    path('movimientos/', views.reporte_movimientos, name='movimientos'),
    path('movimientos/excel/', views.exportar_movimientos_excel, name='movimientos_excel'),
    
    # Reporte por responsable
    path('responsable/<int:user_id>/', views.reporte_por_responsable, name='por_responsable'),
    path('responsable/excel/<int:user_id>/', views.exportar_responsable_excel, name='responsable_excel'),
    
    # Gráficos
    path('graficos/estados/', views.datos_grafico_estados, name='grafico_estados'),
    path('graficos/categorias/', views.datos_grafico_categorias, name='grafico_categorias'),
    path('graficos/mensual/', views.datos_grafico_mensual, name='grafico_mensual'),
]