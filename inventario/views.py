from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from .models import Activo
from .forms import ActivoForm
from movimientos.models import Movimiento
from catalogos.models import Estado, TipoActivo

@login_required
@permission_required('inventario.view_activo', raise_exception=True)
def lista_activos(request):
    # Obtener todos los activos con relaciones
    activos_list = Activo.objects.select_related(
        'tipo', 'categoria', 'marca', 'estado', 'ubicacion', 'responsable'
    ).all().order_by('-fecha_creacion')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        activos_list = activos_list.filter(
            Q(codigo__icontains=query) |
            Q(modelo__icontains=query) |
            Q(marca__nombre__icontains=query) |
            Q(responsable__first_name__icontains=query) |
            Q(responsable__last_name__icontains=query)
        )
    
    # Filtros adicionales
    estado = request.GET.get('estado')
    if estado:
        activos_list = activos_list.filter(estado_id=estado)
    
    tipo = request.GET.get('tipo')
    if tipo:
        activos_list = activos_list.filter(tipo_id=tipo)
    
    # Obtener listas para filtros
    estados = Estado.objects.all()
    tipos = TipoActivo.objects.all()
    
    context = {
        'activos': activos_list,
        'estados': estados,
        'tipos': tipos,
        'query': query,
        'filtro_estado': estado,
        'filtro_tipo': tipo,
    }
    return render(request, 'inventario/lista_activos.html', context)

@login_required
@permission_required('inventario.view_activo', raise_exception=True)
def detalle_activo(request, pk):
    activo = get_object_or_404(
        Activo.objects.select_related(
            'tipo', 'categoria', 'marca', 'estado', 'ubicacion', 'responsable', 'creado_por'
        ),
        pk=pk
    )
    
    # Obtener movimientos del activo
    movimientos = activo.movimientos.select_related('usuario').all().order_by('-fecha')[:10]
    
    # Obtener historial de asignaciones
    asignaciones = activo.asignaciones.select_related('usuario_asignado', 'asignado_por').all().order_by('-fecha_asignacion')[:5]
    
    context = {
        'activo': activo,
        'movimientos': movimientos,
        'asignaciones': asignaciones,
    }
    return render(request, 'inventario/detalle_activo.html', context)

@login_required
@permission_required('inventario.add_activo', raise_exception=True)
def crear_activo(request):
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            activo = form.save(commit=False)
            activo.creado_por = request.user
            activo.save()
            
            # Registrar movimiento de creación
            Movimiento.objects.create(
                activo=activo,
                tipo='ENTRADA',
                usuario=request.user,
                ubicacion_destino=activo.ubicacion,
                estado_destino=activo.estado,
                observaciones=f"Activo creado por {request.user.get_full_name()}"
            )
            
            messages.success(request, f'Activo {activo.codigo} creado exitosamente.')
            
            if 'guardar_y_nuevo' in request.POST:
                return redirect('inventario:crear')
            
            return redirect('inventario:detalle', pk=activo.pk)
    else:
        form = ActivoForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Activo',
        'boton': 'Crear Activo'
    }
    return render(request, 'inventario/activo_form.html', context)

@login_required
@permission_required('inventario.change_activo', raise_exception=True)
def editar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    old_values = {
        'estado': activo.estado,
        'ubicacion': activo.ubicacion,
        'responsable': activo.responsable,
    }
    
    if request.method == 'POST':
        form = ActivoForm(request.POST, instance=activo)
        if form.is_valid():
            activo_actualizado = form.save()
            
            # Verificar cambios y registrar movimientos
            new_values = {
                'estado': activo_actualizado.estado,
                'ubicacion': activo_actualizado.ubicacion,
                'responsable': activo_actualizado.responsable,
            }
            
            # Registrar cambios significativos
            if old_values['estado'] != new_values['estado']:
                Movimiento.objects.create(
                    activo=activo_actualizado,
                    tipo='CAMBIO_ESTADO',
                    usuario=request.user,
                    estado_origen=old_values['estado'],
                    estado_destino=new_values['estado'],
                    observaciones=f"Cambio de estado por {request.user.get_full_name()}"
                )
            
            if old_values['ubicacion'] != new_values['ubicacion']:
                Movimiento.objects.create(
                    activo=activo_actualizado,
                    tipo='TRASLADO',
                    usuario=request.user,
                    ubicacion_origen=old_values['ubicacion'],
                    ubicacion_destino=new_values['ubicacion'],
                    observaciones=f"Traslado realizado por {request.user.get_full_name()}"
                )
            
            messages.success(request, f'Activo {activo.codigo} actualizado exitosamente.')
            return redirect('inventario:detalle', pk=activo.pk)
    else:
        form = ActivoForm(instance=activo)
    
    context = {
        'form': form,
        'activo': activo,
        'titulo': f'Editar Activo: {activo.codigo}',
        'boton': 'Actualizar Activo'
    }
    return render(request, 'inventario/activo_form.html', context)

@login_required
@permission_required('inventario.delete_activo', raise_exception=True)
def eliminar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    
    if request.method == 'POST':
        codigo = activo.codigo
        # Registrar movimiento de baja
        Movimiento.objects.create(
            activo=activo,
            tipo='BAJA',
            usuario=request.user,
            observaciones=f"Activo dado de baja por {request.user.get_full_name()}"
        )
        activo.delete()
        messages.success(request, f'Activo {codigo} eliminado exitosamente.')
        return redirect('inventario:lista')
    
    context = {
        'activo': activo
    }
    return render(request, 'inventario/confirmar_eliminar.html', context)