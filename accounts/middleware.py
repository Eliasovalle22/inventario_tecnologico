import logging
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
import datetime

logger = logging.getLogger('django.security')


class SessionTimeoutMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener la última actividad de la sesión
            last_activity = request.session.get('last_activity')
            now = timezone.now()
            
            # Tiempo de inactividad permitido
            timeout = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800)
            
            if last_activity:
                try:
                    last_activity = datetime.datetime.fromisoformat(last_activity)
                    if timezone.is_naive(last_activity):
                        last_activity = timezone.make_aware(last_activity)
                except (ValueError, TypeError):
                    # Si el formato es inválido, forzar logout por seguridad
                    last_activity = None
                
                if last_activity:
                    inactive_time = (now - last_activity).total_seconds()
                    
                    if inactive_time > timeout:
                        # Registrar en el log
                        username = request.user.username
                        logger.info(
                            f'Sesión expirada por inactividad para usuario: {username} '
                            f'(inactivo {int(inactive_time)}s, límite {timeout}s)'
                        )
                        
                        # Cerrar sesión
                        from django.contrib.auth import logout
                        logout(request)
                        
                        # Mensaje para el usuario
                        messages.warning(
                            request,
                            'Tu sesión ha expirado por inactividad. '
                            'Por favor, inicia sesión nuevamente.'
                        )
                        
                        # Limpiar la sesión
                        request.session.flush()
                        
                        # Redirigir al login
                        return redirect('accounts:login')
            
            # Actualizar la última actividad
            request.session['last_activity'] = now.isoformat()
        
        response = self.get_response(request)
        return response