"""
Script para crear migraciones y aplicarlas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.management import call_command

print("="*60)
print("CREANDO MIGRACIONES PARA AUDITLOG")
print("="*60)

try:
    # Crear migraciones
    call_command('makemigrations', 'gastos', verbosity=2)
    print("\n✅ Migraciones creadas exitosamente")

    # Aplicar migraciones
    print("\n" + "="*60)
    print("APLICANDO MIGRACIONES")
    print("="*60)
    call_command('migrate', 'gastos', verbosity=2)
    print("\n✅ Migraciones aplicadas exitosamente")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
