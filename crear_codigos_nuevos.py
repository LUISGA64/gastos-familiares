"""
Script para crear/verificar planes y generar códigos de invitación de prueba
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import PlanSuscripcion, CodigoInvitacion
from decimal import Decimal
import random
import string

def generar_codigo():
    """Genera un código aleatorio de 12 caracteres"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def crear_planes():
    """Crea los planes de suscripción si no existen"""
    print("=" * 70)
    print("📋 VERIFICANDO/CREANDO PLANES DE SUSCRIPCIÓN")
    print("=" * 70)
    print()

    planes_config = [
        {
            'nombre': 'Plan Gratuito',
            'tipo': 'GRATIS',
            'precio_mensual': Decimal('0'),
            'max_aportantes': 2,
            'max_gastos_mes': 30,
            'max_categorias': 5,
            'dias_prueba': 0,
            'caracteristicas': 'Ideal para comenzar\nSoporte básico'
        },
        {
            'nombre': 'Plan Básico',
            'tipo': 'BASICO',
            'precio_mensual': Decimal('9900'),
            'max_aportantes': 4,
            'max_gastos_mes': 100,
            'max_categorias': 15,
            'dias_prueba': 15,
            'caracteristicas': 'Perfecto para parejas\nSoporte por email\n15 días de prueba gratis'
        },
        {
            'nombre': 'Plan Premium',
            'tipo': 'PREMIUM',
            'precio_mensual': Decimal('19900'),
            'max_aportantes': 999,
            'max_gastos_mes': 9999,
            'max_categorias': 50,
            'dias_prueba': 15,
            'caracteristicas': 'Para familias grandes\nReportes avanzados\nSoporte prioritario\n15 días de prueba gratis'
        },
        {
            'nombre': 'Plan Empresarial',
            'tipo': 'EMPRESARIAL',
            'precio_mensual': Decimal('49900'),
            'max_aportantes': 9999,
            'max_gastos_mes': 99999,
            'max_categorias': 100,
            'dias_prueba': 30,
            'caracteristicas': 'Para empresas\nGastos ilimitados\nReportes personalizados\nSoporte 24/7\n30 días de prueba gratis'
        }
    ]

    planes_creados = 0
    for plan_config in planes_config:
        plan, created = PlanSuscripcion.objects.get_or_create(
            tipo=plan_config['tipo'],
            defaults=plan_config
        )

        if created:
            print(f"✅ Creado: {plan.nombre} - ${plan.precio_mensual:,.0f}/mes")
            planes_creados += 1
        else:
            print(f"ℹ️  Ya existe: {plan.nombre} - ${plan.precio_mensual:,.0f}/mes")

    print()
    print(f"Total de planes en sistema: {PlanSuscripcion.objects.count()}")
    print()
    return planes_creados

def generar_codigos_prueba():
    """Genera códigos de prueba para cada plan"""

    print("=" * 70)
    print("🎫 GENERANDO CÓDIGOS DE INVITACIÓN DE PRUEBA")
    print("=" * 70)
    print()

    # Verificar códigos existentes disponibles
    codigos_disponibles = CodigoInvitacion.objects.filter(usado=False)
    print(f"📊 Códigos disponibles actualmente: {codigos_disponibles.count()}")
    print()

    # Configuración de códigos a generar
    cantidad_por_plan = {
        'GRATIS': 5,
        'BASICO': 10,
        'PREMIUM': 5,
        'EMPRESARIAL': 3
    }

    codigos_generados = {}

    for tipo_plan, cantidad in cantidad_por_plan.items():
        try:
            plan = PlanSuscripcion.objects.get(tipo=tipo_plan)
            codigos_generados[tipo_plan] = []

            print(f"🔹 Generando {cantidad} códigos para: {plan.nombre}")

            for i in range(cantidad):
                codigo = generar_codigo()
                # Verificar que el código no exista
                while CodigoInvitacion.objects.filter(codigo=codigo).exists():
                    codigo = generar_codigo()

                CodigoInvitacion.objects.create(
                    codigo=codigo,
                    plan=plan
                )
                codigos_generados[tipo_plan].append(codigo)

            print(f"   ✅ {cantidad} códigos generados")

        except PlanSuscripcion.DoesNotExist:
            print(f"   ⚠️  Plan {tipo_plan} no encontrado")

        print()

    return codigos_generados

def mostrar_codigos(codigos_generados):
    """Muestra los códigos generados de forma organizada"""

    print("=" * 70)
    print("✅ CÓDIGOS GENERADOS EXITOSAMENTE")
    print("=" * 70)
    print()

    for tipo_plan, codigos in codigos_generados.items():
        if codigos:
            try:
                plan = PlanSuscripcion.objects.get(tipo=tipo_plan)
                print(f"📌 {plan.nombre.upper()}")

                if plan.precio_mensual > 0:
                    print(f"   💰 ${plan.precio_mensual:,.0f}/mes")
                    if plan.dias_prueba > 0:
                        print(f"   🎁 {plan.dias_prueba} días de prueba gratis")
                else:
                    print(f"   🆓 Plan Gratuito")

                print(f"   👥 Hasta {plan.max_aportantes} aportantes")
                print(f"   📝 Hasta {plan.max_gastos_mes} gastos/mes")
                print(f"   📂 Hasta {plan.max_categorias} categorías")
                print()

                for codigo in codigos:
                    print(f"      {codigo}")
                print()
            except PlanSuscripcion.DoesNotExist:
                pass

    # Estadísticas finales
    total_generados = sum(len(codigos) for codigos in codigos_generados.values())
    total_disponibles = CodigoInvitacion.objects.filter(usado=False).count()

    print("=" * 70)
    print("📈 ESTADÍSTICAS")
    print("=" * 70)
    print(f"✨ Códigos generados en esta ejecución: {total_generados}")
    print(f"📦 Total de códigos disponibles: {total_disponibles}")
    print()
    print("=" * 70)
    print("🎯 INSTRUCCIONES DE USO")
    print("=" * 70)
    print()
    print("1️⃣  Inicia el servidor: python manage.py runserver")
    print("2️⃣  Ve a: http://127.0.0.1:8000/registro/")
    print("3️⃣  Usa cualquiera de los códigos de arriba para registrarte")
    print("4️⃣  ¡Disfruta del sistema!")
    print()
    print("=" * 70)

def main():
    """Función principal"""
    try:
        # Paso 1: Crear/verificar planes
        crear_planes()

        # Paso 2: Generar códigos
        codigos = generar_codigos_prueba()

        # Paso 3: Mostrar resultados
        mostrar_codigos(codigos)

        print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

