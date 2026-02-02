from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
from .models import Familia, PlanSuscripcion, CodigoInvitacion, InvitacionFamilia
from .security_utils import registrar_auditoria, verificar_intentos_login, limpiar_intentos_login
import random
import string
import logging

logger = logging.getLogger(__name__)


def inicio(request):
    """Vista de inicio - redirige según autenticación"""
    if request.user.is_authenticated:
        # Si ya está autenticado, ir al dashboard
        return redirect('dashboard')
    else:
        # Si no está autenticado, ir al login
        return redirect('login')


def generar_codigo_invitacion():
    """Genera un código de invitación único"""
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        if not CodigoInvitacion.objects.filter(codigo=codigo).exists():
            return codigo


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Obtener IP del cliente para rate limiting
        from .security_utils import get_client_ip
        ip_address = get_client_ip(request)

        # Verificar intentos de login
        bloqueado, intentos_restantes = verificar_intentos_login(username, ip_address)

        if bloqueado:
            messages.error(request, f'Demasiados intentos fallidos. Por favor, espera 15 minutos antes de intentar nuevamente.')
            registrar_auditoria(
                request,
                accion='LOGIN_FAILED',
                modelo='User',
                descripcion=f'Cuenta bloqueada temporalmente por múltiples intentos - Username: {username}'
            )
            return render(request, 'gastos/auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verificar que tenga al menos una familia activa con suscripción
            familias = user.familias.filter(activo=True)

            if familias.exists():
                # Verificar que al menos una familia tenga suscripción activa
                familia_activa = None
                for familia in familias:
                    if familia.esta_suscripcion_activa():
                        familia_activa = familia
                        break

                if familia_activa:
                    login(request, user)
                    # Guardar familia actual en sesión
                    request.session['familia_id'] = familia_activa.id

                    # Limpiar intentos fallidos de login
                    limpiar_intentos_login(ip_address)

                    # Registrar login exitoso
                    registrar_auditoria(
                        request,
                        accion='LOGIN',
                        modelo='User',
                        objeto_id=user.id,
                        descripcion=f'Login exitoso - Familia: {familia_activa.nombre}',
                        familia=familia_activa
                    )

                    # Enviar notificación de seguridad por email (async)
                    try:
                        enviar_notificacion_login(user, request)
                    except Exception as e:
                        logger.warning(f"No se pudo enviar notificación de login: {e}")

                    messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Tu suscripción ha expirado. Por favor, renueva tu plan.')
                    registrar_auditoria(
                        request,
                        accion='LOGIN_FAILED',
                        modelo='User',
                        objeto_id=user.id,
                        descripcion='Login fallido - Suscripción expirada'
                    )
            else:
                login(request, user)
                registrar_auditoria(
                    request,
                    accion='LOGIN',
                    modelo='User',
                    objeto_id=user.id,
                    descripcion='Login exitoso - Sin familia'
                )
                messages.warning(request, 'No tienes una familia registrada. Crea una ahora.')
                return redirect('crear_familia')
        else:
            # Login fallido
            registrar_auditoria(
                request,
                accion='LOGIN_FAILED',
                modelo='User',
                descripcion=f'Credenciales inválidas - Username: {username}'
            )

            if intentos_restantes > 1:
                messages.error(request, f'Usuario o contraseña incorrectos. Te quedan {intentos_restantes - 1} intentos.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'gastos/auth/login.html')


@login_required
def logout_view(request):
    """Vista de logout - sin mensaje para evitar duplicación"""
    # Registrar logout antes de cerrar sesión
    registrar_auditoria(
        request,
        accion='LOGOUT',
        modelo='User',
        objeto_id=request.user.id,
        descripcion='Logout exitoso'
    )

    logout(request)
    # No agregar mensaje aquí para evitar alertas duplicadas
    return redirect('login')


def registro_view(request, codigo=None):
    """Vista de registro simplificada - acepta código de invitación por URL"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Obtener código de invitación de URL o query params
    codigo_url = codigo or request.GET.get('codigo', '')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        codigo_invitacion = request.POST.get('codigo_invitacion', '').strip()

        # Validaciones
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'gastos/auth/registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'gastos/auth/registro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'gastos/auth/registro.html')

        # Determinar el plan a asignar
        plan = None
        dias_prueba = 0
        mensaje_plan = ""
        invitacion_familia = None

        # Si proporciona un código de invitación, validarlo
        if codigo_invitacion:
            # Primero verificar si es una invitación a familia
            try:
                invitacion_familia = InvitacionFamilia.objects.get(codigo=codigo_invitacion.upper())
                if invitacion_familia.esta_valido():
                    # Es una invitación a familia, usar el plan de esa familia
                    plan = invitacion_familia.familia.plan
                    dias_prueba = 0  # Ya se une a familia existente
                    mensaje_plan = f"Te has unido a {invitacion_familia.familia.nombre}."
                else:
                    invitacion_familia = None
                    messages.warning(request, 'El código de invitación ha expirado o no es válido.')
            except InvitacionFamilia.DoesNotExist:
                # No es invitación a familia, verificar si es código de plan
                try:
                    codigo = CodigoInvitacion.objects.get(codigo=codigo_invitacion)
                    if codigo.esta_valido():
                        plan = codigo.plan
                        dias_prueba = plan.dias_prueba
                        # Marcar código como usado
                        codigo.marcar_como_usado(None)  # Se marcará con el usuario después
                        mensaje_plan = f"Tienes {dias_prueba} días de prueba del {plan.nombre}."
                    else:
                        messages.warning(request, 'El código de invitación no es válido. Se te asignará el plan gratuito.')
                except CodigoInvitacion.DoesNotExist:
                    messages.warning(request, 'El código de invitación no existe. Se te asignará el plan gratuito.')

        # Si no hay código o el código es inválido, asignar plan gratuito con periodo de prueba
        if plan is None:
            try:
                # Intentar obtener el plan básico para darles un periodo de prueba
                plan = PlanSuscripcion.objects.get(tipo='BASICO')
                dias_prueba = plan.dias_prueba
                mensaje_plan = f"¡Bienvenido! Tienes {dias_prueba} días de prueba gratis del {plan.nombre}."
            except PlanSuscripcion.DoesNotExist:
                # Si no existe plan básico, usar el gratuito
                try:
                    plan = PlanSuscripcion.objects.get(tipo='GRATIS')
                    dias_prueba = 0
                    mensaje_plan = "Has sido registrado con el plan gratuito."
                except PlanSuscripcion.DoesNotExist:
                    # Si no hay ningún plan, usar el primero disponible
                    plan = PlanSuscripcion.objects.first()
                    if plan:
                        dias_prueba = plan.dias_prueba
                        mensaje_plan = f"Has sido registrado con el {plan.nombre}."
                    else:
                        messages.error(request, 'Error: No hay planes disponibles. Contacta al administrador.')
                        return render(request, 'gastos/auth/registro.html')

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Si usó un código, actualizar el usuario asociado
        if codigo_invitacion:
            try:
                codigo = CodigoInvitacion.objects.get(codigo=codigo_invitacion)
                codigo.marcar_como_usado(user)
            except:
                pass

        # Decidir si crear nueva familia o unirse a una existente
        if invitacion_familia:
            # Unirse a familia existente
            familia = invitacion_familia.familia
            invitacion_familia.usar_invitacion(user)

            # Crear aportante automáticamente
            from .models import Aportante
            Aportante.objects.create(
                familia=familia,
                nombre=f"{first_name} {last_name}",
                email=email,
                ingreso_mensual=0,  # Por defecto, puede actualizar después
                activo=True
            )

            # Login automático
            login(request, user)
            request.session['familia_id'] = familia.id

            messages.success(
                request,
                f'¡Registro exitoso! Te has unido a {familia.nombre}. '
                f'No olvides actualizar tu ingreso mensual en la sección de Aportantes.'
            )
            return redirect('dashboard')
        else:
            # Crear familia automáticamente
            familia = Familia.objects.create(
                nombre=f"Familia {last_name}",
                creado_por=user,
                plan=plan,
                en_periodo_prueba=dias_prueba > 0,
                fecha_inicio_suscripcion=timezone.now(),
                fecha_fin_suscripcion=timezone.now() + timedelta(days=dias_prueba) if dias_prueba > 0 else None
            )
            familia.miembros.add(user)

            # Login automático
            login(request, user)
            request.session['familia_id'] = familia.id

            messages.success(request, f'¡Registro exitoso! Bienvenido {first_name}. {mensaje_plan}')
            return redirect('dashboard')

    # Pasar código al template
    context = {
        'codigo_prellenado': codigo_url
    }
    return render(request, 'gastos/auth/registro.html', context)


@login_required
def crear_familia(request):
    """Vista para crear una nueva familia"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        # Obtener plan gratuito o básico
        try:
            plan = PlanSuscripcion.objects.get(tipo='GRATIS')
        except PlanSuscripcion.DoesNotExist:
            plan = PlanSuscripcion.objects.first()

        # Si no hay ningún plan en la base de datos, mostrar error
        if plan is None:
            messages.error(
                request,
                'Error: No hay planes de suscripción configurados. '
                'Por favor contacta al administrador del sistema.'
            )
            return render(request, 'gastos/familias/crear.html')

        familia = Familia.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            creado_por=request.user,
            plan=plan,
            en_periodo_prueba=plan.dias_prueba > 0,
            fecha_inicio_suscripcion=timezone.now()
        )
        familia.miembros.add(request.user)

        request.session['familia_id'] = familia.id
        messages.success(request, f'Familia "{nombre}" creada exitosamente.')
        return redirect('dashboard')

    return render(request, 'gastos/familias/crear.html')


@login_required
def seleccionar_familia(request):
    """Vista para seleccionar familia activa"""
    familias = request.user.familias.filter(activo=True)

    if request.method == 'POST':
        familia_id = request.POST.get('familia_id')
        try:
            familia = familias.get(id=familia_id)
            if familia.esta_suscripcion_activa():
                request.session['familia_id'] = familia.id
                messages.success(request, f'Familia "{familia.nombre}" seleccionada.')
                return redirect('dashboard')
            else:
                messages.error(request, 'La suscripción de esta familia ha expirado.')
        except Familia.DoesNotExist:
            messages.error(request, 'Familia no encontrada.')

    context = {
        'familias': familias,
    }
    return render(request, 'gastos/familias/seleccionar.html', context)


@login_required
def estado_suscripcion(request):
    """Vista para ver el estado de la suscripción"""
    familia_id = request.session.get('familia_id')

    if not familia_id:
        messages.warning(request, 'Selecciona una familia primero.')
        return redirect('seleccionar_familia')

    try:
        familia = Familia.objects.get(id=familia_id)

        # Verificar acceso
        if not familia.puede_acceder(request.user):
            messages.error(request, 'No tienes acceso a esta familia.')
            return redirect('seleccionar_familia')

        context = {
            'familia': familia,
            'dias_restantes': familia.dias_restantes_suscripcion(),
            'suscripcion_activa': familia.esta_suscripcion_activa(),
            'planes_disponibles': PlanSuscripcion.objects.filter(activo=True).order_by('precio_mensual'),
        }

        return render(request, 'gastos/suscripcion/estado.html', context)

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')


def planes_precios(request):
    """Vista pública de planes y precios"""
    planes = PlanSuscripcion.objects.filter(activo=True).order_by('precio_mensual')

    context = {
        'planes': planes,
    }

    return render(request, 'gastos/publico/planes.html', context)


@login_required
def generar_invitacion_familia(request):
    """Genera un código de invitación para que otros usuarios se unan a la familia"""
    familia_id = request.session.get('familia_id')

    if not familia_id:
        messages.warning(request, 'Selecciona una familia primero.')
        return redirect('seleccionar_familia')

    try:
        familia = Familia.objects.get(id=familia_id)

        # Verificar que el usuario tenga permiso (creador o admin)
        if familia.creado_por != request.user and not request.user.is_superuser:
            messages.error(request, 'Solo el creador de la familia puede generar invitaciones.')
            return redirect('dashboard')

        if request.method == 'POST':
            email_invitado = request.POST.get('email_invitado', '').strip()
            mensaje = request.POST.get('mensaje', '').strip()
            dias_validez = int(request.POST.get('dias_validez', 7))
            usos_maximos = int(request.POST.get('usos_maximos', 1))

            # Generar código único
            codigo = InvitacionFamilia.generar_codigo_unico()

            # Calcular fecha de expiración
            fecha_expiracion = timezone.now() + timedelta(days=dias_validez)

            # Crear invitación
            invitacion = InvitacionFamilia.objects.create(
                familia=familia,
                codigo=codigo,
                creado_por=request.user,
                email_invitado=email_invitado or None,
                mensaje_invitacion=mensaje,
                fecha_expiracion=fecha_expiracion,
                usos_maximos=usos_maximos
            )

            messages.success(
                request,
                f'¡Código de invitación generado! Código: {codigo}. '
                f'Válido por {dias_validez} días.'
            )

            # Registrar en logs
            import logging
            logger = logging.getLogger('gastos')
            logger.info(
                f"Invitación creada - Familia: {familia.nombre} - Código: {codigo} - "
                f"Creado por: {request.user.username}"
            )

            return redirect('gestionar_invitaciones')

        # Obtener invitaciones activas de la familia
        invitaciones_activas = familia.invitaciones.filter(
            estado='PENDIENTE',
            fecha_expiracion__gt=timezone.now()
        ).order_by('-fecha_creacion')[:5]

        context = {
            'familia': familia,
            'invitaciones_activas': invitaciones_activas,
        }

        return render(request, 'gastos/familias/generar_invitacion.html', context)

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')


@login_required
def gestionar_invitaciones(request):
    """Vista para gestionar todas las invitaciones de la familia"""
    familia_id = request.session.get('familia_id')

    if not familia_id:
        messages.warning(request, 'Selecciona una familia primero.')
        return redirect('seleccionar_familia')

    try:
        familia = Familia.objects.get(id=familia_id)

        # Verificar acceso
        if not familia.puede_acceder(request.user):
            messages.error(request, 'No tienes acceso a esta familia.')
            return redirect('seleccionar_familia')

        # Obtener todas las invitaciones
        invitaciones = familia.invitaciones.all().order_by('-fecha_creacion')

        # Separar por estado
        pendientes = invitaciones.filter(estado='PENDIENTE', fecha_expiracion__gt=timezone.now())
        aceptadas = invitaciones.filter(estado='ACEPTADA')
        expiradas = invitaciones.filter(estado='EXPIRADA') | invitaciones.filter(
            estado='PENDIENTE',
            fecha_expiracion__lte=timezone.now()
        )

        context = {
            'familia': familia,
            'invitaciones_pendientes': pendientes,
            'invitaciones_aceptadas': aceptadas,
            'invitaciones_expiradas': expiradas,
            'total_invitaciones': invitaciones.count(),
        }

        return render(request, 'gastos/familias/gestionar_invitaciones.html', context)

    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')


@login_required
def cancelar_invitacion(request, invitacion_id):
    """Cancela una invitación pendiente"""
    try:
        invitacion = InvitacionFamilia.objects.get(id=invitacion_id)

        # Verificar que el usuario sea el creador de la familia
        if invitacion.familia.creado_por != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para cancelar esta invitación.')
            return redirect('gestionar_invitaciones')

        if invitacion.estado == 'PENDIENTE':
            invitacion.estado = 'RECHAZADA'
            invitacion.save()
            messages.success(request, f'Invitación {invitacion.codigo} cancelada.')
        else:
            messages.warning(request, 'Esta invitación ya no está pendiente.')

        return redirect('gestionar_invitaciones')

    except InvitacionFamilia.DoesNotExist:
        messages.error(request, 'Invitación no encontrada.')
        return redirect('gestionar_invitaciones')


def unirse_familia(request, codigo=None):
    """Vista para que un usuario se una a una familia usando un código de invitación"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para unirte a una familia.')
        return redirect('login')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()

        if not codigo:
            messages.error(request, 'Debes ingresar un código de invitación.')
            return render(request, 'gastos/familias/unirse.html')

        try:
            invitacion = InvitacionFamilia.objects.get(codigo=codigo)

            # Verificar si es válido
            if not invitacion.esta_valido():
                if invitacion.estado == 'EXPIRADA' or timezone.now() > invitacion.fecha_expiracion:
                    messages.error(request, 'Este código de invitación ha expirado.')
                elif invitacion.estado == 'ACEPTADA':
                    messages.error(request, 'Este código ya alcanzó el máximo de usos.')
                else:
                    messages.error(request, 'Este código de invitación no es válido.')
                return render(request, 'gastos/familias/unirse.html')

            # Verificar que no esté ya en la familia
            if invitacion.familia.miembros.filter(id=request.user.id).exists():
                messages.warning(request, f'Ya eres miembro de {invitacion.familia.nombre}.')
                request.session['familia_id'] = invitacion.familia.id
                return redirect('dashboard')

            # Unir a la familia
            if invitacion.usar_invitacion(request.user):
                request.session['familia_id'] = invitacion.familia.id
                messages.success(
                    request,
                    f'¡Te has unido exitosamente a {invitacion.familia.nombre}!'
                )

                # Registrar en logs
                import logging
                logger = logging.getLogger('gastos')
                logger.info(
                    f"Usuario {request.user.username} se unió a familia {invitacion.familia.nombre} "
                    f"usando código {codigo}"
                )

                return redirect('dashboard')
            else:
                messages.error(request, 'Hubo un error al unirte a la familia. Intenta de nuevo.')

        except InvitacionFamilia.DoesNotExist:
            messages.error(request, 'El código de invitación no existe.')
        except Exception as e:
            import logging
            logger = logging.getLogger('gastos')
            logger.error(f"Error al unirse a familia: {e}", exc_info=True)
            messages.error(request, 'Ocurrió un error. Por favor, intenta de nuevo.')

    # Si viene con código en la URL, pre-llenar el formulario
    context = {
        'codigo_prellenado': codigo if codigo else ''
    }

    return render(request, 'gastos/familias/unirse.html', context)


def password_reset_request(request):
    """Vista para solicitar restablecimiento de contraseña - Con validación de email"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        # Validar que el email no esté vacío
        if not email:
            messages.error(request, '❌ Por favor ingresa un correo electrónico.')
            return render(request, 'gastos/auth/password_reset.html')

        # Validar formato de email básico
        if '@' not in email or '.' not in email:
            messages.error(request, '❌ Por favor ingresa un correo electrónico válido.')
            return render(request, 'gastos/auth/password_reset.html')

        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)

            # Generar token único
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))

            # Crear token en BD (expira en 1 hora)
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=1),
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # Crear URL de restablecimiento
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': token})
            )

            # Intentar enviar email
            email_sent = False
            try:
                send_mail(
                    subject='Restablecer Contraseña - Gastos Familiares',
                    message=f'''Hola {user.first_name or user.username},

Has solicitado restablecer tu contraseña.

Para crear una nueva contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, ignora este correo.

Saludos,
Equipo de Gastos Familiares
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

                email_sent = True
                messages.success(
                    request,
                    f'✅ Se ha enviado un enlace de recuperación a {email}. Por favor, revisa tu correo (y carpeta de spam).'
                )
                logger.info(f"Email de recuperación enviado a {email}")

            except Exception as e:
                logger.error(f"Error al enviar email de recuperación: {e}")

                # Si no se pudo enviar email, mostrar el enlace directamente (UN SOLO MENSAJE)
                messages.warning(
                    request,
                    f'⚠️ No se pudo enviar el email. Copia y pega este enlace en tu navegador (expira en 1 hora): {reset_url}'
                )

        except User.DoesNotExist:
            # UN SOLO MENSAJE con toda la información
            messages.error(
                request,
                f'❌ El correo "{email}" no está registrado en el sistema. Verifica que sea correcto o <a href="/registro/" class="alert-link fw-bold">regístrate aquí</a>.'
            )
            logger.warning(f"Intento de reset para email no registrado: {email}")

    return render(request, 'gastos/auth/password_reset.html')


def password_reset_confirm(request, token):
    """Vista para confirmar y establecer nueva contraseña usando token de BD"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Buscar token en BD
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, '❌ El enlace de recuperación no es válido.')
        return redirect('password_reset')

    # Verificar que el token sea válido
    if not reset_token.is_valid():
        if reset_token.used:
            messages.error(request, '❌ Este enlace ya fue utilizado. Solicita uno nuevo.')
        else:
            messages.error(request, '⏰ El enlace ha expirado (válido por 1 hora). Solicita uno nuevo.')
        return redirect('password_reset')

    user = reset_token.user

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'gastos/auth/password_reset_confirm.html')

        if len(new_password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'gastos/auth/password_reset_confirm.html')

        # Cambiar contraseña
        user.set_password(new_password)
        user.save()

        # Marcar token como usado
        reset_token.mark_as_used()

        messages.success(request, '✅ ¡Contraseña restablecida exitosamente! Ya puedes iniciar sesión.')
        logger.info(f"Contraseña restablecida para usuario: {user.username}")

        return redirect('login')

    # Pasar datos del usuario al template
    context = {
        'user_name': user.first_name or user.username,
        'token_valid': True
    }

    return render(request, 'gastos/auth/password_reset_confirm.html', context)


# ============================================================================
# VISTAS DE LEGAL Y PRIVACIDAD
# ============================================================================

def politica_privacidad(request):
    """Vista de política de privacidad"""
    return render(request, 'gastos/politica_privacidad.html')


def terminos(request):
    """Vista de términos y condiciones"""
    return render(request, 'gastos/terminos.html')


@login_required
def cambiar_password(request):
    """Vista para cambiar contraseña del usuario logueado"""
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_nueva2 = request.POST.get('password_nueva2')

        # Verificar contraseña actual
        if not request.user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('cambiar_password')

        # Verificar que las contraseñas nuevas coincidan
        if password_nueva != password_nueva2:
            messages.error(request, 'Las contraseñas nuevas no coinciden.')
            return redirect('cambiar_password')

        # Cambiar contraseña
        try:
            request.user.set_password(password_nueva)
            request.user.save()

            # Actualizar sesión para mantener al usuario logueado
            update_session_auth_hash(request, request.user)

            # Enviar notificación
            try:
                enviar_notificacion_cambio_password(request.user)
            except Exception as e:
                logger.warning(f"No se pudo enviar notificación de cambio de password: {e}")

            # Registrar en audit log
            registrar_auditoria(
                request,
                accion='PASSWORD_CHANGE',
                modelo='User',
                objeto_id=request.user.id,
                descripcion='Cambio de contraseña exitoso'
            )

            messages.success(request, '✅ Contraseña cambiada exitosamente.')
            return redirect('mis_datos')

        except Exception as e:
            messages.error(request, f'Error al cambiar contraseña: {str(e)}')
            return redirect('cambiar_password')

    return render(request, 'gastos/auth/cambiar_password.html')


@login_required
def mis_datos(request):
    """Panel de gestión de datos personales (RGPD)"""
    from .models import Gasto, AuditLog
    from django.utils import timezone

    # Obtener estadísticas
    total_gastos = Gasto.objects.filter(
        pagado_por__in=request.user.familias.values_list('aportantes', flat=True)
    ).count()

    total_familias = request.user.familias.filter(activo=True).count()
    total_logs = AuditLog.objects.filter(usuario=request.user).count()

    # Calcular días activo
    dias_activo = (timezone.now().date() - request.user.date_joined.date()).days

    # Obtener últimos accesos
    ultimos_accesos = AuditLog.objects.filter(
        usuario=request.user,
        accion__in=['LOGIN', 'LOGOUT']
    ).order_by('-timestamp')[:10]

    context = {
        'total_gastos': total_gastos,
        'total_familias': total_familias,
        'total_logs': total_logs,
        'dias_activo': dias_activo,
        'ultimos_accesos': ultimos_accesos,
    }

    return render(request, 'gastos/mis_datos.html', context)


@login_required
def exportar_datos_usuario(request):
    """Exporta todos los datos del usuario (portabilidad RGPD)"""
    if request.method == 'POST':
        from .security_utils import exportar_datos_usuario as export_data
        from .notifications import enviar_notificacion_exportacion
        import json
        from django.http import JsonResponse, HttpResponse

        try:
            # Exportar datos
            datos = export_data(request.user)

            # Registrar exportación
            registrar_auditoria(
                request,
                accion='EXPORT',
                modelo='User',
                objeto_id=request.user.id,
                descripcion='Exportación completa de datos (RGPD)'
            )

            # Enviar notificación
            try:
                enviar_notificacion_exportacion(request.user, 'Exportación completa de datos')
            except Exception as e:
                logger.warning(f"No se pudo enviar notificación de exportación: {e}")

            # Crear respuesta JSON para descarga
            response = HttpResponse(
                json.dumps(datos, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="mis_datos_finanbot_{request.user.username}.json"'

            messages.success(request, '✅ Tus datos han sido exportados. Se ha enviado una copia a tu email.')
            return response

        except Exception as e:
            logger.error(f"Error al exportar datos: {e}")
            messages.error(request, 'Error al exportar datos. Por favor, inténtalo de nuevo.')
            return redirect('mis_datos')

    return redirect('mis_datos')


@login_required
def eliminar_cuenta(request):
    """Elimina la cuenta del usuario y todos sus datos (derecho al olvido RGPD)"""
    if request.method == 'POST':
        confirmacion = request.POST.get('confirmacion', '')

        if confirmacion != 'ELIMINAR':
            messages.error(request, 'Confirmación incorrecta.')
            return redirect('mis_datos')

        try:
            from .security_utils import anonimizar_datos_usuario

            # Registrar eliminación antes de anonimizar
            registrar_auditoria(
                request,
                accion='DELETE',
                modelo='User',
                objeto_id=request.user.id,
                descripcion='Solicitud de eliminación de cuenta (derecho al olvido)'
            )

            # Anonimizar datos
            anonimo_id = anonimizar_datos_usuario(request.user)

            # Cerrar sesión
            logout(request)

            messages.success(request, f'✅ Tu cuenta ha sido eliminada. Código de referencia: {anonimo_id}')
            return redirect('login')

        except Exception as e:
            logger.error(f"Error al eliminar cuenta: {e}")
            messages.error(request, 'Error al eliminar cuenta. Por favor, contacta a soporte.')
            return redirect('mis_datos')

    return redirect('mis_datos')


