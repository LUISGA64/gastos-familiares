"""
Script para actualizar registros de Pago existentes con los nuevos campos de seguridad
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import Pago
from django.utils import timezone
from datetime import timedelta

def actualizar_pagos():
    """Actualiza todos los pagos para agregar campos de seguridad faltantes"""

    print("=" * 60)
    print("🔧 ACTUALIZANDO REGISTROS DE PAGOS")
    print("=" * 60)

    pagos = Pago.objects.all()
    total = pagos.count()

    if total == 0:
        print("✅ No hay pagos para actualizar")
        return

    print(f"\n📊 Total de pagos encontrados: {total}")

    actualizados = 0
    errores = 0

    for pago in pagos:
        try:
            cambios = False

            # Agregar expiración si no existe
            if not pago.expira_en:
                # Expirar 24 horas después de la fecha de pago
                pago.expira_en = pago.fecha_pago + timedelta(hours=24)
                cambios = True

            # Inicializar intentos si no existe
            if pago.intentos_subida is None:
                pago.intentos_subida = 0 if pago.estado == 'PENDIENTE' else 1
                cambios = True

            # Inicializar max_intentos si no existe
            if pago.max_intentos is None or pago.max_intentos == 0:
                pago.max_intentos = 5
                cambios = True

            # Generar firma si no existe
            if not pago.firma_qr or pago.firma_qr == '':
                pago.firma_qr = pago.generar_firma()
                cambios = True

            if cambios:
                pago.save()
                actualizados += 1
                print(f"✅ Pago {pago.referencia_pago} actualizado")

        except Exception as e:
            errores += 1
            print(f"❌ Error en pago {pago.id}: {str(e)}")

    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"Total pagos: {total}")
    print(f"✅ Actualizados: {actualizados}")
    print(f"❌ Errores: {errores}")
    print(f"⏭️  Sin cambios: {total - actualizados - errores}")
    print("=" * 60)

    if errores > 0:
        print("\n⚠️  Hubo errores. Revisa los mensajes anteriores.")
    else:
        print("\n🎉 ¡Todos los pagos actualizados exitosamente!")

if __name__ == '__main__':
    actualizar_pagos()
