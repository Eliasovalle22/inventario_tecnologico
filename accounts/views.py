import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from .forms import RegistroUsuarioForm, PerfilForm

logger = logging.getLogger('django.security')


@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login con protección contra fuerza bruta (django-axes)."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Manejar "recordar sesión"
                if not request.POST.get('remember'):
                    # Si no marcó "recordar", la sesión expira al cerrar el navegador
                    request.session.set_expiry(0)

                full_name = user.get_full_name() or user.username
                messages.success(request, f'¡Bienvenido {full_name}!')
                logger.info(f'Login exitoso para usuario: {username} desde IP: {_get_client_ip(request)}')
                return redirect('core:dashboard')
            else:
                logger.warning(
                    f'Intento de login fallido para usuario: {username} desde IP: {_get_client_ip(request)}'
                )
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            # Puede ser que axes haya bloqueado al usuario
            messages.error(request, 'Error en el formulario. Verifica tus credenciales.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def axes_lockout_view(request, credentials=None, *args, **kwargs):
    """Vista personalizada cuando el usuario es bloqueado por demasiados intentos."""
    logger.warning(
        f'Cuenta bloqueada por exceso de intentos - '
        f'Usuario: {credentials.get("username", "desconocido") if credentials else "desconocido"} '
        f'IP: {_get_client_ip(request)}'
    )
    messages.error(
        request,
        '⚠️ Tu cuenta ha sido bloqueada temporalmente por demasiados intentos fallidos. '
        'Por favor, espera 30 minutos e inténtalo de nuevo o contacta al administrador.'
    )
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'locked_out': True}, status=403)


@login_required
@require_POST
def logout_view(request):
    """Logout seguro — solo acepta peticiones POST para prevenir CSRF via enlaces."""
    username = request.user.username
    logout(request)
    request.session.flush()
    logger.info(f'Logout exitoso para usuario: {username}')
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('accounts:login')


@login_required
@require_http_methods(["GET", "POST"])
def registro_view(request):
    """Registro de nuevos usuarios — solo accesible por superuser o DirectorTI."""
    if not (request.user.is_superuser or request.user.groups.filter(name='DirectorTI').exists()):
        messages.error(request, 'No tienes permiso para registrar usuarios.')
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

            # Crear perfil con datos adicionales
            if hasattr(user, 'perfil'):
                user.perfil.telefono = form.cleaned_data.get('telefono', '')
                user.perfil.departamento = form.cleaned_data.get('departamento', '')
                user.perfil.cargo = form.cleaned_data.get('cargo', '')
                user.perfil.save()

            logger.info(
                f'Nuevo usuario creado: {user.username} por {request.user.username}'
            )
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('accounts:lista_usuarios')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def lista_usuarios(request):
    """Lista de usuarios — solo accesible por superuser o DirectorTI."""
    if not (request.user.is_superuser or request.user.groups.filter(name='DirectorTI').exists()):
        messages.error(request, 'No tienes permiso para ver esta página.')
        return redirect('core:dashboard')

    usuarios = User.objects.all().prefetch_related('groups')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@require_http_methods(["GET", "POST"])
def perfil_view(request):
    """Perfil del usuario — usa formulario con validación."""
    if request.method == 'POST':
        form = PerfilForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Actualizar perfil extendido
            if hasattr(user, 'perfil'):
                user.perfil.telefono = form.cleaned_data.get('telefono', '')
                user.perfil.departamento = form.cleaned_data.get('departamento', '')
                user.perfil.cargo = form.cleaned_data.get('cargo', '')
                user.perfil.save()

            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        if hasattr(request.user, 'perfil'):
            initial.update({
                'telefono': request.user.perfil.telefono,
                'departamento': request.user.perfil.departamento,
                'cargo': request.user.perfil.cargo,
            })
        form = PerfilForm(initial=initial, user=request.user)

    return render(request, 'accounts/perfil.html', {'form': form})


def _get_client_ip(request):
    """Obtiene la IP real del cliente, considerando proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'desconocida')