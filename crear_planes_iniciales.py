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
            'precio_mensual': Decimal('0.00'),
            'max_aportantes': 2,
            'max_gastos_mes': 50,
            'max_categorias': 10,
            'dias_prueba': 0,
            'activo': True,
            'caracteristicas': 'Funcionalidades básicas\nHasta 2 aportantes\n50 gastos por mes\n10 categorías\nHistorial de 3 meses',
            'permite_reportes_avanzados': False,
            'permite_conciliacion_automatica': False,
            'permite_notificaciones_email': False,
            'permite_historial_completo': False,
            'permite_exportar_datos': False,
            'soporte_prioritario': False,
        },
        {
            'nombre': 'Plan Básico',
            'tipo': 'BASICO',
            'precio_mensual': Decimal('9990.00'),
            'max_aportantes': 4,
            'max_gastos_mes': 200,
            'max_categorias': 20,
            'dias_prueba': 15,
            'activo': True,
            'caracteristicas': '15 días de prueba gratis\nHasta 4 aportantes\n200 gastos por mes\n20 categorías\nExportar a Excel/PDF',
            'permite_reportes_avanzados': False,
            'permite_conciliacion_automatica': True,
            'permite_notificaciones_email': True,
            'permite_historial_completo': False,
            'permite_exportar_datos': True,
            'soporte_prioritario': False,
        },
        {
            'nombre': 'Plan Familiar',
            'tipo': 'FAMILIAR',
            'precio_mensual': Decimal('19990.00'),
            'max_aportantes': 8,
            'max_gastos_mes': 500,
            'max_categorias': 50,
            'dias_prueba': 15,
            'activo': True,
            'caracteristicas': '15 días de prueba gratis\nHasta 8 aportantes\n500 gastos por mes\n50 categorías\nReportes avanzados\nHistorial completo\nSoporte prioritario',
            'permite_reportes_avanzados': True,
            'permite_conciliacion_automatica': True,
            'permite_notificaciones_email': True,
            'permite_historial_completo': True,
            'permite_exportar_datos': True,
            'soporte_prioritario': True,
        },
        {
            'nombre': 'Plan Premium',
            'tipo': 'PREMIUM',
            'precio_mensual': Decimal('29990.00'),
            'max_aportantes': 999,  # Sin límite
            'max_gastos_mes': 9999,  # Sin límite
            'max_categorias': 999,  # Sin límite
            'dias_prueba': 30,
            'activo': True,
            'caracteristicas': '30 días de prueba gratis\nAportantes ilimitados\nGastos ilimitados\nCategorías ilimitadas\nTodas las características\nSoporte prioritario 24/7',
            'permite_reportes_avanzados': True,
            'permite_conciliacion_automatica': True,
            'permite_notificaciones_email': True,
            'permite_historial_completo': True,
            'permite_exportar_datos': True,
            'soporte_prioritario': True,
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
        print(f"   Max. aportantes: {plan.max_aportantes}")
        print(f"   Max. gastos/mes: {plan.max_gastos_mes}")
        print(f"   Días de prueba: {plan.dias_prueba}")
        print(f"   Características:")
        print(f"     - Exportar datos: {'Sí' if plan.permite_exportar_datos else 'No'}")
        print(f"     - Reportes avanzados: {'Sí' if plan.permite_reportes_avanzados else 'No'}")
        print(f"     - Soporte prioritario: {'Sí' if plan.soporte_prioritario else 'No'}")
        print(f"     - Conciliación automática: {'Sí' if plan.permite_conciliacion_automatica else 'No'}")
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
        print(f"  ${plan.precio_mensual:,.0f}/mes - {plan.max_aportantes} aportantes - {plan.dias_prueba} días prueba")

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
