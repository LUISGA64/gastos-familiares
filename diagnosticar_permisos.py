"""
Script de diagnóstico para verificar permisos de exportación
"""

from django.contrib.auth.models import User
from gastos.models import PlanSuscripcion, PerfilGamificacion
from django.utils import timezone

def diagnosticar_usuario():
    """Diagnostica el problema de exportación"""

    # Obtener todos los usuarios
    usuarios = User.objects.all()

    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE PERMISOS DE EXPORTACIÓN")
    print("=" * 60)

    for usuario in usuarios:
        try:
            perfil = usuario.perfil_gamificacion

            print(f"\n👤 Usuario: {usuario.username}")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # Información del plan
            print(f"📋 Plan: {perfil.plan.nombre}")
            print(f"💰 Precio: ${perfil.plan.precio:,.0f}/mes")

            # Fechas de suscripción
            if perfil.fecha_inicio_suscripcion:
                print(f"📅 Inicio: {perfil.fecha_inicio_suscripcion.strftime('%d/%m/%Y %H:%M')}")
            else:
                print(f"📅 Inicio: No establecido ❌")

            if perfil.fecha_fin_suscripcion:
                print(f"📅 Fin: {perfil.fecha_fin_suscripcion.strftime('%d/%m/%Y %H:%M')}")

                # Verificar si está vencida
                if perfil.fecha_fin_suscripcion < timezone.now():
                    print(f"⚠️  SUSCRIPCIÓN VENCIDA")
            else:
                print(f"📅 Fin: No establecido ❌")

            # Estado de suscripción
            esta_activa = perfil.esta_suscripcion_activa()
            print(f"\n✅ Suscripción Activa: {esta_activa}")

            # Permisos del plan
            print(f"\n📊 PERMISOS DEL PLAN:")
            print(f"   - permite_exportar_datos: {perfil.plan.permite_exportar_datos}")

            # Verificación del método tiene_exportar_datos()
            puede_exportar = perfil.tiene_exportar_datos()
            print(f"\n🔐 RESULTADO DE tiene_exportar_datos():")
            print(f"   Puede exportar: {puede_exportar}")

            if not puede_exportar:
                print(f"\n❌ RAZONES POR LAS QUE NO PUEDE EXPORTAR:")
                if not esta_activa:
                    print(f"   1. Suscripción NO activa")
                if not perfil.plan.permite_exportar_datos:
                    print(f"   2. El plan '{perfil.plan.nombre}' NO permite exportar")

            # Otros permisos
            print(f"\n📋 OTROS PERMISOS:")
            print(f"   - Max aportantes: {perfil.plan.max_aportantes}")
            print(f"   - Max gastos/mes: {perfil.plan.max_gastos_por_mes}")
            print(f"   - Chatbot IA: {perfil.plan.tiene_chatbot_ia}")

        except Exception as e:
            print(f"\n❌ Error al analizar usuario {usuario.username}: {e}")

    # Mostrar todos los planes disponibles
    print("\n" + "=" * 60)
    print("📋 PLANES DISPONIBLES EN EL SISTEMA")
    print("=" * 60)

    planes = PlanSuscripcion.objects.all().order_by('precio')
    for plan in planes:
        print(f"\n{plan.nombre} - ${plan.precio:,.0f}/mes")
        print(f"   permite_exportar_datos: {plan.permite_exportar_datos}")


if __name__ == '__main__':
    diagnosticar_usuario()
