from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Familia, PlanSuscripcion, CodigoInvitacion
import random
import string


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
                    messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Tu suscripción ha expirado. Por favor, renueva tu plan.')
            else:
                login(request, user)
                messages.warning(request, 'No tienes una familia registrada. Crea una ahora.')
                return redirect('crear_familia')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'gastos/auth/login.html')


@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


def registro_view(request):
    """Vista de registro con código de invitación"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        codigo_invitacion = request.POST.get('codigo_invitacion')

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

        # Validar código de invitación
        try:
            codigo = CodigoInvitacion.objects.get(codigo=codigo_invitacion)
            if not codigo.esta_valido():
                messages.error(request, 'El código de invitación no es válido o ya fue usado.')
                return render(request, 'gastos/auth/registro.html')
        except CodigoInvitacion.DoesNotExist:
            messages.error(request, 'El código de invitación no existe.')
            return render(request, 'gastos/auth/registro.html')

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Marcar código como usado
        codigo.marcar_como_usado(user)

        # Crear familia automáticamente
        familia = Familia.objects.create(
            nombre=f"Familia {last_name}",
            creado_por=user,
            plan=codigo.plan,
            en_periodo_prueba=codigo.plan.dias_prueba > 0,
            fecha_inicio_suscripcion=timezone.now(),
            fecha_fin_suscripcion=timezone.now() + timedelta(days=codigo.plan.dias_prueba) if codigo.plan.dias_prueba > 0 else None
        )
        familia.miembros.add(user)

        # Login automático
        login(request, user)
        request.session['familia_id'] = familia.id

        messages.success(request, f'¡Registro exitoso! Bienvenido {first_name}. Tienes {codigo.plan.dias_prueba} días de prueba gratis.')
        return redirect('dashboard')

    return render(request, 'gastos/auth/registro.html')


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

