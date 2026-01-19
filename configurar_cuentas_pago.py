"""
Script para configurar las cuentas de pago (Bancolombia y Nequi)
Ejecutar con: python configurar_cuentas_pago.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import ConfiguracionCuentaPago

def configurar_cuentas():
    """Crea o actualiza las cuentas de pago"""

    print("=" * 60)
    print("🏦 CONFIGURACIÓN DE CUENTAS DE PAGO")
    print("=" * 60)

    # Configuración de Bancolombia
    bancolombia, created = ConfiguracionCuentaPago.objects.update_or_create(
        metodo='BANCOLOMBIA',
        defaults={
            'activo': True,
            'nombre_banco': 'Bancolombia',
            'tipo_cuenta': 'AHORROS',
            'numero_cuenta': '12345678901',  # ← CAMBIAR POR TU CUENTA REAL
            'titular': 'Gestor Gastos Familiares SAS',  # ← CAMBIAR POR TU NOMBRE/EMPRESA
            'nit': '900.123.456-7',  # ← CAMBIAR POR TU NIT (opcional)
            'color': '#FFDD00',
            'icono': '🏦',
            'instrucciones': '''Abre la app de Bancolombia
Ve a "Transferencias"
Escanea el código QR o ingresa los datos manualmente
Confirma el monto y la referencia
Completa la transferencia
Sube el comprobante aquí'''
        }
    )

    if created:
        print(f"✅ Bancolombia creada: {bancolombia.numero_cuenta}")
    else:
        print(f"🔄 Bancolombia actualizada: {bancolombia.numero_cuenta}")

    # Configuración de Nequi
    nequi, created = ConfiguracionCuentaPago.objects.update_or_create(
        metodo='NEQUI',
        defaults={
            'activo': True,
            'nombre_banco': 'Nequi',
            'tipo_cuenta': 'NEQUI',
            'numero_cuenta': '300 123 4567',  # ← CAMBIAR POR TU NÚMERO NEQUI REAL
            'titular': 'Gestor Gastos Familiares',  # ← CAMBIAR POR TU NOMBRE
            'nit': '',
            'color': '#FF006B',
            'icono': '💰',
            'instrucciones': '''Abre la app de Nequi
Ve a "Enviar plata"
Escanea el código QR
Confirma el monto
Completa la transferencia
Sube el comprobante aquí'''
        }
    )

    if created:
        print(f"✅ Nequi creada: {nequi.numero_cuenta}")
    else:
        print(f"🔄 Nequi actualizada: {nequi.numero_cuenta}")

    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("=" * 60)

    cuentas = ConfiguracionCuentaPago.objects.all()
    for cuenta in cuentas:
        print(f"\n{cuenta.icono} {cuenta.nombre_banco}")
        print(f"   Método: {cuenta.metodo}")
        print(f"   Tipo: {cuenta.get_tipo_cuenta_display()}")
        print(f"   Número: {cuenta.numero_cuenta}")
        print(f"   Titular: {cuenta.titular}")
        print(f"   Estado: {'✅ Activo' if cuenta.activo else '❌ Inactivo'}")

    print("\n" + "=" * 60)
    print("⚠️  IMPORTANTE: EDITA LAS CUENTAS REALES")
    print("=" * 60)
    print("Los datos actuales son DE EJEMPLO.")
    print("Para configurar tus cuentas reales:")
    print("")
    print("1. Ir al admin de Django:")
    print("   http://127.0.0.1:8000/admin/")
    print("")
    print("2. Buscar: 'Configuraciones de Cuentas de Pago'")
    print("")
    print("3. Editar cada cuenta con tus datos reales:")
    print("   - Bancolombia: número de cuenta y titular")
    print("   - Nequi: número de celular y titular")
    print("")
    print("4. Guardar cambios")
    print("=" * 60)


if __name__ == '__main__':
    configurar_cuentas()
