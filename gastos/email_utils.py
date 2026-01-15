"""
Utilidades para envío de emails
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def enviar_codigo_confirmacion_conciliacion(detalle_conciliacion):
    """
    Envía el código de confirmación al email del aportante

    Args:
        detalle_conciliacion: Instancia de DetalleConciliacion

    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    aportante = detalle_conciliacion.aportante

    # Verificar que el aportante tenga email
    if not aportante.email:
        return False

    # Generar código si no existe
    if not detalle_conciliacion.codigo_confirmacion:
        detalle_conciliacion.generar_codigo_confirmacion()

    conciliacion = detalle_conciliacion.conciliacion
    meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_nombre = meses[conciliacion.mes]

    # Contexto del email
    contexto = {
        'aportante': aportante,
        'conciliacion': conciliacion,
        'detalle': detalle_conciliacion,
        'mes_nombre': mes_nombre,
        'codigo': detalle_conciliacion.codigo_confirmacion,
    }

    # Asunto del email
    asunto = f'Confirma la Conciliación de {mes_nombre} {conciliacion.anio} - Gastos Familiares'

    # Mensaje HTML
    mensaje_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
            .code-box {{ background-color: #007bff; color: white; font-size: 32px; font-weight: bold; 
                         text-align: center; padding: 20px; margin: 20px 0; border-radius: 5px; letter-spacing: 5px; }}
            .details {{ background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
            .balance-positive {{ color: #28a745; font-weight: bold; }}
            .balance-negative {{ color: #dc3545; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
            .button {{ background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; 
                       border-radius: 5px; display: inline-block; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧾 Conciliación de Gastos</h1>
                <p>{conciliacion.familia.nombre}</p>
            </div>
            <div class="content">
                <h2>Hola {aportante.nombre},</h2>
                <p>Se ha generado la conciliación de gastos para <strong>{mes_nombre} {conciliacion.anio}</strong>.</p>
                
                <div class="details">
                    <h3>📊 Tu Resumen:</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Porcentaje de aporte:</strong></td>
                            <td style="text-align: right;">{detalle_conciliacion.porcentaje_esperado:.1f}%</td>
                        </tr>
                        <tr>
                            <td><strong>Debías pagar:</strong></td>
                            <td style="text-align: right;">${detalle_conciliacion.monto_debe_pagar:,.0f}</td>
                        </tr>
                        <tr>
                            <td><strong>Pagaste realmente:</strong></td>
                            <td style="text-align: right;">${detalle_conciliacion.monto_pago_real:,.0f}</td>
                        </tr>
                        <tr style="border-top: 2px solid #dee2e6;">
                            <td><strong>Balance:</strong></td>
                            <td style="text-align: right;" class="{'balance-positive' if detalle_conciliacion.balance > 0 else 'balance-negative' if detalle_conciliacion.balance < 0 else ''}">
                                ${detalle_conciliacion.balance:,.0f}
                                {'(debes recibir)' if detalle_conciliacion.balance > 0 else '(debes pagar)' if detalle_conciliacion.balance < 0 else '(equilibrado)'}
                            </td>
                        </tr>
                    </table>
                </div>
                
                <p><strong>Para confirmar que estás de acuerdo con esta conciliación, ingresa el siguiente código:</strong></p>
                
                <div class="code-box">
                    {detalle_conciliacion.codigo_confirmacion}
                </div>
                
                <p style="text-align: center;">
                    <a href="http://localhost:8000/conciliacion/" class="button">
                        ✅ Ir a Confirmar Conciliación
                    </a>
                </p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #6c757d;">
                    <strong>Nota:</strong> Este código es válido solo para esta conciliación. 
                    Una vez que todos los aportantes confirmen, la conciliación se cerrará automáticamente.
                </p>
                
                <div class="footer">
                    <p>Gastos Familiares - Sistema de Gestión de Finanzas del Hogar</p>
                    <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Versión texto plano
    mensaje_texto = f"""
    Hola {aportante.nombre},
    
    Se ha generado la conciliación de gastos para {mes_nombre} {conciliacion.anio}.
    
    TU RESUMEN:
    -----------
    Porcentaje de aporte: {detalle_conciliacion.porcentaje_esperado:.1f}%
    Debías pagar: ${detalle_conciliacion.monto_debe_pagar:,.0f}
    Pagaste realmente: ${detalle_conciliacion.monto_pago_real:,.0f}
    Balance: ${detalle_conciliacion.balance:,.0f} {'(debes recibir)' if detalle_conciliacion.balance > 0 else '(debes pagar)' if detalle_conciliacion.balance < 0 else '(equilibrado)'}
    
    CÓDIGO DE CONFIRMACIÓN:
    {detalle_conciliacion.codigo_confirmacion}
    
    Para confirmar que estás de acuerdo con esta conciliación, ingresa este código en:
    http://localhost:8000/conciliacion/
    
    ---
    Gastos Familiares - Sistema de Gestión de Finanzas del Hogar
    """

    try:
        # Enviar email
        send_mail(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [aportante.email],
            html_message=mensaje_html,
            fail_silently=False,
        )

        # Marcar como enviado
        from django.utils import timezone
        detalle_conciliacion.email_enviado = True
        detalle_conciliacion.fecha_envio_email = timezone.now()
        detalle_conciliacion.save()

        return True
    except Exception as e:
        print(f"Error al enviar email a {aportante.email}: {str(e)}")
        return False


def enviar_notificacion_conciliacion_cerrada(conciliacion):
    """
    Envía notificación a todos los aportantes cuando se cierra la conciliación
    """
    meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_nombre = meses[conciliacion.mes]

    for detalle in conciliacion.detalles.all():
        if not detalle.aportante.email:
            continue

        asunto = f'Conciliación de {mes_nombre} {conciliacion.anio} Cerrada - Gastos Familiares'

        mensaje = f"""
        Hola {detalle.aportante.nombre},
        
        La conciliación de {mes_nombre} {conciliacion.anio} ha sido cerrada exitosamente.
        
        Todos los aportantes han confirmado y están de acuerdo.
        
        Puedes consultar el historial en:
        http://localhost:8000/conciliacion/historial/
        
        ---
        Gastos Familiares
        """

        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [detalle.aportante.email],
                fail_silently=True,
            )
        except:
            pass

