#!/usr/bin/env python
"""
Script para crear los planes de suscripción iniciales en la base de datos.
Ejecutar con: python crear_planes_iniciales.py
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import PlanSuscripcion
from decimal import Decimal

def crear_planes():
    """Crear los planes de suscripción iniciales si no existen."""

    print("=" * 70)
    print("CREACIÓN DE PLANES DE SUSCRIPCIÓN INICIALES")
    print("=" * 70)
    print()

    planes_iniciales = [
        {
            'nombre': 'Plan Gratuito',
            'tipo': 'GRATIS',
            'descripcion': 'Plan básico gratuito con funcionalidades limitadas',
            'precio_mensual': Decimal('0.00'),
            'max_miembros': 3,
            'max_categorias': 10,
            'soporte_prioritario': False,
            'exportar_datos': False,
            'reportes_avanzados': False,
            'dias_prueba': 0,
            'activo': True,
        },
        {
            'nombre': 'Plan Básico',
            'tipo': 'BASICO',
            'descripcion': 'Plan básico con funcionalidades estándar y periodo de prueba',
            'precio_mensual': Decimal('9990.00'),
            'max_miembros': 5,
            'max_categorias': 20,
            'soporte_prioritario': False,
            'exportar_datos': True,
            'reportes_avanzados': False,
            'dias_prueba': 15,
            'activo': True,
        },
        {
            'nombre': 'Plan Familiar',
            'tipo': 'FAMILIAR',
            'descripcion': 'Plan familiar con funcionalidades completas y periodo de prueba extendido',
            'precio_mensual': Decimal('19990.00'),
            'max_miembros': 10,
            'max_categorias': 50,
            'soporte_prioritario': True,
            'exportar_datos': True,
            'reportes_avanzados': True,
            'dias_prueba': 15,
            'activo': True,
        },
        {
            'nombre': 'Plan Premium',
            'tipo': 'PREMIUM',
            'descripcion': 'Plan premium con todas las funcionalidades y soporte prioritario',
            'precio_mensual': Decimal('29990.00'),
            'max_miembros': 999,  # Sin límite
            'max_categorias': 999,  # Sin límite
            'soporte_prioritario': True,
            'exportar_datos': True,
            'reportes_avanzados': True,
            'dias_prueba': 30,
            'activo': True,
        },
    ]

    planes_creados = 0
    planes_existentes = 0

    for plan_data in planes_iniciales:
        tipo = plan_data['tipo']

        # Verificar si el plan ya existe
        if PlanSuscripcion.objects.filter(tipo=tipo).exists():
            print(f"⚠️  Plan {plan_data['nombre']} ({tipo}) ya existe - OMITIENDO")
            planes_existentes += 1
            continue

        # Crear el plan
        plan = PlanSuscripcion.objects.create(**plan_data)
        planes_creados += 1

        print(f"✅ Plan creado: {plan.nombre}")
        print(f"   Tipo: {plan.tipo}")
        print(f"   Precio: ${plan.precio_mensual:,.0f}/mes")
        print(f"   Max. miembros: {plan.max_miembros}")
        print(f"   Días de prueba: {plan.dias_prueba}")
        print(f"   Características:")
        print(f"     - Exportar datos: {'Sí' if plan.exportar_datos else 'No'}")
        print(f"     - Reportes avanzados: {'Sí' if plan.reportes_avanzados else 'No'}")
        print(f"     - Soporte prioritario: {'Sí' if plan.soporte_prioritario else 'No'}")
        print()

    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"✅ Planes creados: {planes_creados}")
    print(f"⚠️  Planes que ya existían: {planes_existentes}")
    print(f"📊 Total de planes en DB: {PlanSuscripcion.objects.count()}")
    print()

    # Mostrar todos los planes
    print("Planes disponibles en la base de datos:")
    print("-" * 70)
    for plan in PlanSuscripcion.objects.all().order_by('precio_mensual'):
        print(f"• {plan.nombre} ({plan.tipo})")
        print(f"  ${plan.precio_mensual:,.0f}/mes - {plan.max_miembros} miembros - {plan.dias_prueba} días prueba")

    print()
    print("=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)

    if planes_creados > 0:
        print()
        print("🎉 Los planes han sido creados exitosamente.")
        print("   Ahora los usuarios pueden crear familias sin errores.")
        print()
        print("📝 Siguiente paso:")
        print("   1. Reinicia Gunicorn en el servidor: sudo systemctl restart gunicorn")
        print("   2. Prueba crear una familia desde la aplicación")
        print()

if __name__ == '__main__':
    try:
        crear_planes()
    except Exception as e:
        print(f"❌ Error al crear planes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
