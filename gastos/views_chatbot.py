"""
Vistas para el Chatbot IA
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json

from .chatbot_service import ChatbotIAService
from .models import ConversacionChatbot, MensajeChatbot, AnalisisIA


@login_required
def chatbot_dashboard(request):
    """Dashboard principal del chatbot"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # Obtener familia
    from .models import Familia
    familia = Familia.objects.get(id=familia_id)

    # Obtener conversaciones recientes
    chatbot_service = ChatbotIAService()
    conversaciones = chatbot_service.obtener_conversaciones_usuario(request.user, familia)

    # Obtener análisis recientes
    analisis_recientes = AnalisisIA.objects.filter(
        user=request.user,
        familia=familia
    ).order_by('-fecha_generacion')[:5]

    context = {
        'conversaciones': conversaciones,
        'analisis_recientes': analisis_recientes,
        'familia': familia,
    }

    return render(request, 'gastos/chatbot/dashboard.html', context)


@login_required
def chatbot_conversacion(request, conversacion_id=None):
    """Vista de conversación con el chatbot"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    from .models import Familia
    familia = Familia.objects.get(id=familia_id)

    chatbot_service = ChatbotIAService()

    # Obtener o crear conversación
    if conversacion_id:
        try:
            conversacion = ConversacionChatbot.objects.get(
                id=conversacion_id,
                user=request.user
            )
        except ConversacionChatbot.DoesNotExist:
            conversacion = chatbot_service.obtener_o_crear_conversacion(request.user, familia)
    else:
        conversacion = chatbot_service.obtener_o_crear_conversacion(request.user, familia)

    # Obtener mensajes
    mensajes = conversacion.mensajes.all()

    context = {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'familia': familia,
    }

    return render(request, 'gastos/chatbot/conversacion.html', context)


@login_required
@require_http_methods(["POST"])
def chatbot_enviar_mensaje(request):
    """Endpoint para enviar mensaje al chatbot (AJAX)"""
    try:
        data = json.loads(request.body)
        mensaje = data.get('mensaje', '').strip()

        if not mensaje:
            return JsonResponse({
                'success': False,
                'error': 'El mensaje no puede estar vacío'
            })

        familia_id = request.session.get('familia_id')
        if not familia_id:
            return JsonResponse({
                'success': False,
                'error': 'Debes seleccionar una familia'
            })

        from .models import Familia
        familia = Familia.objects.get(id=familia_id)

        # Enviar mensaje al chatbot
        chatbot_service = ChatbotIAService()
        resultado = chatbot_service.enviar_mensaje(request.user, familia, mensaje)

        if resultado['success']:
            return JsonResponse({
                'success': True,
                'respuesta': resultado['respuesta'],
                'conversacion_id': resultado['conversacion_id'],
                'tokens_usados': resultado.get('tokens_usados', 0)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': resultado.get('error', 'Error desconocido'),
                'respuesta': resultado.get('respuesta', '')
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def chatbot_generar_analisis(request):
    """Genera análisis automático de ahorro"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    from .models import Familia
    familia = Familia.objects.get(id=familia_id)

    chatbot_service = ChatbotIAService()
    analisis = chatbot_service.generar_analisis_automatico(request.user, familia)

    if analisis:
        messages.success(request, '¡Análisis generado exitosamente!')
    else:
        messages.warning(request, 'No se pudo generar el análisis en este momento.')

    return redirect('chatbot_dashboard')


@login_required
def chatbot_generar_prediccion(request):
    """Genera predicción de gastos del próximo mes"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    from .models import Familia
    familia = Familia.objects.get(id=familia_id)

    chatbot_service = ChatbotIAService()
    prediccion = chatbot_service.generar_prediccion_mes(request.user, familia)

    if prediccion:
        messages.success(request, '¡Predicción generada exitosamente!')
    else:
        messages.warning(request, 'No se pudo generar la predicción en este momento.')

    return redirect('chatbot_dashboard')


@login_required
@require_http_methods(["POST"])
def chatbot_cerrar_conversacion(request, conversacion_id):
    """Cierra una conversación"""
    try:
        conversacion = ConversacionChatbot.objects.get(
            id=conversacion_id,
            user=request.user
        )
        conversacion.activa = False
        conversacion.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def chatbot_historial(request):
    """Historial de conversaciones"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    from .models import Familia
    familia = Familia.objects.get(id=familia_id)

    conversaciones = ConversacionChatbot.objects.filter(
        user=request.user,
        familia=familia
    ).order_by('-actualizada_en')

    context = {
        'conversaciones': conversaciones,
        'familia': familia,
    }

    return render(request, 'gastos/chatbot/historial.html', context)
