"""
Actualizar precios de planes y corregir Plan Básico a $9,900
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import PlanSuscripcion

print("💰 ACTUALIZANDO PRECIOS DE PLANES")
print("=" * 60)

# Actualizar precios correctos
planes_precios = {
    'GRATIS': 0,
    'BASICO': 9900,
    'PREMIUM': 15900,
    'EMPRESARIAL': 49900
}

for tipo, precio in planes_precios.items():
    plan = PlanSuscripcion.objects.get(tipo=tipo)
    plan.precio_mensual = precio
    plan.save()
    print(f"✅ {plan.nombre}: ${precio:,.0f}/mes")

print("\n" + "=" * 60)
print("✅ PRECIOS ACTUALIZADOS CORRECTAMENTE")
print("\nPlan Básico ahora es: $9,900/mes")
print("Más accesible para familias colombianas!")

