"""
Script para activar Plan Premium en un usuario
Útil para testing de exportación PDF/Excel
"""

from django.contrib.auth.models import User
from gastos.models import PlanSuscripcion, PerfilGamificacion
from django.utils import timezone
from datetime import timedelta


def activar_plan_premium(username):
    """Activa plan Premium para un usuario"""
    try:
        # Obtener usuario
        usuario = User.objects.get(username=username)
        print(f"✅ Usuario encontrado: {usuario.username}")

        # Obtener plan premium
        plan_premium = PlanSuscripcion.objects.get(nombre='Premium')
        print(f"✅ Plan Premium encontrado: {plan_premium.nombre}")

        # Actualizar perfil
        perfil = usuario.perfil_gamificacion
        perfil.plan = plan_premium
        perfil.fecha_inicio_suscripcion = timezone.now()
        perfil.fecha_fin_suscripcion = timezone.now() + timedelta(days=30)
        perfil.save()

        print(f"\n🎉 ¡PLAN PREMIUM ACTIVADO!")
        print(f"📅 Válido hasta: {perfil.fecha_fin_suscripcion.strftime('%d/%m/%Y')}")
        print(f"✅ Puede exportar datos: {perfil.tiene_exportar_datos()}")
        print(f"✅ Max aportantes: {perfil.plan.max_aportantes}")
        print(f"✅ Max gastos/mes: {perfil.plan.max_gastos_por_mes}")

        return True

    except User.DoesNotExist:
        print(f"❌ Error: Usuario '{username}' no existe")
        print("💡 Usuarios disponibles:")
        for u in User.objects.all():
            print(f"   - {u.username}")
        return False

    except PlanSuscripcion.DoesNotExist:
        print("❌ Error: Plan Premium no existe en la base de datos")
        print("💡 Ejecuta: python actualizar_planes.py")
        return False

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def mostrar_estado_usuario(username):
    """Muestra el estado actual del usuario"""
    try:
        usuario = User.objects.get(username=username)
        perfil = usuario.perfil_gamificacion

        print(f"\n📊 ESTADO ACTUAL DE {username}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Plan actual: {perfil.plan.nombre}")
        print(f"Precio: ${perfil.plan.precio:,.0f}/mes")
        print(f"Suscripción activa: {perfil.esta_suscripcion_activa()}")

        if perfil.fecha_fin_suscripcion:
            print(f"Válido hasta: {perfil.fecha_fin_suscripcion.strftime('%d/%m/%Y')}")

        print(f"\n📋 PERMISOS:")
        print(f"✅ Exportar datos: {perfil.tiene_exportar_datos()}")
        print(f"✅ Max aportantes: {perfil.plan.max_aportantes}")
        print(f"✅ Max gastos/mes: {perfil.plan.max_gastos_por_mes}")
        print(f"✅ Chatbot IA: {perfil.plan.tiene_chatbot_ia}")

        print(f"\n🎮 GAMIFICACIÓN:")
        print(f"Nivel: {perfil.nivel}")
        print(f"Puntos: {perfil.puntos_totales}")
        print(f"Racha: {perfil.dias_racha} días 🔥")

        return True

    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no existe")
        return False


# Ejecución directa
if __name__ == '__main__':
    import sys

    print("=" * 50)
    print("🔧 ACTIVADOR DE PLAN PREMIUM")
    print("=" * 50)

    # Obtener username del argumento o usar el primero disponible
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        # Usar el primer usuario disponible
        try:
            username = User.objects.first().username
            print(f"ℹ️ Usando primer usuario disponible: {username}")
        except:
            print("❌ No hay usuarios en la base de datos")
            print("💡 Crea uno con: python manage.py createsuperuser")
            sys.exit(1)

    # Mostrar estado actual
    mostrar_estado_usuario(username)

    # Preguntar si quiere activar Premium
    print("\n" + "=" * 50)
    respuesta = input(f"\n¿Activar Plan Premium para {username}? (s/n): ").lower()

    if respuesta == 's':
        if activar_plan_premium(username):
            print("\n✅ ¡Listo! Ahora puedes probar la exportación PDF/Excel")
            print(f"🌐 http://127.0.0.1:8000/dashboard/")
    else:
        print("❌ Operación cancelada")
