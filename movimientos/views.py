from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q

from catalogos.models import Estado
from .models import Movimiento
from .forms import MovimientoForm, MovimientoFiltroForm
from inventario.models import Activo
from django.core.paginator import Paginator

@login_required
@permission_required('movimientos.view_movimiento', raise_exception=True)
def lista_movimientos(request):
    movimientos_list = Movimiento.objects.select_related(
        'activo', 'usuario', 'ubicacion_destino', 'estado_destino'
    ).all().order_by('-fecha')
    
    # Aplicar filtros
    filter_form = MovimientoFiltroForm(request.GET)
    if filter_form.is_valid():
        fecha_desde = filter_form.cleaned_data.get('fecha_desde')
        fecha_hasta = filter_form.cleaned_data.get('fecha_hasta')
        tipo = filter_form.cleaned_data.get('tipo')
        activo = filter_form.cleaned_data.get('activo')
        usuario = filter_form.cleaned_data.get('usuario')
        
        if fecha_desde:
            movimientos_list = movimientos_list.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            movimientos_list = movimientos_list.filter(fecha__date__lte=fecha_hasta)
        if tipo:
            movimientos_list = movimientos_list.filter(tipo=tipo)
        if activo:
            movimientos_list = movimientos_list.filter(
                Q(activo__codigo__icontains=activo) |
                Q(activo__serial__icontains=activo)
            )
        if usuario:
            movimientos_list = movimientos_list.filter(
                Q(usuario__username__icontains=usuario) |
                Q(usuario__first_name__icontains=usuario) |
                Q(usuario__last_name__icontains=usuario)
            )
    
    # Estadísticas rápidas
    total_movimientos = movimientos_list.count()
    movimientos_hoy = movimientos_list.filter(fecha__date=timezone.now().date()).count()
    
    # Conteo por tipo
    tipos_count = {}
    for tipo, _ in Movimiento.TIPO_MOVIMIENTO:
        count = movimientos_list.filter(tipo=tipo).count()
        if count > 0:
            tipos_count[tipo] = count
    
    context = {
        'movimientos': movimientos_list,
        'filter_form': filter_form,
        'total_movimientos': total_movimientos,
        'movimientos_hoy': movimientos_hoy,
        'tipos_count': tipos_count,
    }
    return render(request, 'movimientos/lista_movimientos.html', context)

@login_required
@permission_required('movimientos.view_movimiento', raise_exception=True)
def detalle_movimiento(request, pk):
    movimiento = get_object_or_404(
        Movimiento.objects.select_related(
            'activo', 'usuario', 'ubicacion_origen', 'ubicacion_destino',
            'estado_origen', 'estado_destino', 'responsable_anterior',
            'responsable_nuevo', 'asignacion'
        ),
        pk=pk
    )
    
    context = {
        'movimiento': movimiento
    }
    return render(request, 'movimientos/detalle_movimiento.html', context)

@login_required
@permission_required('movimientos.add_movimiento', raise_exception=True)
def crear_movimiento(request):
    
    if request.method == 'POST':
        form = MovimientoForm(request.POST, request=request)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            
            # Obtener valores anteriores
            activo = movimiento.activo
            movimiento.ubicacion_origen = activo.ubicacion
            movimiento.estado_origen = activo.estado
            movimiento.responsable_anterior = activo.responsable
            
            # Guardar el movimiento
            movimiento.save()
            
            # Actualizar el activo según el tipo de movimiento
            if movimiento.tipo == 'TRASLADO' and movimiento.ubicacion_destino:
                activo.ubicacion = movimiento.ubicacion_destino
                
            elif movimiento.tipo == 'CAMBIO_ESTADO' and movimiento.estado_destino:
                activo.estado = movimiento.estado_destino
                
            elif movimiento.tipo == 'ASIGNACION' and movimiento.responsable_nuevo:
                activo.responsable = movimiento.responsable_nuevo
                estado_asignado = Estado.objects.filter(nombre='Asignado').first()
                if estado_asignado:
                    activo.estado = estado_asignado
                    
            elif movimiento.tipo == 'DEVOLUCION':
                activo.responsable = None
                estado_disponible = Estado.objects.filter(nombre='Disponible').first()
                if estado_disponible:
                    activo.estado = estado_disponible
                    
            elif movimiento.tipo == 'REPARACION':
                estado_reparacion = Estado.objects.filter(nombre='En reparación').first()
                if estado_reparacion:
                    activo.estado = estado_reparacion
            
            activo.save()
            
            messages.success(request, f'Movimiento {movimiento.get_tipo_display()} registrado exitosamente.')
            return redirect('movimientos:detalle', pk=movimiento.pk)
    else:
        # Si viene un activo específico, precargarlo
        activo_id = request.GET.get('activo')
        initial = {}
        if activo_id:
            try:
                activo = Activo.objects.get(pk=activo_id)
                initial['activo'] = activo
            except Activo.DoesNotExist:
                pass
        form = MovimientoForm(initial=initial, request=request)
    
    context = {
        'form': form,
        'titulo': 'Registrar Movimiento Manual',
        'boton': 'Registrar Movimiento'
    }
    return render(request, 'movimientos/movimiento_form.html', context)

@login_required
@permission_required('movimientos.view_movimiento', raise_exception=True)
def movimientos_por_activo(request, activo_id):
    """Ver todos los movimientos de un activo específico"""
    activo = get_object_or_404(Activo, pk=activo_id)
    movimientos = activo.movimientos.select_related('usuario').all().order_by('-fecha')
    
    context = {
        'activo': activo,
        'movimientos': movimientos,
    }
    return render(request, 'movimientos/por_activo.html', context)

@login_required
def dashboard_movimientos(request):
    """Dashboard con estadísticas de movimientos"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Movimientos por día (últimos 30 días)
    fecha_limite = timezone.now() - timedelta(days=30)
    movimientos_recientes = Movimiento.objects.filter(fecha__gte=fecha_limite)
    
    movimientos_por_dia = movimientos_recientes.extra(
        {'dia': "date(fecha)"}
    ).values('dia').annotate(total=Count('id')).order_by('dia')
    
    # Movimientos por tipo
    movimientos_por_tipo = Movimiento.objects.values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Usuarios más activos
    usuarios_top = Movimiento.objects.values(
        'usuario__username', 'usuario__first_name', 'usuario__last_name'
    ).annotate(total=Count('id')).order_by('-total')[:10]
    
    context = {
        'movimientos_por_dia': list(movimientos_por_dia),
        'movimientos_por_tipo': movimientos_por_tipo,
        'usuarios_top': usuarios_top,
        'total_movimientos': Movimiento.objects.count(),
        'movimientos_30dias': movimientos_recientes.count(),
    }
    return render(request, 'movimientos/dashboard.html', context)