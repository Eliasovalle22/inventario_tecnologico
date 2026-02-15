from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Asignacion

@login_required
@permission_required('asignaciones.view_asignacion', raise_exception=True)
def lista_asignaciones(request):

    asignaciones = Asignacion.objects.select_related(
        'activo', 'usuario_asignado', 'asignado_por'
    ).all().order_by('-fecha_asignacion')[:20]  # Solo las últimas 20
    
    context = {
        'asignaciones': asignaciones,
        'es_desarrollo': True,
    }
    return render(request, 'asignaciones/lista.html', context)

@login_required
def dashboard_asignaciones(request):
    context = {
        'total_asignaciones': Asignacion.objects.count(),
        'activas': Asignacion.objects.filter(activo_actual=True).count(),
    }
    return render(request, 'asignaciones/dashboard.html', context)