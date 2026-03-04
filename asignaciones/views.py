from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from catalogos.models import Estado
from .models import Asignacion
from .forms import AsignacionForm, DevolucionForm, AsignacionFiltroForm
from inventario.models import Activo
from movimientos.models import Movimiento
from django.contrib.auth.models import User
from django.db import models

@login_required
@permission_required('asignaciones.view_asignacion', raise_exception=True)
def lista_asignaciones(request):
    """Lista todas las asignaciones con filtros"""
    asignaciones_list = Asignacion.objects.select_related(
        'activo', 'usuario_asignado', 'asignado_por'
    ).all().order_by('-fecha_asignacion')
    
    # Aplicar filtros
    filter_form = AsignacionFiltroForm(request.GET)
    if filter_form.is_valid():
        estado = filter_form.cleaned_data.get('estado')
        usuario = filter_form.cleaned_data.get('usuario')
        activo = filter_form.cleaned_data.get('activo')
        fecha_desde = filter_form.cleaned_data.get('fecha_desde')
        fecha_hasta = filter_form.cleaned_data.get('fecha_hasta')
        
        if estado == 'activas':
            asignaciones_list = asignaciones_list.filter(activo_actual=True)
        elif estado == 'devueltas':
            asignaciones_list = asignaciones_list.filter(activo_devuelto=True)
        elif estado == 'vencidas':
            asignaciones_list = asignaciones_list.filter(
                activo_actual=True,
                fecha_estimada_devolucion__lt=timezone.now()
            )
        
        if usuario:
            asignaciones_list = asignaciones_list.filter(
                Q(usuario_asignado__username__icontains=usuario) |
                Q(usuario_asignado__first_name__icontains=usuario) |
                Q(usuario_asignado__last_name__icontains=usuario)
            )
        
        if activo:
            asignaciones_list = asignaciones_list.filter(
                Q(activo__codigo__icontains=activo) |
                Q(activo__serial__icontains=activo)
            )
        
        if fecha_desde:
            asignaciones_list = asignaciones_list.filter(
                fecha_asignacion__date__gte=fecha_desde
            )
        
        if fecha_hasta:
            asignaciones_list = asignaciones_list.filter(
                fecha_asignacion__date__lte=fecha_hasta
            )
    
    # Estadísticas
    total_activas = Asignacion.objects.filter(activo_actual=True).count()
    total_vencidas = Asignacion.objects.filter(
        activo_actual=True,
        fecha_estimada_devolucion__lt=timezone.now()
    ).count()
    total_usuarios = User.objects.filter(
        asignaciones_recibidas__activo_actual=True
    ).distinct().count()
    
    context = {
        'asignaciones': asignaciones_list,
        'filter_form': filter_form,
        'total_asignaciones': asignaciones_list.count(),
        'total_activas': total_activas,
        'total_vencidas': total_vencidas,
        'total_usuarios': total_usuarios,
        'now': timezone.now(),
    }
    return render(request, 'asignaciones/lista.html', context)

@login_required
@permission_required('asignaciones.add_asignacion', raise_exception=True)
def crear_asignacion(request):
    """Crear una nueva asignación"""
    if request.method == 'POST':
        form = AsignacionForm(request.POST, request=request)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.asignado_por = request.user
            asignacion.save()
            
            # Registrar movimiento
            Movimiento.objects.create(
                activo=asignacion.activo,
                tipo='ASIGNACION',
                usuario=request.user,
                responsable_nuevo=asignacion.usuario_asignado,
                observaciones=f"Asignación #{asignacion.id}: {asignacion.motivo}",
                asignacion=asignacion
            )
            
            messages.success(
                request, 
                f'Activo {asignacion.activo.codigo} asignado a {asignacion.usuario_asignado.get_full_name()}'
            )
            return redirect('asignaciones:detalle', pk=asignacion.pk)
    else:
        # Precargar activo si viene por URL
        initial = {}
        activo_id = request.GET.get('activo')
        if activo_id:
            try:
                activo = Activo.objects.get(pk=activo_id)
                if activo.estado.nombre in ['Disponible', 'En bodega']:
                    initial['activo'] = activo
                else:
                    messages.warning(request, 'Este activo no está disponible para asignación')
            except Activo.DoesNotExist:
                pass
        
        # Precargar usuario si viene por URL
        usuario_id = request.GET.get('usuario')
        if usuario_id:
            try:
                usuario = User.objects.get(pk=usuario_id)
                initial['usuario_asignado'] = usuario
            except User.DoesNotExist:
                pass
        
        form = AsignacionForm(initial=initial, request=request)
    
    context = {
        'form': form,
        'titulo': 'Nueva Asignación',
        'boton': 'Asignar Activo'
    }
    return render(request, 'asignaciones/asignacion_form.html', context)

