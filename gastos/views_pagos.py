"""
Vistas para pagos con QR
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Pago, PlanSuscripcion, Familia
from .qr_utils import GeneradorQRPago, VerificadorPagos, get_info_cuentas_colombia
from decimal import Decimal
from django.utils import timezone


@login_required
def pagar_suscripcion(request):
    """Vista para iniciar pago de suscripción"""
    # Obtener familia del usuario
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    familia = get_object_or_404(Familia, id=familia_id)

    # Obtener planes disponibles
    planes = PlanSuscripcion.objects.filter(activo=True).order_by('precio_mensual')

    # Obtener pagos previos
    pagos_anteriores = Pago.objects.filter(familia=familia).order_by('-fecha_pago')[:5]

    # Obtener plan_id del query string si existe (desde página de planes)
    plan_id_seleccionado = request.GET.get('plan_id', None)
    plan_seleccionado = None
    if plan_id_seleccionado:
        try:
            plan_seleccionado = PlanSuscripcion.objects.get(id=plan_id_seleccionado, activo=True)
        except PlanSuscripcion.DoesNotExist:
            pass

    context = {
        'familia': familia,
        'planes': planes,
        'plan_seleccionado': plan_seleccionado,
        'pagos_anteriores': pagos_anteriores,
        'info_cuentas': get_info_cuentas_colombia()  # Obtener desde BD
    }

    return render(request, 'gastos/suscripcion/pagar.html', context)


@login_required
def generar_qr_pago(request, plan_id, metodo):
    """Genera código QR para pago"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    familia = get_object_or_404(Familia, id=familia_id)
    plan = get_object_or_404(PlanSuscripcion, id=plan_id)

    # Generar referencia única
    referencia = GeneradorQRPago.generar_referencia_unica()

    # Generar QR según el método
    qr_base64 = None
    datos_qr = None
    info_cuenta = None

    # Obtener info de cuentas desde BD
    info_cuentas = get_info_cuentas_colombia()

    if metodo == 'bancolombia':
        qr_base64, datos_qr = GeneradorQRPago.generar_qr_bancolombia(
            plan.precio_mensual,
            referencia,
            f"Suscripción {plan.nombre}"
        )
        info_cuenta = info_cuentas.get('bancolombia', {})
        metodo_pago = 'QR_BANCOLOMBIA'

    elif metodo == 'nequi':
        qr_base64, datos_qr = GeneradorQRPago.generar_qr_nequi(
            plan.precio_mensual,
            referencia,
            f"Suscripción {plan.nombre}"
        )
        info_cuenta = info_cuentas.get('nequi', {})
        metodo_pago = 'QR_NEQUI'

    else:
        messages.error(request, 'Método de pago no soportado.')
        return redirect('pagar_suscripcion')

    # Crear registro de pago pendiente con medidas de seguridad
    pago = Pago.objects.create(
        familia=familia,
        plan=plan,
        monto=plan.precio_mensual,
        metodo_pago=metodo_pago,
        estado='PENDIENTE',
        referencia_pago=referencia,
        datos_qr=datos_qr,
        expira_en=timezone.now() + timedelta(hours=24),  # Expira en 24 horas
        ip_origen=request.META.get('REMOTE_ADDR', None)
    )

    # Generar y guardar firma digital
    pago.firma_qr = pago.generar_firma()
    pago.save(update_fields=['firma_qr'])

    context = {
        'familia': familia,
        'plan': plan,
        'pago': pago,
        'qr_base64': qr_base64,
        'referencia': referencia,
        'info_cuenta': info_cuenta,
        'metodo': metodo
    }

    return render(request, 'gastos/suscripcion/qr_pago.html', context)


@login_required
@require_POST
def subir_comprobante(request, pago_id):
    """Sube comprobante de pago"""
    pago = get_object_or_404(Pago, id=pago_id)

    # Verificar que el pago pertenece a la familia del usuario
    familia_id = request.session.get('familia_id')
    if pago.familia.id != familia_id:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    # Validaciones de seguridad
    if pago.esta_expirado():
        return JsonResponse({
            'success': False,
            'error': 'Este QR ha expirado. Por favor genera uno nuevo.'
        }, status=400)

    if not pago.puede_subir_comprobante():
        if pago.intentos_subida >= pago.max_intentos:
            return JsonResponse({
                'success': False,
                'error': f'Has excedido el máximo de {pago.max_intentos} intentos. Contacta a soporte.'
            }, status=400)
        return JsonResponse({
            'success': False,
            'error': 'No puedes subir comprobantes para este pago.'
        }, status=400)

    if 'comprobante' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No se envió ningún archivo'})

    comprobante = request.FILES['comprobante']

    # Validar comprobante
    es_valido, mensaje_error = GeneradorQRPago.validar_comprobante(comprobante)
    if not es_valido:
        pago.registrar_intento_subida()  # Registrar intento fallido
        return JsonResponse({'success': False, 'error': mensaje_error})

    # Guardar comprobante
    pago.comprobante = comprobante
    pago.estado = 'VERIFICANDO'
    pago.registrar_intento_subida()  # Registrar intento exitoso

    # Guardar número de transacción si se proporcionó
    numero_transaccion = request.POST.get('numero_transaccion', '')
    if numero_transaccion:
        pago.numero_transaccion = numero_transaccion

    pago.save()

    return JsonResponse({
        'success': True,
        'mensaje': 'Comprobante subido correctamente. Tu pago será verificado pronto.'
    })


@login_required
def estado_pago(request, pago_id):
    """Muestra el estado de un pago"""
    pago = get_object_or_404(Pago, id=pago_id)

    # Verificar que el pago pertenece a la familia del usuario
    familia_id = request.session.get('familia_id')
    if pago.familia.id != familia_id:
        messages.error(request, 'No autorizado.')
        return redirect('dashboard')

    context = {
        'pago': pago,
        'familia': pago.familia
    }

    return render(request, 'gastos/suscripcion/estado_pago.html', context)


@login_required
def mis_pagos(request):
    """Lista de pagos de la familia"""
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.error(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    familia = get_object_or_404(Familia, id=familia_id)
    pagos = Pago.objects.filter(familia=familia).order_by('-fecha_pago')

    context = {
        'familia': familia,
        'pagos': pagos
    }

    return render(request, 'gastos/suscripcion/mis_pagos.html', context)


# Vistas de administración (solo para staff)
@login_required
def verificar_pagos(request):
    """Panel de verificación de pagos (solo staff)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard')

    pagos_pendientes = VerificadorPagos.obtener_pagos_pendientes()

    context = {
        'pagos_pendientes': pagos_pendientes
    }

    return render(request, 'gastos/admin/verificar_pagos.html', context)


@login_required
@require_POST
def aprobar_pago_ajax(request, pago_id):
    """Aprueba un pago vía AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    pago = get_object_or_404(Pago, id=pago_id)

    if VerificadorPagos.verificar_pago(pago, request.user):
        return JsonResponse({
            'success': True,
            'mensaje': f'Pago aprobado. Suscripción de {pago.familia.nombre} activada.'
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'El pago no está en estado de verificación.'
        })


@login_required
@require_POST
def rechazar_pago_ajax(request, pago_id):
    """Rechaza un pago vía AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    pago = get_object_or_404(Pago, id=pago_id)
    motivo = request.POST.get('motivo', 'Sin motivo especificado')

    VerificadorPagos.rechazar_pago(pago, motivo, request.user)

    return JsonResponse({
        'success': True,
        'mensaje': f'Pago rechazado.'
    })

