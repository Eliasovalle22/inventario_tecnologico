from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from inventario.models import Activo
from movimientos.models import Movimiento
from asignaciones.models import Asignacion
from catalogos.models import Estado

@login_required
def dashboard(request):
    """Dashboard unificado - muestra secciones según permisos del usuario"""
    user = request.user
    context = {}
    
    # Verificar si tiene algún permiso relevante
    tiene_permisos = (
        user.is_superuser or
        user.has_perm('inventario.view_activo') or
        user.has_perm('asignaciones.view_asignacion') or
        user.has_perm('movimientos.view_movimiento')
    )
    context['tiene_permisos'] = tiene_permisos
    
    if not tiene_permisos:
        context['mensaje'] = 'No tienes permisos asignados. Contacta al administrador.'
        return render(request, 'core/dashboard.html', context)
    
    # --- Sección: KPIs y estadísticas (inventario) ---
    if user.has_perm('inventario.view_activo') or user.is_superuser:
        try:
            context['total_activos'] = Activo.objects.count()
            
            # Activos por estado
            activos_por_estado = []
            for estado in Estado.objects.all():
                count = Activo.objects.filter(estado=estado).count()
                activos_por_estado.append({
                    'estado': estado.nombre,
                    'count': count,
                    'color': estado.color
                })
            context['activos_por_estado'] = activos_por_estado
            
            # Activos por categoría para el gráfico
            context['activos_por_categoria'] = Activo.objects.values(
                'categoria__nombre'
            ).annotate(total=Count('id')).order_by('-total')
            
            # Activos recientes
            context['activos_recientes'] = Activo.objects.select_related(
                'tipo', 'categoria', 'marca', 'estado', 'ubicacion', 'responsable'
            ).order_by('-fecha_creacion')[:10]
        except:
            context['total_activos'] = 0
            context['activos_por_estado'] = []
            context['activos_por_categoria'] = []
            context['activos_recientes'] = []
    
    # --- Sección: Movimientos ---
    if user.has_perm('movimientos.view_movimiento') or user.is_superuser:
        try:
            context['ultimos_movimientos'] = Movimiento.objects.select_related(
                'activo', 'usuario'
            ).order_by('-fecha')[:10]
        except:
            context['ultimos_movimientos'] = []
    
    # --- Sección: Asignaciones ---
    if user.has_perm('asignaciones.view_asignacion') or user.is_superuser:
        try:
            context['total_asignaciones_activas'] = Asignacion.objects.filter(activo_actual=True).count()
            context['mis_asignaciones'] = Asignacion.objects.filter(
                usuario_asignado=user,
                activo_actual=True
            ).count()
        except:
            context['total_asignaciones_activas'] = 0
            context['mis_asignaciones'] = 0
    
    return render(request, 'core/dashboard.html', context)