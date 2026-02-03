"""
Context processors para gamificación y privacidad
Hace disponible información de gamificación y preferencias en todos los templates
"""

def gamificacion_context(request):
    """
    Agrega información de gamificación y privacidad al contexto de todos los templates
    """
    context = {}

    if request.user.is_authenticated:
        try:
            from gastos.models import PerfilUsuario, PreferenciasUsuario

            # Obtener o crear perfil de gamificación
            perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)

            # Contar notificaciones no vistas
            notificaciones_count = perfil.notificaciones_logro.filter(visto=False).count()

            context['notificaciones_logros_count'] = notificaciones_count
            context['tiene_notificaciones_logros'] = notificaciones_count > 0
            context['perfil_gamificacion'] = perfil

            # Obtener preferencias de privacidad
            preferencias, created = PreferenciasUsuario.objects.get_or_create(usuario=request.user)
            context['ocultar_valores'] = preferencias.ocultar_valores_monetarios

        except Exception as e:
            # Si falla, no romper la aplicación
            context['notificaciones_logros_count'] = 0
            context['tiene_notificaciones_logros'] = False
            context['ocultar_valores'] = False

    else:
        # Usuario no autenticado
        context['ocultar_valores'] = False

    return context
