"""
Script para actualizar los planes con características diferenciadas
Ejecutar: python actualizar_planes.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import PlanSuscripcion

print("🔧 ACTUALIZANDO PLANES CON CARACTERÍSTICAS DIFERENCIADAS")
print("=" * 60)

# Plan Gratuito - Muy limitado
plan_gratis = PlanSuscripcion.objects.get(tipo='GRATIS')
plan_gratis.max_aportantes = 2
plan_gratis.max_gastos_mes = 30
plan_gratis.max_categorias = 5
plan_gratis.permite_reportes_avanzados = False
plan_gratis.permite_conciliacion_automatica = False
plan_gratis.permite_notificaciones_email = False
plan_gratis.permite_historial_completo = False  # Solo 3 meses
plan_gratis.permite_exportar_datos = False
plan_gratis.soporte_prioritario = False
plan_gratis.max_archivos_adjuntos = 0  # Sin adjuntos
plan_gratis.save()
print("✅ Plan Gratuito actualizado:")
print("   - 2 aportantes, 30 gastos/mes, 5 categorías")
print("   - SIN reportes avanzados")
print("   - SIN conciliación automática")
print("   - SIN notificaciones email")
print("   - Historial limitado (3 meses)")
print("   - SIN exportar datos")
print("   - SIN archivos adjuntos")
print("   - Soporte por email (48-72 hrs)")

# Plan Básico - Valor medio con características útiles
plan_basico = PlanSuscripcion.objects.get(tipo='BASICO')
plan_basico.max_aportantes = 4
plan_basico.max_gastos_mes = 100
plan_basico.max_categorias = 15
plan_basico.permite_reportes_avanzados = True  # ⭐ DIFERENCIADOR
plan_basico.permite_conciliacion_automatica = True  # ⭐ DIFERENCIADOR
plan_basico.permite_notificaciones_email = True  # ⭐ DIFERENCIADOR
plan_basico.permite_historial_completo = True  # ⭐ DIFERENCIADOR
plan_basico.permite_exportar_datos = False  # Premium only
plan_basico.soporte_prioritario = False
plan_basico.max_archivos_adjuntos = 1  # ⭐ DIFERENCIADOR (1 por gasto)
plan_basico.save()
print("\n✅ Plan Básico actualizado:")
print("   - 4 aportantes, 100 gastos/mes, 15 categorías")
print("   - ✅ Reportes avanzados con gráficos")
print("   - ✅ Conciliación automática")
print("   - ✅ Notificaciones por email")
print("   - ✅ Historial completo ilimitado")
print("   - ✅ 1 archivo adjunto por gasto")
print("   - Soporte estándar (24-48 hrs)")

# Plan Premium - Todo incluido
plan_premium = PlanSuscripcion.objects.get(tipo='PREMIUM')
plan_premium.max_aportantes = 8
plan_premium.max_gastos_mes = 500
plan_premium.max_categorias = 50
plan_premium.permite_reportes_avanzados = True
plan_premium.permite_conciliacion_automatica = True
plan_premium.permite_notificaciones_email = True
plan_premium.permite_historial_completo = True
plan_premium.permite_exportar_datos = True  # ⭐ DIFERENCIADOR
plan_premium.soporte_prioritario = True  # ⭐ DIFERENCIADOR
plan_premium.max_archivos_adjuntos = 5  # ⭐ DIFERENCIADOR
plan_premium.save()
print("\n✅ Plan Premium actualizado:")
print("   - 8 aportantes, 500 gastos/mes, 50 categorías")
print("   - ✅ Todo lo del Básico +")
print("   - ✅ Exportar a Excel/PDF/CSV")
print("   - ✅ 5 archivos adjuntos por gasto")
print("   - ✅ Soporte prioritario (<24 hrs)")

# Plan Empresarial - Sin límites
plan_empresarial = PlanSuscripcion.objects.get(tipo='EMPRESARIAL')
plan_empresarial.max_aportantes = 999
plan_empresarial.max_gastos_mes = 999999
plan_empresarial.max_categorias = 999
plan_empresarial.permite_reportes_avanzados = True
plan_empresarial.permite_conciliacion_automatica = True
plan_empresarial.permite_notificaciones_email = True
plan_empresarial.permite_historial_completo = True
plan_empresarial.permite_exportar_datos = True
plan_empresarial.soporte_prioritario = True
plan_empresarial.max_archivos_adjuntos = 10
plan_empresarial.save()
print("\n✅ Plan Empresarial actualizado:")
print("   - Ilimitado todo")
print("   - 10 archivos adjuntos")
print("   - Soporte dedicado")

print("\n" + "=" * 60)
print("🎉 PLANES ACTUALIZADOS EXITOSAMENTE")
print("=" * 60)

# Mostrar comparación
print("\n📊 COMPARACIÓN DE CARACTERÍSTICAS:")
print("-" * 60)
print(f"{'Característica':<35} {'GRATIS':<10} {'BÁSICO':<10} {'PREMIUM':<10}")
print("-" * 60)
print(f"{'Reportes Avanzados':<35} {'❌':<10} {'✅':<10} {'✅':<10}")
print(f"{'Conciliación Automática':<35} {'❌':<10} {'✅':<10} {'✅':<10}")
print(f"{'Notificaciones Email':<35} {'❌':<10} {'✅':<10} {'✅':<10}")
print(f"{'Historial Completo':<35} {'❌ 3m':<10} {'✅':<10} {'✅':<10}")
print(f"{'Exportar Datos':<35} {'❌':<10} {'❌':<10} {'✅':<10}")
print(f"{'Archivos Adjuntos':<35} {'0':<10} {'1':<10} {'5':<10}")
print(f"{'Soporte':<35} {'48-72h':<10} {'24-48h':<10} {'<24h':<10}")
print("-" * 60)

print("\n💡 VALOR AGREGADO PLAN BÁSICO:")
print("   ⭐ Reportes con gráficos interactivos")
print("   ⭐ Conciliación automática (ahorra tiempo)")
print("   ⭐ Notificaciones de vencimientos y alertas")
print("   ⭐ Historial sin límite de tiempo")
print("   ⭐ Adjuntar comprobantes (1 por gasto)")
print("   ⭐ Soporte más rápido")
print("\n   💰 Por solo $9,900/mes ¡Vale la pena!")

