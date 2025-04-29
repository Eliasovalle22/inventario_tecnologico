from django.shortcuts import render, get_object_or_404, redirect
from .models import Equipo, Sede, Dependencia
from .forms import EquipoForm, CambioParteForm
# Create your views here.

def lista_equipos(request):
    equipos = Equipo.objects.select_related('salon__dependencia__sede')

    # Filtros
    sede_id = request.GET.get('sede')
    dependencia_id = request.GET.get('dependencia')
    asignado = request.GET.get('asignado_a')

    if sede_id:
        equipos = equipos.filter(salon__dependencia__sede__id=sede_id)

    if dependencia_id:
        equipos = equipos.filter(salon__dependencia__id=dependencia_id)

    if asignado:
        equipos = equipos.filter(asignado_a__icontains=asignado)

    sedes = Sede.objects.all()
    dependencias = Dependencia.objects.all()

    context = {
        'equipos': equipos,
        'sedes': sedes,
        'dependencias': dependencias,
        'filtros': {
            'sede': sede_id,
            'dependencia': dependencia_id,
            'asignado_a': asignado,
        }
    }
    return render(request, 'equipos/lista_equipos.html', context)

def detalle_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    return render(request, 'equipos/detalle_equipo.html', {'equipo': equipo})


#
# ---------------------------- VISTAS PARA CREAR EQUIPOS Y REALIZAR CAMBIOS ---------------------------------
#

def crear_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_equipos')
    else:
        form = EquipoForm()
    return render(request, 'equipos/form_equipo.html', {'form': form})

def crear_cambio_parte(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    if request.method == 'POST':
        form = CambioParteForm(request.POST)
        if form.is_valid():
            cambio = form.save(commit=False)
            cambio.equipo = equipo
            cambio.save()
            return redirect('detalle_equipo', equipo_id=equipo.id)
    else:
        form = CambioParteForm(initial={'equipo': equipo})
    return render(request, 'equipos/form_cambio_parte.html', {'form': form, 'equipo': equipo})


def crear_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_equipos')
    else:
        form = EquipoForm()
    return render(request, 'equipos/form_equipo.html', {'form': form})

def editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            return redirect('lista_equipos')
    else:
        form = EquipoForm(instance=equipo)
    return render(request, 'equipos/form_equipo.html', {'form': form})