"""
Script de prueba para verificar el formato de moneda
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from decimal import Decimal
from gastos.templatetags.gastos_extras import formato_moneda, formato_moneda_privado

# Casos de prueba
test_cases = [
    (0, "$0"),
    (1000, "$1.000"),
    (1000000, "$1.000.000"),
    (1500000, "$1.500.000"),
    (999, "$999"),
    (10000000, "$10.000.000"),
    (Decimal('1234567.89'), "$1.234.568"),
    (Decimal('500.50'), "$501"),
    (-1000, "-$1.000"),
    (-1500000, "-$1.500.000"),
]

print("=" * 60)
print("PRUEBA DE FORMATO DE MONEDA")
print("=" * 60)

for valor, esperado in test_cases:
    resultado = formato_moneda(valor)
    status = "✅ OK" if resultado == esperado else f"❌ FALLO (esperado: {esperado})"
    print(f"{str(valor):>15} -> {resultado:>15} {status}")

print("\n" + "=" * 60)
print("PRUEBA DE PRIVACIDAD")
print("=" * 60)

# Prueba con privacidad activada
for valor in [1000, 1000000, -500000]:
    resultado_visible = formato_moneda_privado(valor, False)
    resultado_oculto = formato_moneda_privado(valor, True)
    print(f"Valor {valor:>10}: Visible={resultado_visible:>15}, Oculto={resultado_oculto}")

print("\n✅ Todas las pruebas completadas")
