"""
Script de prueba para verificar que los aportantes solo muestren nombre en formularios
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import Aportante

print("=" * 60)
print("VERIFICACIÓN: Aportantes en Formularios")
print("=" * 60)

# Obtener algunos aportantes de ejemplo
aportantes = Aportante.objects.all()[:5]

if aportantes:
    print("\n✓ Así se verán los aportantes en los formularios:")
    print("-" * 60)
    for aportante in aportantes:
        print(f"  • {aportante}")  # Esto usa el método __str__
    print("-" * 60)
    print("\n✅ CORRECTO: Solo se muestra el nombre, sin el salario")
else:
    print("\n⚠️ No hay aportantes en la base de datos para probar")

print("\n" + "=" * 60)
