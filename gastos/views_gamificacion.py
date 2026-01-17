"""
Vistas para el sistema de gamificación
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import PerfilUsuario, LogroDesbloqueado, Logro, NotificacionLogro
from .gamificacion_service import GamificacionService


@login_required
def dashboard_gamificacion(request):
    """Dashboard de gamificación del usuario"""
    perfil = GamificacionService.obtener_o_crear_perfil(request.user)

    # Obtener logros desbloqueados
    logros_desbloqueados = LogroDesbloqueado.objects.filter(
        perfil=perfil
    ).select_related('logro').order_by('-fecha_desbloqueo')

    # Obtener logros disponibles (no desbloqueados, no secretos)
    logros_disponibles = Logro.objects.filter(
        activo=True,
        es_secreto=False
    ).exclude(
        id__in=logros_desbloqueados.values_list('logro_id', flat=True)
    ).order_by('tipo', 'puntos_recompensa')

    # Obtener logros secretos desbloqueados
    logros_secretos = LogroDesbloqueado.objects.filter(
        perfil=perfil,
        logro__es_secreto=True
    ).select_related('logro')

    # Calcular estadísticas
    stats = GamificacionService.calcular_estadisticas_usuario(request.user)

    # Obtener últimas notificaciones
    notificaciones = perfil.notificaciones_logro.all()[:10]
    notificaciones_no_vistas = perfil.notificaciones_logro.filter(visto=False).count()

    # Obtener historial de puntos reciente
    historial_reciente = perfil.historial_puntos.all()[:20]

    # Obtener ranking (top 10)
    ranking = GamificacionService.obtener_ranking_usuarios(10)
    posicion_usuario = None
    for idx, p in enumerate(ranking, 1):
        if p.id == perfil.id:
            posicion_usuario = idx
            break

    context = {
        'perfil': perfil,
        'logros_desbloqueados': logros_desbloqueados,
        'logros_disponibles': logros_disponibles,
        'logros_secretos': logros_secretos,
        'porcentaje_completado': stats['porcentaje_completado'],
        'puntos_siguiente_nivel': stats['puntos_siguiente_nivel'],
        'notificaciones': notificaciones,
        'notificaciones_no_vistas': notificaciones_no_vistas,
        'historial_reciente': historial_reciente,
        'ranking': ranking,
        'posicion_usuario': posicion_usuario,
        'total_logros': stats['total_logros'],
    }

    # Marcar notificaciones como vistas
    GamificacionService.marcar_notificaciones_vistas(request.user)

    return render(request, 'gastos/gamificacion/dashboard.html', context)


@login_required
def logros_lista(request):
    """Lista completa de todos los logros"""
    perfil = GamificacionService.obtener_o_crear_perfil(request.user)

    # Obtener todos los logros no secretos
    todos_logros = Logro.objects.filter(activo=True, es_secreto=False)
    logros_desbloqueados_ids = perfil.logros.values_list('logro_id', flat=True)

    # Organizar por tipo
    logros_por_tipo = {}
    logros_por_tipo_data = {}

    for tipo_codigo, tipo_nombre in Logro.TIPO_LOGRO:
        logros_por_tipo[tipo_codigo] = tipo_nombre
        logros_por_tipo_data[tipo_codigo] = {
            'desbloqueados': [],
            'bloqueados': [],
            'total': 0
        }

    for logro in todos_logros:
        if logro.id in logros_desbloqueados_ids:
            # Obtener la fecha de desbloqueo
            logro_desb = perfil.logros.get(logro=logro)
            logros_por_tipo_data[logro.tipo]['desbloqueados'].append({
                'logro': logro,
                'fecha': logro_desb.fecha_desbloqueo
            })
        else:
            logros_por_tipo_data[logro.tipo]['bloqueados'].append(logro)

        logros_por_tipo_data[logro.tipo]['total'] += 1

    context = {
        'perfil': perfil,
        'logros_por_tipo': logros_por_tipo,
        'logros_por_tipo_data': logros_por_tipo_data,
        'total_logros': todos_logros.count(),
    }

    return render(request, 'gastos/gamificacion/logros_lista.html', context)


@login_required
def ranking_general(request):
    """Ranking general de usuarios"""
    perfil = GamificacionService.obtener_o_crear_perfil(request.user)

    # Obtener top 100
    ranking = GamificacionService.obtener_ranking_usuarios(100)

    # Encontrar posición del usuario
    posicion_usuario = None
    for idx, p in enumerate(ranking, 1):
        if p.id == perfil.id:
            posicion_usuario = idx
            break

    context = {
        'perfil': perfil,
        'ranking': ranking,
        'posicion_usuario': posicion_usuario,
    }

    return render(request, 'gastos/gamificacion/ranking.html', context)


@login_required
def notificaciones_logros(request):
    """Lista de notificaciones de logros"""
    perfil = GamificacionService.obtener_o_crear_perfil(request.user)
    notificaciones = perfil.notificaciones_logro.all()

    # Marcar todas como vistas
    if request.method == 'POST':
        GamificacionService.marcar_notificaciones_vistas(request.user)
        messages.success(request, 'Notificaciones marcadas como vistas')
        return redirect('notificaciones_logros')

    context = {
        'perfil': perfil,
        'notificaciones': notificaciones,
    }

    return render(request, 'gastos/gamificacion/notificaciones.html', context)


@login_required
def verificar_logros_ajax(request):
    """Endpoint AJAX para verificar logros (usado en background)"""
    logros_nuevos = GamificacionService.verificar_logros_usuario(request.user)

    if logros_nuevos:
        return JsonResponse({
            'success': True,
            'logros_nuevos': [
                {
                    'nombre': logro.nombre,
                    'icono': logro.icono,
                    'puntos': logro.puntos_recompensa,
                }
                for logro in logros_nuevos
            ]
        })
    else:
        return JsonResponse({'success': True, 'logros_nuevos': []})


@login_required
def estadisticas_usuario(request):
    """Vista de estadísticas detalladas del usuario"""
    stats = GamificacionService.calcular_estadisticas_usuario(request.user)
    perfil = stats['perfil']

    # Calcular progreso por tipo de logro
    tipos_logro = Logro.TIPO_LOGRO
    progreso_por_tipo = {}

    for codigo, nombre in tipos_logro:
        total = Logro.objects.filter(tipo=codigo, activo=True, es_secreto=False).count()
        desbloqueados = perfil.logros.filter(logro__tipo=codigo).count()
        porcentaje = (desbloqueados / total * 100) if total > 0 else 0
        progreso_por_tipo[nombre] = {
            'total': total,
            'desbloqueados': desbloqueados,
            'porcentaje': porcentaje
        }

    context = {
        'perfil': perfil,
        'stats': stats,
        'progreso_por_tipo': progreso_por_tipo,
    }

    return render(request, 'gastos/gamificacion/estadisticas.html', context)
