from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from .forms import RegistroUsuarioForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                full_name = user.get_full_name() or user.username
                messages.success(request, f'¡Bienvenido {full_name}!')
                
                # Redirección basada en el rol
                if user.is_superuser:
                    return redirect('core:dashboard_director')
                elif user.groups.filter(name='DirectorTI').exists():
                    return redirect('core:dashboard_director')
                elif user.groups.filter(name='Asistente').exists():
                    return redirect('core:dashboard_asistente')
                else:
                    return redirect('core:dashboard_basico')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Error en el formulario')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('accounts:login')

@login_required
def registro_view(request):
    # Solo accesible por superuser o director
    if not (request.user.is_superuser or request.user.groups.filter(name='DirectorTI').exists()):
        messages.error(request, 'No tienes permiso para registrar usuarios')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Asignar grupo
            grupo_nombre = form.cleaned_data['grupo']
            grupo = Group.objects.get(name=grupo_nombre)
            user.groups.add(grupo)
            
            messages.success(request, f'Usuario {user.username} creado exitosamente')
            return redirect('accounts:lista_usuarios')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'accounts/registro.html', {'form': form})

@login_required
def lista_usuarios(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='DirectorTI').exists()):
        messages.error(request, 'No tienes permiso para ver esta página')
        return redirect('core:dashboard')
    
    usuarios = User.objects.all().prefetch_related('groups')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def perfil_view(request):
    if request.method == 'POST':
        # Actualizar perfil
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Actualizar perfil extendido si existe
        if hasattr(user, 'perfil'):
            user.perfil.telefono = request.POST.get('telefono', '')
            user.perfil.departamento = request.POST.get('departamento', '')
            user.perfil.cargo = request.POST.get('cargo', '')
            user.perfil.save()
        
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('accounts:perfil')
    
    return render(request, 'accounts/perfil.html')