@login_required
@permission_required('asignaciones.view_asignacion', raise_exception=True)
def detalle_asignacion(request, pk):
    """Ver detalle de una asignación"""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related(
            'activo', 'usuario_asignado', 'asignado_por'
        ),
        pk=pk
    )
    
    # Obtener movimientos relacionados
    movimientos = asignacion.movimientos.all().order_by('-fecha')
    
    # Verificar si está vencida
    vencida = False
    if (asignacion.activo_actual and 
        asignacion.fecha_estimada_devolucion and 
        asignacion.fecha_estimada_devolucion < timezone.now()):
        vencida = True
    
    context = {
        'asignacion': asignacion,
        'movimientos': movimientos,
        'vencida': vencida,
    }
    return render(request, 'asignaciones/detalle.html', context)

@login_required
@permission_required('asignaciones.change_asignacion', raise_exception=True)
def devolver_asignacion(request, pk):
    """Registrar devolución de un activo"""
    asignacion = get_object_or_404(Asignacion, pk=pk, activo_actual=True)
    
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            # Registrar devolución
            asignacion.devolver(
                fecha_devolucion=form.cleaned_data['fecha_devolucion'],
                observaciones=form.cleaned_data['observaciones']
            )
            
            # Actualizar estado del activo según condición reportada
            activo = asignacion.activo
            estado_activo_form = form.cleaned_data['estado_activo']
            if estado_activo_form == 'REPARACION':
                estado_reparacion = Estado.objects.filter(nombre='En reparación').first()
                if estado_reparacion:
                    activo.estado = estado_reparacion
            elif estado_activo_form == 'MALO':
                estado_malo = Estado.objects.filter(nombre='Malo').first()
                if estado_malo:
                    activo.estado = estado_malo
            else:
                # Estado BUENO o REGULAR: restaurar a "En bodega"
                estado_bodega = Estado.objects.filter(nombre='En bodega').first()
                if estado_bodega:
                    activo.estado = estado_bodega
            
            # Guardar observaciones del estado
            if form.cleaned_data['observaciones_estado']:
                activo.observaciones = (activo.observaciones or "") + \
                    f"\n[Devolución] {form.cleaned_data['observaciones_estado']}"
            activo.save()
            
            messages.success(request, 'Devolución registrada exitosamente')
            return redirect('asignaciones:detalle', pk=asignacion.pk)
    else:
        form = DevolucionForm(initial={
            'fecha_devolucion': timezone.now()
        })
    
    context = {
        'asignacion': asignacion,
        'form': form,
    }
    return render(request, 'asignaciones/devolver.html', context)

@login_required
def mis_asignaciones(request):
    asignaciones = Asignacion.objects.filter(
        usuario_asignado=request.user
    ).select_related('activo', 'asignado_por').order_by('-fecha_asignacion')
    
    activas = asignaciones.filter(activo_actual=True)
    historial = asignaciones.filter(activo_actual=False)
    
    context = {
        'activas': activas,
        'historial': historial,
    }
    return render(request, 'asignaciones/mis_asignaciones.html', context)

@login_required
@permission_required('asignaciones.view_asignacion', raise_exception=True)
def dashboard_asignaciones(request):
    # Estadísticas generales
    total_asignaciones = Asignacion.objects.count()
    activas = Asignacion.objects.filter(activo_actual=True).count()
    devueltas = Asignacion.objects.filter(activo_devuelto=True).count()
    
    # Vencidas
    vencidas = Asignacion.objects.filter(
        activo_actual=True,
        fecha_estimada_devolucion__lt=timezone.now()
    ).count()
    
    # Próximas a vencer (próximos 3 días)
    proximas_vencer = Asignacion.objects.filter(
        activo_actual=True,
        fecha_estimada_devolucion__range=[
            timezone.now(),
            timezone.now() + timedelta(days=3)
        ]
    ).count()
    
    # Top usuarios con más asignaciones
    from django.contrib.auth.models import User
    top_usuarios = User.objects.filter(
        asignaciones_recibidas__isnull=False
    ).annotate(
        total=Count('asignaciones_recibidas'),
        activas=Count('asignaciones_recibidas', filter=models.Q(asignaciones_recibidas__activo_actual=True))
    ).order_by('-total')[:10]
    
    # Top activos más asignados
    from inventario.models import Activo
    top_activos = Activo.objects.filter(
        asignaciones__isnull=False
    ).annotate(
        total=Count('asignaciones')
    ).select_related('marca', 'estado').order_by('-total')[:10]
    
    context = {
        'total_asignaciones': total_asignaciones,
        'activas': activas,
        'devueltas': devueltas,
        'vencidas': vencidas,
        'proximas_vencer': proximas_vencer,
        'top_usuarios': top_usuarios,
        'top_activos': top_activos,
    }
    return render(request, 'asignaciones/dashboard.html', context)

@login_required
@permission_required('asignaciones.delete_asignacion', raise_exception=True)
def eliminar_asignacion(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    
    if asignacion.activo_actual:
        messages.error(request, 'No se puede eliminar una asignación activa')
        return redirect('asignaciones:detalle', pk=pk)
    
    if request.method == 'POST':
        codigo = asignacion.activo.codigo
        asignacion.delete()
        messages.success(request, f'Asignación del activo {codigo} eliminada')
        return redirect('asignaciones:lista')
    
    context = {
        'asignacion': asignacion
    }
    return render(request, 'asignaciones/confirmar_eliminar.html', context)