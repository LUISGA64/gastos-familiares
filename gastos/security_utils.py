"""
Utilidades de seguridad y auditoría
"""
from .models import AuditLog


def get_client_ip(request):
    """
    Obtiene la IP real del cliente, considerando proxies y load balancers
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Obtiene el User Agent del navegador
    """
    return request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar a 500 caracteres


def registrar_auditoria(request, accion, modelo, objeto_id=None,
                       datos_anteriores=None, datos_nuevos=None,
                       descripcion='', familia=None):
    """
    Helper para registrar acciones en el audit log

    Uso:
        from gastos.security_utils import registrar_auditoria

        registrar_auditoria(
            request=request,
            accion='CREATE',
            modelo='Gasto',
            objeto_id=gasto.id,
            descripcion=f'Nuevo gasto: {gasto.descripcion}'
        )
    """
    return AuditLog.registrar(
        usuario=request.user if request.user.is_authenticated else None,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        descripcion=descripcion,
        familia=familia
    )


def verificar_intentos_login(username, ip_address, max_intentos=5, ventana_minutos=15):
    """
    Verifica si se excedió el número de intentos de login fallidos

    Returns:
        tuple: (bloqueado: bool, intentos_restantes: int)
    """
    from django.utils import timezone
    from datetime import timedelta

    ventana_tiempo = timezone.now() - timedelta(minutes=ventana_minutos)

    # Contar intentos fallidos en la ventana de tiempo
    intentos = AuditLog.objects.filter(
        accion='LOGIN_FAILED',
        ip_address=ip_address,
        timestamp__gte=ventana_tiempo
    ).count()

    bloqueado = intentos >= max_intentos
    intentos_restantes = max(0, max_intentos - intentos)

    return bloqueado, intentos_restantes


def limpiar_intentos_login(ip_address):
    """
    Limpia los intentos fallidos de login después de un login exitoso
    """
    from django.utils import timezone
    from datetime import timedelta

    ventana_tiempo = timezone.now() - timedelta(minutes=15)

    AuditLog.objects.filter(
        accion='LOGIN_FAILED',
        ip_address=ip_address,
        timestamp__gte=ventana_tiempo
    ).delete()


def obtener_sesiones_activas(usuario):
    """
    Obtiene información sobre las sesiones activas del usuario
    (Requiere implementación adicional con django.contrib.sessions)
    """
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    sesiones_activas = []
    sesiones = Session.objects.filter(expire_date__gte=timezone.now())

    for sesion in sesiones:
        data = sesion.get_decoded()
        if data.get('_auth_user_id') == str(usuario.id):
            sesiones_activas.append({
                'session_key': sesion.session_key,
                'expire_date': sesion.expire_date,
            })

    return sesiones_activas


def cerrar_otras_sesiones(usuario, sesion_actual_key):
    """
    Cierra todas las sesiones del usuario excepto la actual
    """
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    sesiones = Session.objects.filter(expire_date__gte=timezone.now())
    cerradas = 0

    for sesion in sesiones:
        if sesion.session_key != sesion_actual_key:
            data = sesion.get_decoded()
            if data.get('_auth_user_id') == str(usuario.id):
                sesion.delete()
                cerradas += 1

    return cerradas


def anonimizar_datos_usuario(usuario):
    """
    Anonimiza los datos de un usuario para cumplir con derecho al olvido

    IMPORTANTE: Esto es irreversible
    """
    import hashlib
    from django.utils import timezone

    # Generar ID anónimo único basado en timestamp
    anonimo_id = hashlib.md5(
        f"{usuario.id}{timezone.now().timestamp()}".encode()
    ).hexdigest()[:12]

    # Anonimizar datos
    usuario.username = f"usuario_eliminado_{anonimo_id}"
    usuario.email = f"eliminado_{anonimo_id}@anonimo.local"
    usuario.first_name = "Usuario"
    usuario.last_name = "Eliminado"
    usuario.is_active = False
    usuario.save()

    # Registrar en audit log
    AuditLog.registrar(
        usuario=None,
        accion='DELETE',
        modelo='User',
        objeto_id=usuario.id,
        descripcion=f'Datos de usuario anonimizados - Derecho al olvido'
    )

    return anonimo_id


def exportar_datos_usuario(usuario):
    """
    Exporta todos los datos del usuario en formato JSON
    Para cumplir con RGPD/GDPR (derecho de portabilidad)
    """
    from gastos.models import Gasto, IngresoAportante

    datos = {
        'usuario': {
            'username': usuario.username,
            'email': usuario.email,
            'nombre': f"{usuario.first_name} {usuario.last_name}",
            'fecha_registro': usuario.date_joined.isoformat() if usuario.date_joined else None,
        },
        'familias': [],
        'audit_log': []
    }

    # Familias del usuario
    for familia in usuario.familias.all():
        familia_data = {
            'nombre': familia.nombre,
            'fecha_creacion': familia.fecha_creacion.isoformat() if familia.fecha_creacion else None,
            'aportantes': [],
            'gastos': [],
            'ingresos': []
        }

        # Aportantes
        for aportante in familia.aportantes.all():
            familia_data['aportantes'].append({
                'nombre': aportante.nombre,
                'email': aportante.email,
                'ingreso_mensual': float(aportante.ingreso_mensual),
            })

        # Gastos
        for gasto in Gasto.objects.filter(
            subcategoria__categoria__familia=familia
        ):
            familia_data['gastos'].append({
                'descripcion': gasto.descripcion,
                'monto': float(gasto.monto),
                'fecha': gasto.fecha.isoformat() if gasto.fecha else None,
                'tipo': gasto.tipo_gasto,
            })

        # Ingresos
        for ingreso in IngresoAportante.objects.filter(
            aportante__familia=familia
        ):
            familia_data['ingresos'].append({
                'descripcion': ingreso.descripcion,
                'monto': float(ingreso.monto),
                'fecha': ingreso.fecha.isoformat() if ingreso.fecha else None,
                'tipo': ingreso.tipo_ingreso,
            })

        datos['familias'].append(familia_data)

    # Audit logs
    for log in AuditLog.objects.filter(usuario=usuario).order_by('-timestamp')[:100]:
        datos['audit_log'].append({
            'accion': log.get_accion_display(),
            'modelo': log.modelo,
            'fecha': log.timestamp.isoformat(),
            'descripcion': log.descripcion,
        })

    return datos
