from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from inventario.models import Activo
from movimientos.models import Movimiento
from asignaciones.models import Asignacion
from catalogos.models import Estado

@login_required
def dashboard(request):
    """Vista principal del dashboard - Redirige según el rol"""
    if request.user.is_superuser:
        return redirect('core:dashboard_director')
    elif request.user.groups.filter(name='DirectorTI').exists():
        return redirect('core:dashboard_director')
    elif request.user.groups.filter(name='Asistente').exists():
        return redirect('core:dashboard_asistente')
    else:
        return redirect('core:dashboard_basico')

@login_required
def dashboard_director(request):
    """Dashboard para Directores TI y Superusuarios"""
    try:
        total_activos = Activo.objects.count()
    except:
        total_activos = 0
    
    # Activos por estado
    activos_por_estado = []
    try:
        estados = Estado.objects.all()
        for estado in estados:
            count = Activo.objects.filter(estado=estado).count()
            activos_por_estado.append({
                'estado': estado.nombre,
                'count': count,
                'color': estado.color
            })
    except:
        pass
    
    # Últimos movimientos
    try:
        ultimos_movimientos = Movimiento.objects.select_related(
            'activo', 'usuario'
        ).order_by('-fecha')[:10]
    except:
        ultimos_movimientos = []
    
    # Activos recientes
    try:
        activos_recientes = Activo.objects.select_related(
            'categoria', 'marca', 'estado', 'ubicacion', 'responsable'
        ).order_by('-fecha_creacion')[:10]
    except:
        activos_recientes = []
    
    # Activos por categoría para el gráfico
    try:
        activos_por_categoria = Activo.objects.values(
            'categoria__nombre'
        ).annotate(total=Count('id')).order_by('-total')
    except:
        activos_por_categoria = []
    
    context = {
        'total_activos': total_activos,
        'activos_por_estado': activos_por_estado,
        'ultimos_movimientos': ultimos_movimientos,
        'activos_recientes': activos_recientes,
        'activos_por_categoria': activos_por_categoria,
    }
    return render(request, 'core/dashboard_director.html', context)

@login_required
def dashboard_asistente(request):
    """Dashboard para Asistentes"""
    try:
        activos_disponibles = Activo.objects.filter(estado__nombre='Disponible').count()
        activos_asignados = Activo.objects.filter(estado__nombre='Asignado').count()
        mis_asignaciones = Asignacion.objects.filter(
            usuario_asignado=request.user,
            activo_actual=True
        ).count()
    except:
        activos_disponibles = 0
        activos_asignados = 0
        mis_asignaciones = 0
    
    try:
        ultimos_movimientos = Movimiento.objects.filter(
            usuario=request.user
        ).select_related('activo').order_by('-fecha')[:10]
    except:
        ultimos_movimientos = []
    
    try:
        activos_recientes = Activo.objects.all().order_by('-fecha_creacion')[:10]
    except:
        activos_recientes = []
    
    context = {
        'activos_disponibles': activos_disponibles,
        'activos_asignados': activos_asignados,
        'mis_asignaciones': mis_asignaciones,
        'ultimos_movimientos': ultimos_movimientos,
        'activos_recientes': activos_recientes,
    }
    return render(request, 'core/dashboard_asistente.html', context)

@login_required
def dashboard_basico(request):
    """Dashboard para usuarios sin permisos específicos"""
    context = {
        'mensaje': 'No tienes permisos asignados. Contacta al administrador.'
    }
    return render(request, 'core/dashboard_basico.html', context)