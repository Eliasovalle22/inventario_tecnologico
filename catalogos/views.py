from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Categoria, Marca, Ubicacion, Sede, Estado, TipoActivo

# ========== CATEGORÍAS ==========
@login_required
@permission_required('catalogos.view_categoria', raise_exception=True)
def lista_categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'catalogos/categorias.html', {'categorias': categorias})

@login_required
@permission_required('catalogos.add_categoria', raise_exception=True)
def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('catalogos:categorias')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/categoria_form.html')

@login_required
@permission_required('catalogos.change_categoria', raise_exception=True)
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            categoria.nombre = nombre
            categoria.descripcion = request.POST.get('descripcion')
            categoria.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('catalogos:categorias')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/categoria_form.html', {'categoria': categoria})

@login_required
@permission_required('catalogos.delete_categoria', raise_exception=True)
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    messages.success(request, 'Categoría eliminada exitosamente')
    return redirect('catalogos:categorias')

# ========== MARCAS ==========
@login_required
@permission_required('catalogos.view_marca', raise_exception=True)
def lista_marcas(request):
    marcas = Marca.objects.all().order_by('nombre')
    return render(request, 'catalogos/marcas.html', {'marcas': marcas})

@login_required
@permission_required('catalogos.add_marca', raise_exception=True)
def crear_marca(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            Marca.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, 'Marca creada exitosamente')
            return redirect('catalogos:marcas')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/marca_form.html')

@login_required
@permission_required('catalogos.change_marca', raise_exception=True)
def editar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            marca.nombre = nombre
            marca.descripcion = request.POST.get('descripcion')
            marca.save()
            messages.success(request, 'Marca actualizada exitosamente')
            return redirect('catalogos:marcas')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/marca_form.html', {'marca': marca})

@login_required
@permission_required('catalogos.delete_marca', raise_exception=True)
def eliminar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)
    marca.delete()
    messages.success(request, 'Marca eliminada exitosamente')
    return redirect('catalogos:marcas')

# ========== UBICACIONES ==========
@login_required
@permission_required('catalogos.view_ubicacion', raise_exception=True)
def lista_ubicaciones(request):
    ubicaciones = Ubicacion.objects.all().order_by('nombre')
    return render(request, 'catalogos/ubicaciones.html', {'ubicaciones': ubicaciones})

@login_required
@permission_required('catalogos.add_ubicacion', raise_exception=True)
def crear_ubicacion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        if nombre:
            Ubicacion.objects.create(
                nombre=nombre, 
                direccion=direccion
            )
            messages.success(request, 'Ubicación creada exitosamente')
            return redirect('catalogos:ubicaciones')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/ubicacion_form.html')

@login_required
@permission_required('catalogos.change_ubicacion', raise_exception=True)
def editar_ubicacion(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            ubicacion.nombre = nombre
            ubicacion.direccion = request.POST.get('direccion')
            ubicacion.save()
            messages.success(request, 'Ubicación actualizada exitosamente')
            return redirect('catalogos:ubicaciones')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/ubicacion_form.html', {'ubicacion': ubicacion})

@login_required
@permission_required('catalogos.delete_ubicacion', raise_exception=True)
def eliminar_ubicacion(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    ubicacion.delete()
    messages.success(request, 'Ubicación eliminada exitosamente')
    return redirect('catalogos:ubicaciones')

# ========== SEDES ==========
@login_required
@permission_required('catalogos.view_sede', raise_exception=True)
def lista_sedes(request):
    sedes = Sede.objects.all().order_by('nombre')
    return render(request, 'catalogos/sedes.html', {'sedes': sedes})

@login_required
@permission_required('catalogos.add_sede', raise_exception=True)
def crear_sede(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        if nombre:
            Sede.objects.create(
                nombre=nombre, 
                descripcion=descripcion,
                direccion=direccion,
                ciudad=ciudad
            )
            messages.success(request, 'Sede creada exitosamente')
            return redirect('catalogos:sedes')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/sede_form.html')

@login_required
@permission_required('catalogos.change_sede', raise_exception=True)
def editar_sede(request, pk):
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            sede.nombre = nombre
            sede.descripcion = request.POST.get('descripcion')
            sede.direccion = request.POST.get('direccion')
            sede.ciudad = request.POST.get('ciudad')
            sede.save()
            messages.success(request, 'Sede actualizada exitosamente')
            return redirect('catalogos:sedes')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/sede_form.html', {'sede': sede})

@login_required
@permission_required('catalogos.delete_sede', raise_exception=True)
def eliminar_sede(request, pk):
    sede = get_object_or_404(Sede, pk=pk)
    sede.delete()
    messages.success(request, 'Sede eliminada exitosamente')
    return redirect('catalogos:sedes')

# ========== ESTADOS ==========
@login_required
@permission_required('catalogos.view_estado', raise_exception=True)
def lista_estados(request):
    estados = Estado.objects.all().order_by('nombre')
    return render(request, 'catalogos/estados.html', {'estados': estados})

@login_required
@permission_required('catalogos.add_estado', raise_exception=True)
def crear_estado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        color = request.POST.get('color', '#6c757d')
        if nombre:
            Estado.objects.create(
                nombre=nombre, 
                descripcion=descripcion,
                color=color
            )
            messages.success(request, 'Estado creado exitosamente')
            return redirect('catalogos:estados')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/estado_form.html')

@login_required
@permission_required('catalogos.change_estado', raise_exception=True)
def editar_estado(request, pk):
    estado = get_object_or_404(Estado, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            estado.nombre = nombre
            estado.descripcion = request.POST.get('descripcion')
            estado.color = request.POST.get('color', estado.color)
            estado.save()
            messages.success(request, 'Estado actualizado exitosamente')
            return redirect('catalogos:estados')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/estado_form.html', {'estado': estado})

@login_required
@permission_required('catalogos.delete_estado', raise_exception=True)
def eliminar_estado(request, pk):
    estado = get_object_or_404(Estado, pk=pk)
    estado.delete()
    messages.success(request, 'Estado eliminado exitosamente')
    return redirect('catalogos:estados')

# ========== TIPOS DE ACTIVO ==========
@login_required
@permission_required('catalogos.view_tipoactivo', raise_exception=True)
def lista_tipos_activo(request):
    tipos = TipoActivo.objects.all().order_by('nombre')
    return render(request, 'catalogos/tipos_activo.html', {'tipos': tipos})

@login_required
@permission_required('catalogos.add_tipoactivo', raise_exception=True)
def crear_tipo_activo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            TipoActivo.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, 'Tipo de activo creado exitosamente')
            return redirect('catalogos:tipos_activo')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/tipo_activo_form.html')

@login_required
@permission_required('catalogos.change_tipoactivo', raise_exception=True)
def editar_tipo_activo(request, pk):
    tipo = get_object_or_404(TipoActivo, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            tipo.nombre = nombre
            tipo.descripcion = request.POST.get('descripcion')
            tipo.save()
            messages.success(request, 'Tipo de activo actualizado exitosamente')
            return redirect('catalogos:tipos_activo')
        else:
            messages.error(request, 'El nombre es obligatorio')
    return render(request, 'catalogos/tipo_activo_form.html', {'tipo': tipo})

@login_required
@permission_required('catalogos.delete_tipoactivo', raise_exception=True)
def eliminar_tipo_activo(request, pk):
    tipo = get_object_or_404(TipoActivo, pk=pk)
    tipo.delete()
    messages.success(request, 'Tipo de activo eliminado exitosamente')
    return redirect('catalogos:tipos_activo')