"""
Sistema de notificaciones de seguridad por email
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def enviar_notificacion_login(usuario, request):
    """
    Envía notificación por email cuando hay un nuevo login
    """
    from gastos.security_utils import get_client_ip, get_user_agent

    if not usuario.email:
        return False

    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Detectar navegador y SO
    navegador = "Desconocido"
    sistema_operativo = "Desconocido"

    if user_agent:
        if 'Chrome' in user_agent:
            navegador = 'Chrome'
        elif 'Firefox' in user_agent:
            navegador = 'Firefox'
        elif 'Safari' in user_agent:
            navegador = 'Safari'
        elif 'Edge' in user_agent:
            navegador = 'Edge'

        if 'Windows' in user_agent:
            sistema_operativo = 'Windows'
        elif 'Mac' in user_agent:
            sistema_operativo = 'macOS'
        elif 'Linux' in user_agent:
            sistema_operativo = 'Linux'
        elif 'Android' in user_agent:
            sistema_operativo = 'Android'
        elif 'iOS' in user_agent or 'iPhone' in user_agent:
            sistema_operativo = 'iOS'

    contexto = {
        'usuario': usuario,
        'ip_address': ip_address,
        'navegador': navegador,
        'sistema_operativo': sistema_operativo,
        'fecha_hora': timezone.now(),
    }

    asunto = f'🔐 Nuevo acceso a tu cuenta de FinanBot'

    # Crear mensaje HTML
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4A90E2;">🔐 Nuevo acceso detectado</h2>
                
                <p>Hola <strong>{usuario.first_name or usuario.username}</strong>,</p>
                
                <p>Se ha detectado un nuevo acceso a tu cuenta de FinanBot:</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>📅 Fecha y hora:</strong> {contexto['fecha_hora'].strftime('%d/%m/%Y a las %H:%M:%S')}</p>
                    <p style="margin: 5px 0;"><strong>🌐 Dirección IP:</strong> {ip_address}</p>
                    <p style="margin: 5px 0;"><strong>💻 Navegador:</strong> {navegador}</p>
                    <p style="margin: 5px 0;"><strong>🖥️ Sistema operativo:</strong> {sistema_operativo}</p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ ¿No fuiste tú?</strong></p>
                    <p style="margin: 10px 0 0 0;">Si no reconoces este acceso, te recomendamos:</p>
                    <ul style="margin: 10px 0;">
                        <li>Cambiar tu contraseña inmediatamente</li>
                        <li>Revisar la actividad reciente de tu cuenta</li>
                        <li>Contactar a soporte si sospechas actividad no autorizada</li>
                    </ul>
                </div>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                    Este es un email automático de seguridad. Si fuiste tú quien inició sesión, puedes ignorar este mensaje.
                </p>
                
                <p style="color: #666; font-size: 12px;">
                    <strong>FinanBot</strong> - Gestión de gastos familiares<br>
                    © 2026 Todos los derechos reservados
                </p>
            </div>
        </body>
    </html>
    """

    mensaje_texto = strip_tags(mensaje_html)

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        logger.info(f"Notificación de login enviada a {usuario.email}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar notificación de login: {e}")
        return False


def enviar_notificacion_cambio_password(usuario):
    """
    Envía notificación cuando se cambia la contraseña
    """
    if not usuario.email:
        return False

    asunto = '🔑 Tu contraseña ha sido cambiada'

    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #28a745;">🔑 Contraseña actualizada</h2>
                
                <p>Hola <strong>{usuario.first_name or usuario.username}</strong>,</p>
                
                <p>Tu contraseña de FinanBot ha sido cambiada exitosamente.</p>
                
                <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                    <p style="margin: 0;"><strong>✅ Cambio confirmado</strong></p>
                    <p style="margin: 10px 0 0 0;">Fecha y hora: {timezone.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ ¿No fuiste tú?</strong></p>
                    <p style="margin: 10px 0 0 0;">Si no realizaste este cambio, tu cuenta podría estar comprometida. 
                    Por favor contacta inmediatamente a soporte.</p>
                </div>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                    Este es un email automático de seguridad.
                </p>
                
                <p style="color: #666; font-size: 12px;">
                    <strong>FinanBot</strong> - Gestión de gastos familiares
                </p>
            </div>
        </body>
    </html>
    """

    mensaje_texto = strip_tags(mensaje_html)

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        logger.info(f"Notificación de cambio de contraseña enviada a {usuario.email}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar notificación de cambio de contraseña: {e}")
        return False


def enviar_notificacion_exportacion(usuario, tipo_exportacion):
    """
    Envía notificación cuando se exportan datos
    """
    if not usuario.email:
        return False

    asunto = f'📊 Exportación de datos realizada - {tipo_exportacion}'

    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4A90E2;">📊 Exportación de datos</h2>
                
                <p>Hola <strong>{usuario.first_name or usuario.username}</strong>,</p>
                
                <p>Se ha realizado una exportación de datos desde tu cuenta:</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>📄 Tipo:</strong> {tipo_exportacion}</p>
                    <p style="margin: 5px 0;"><strong>📅 Fecha y hora:</strong> {timezone.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 20px 0;">
                    <p style="margin: 0;"><strong>ℹ️ Recordatorio de seguridad</strong></p>
                    <p style="margin: 10px 0 0 0;">Los archivos exportados contienen información financiera sensible. 
                    Asegúrate de mantenerlos en un lugar seguro y eliminarlos cuando ya no los necesites.</p>
                </div>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                    Este es un email automático de seguridad.
                </p>
                
                <p style="color: #666; font-size: 12px;">
                    <strong>FinanBot</strong> - Gestión de gastos familiares
                </p>
            </div>
        </body>
    </html>
    """

    mensaje_texto = strip_tags(mensaje_html)

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        logger.info(f"Notificación de exportación enviada a {usuario.email}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar notificación de exportación: {e}")
        return False


# Importar timezone al inicio del archivo
from django.utils import timezone
