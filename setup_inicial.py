"""
Script para crear planes de suscripción y códigos de invitación iniciales
"""

from gastos.models import PlanSuscripcion, CodigoInvitacion
from decimal import Decimal
import random
import string

def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

print("="*60)
print("CONFIGURACIÓN INICIAL DEL SISTEMA")
print("="*60)

# PASO 2: Crear Planes
print("\n📋 PASO 2: Creando planes de suscripción...")

# Limpiar planes existentes (solo para desarrollo)
PlanSuscripcion.objects.all().delete()

# Plan Gratuito
plan_gratis = PlanSuscripcion.objects.create(
    nombre="Plan Gratuito",
    tipo="GRATIS",
    precio_mensual=Decimal('0'),
    max_aportantes=2,
    max_gastos_mes=30,
    max_categorias=5,
    dias_prueba=0,
    caracteristicas="Ideal para comenzar\nSoporte básico"
)
print("✅ Plan Gratuito creado")

# Plan Básico
plan_basico = PlanSuscripcion.objects.create(
    nombre="Plan Básico",
    tipo="BASICO",
    precio_mensual=Decimal('9900'),
    max_aportantes=4,
    max_gastos_mes=100,
    max_categorias=15,
    dias_prueba=15,
    caracteristicas="Perfecto para parejas\nSoporte por email\n15 días de prueba gratis"
)
print("✅ Plan Básico creado ($9,900/mes)")

# Plan Premium
plan_premium = PlanSuscripcion.objects.create(
    nombre="Plan Premium",
    tipo="PREMIUM",
    precio_mensual=Decimal('19900'),
    max_aportantes=999,
    max_gastos_mes=999999,
    max_categorias=999,
    dias_prueba=15,
    caracteristicas="Todo ilimitado\nSoporte prioritario\nExportación de datos\nReportes avanzados"
)
print("✅ Plan Premium creado ($19,900/mes)")

# Plan Empresarial
plan_empresarial = PlanSuscripcion.objects.create(
    nombre="Plan Empresarial",
    tipo="EMPRESARIAL",
    precio_mensual=Decimal('49900'),
    max_aportantes=999,
    max_gastos_mes=999999,
    max_categorias=999,
    dias_prueba=30,
    caracteristicas="Múltiples familias\nAPI personalizada\nSoporte 24/7\nCapacitación incluida"
)
print("✅ Plan Empresarial creado ($49,900/mes)")

# PASO 3: Generar Códigos de Invitación
print("\n📋 PASO 3: Generando códigos de invitación...")

# Limpiar códigos existentes (solo para desarrollo)
CodigoInvitacion.objects.all().delete()

print("\n📌 CÓDIGOS PLAN GRATUITO (Para pruebas):")
for i in range(5):
    codigo = generar_codigo()
    CodigoInvitacion.objects.create(codigo=codigo, plan=plan_gratis)
    print(f"  {codigo}")

print("\n💰 CÓDIGOS PLAN BÁSICO ($9,900/mes):")
for i in range(10):
    codigo = generar_codigo()
    CodigoInvitacion.objects.create(codigo=codigo, plan=plan_basico)
    print(f"  {codigo}")

print("\n⭐ CÓDIGOS PLAN PREMIUM ($19,900/mes):")
for i in range(5):
    codigo = generar_codigo()
    CodigoInvitacion.objects.create(codigo=codigo, plan=plan_premium)
    print(f"  {codigo}")

print("\n" + "="*60)
print("✅ CONFIGURACIÓN COMPLETADA")
print("="*60)
print(f"\nPlanes creados: {PlanSuscripcion.objects.count()}")
print(f"Códigos generados: {CodigoInvitacion.objects.count()}")
print("\n🚀 El sistema está listo para usar!")
print("\nPróximos pasos:")
print("1. python manage.py createsuperuser")
print("2. python manage.py runserver")
print("3. Ir a http://127.0.0.1:8000/planes/")
print("\n")

