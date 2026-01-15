"""
Script para probar que el formulario de gastos funciona correctamente
"""

from gastos.models import Aportante, SubcategoriaGasto, Gasto
from gastos.forms import GastoForm
from datetime import date
from decimal import Decimal

print("=" * 60)
print("VERIFICANDO SISTEMA DE GASTOS")
print("=" * 60)

# 1. Verificar aportantes
print("\n1. Aportantes activos:")
aportantes = Aportante.objects.filter(activo=True)
if aportantes.exists():
    for a in aportantes:
        print(f"   ✓ {a.nombre}")
else:
    print("   ❌ NO HAY APORTANTES ACTIVOS")
    print("   Solución: python manage.py cargar_datos_ejemplo")

# 2. Verificar subcategorías
print("\n2. Subcategorías activas:")
subcategorias = SubcategoriaGasto.objects.filter(activo=True)
if subcategorias.exists():
    print(f"   ✓ {subcategorias.count()} subcategorías disponibles")
    for s in subcategorias[:3]:
        print(f"     - {s}")
else:
    print("   ❌ NO HAY SUBCATEGORÍAS ACTIVAS")
    print("   Solución: python manage.py cargar_datos_ejemplo")

# 3. Probar creación de gasto
print("\n3. Probando creación de gasto:")
if aportantes.exists() and subcategorias.exists():
    try:
        # Datos de prueba
        datos = {
            'subcategoria': subcategorias.first().id,
            'descripcion': 'Gasto de prueba',
            'monto': Decimal('50000'),
            'fecha': date.today(),
            'pagado_por': aportantes.first().id,
            'pagado': True,
        }

        form = GastoForm(data=datos)

        if form.is_valid():
            print("   ✓ Formulario VÁLIDO")
            print("   ✓ Se puede guardar el gasto")

            # No guardamos realmente, solo probamos
            # gasto = form.save()
            # print(f"   ✓ Gasto creado: {gasto}")
        else:
            print("   ❌ Formulario INVÁLIDO")
            print("   Errores:")
            for field, errors in form.errors.items():
                print(f"     - {field}: {errors}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ⚠ No se puede probar: faltan datos base")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETA")
print("=" * 60)

# 4. Contar gastos existentes
total_gastos = Gasto.objects.count()
print(f"\nGastos registrados actualmente: {total_gastos}")

if total_gastos > 0:
    ultimo = Gasto.objects.latest('fecha_registro')
    print(f"Último gasto: {ultimo.subcategoria.nombre} - ${ultimo.monto}")
    print(f"Pagado por: {ultimo.pagado_por.nombre}")

print("\n✅ Si ves este mensaje, el sistema funciona correctamente")
print("Si ves errores arriba, sigue las soluciones indicadas\n")

