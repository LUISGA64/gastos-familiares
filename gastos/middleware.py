"""
Middleware para gestión de familias y seguridad
"""
from django.shortcuts import redirect
from django.contrib import messages


class FamiliaSecurityMiddleware:
    """
    Middleware que asegura:
    1. Usuario debe tener una familia seleccionada
    2. Usuario solo puede ver datos de su familia
    3. Cada familia está completamente aislada
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # URLs que no requieren familia
        self.exempt_urls = [
            '/login/',
            '/logout/',
            '/registro/',
            '/planes/',
            '/familia/crear/',
            '/familia/seleccionar/',
            '/admin/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Si no está autenticado, continuar (login_required lo manejará)
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Si es superuser o staff, permitir todo
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # Si la URL está exenta, continuar
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)

        # Verificar que tenga familia_id en sesión
        familia_id = request.session.get('familia_id')

        if not familia_id:
            # Usuario no tiene familia seleccionada
            # Verificar si tiene familias disponibles
            if request.user.familias.exists():
                # Redirigir a seleccionar familia
                messages.warning(request, 'Por favor selecciona una familia.')
                return redirect('seleccionar_familia')
            else:
                # No tiene familias, redirigir a crear
                messages.warning(request, 'Debes crear una familia primero.')
                return redirect('crear_familia')

        # Verificar que el usuario pertenece a esa familia
        from .models import Familia
        try:
            familia = Familia.objects.get(id=familia_id)
            if not familia.puede_acceder(request.user):
                # Usuario no pertenece a esta familia
                messages.error(request, 'No tienes permiso para acceder a esa familia.')
                request.session.pop('familia_id', None)
                return redirect('seleccionar_familia')
        except Familia.DoesNotExist:
            # Familia no existe
            messages.error(request, 'La familia seleccionada no existe.')
            request.session.pop('familia_id', None)
            return redirect('seleccionar_familia')

        response = self.get_response(request)
        return response

