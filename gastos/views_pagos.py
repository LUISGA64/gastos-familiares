"""
Vistas para pagos con QR
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Pago, PlanSuscripcion, Familia
from .qr_utils import GeneradorQRPago, VerificadorPagos, INFO_CUENTAS_COLOMBIA
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

    context = {
        'familia': familia,
        'planes': planes,
        'pagos_anteriores': pagos_anteriores,
        'info_cuentas': INFO_CUENTAS_COLOMBIA
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

    if metodo == 'bancolombia':
        qr_base64, datos_qr = GeneradorQRPago.generar_qr_bancolombia(
            plan.precio_mensual,
            referencia,
            f"Suscripción {plan.nombre}"
        )
        info_cuenta = INFO_CUENTAS_COLOMBIA['bancolombia']
        metodo_pago = 'QR_BANCOLOMBIA'

    elif metodo == 'nequi':
        qr_base64, datos_qr = GeneradorQRPago.generar_qr_nequi(
            plan.precio_mensual,
            referencia,
            f"Suscripción {plan.nombre}"
        )
        info_cuenta = INFO_CUENTAS_COLOMBIA['nequi']
        metodo_pago = 'QR_NEQUI'

    else:
        messages.error(request, 'Método de pago no soportado.')
        return redirect('pagar_suscripcion')

    # Crear registro de pago pendiente
    pago = Pago.objects.create(
        familia=familia,
        plan=plan,
        monto=plan.precio_mensual,
        metodo_pago=metodo_pago,
        estado='PENDIENTE',
        referencia_pago=referencia,
        datos_qr=datos_qr
    )

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

    if 'comprobante' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No se envió ningún archivo'})

    comprobante = request.FILES['comprobante']

    # Validar comprobante
    es_valido, mensaje_error = GeneradorQRPago.validar_comprobante(comprobante)
    if not es_valido:
        return JsonResponse({'success': False, 'error': mensaje_error})

    # Guardar comprobante
    pago.comprobante = comprobante
    pago.estado = 'VERIFICANDO'

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

