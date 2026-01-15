"""
Script para listar los códigos de invitación disponibles (sin generar nuevos)
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import PlanSuscripcion, CodigoInvitacion

def listar_codigos_disponibles():
    """Lista todos los códigos de invitación disponibles"""

    print("=" * 70)
    print("📋 CÓDIGOS DE INVITACIÓN DISPONIBLES")
    print("=" * 70)
    print()

    # Obtener estadísticas generales
    total_codigos = CodigoInvitacion.objects.count()
    codigos_disponibles = CodigoInvitacion.objects.filter(usado=False)
    codigos_usados = CodigoInvitacion.objects.filter(usado=True)

    print(f"📊 Total de códigos en sistema: {total_codigos}")
    print(f"✅ Códigos disponibles: {codigos_disponibles.count()}")
    print(f"❌ Códigos usados: {codigos_usados.count()}")
    print()

    if codigos_disponibles.count() == 0:
        print("⚠️  No hay códigos disponibles")
        print()
        print("💡 Ejecuta: python crear_codigos_nuevos.py")
        print("   para generar nuevos códigos")
        print()
        return

    print("=" * 70)
    print()

    # Agrupar por plan
    planes = PlanSuscripcion.objects.all().order_by('precio_mensual')

    for plan in planes:
        codigos_plan = codigos_disponibles.filter(plan=plan)

        if codigos_plan.exists():
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
            print(f"   Códigos disponibles: {codigos_plan.count()}")
            print()

            for codigo in codigos_plan:
                fecha_creacion = codigo.fecha_creacion.strftime("%Y-%m-%d %H:%M")
                print(f"      {codigo.codigo}  (creado: {fecha_creacion})")

            print()

    print("=" * 70)
    print("🎯 INSTRUCCIONES DE USO")
    print("=" * 70)
    print()
    print("Para usar un código:")
    print("1. Inicia el servidor: python manage.py runserver")
    print("2. Ve a: http://127.0.0.1:8000/registro/")
    print("3. Usa cualquiera de los códigos de arriba")
    print()
    print("Para generar más códigos:")
    print("▶️  python crear_codigos_nuevos.py")
    print()
    print("=" * 70)

def listar_codigos_usados():
    """Lista los códigos que ya fueron usados"""

    codigos_usados = CodigoInvitacion.objects.filter(usado=True).select_related('plan', 'usado_por')

    if codigos_usados.count() == 0:
        print("\n✅ No hay códigos usados todavía")
        return

    print()
    print("=" * 70)
    print("📝 CÓDIGOS USADOS")
    print("=" * 70)
    print()

    for codigo in codigos_usados:
        usuario = codigo.usado_por.username if codigo.usado_por else "Desconocido"
        fecha_uso = codigo.fecha_uso.strftime("%Y-%m-%d %H:%M") if codigo.fecha_uso else "N/A"

        print(f"  {codigo.codigo}")
        print(f"    Plan: {codigo.plan.nombre}")
        print(f"    Usuario: {usuario}")
        print(f"    Fecha de uso: {fecha_uso}")
        print()

    print("=" * 70)

def main():
    """Función principal"""
    try:
        listar_codigos_disponibles()
        listar_codigos_usados()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

