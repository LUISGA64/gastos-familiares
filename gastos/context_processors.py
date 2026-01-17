"""
Context processors para gamificación
Hace disponible información de gamificación en todos los templates
"""

def gamificacion_context(request):
    """
    Agrega información de gamificación al contexto de todos los templates
    """
    context = {}

    if request.user.is_authenticated:
        try:
            from gastos.models import PerfilUsuario

            # Obtener o crear perfil
            perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)

            # Contar notificaciones no vistas
            notificaciones_count = perfil.notificaciones_logro.filter(visto=False).count()

            context['notificaciones_logros_count'] = notificaciones_count
            context['tiene_notificaciones_logros'] = notificaciones_count > 0
            context['perfil_gamificacion'] = perfil

        except Exception as e:
            # Si falla, no romper la aplicación
            context['notificaciones_logros_count'] = 0
            context['tiene_notificaciones_logros'] = False

    return context
