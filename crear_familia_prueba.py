# Script para crear una familia de prueba sin autenticación

from django.contrib.auth.models import User
from gastos.models import Familia, PlanSuscripcion
from django.utils import timezone
from datetime import timedelta

print("Creando familia de prueba...")

# Crear o obtener usuario admin
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@ejemplo.com',
        'is_staff': True,
        'is_superuser': True
    }
)

if created:
    user.set_password('admin123')
    user.save()
    print(f"✓ Usuario admin creado")
else:
    print(f"✓ Usuario admin ya existe")

# Obtener plan gratuito
try:
    plan = PlanSuscripcion.objects.get(tipo='GRATIS')
except PlanSuscripcion.DoesNotExist:
    print("❌ No hay planes creados. Ejecuta primero: python manage.py shell < setup_inicial.py")
    exit()

# Crear familia de prueba
familia, created = Familia.objects.get_or_create(
    nombre="Familia de Prueba",
    defaults={
        'creado_por': user,
        'plan': plan,
        'suscripcion_activa': True,
        'en_periodo_prueba': False,
    }
)

if created:
    familia.miembros.add(user)
    print(f"✓ Familia de prueba creada (ID: {familia.id})")
else:
    print(f"✓ Familia de prueba ya existe (ID: {familia.id})")

print(f"\n{'='*60}")
print("FAMILIA DE PRUEBA LISTA")
print(f"{'='*60}")
print(f"ID de Familia: {familia.id}")
print(f"Nombre: {familia.nombre}")
print(f"Plan: {familia.plan.nombre}")
print(f"Suscripción activa: {familia.suscripcion_activa}")
print(f"\nPara usarla, agrega esto en tu sesión o settings:")
print(f"SESSION_FAMILIA_ID = {familia.id}")
print(f"{'='*60}\n")

