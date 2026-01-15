"""
Script para generar códigos de invitación de prueba
"""
import os
import django
import random
import string

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import CodigoInvitacion, PlanSuscripcion

def generar_codigo():
    """Genera un código aleatorio de 12 caracteres"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def generar_codigos_prueba():
    """Genera códigos de prueba para cada plan"""

    print("=" * 60)
    print("🎫 GENERANDO CÓDIGOS DE INVITACIÓN DE PRUEBA")
    print("=" * 60)
    print()

    # Verificar códigos existentes disponibles
    codigos_disponibles = CodigoInvitacion.objects.filter(usado=False)
    print(f"📊 Códigos disponibles actualmente: {codigos_disponibles.count()}")
    print()

    # Configuración de códigos a generar
    cantidad_por_plan = {
        'GRATUITO': 5,
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
            print()

        except PlanSuscripcion.DoesNotExist:
            print(f"   ⚠️  Plan {tipo_plan} no encontrado")
            print()

    # Mostrar resumen
    print("=" * 60)
    print("✅ CÓDIGOS GENERADOS EXITOSAMENTE")
    print("=" * 60)
    print()

    for tipo_plan, codigos in codigos_generados.items():
        if codigos:
            plan = PlanSuscripcion.objects.get(tipo=tipo_plan)
            print(f"📌 {plan.nombre.upper()}")
            if plan.precio_mensual > 0:
                print(f"   💰 ${plan.precio_mensual:,.0f}/mes - {plan.dias_prueba_gratis} días de prueba gratis")
            else:
                print(f"   🆓 Plan Gratuito")
            print()
            for codigo in codigos:
                print(f"   {codigo}")
            print()

    # Estadísticas finales
    total_generados = sum(len(codigos) for codigos in codigos_generados.values())
    total_disponibles = CodigoInvitacion.objects.filter(usado=False).count()

    print("=" * 60)
    print("📈 ESTADÍSTICAS")
    print("=" * 60)
    print(f"Códigos generados en esta ejecución: {total_generados}")
    print(f"Total de códigos disponibles: {total_disponibles}")
    print()
    print("🎯 Los códigos están listos para crear cuentas nuevas")
    print("=" * 60)

if __name__ == '__main__':
    generar_codigos_prueba()

