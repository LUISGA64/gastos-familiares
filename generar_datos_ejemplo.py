"""
Script para generar datos de ejemplo y probar las nuevas funcionalidades
Ejecutar con: python generar_datos_ejemplo.py
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from gastos.models import (
    Familia, PlanSuscripcion, Aportante, CategoriaGasto, SubcategoriaGasto,
    Gasto, MetaAhorro, PresupuestoCategoria, Notificacion
)
from datetime import date, timedelta
from decimal import Decimal

def crear_datos_ejemplo():
    print("🚀 Generando datos de ejemplo para las nuevas funcionalidades...")

    # Obtener o crear usuario admin
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'is_superuser': True, 'is_staff': True}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ Usuario admin creado (username: admin, password: admin123)")

    # Obtener o crear plan
    plan, _ = PlanSuscripcion.objects.get_or_create(
        nombre='Plan Premium',
        defaults={
            'tipo': 'PREMIUM',
            'precio_mensual': Decimal('50000'),
            'max_aportantes': 10,
            'max_gastos_mes': 500,
            'max_categorias': 50,
            'dias_prueba': 30,
        }
    )
    print(f"✅ Plan de suscripción: {plan.nombre}")

    # Obtener o crear familia
    familia, created = Familia.objects.get_or_create(
        nombre='Familia Ejemplo',
        defaults={
            'descripcion': 'Familia de prueba para demostración',
            'creado_por': user,
            'plan': plan,
            'en_periodo_prueba': True,
        }
    )
    if created:
        familia.miembros.add(user)
    print(f"✅ Familia: {familia.nombre}")

    # Obtener aportantes
    aportantes = Aportante.objects.filter(familia=familia)
    if not aportantes.exists():
        print("⚠️  No hay aportantes. Ejecuta primero: python manage.py cargar_datos_ejemplo")
        return

    # Obtener categorías
    categorias = CategoriaGasto.objects.filter(familia=familia)
    if not categorias.exists():
        print("⚠️  No hay categorías. Ejecuta primero: python manage.py cargar_datos_ejemplo")
        return

    print(f"✅ Encontrados {aportantes.count()} aportantes y {categorias.count()} categorías")

    # ========== CREAR METAS DE AHORRO ==========
    print("\n📊 Creando metas de ahorro...")

    metas_data = [
        {
            'nombre': 'Vacaciones Familiares',
            'descripcion': 'Viaje a Cartagena para toda la familia',
            'monto_objetivo': Decimal('5000000'),
            'monto_actual': Decimal('1500000'),
            'fecha_inicio': date.today() - timedelta(days=90),
            'fecha_objetivo': date.today() + timedelta(days=180),
            'prioridad': 'ALTA',
            'icono': 'airplane',
        },
        {
            'nombre': 'Fondo de Emergencia',
            'descripcion': 'Ahorro para imprevistos',
            'monto_objetivo': Decimal('3000000'),
            'monto_actual': Decimal('2100000'),
            'fecha_inicio': date.today() - timedelta(days=180),
            'fecha_objetivo': date.today() + timedelta(days=90),
            'prioridad': 'ALTA',
            'icono': 'shield-check',
        },
        {
            'nombre': 'Computador Nuevo',
            'descripcion': 'Laptop para trabajo',
            'monto_objetivo': Decimal('2500000'),
            'monto_actual': Decimal('800000'),
            'fecha_inicio': date.today() - timedelta(days=60),
            'fecha_objetivo': date.today() + timedelta(days=120),
            'prioridad': 'MEDIA',
            'icono': 'laptop',
        },
    ]

    for meta_data in metas_data:
        meta, created = MetaAhorro.objects.get_or_create(
            familia=familia,
            nombre=meta_data['nombre'],
            defaults=meta_data
        )
        if created:
            print(f"  ✅ Meta creada: {meta.nombre} - {meta.porcentaje_completado:.1f}% completada")

    # ========== CREAR PRESUPUESTOS ==========
    print("\n💰 Creando presupuestos mensuales...")

    mes_actual = date.today().month
    anio_actual = date.today().year

    presupuestos_data = [
        {'categoria': 'Alimentación', 'monto': Decimal('1200000'), 'alerta': 80},
        {'categoria': 'Transporte', 'monto': Decimal('500000'), 'alerta': 75},
        {'categoria': 'Entretenimiento', 'monto': Decimal('300000'), 'alerta': 85},
        {'categoria': 'Servicios Públicos', 'monto': Decimal('400000'), 'alerta': 90},
    ]

    for presup_data in presupuestos_data:
        try:
            categoria = categorias.get(nombre=presup_data['categoria'])
            presup, created = PresupuestoCategoria.objects.get_or_create(
                familia=familia,
                categoria=categoria,
                mes=mes_actual,
                anio=anio_actual,
                defaults={
                    'monto_presupuestado': presup_data['monto'],
                    'alertar_en': presup_data['alerta'],
                }
            )
            if created:
                estado = presup.estado_visual
                emoji = '🟢' if estado == 'success' else '🟡' if estado == 'warning' else '🔴'
                print(f"  {emoji} Presupuesto: {categoria.nombre} - ${presup.monto_presupuestado:,.0f} ({presup.porcentaje_usado:.1f}% usado)")
        except CategoriaGasto.DoesNotExist:
            print(f"  ⚠️  Categoría '{presup_data['categoria']}' no encontrada")

    # ========== CREAR NOTIFICACIONES ==========
    print("\n🔔 Creando notificaciones de ejemplo...")

    notificaciones_data = [
        {
            'tipo': 'GASTO',
            'titulo': 'Nuevo gasto registrado',
            'mensaje': 'Se registró un gasto de $45.000 en Alimentación',
            'icono': 'receipt',
            'importante': False,
        },
        {
            'tipo': 'PRESUPUESTO_ALERTA',
            'titulo': '⚠️ Presupuesto al 85%',
            'mensaje': 'El presupuesto de Entretenimiento está al 85% de su límite',
            'icono': 'exclamation-triangle',
            'importante': True,
        },
        {
            'tipo': 'META_PROGRESO',
            'titulo': '🎯 Progreso en meta',
            'mensaje': 'Ya llevas 30% de tu meta de Vacaciones Familiares',
            'icono': 'trophy',
            'importante': False,
        },
        {
            'tipo': 'SISTEMA',
            'titulo': '✨ Bienvenido al nuevo dashboard',
            'mensaje': 'Ahora tienes gráficos interactivos, metas de ahorro y más!',
            'icono': 'stars',
            'importante': True,
        },
    ]

    for notif_data in notificaciones_data:
        notif, created = Notificacion.objects.get_or_create(
            usuario=user,
            familia=familia,
            titulo=notif_data['titulo'],
            defaults={
                'tipo': notif_data['tipo'],
                'mensaje': notif_data['mensaje'],
                'icono': notif_data['icono'],
                'importante': notif_data['importante'],
            }
        )
        if created:
            estado = '🔴' if notif.importante else '🔵'
            print(f"  {estado} {notif.titulo}")

    print("\n" + "="*60)
    print("✅ ¡Datos de ejemplo creados exitosamente!")
    print("="*60)
    print("\n📋 Resumen:")
    print(f"  • Metas de ahorro: {MetaAhorro.objects.filter(familia=familia).count()}")
    print(f"  • Presupuestos: {PresupuestoCategoria.objects.filter(familia=familia).count()}")
    print(f"  • Notificaciones: {Notificacion.objects.filter(usuario=user).count()}")
    print("\n🌐 Accede al dashboard en: http://localhost:8000/")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n💡 Tip: Cambia al modo oscuro con el botón en el navbar!")

if __name__ == '__main__':
    try:
        crear_datos_ejemplo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

