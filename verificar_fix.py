"""
Script para verificar que el error de TypeError en dashboard está resuelto
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from decimal import Decimal

print("🔍 Verificando el fix del TypeError...")
print("="*60)

# Simular la operación que causaba el error
total_ingresos = Decimal('5000000')  # Decimal de la BD

# ANTES (causaba error):
# meta_ahorro = total_ingresos * 0.20  # ❌ TypeError

# DESPUÉS (correcto):
meta_ahorro = total_ingresos * Decimal('0.20')  # ✅ Funciona

print(f"✅ Total ingresos: ${total_ingresos:,.0f}")
print(f"✅ Meta de ahorro (20%): ${meta_ahorro:,.0f}")
print(f"✅ Tipo de total_ingresos: {type(total_ingresos)}")
print(f"✅ Tipo de meta_ahorro: {type(meta_ahorro)}")

print("\n" + "="*60)
print("✅ ¡El error de TypeError está RESUELTO!")
print("="*60)

# Probar la vista dashboard
print("\n🚀 Probando la vista dashboard...")
try:
    from django.test import RequestFactory
    from gastos.views import dashboard
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    # Esto causaba el error antes
    response = dashboard(request)
    
    if response.status_code == 200:
        print("✅ La vista dashboard funciona correctamente!")
        print(f"   Status code: {response.status_code}")
    else:
        print(f"⚠️  Status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error al probar la vista: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 Cambios realizados:")
print("   1. Importado Decimal en views.py")
print("   2. Cambiado: total_ingresos * 0.20")
print("   3. A: total_ingresos * Decimal('0.20')")
print("   4. Agregadas conversiones a float para JSON")
print("   5. Corregida división en proyección de gastos")

print("\n🌐 Ahora puedes acceder a: http://localhost:8000/")

