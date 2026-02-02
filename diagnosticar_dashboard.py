"""
Script de diagnóstico para error 500 en dashboard
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from gastos.views import dashboard
import traceback

print("=" * 80)
print("DIAGNÓSTICO: Error 500 en Dashboard")
print("=" * 80)

# 1. Verificar usuario
print("\n1. VERIFICANDO USUARIOS")
print("-" * 80)
usuarios = User.objects.all()
print(f"Total usuarios: {usuarios.count()}")
if usuarios.exists():
    user = usuarios.first()
    print(f"Usuario de prueba: {user.username}")
    print(f"Tiene familias: {user.familias.exists() if hasattr(user, 'familias') else 'No tiene atributo familias'}")
else:
    print("❌ No hay usuarios en la base de datos")
    exit(1)

# 2. Probar la vista directamente
print("\n2. PROBANDO VISTA DASHBOARD")
print("-" * 80)
try:
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    request.user = user

    # Simular sesión
    from django.contrib.sessions.middleware import SessionMiddleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()

    # Agregar familia_id a la sesión
    if hasattr(user, 'familias') and user.familias.exists():
        request.session['familia_id'] = user.familias.first().id

    print("Llamando a la vista dashboard...")
    response = dashboard(request)
    print(f"✅ Status Code: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTraceback completo:")
    print("-" * 80)
    traceback.print_exc()

# 3. Probar con Client
print("\n3. PROBANDO CON DJANGO CLIENT")
print("-" * 80)
try:
    client = Client()
    client.force_login(user)
    response = client.get('/dashboard/')
    print(f"Status Code: {response.status_code}")

    if response.status_code == 500:
        print("❌ Error 500 detectado")
        # Intentar ver el contenido del error
        try:
            print("\nContenido parcial de la respuesta:")
            print(str(response.content[:1000], 'utf-8', errors='ignore'))
        except:
            pass
    elif response.status_code == 200:
        print("✅ Dashboard carga correctamente")
    else:
        print(f"⚠️  Status inesperado: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

# 4. Verificar template
print("\n4. VERIFICANDO TEMPLATE BASE.HTML")
print("-" * 80)
import os.path
base_path = 'templates/gastos/base.html'
if os.path.exists(base_path):
    print(f"✅ {base_path} existe")
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"Tamaño: {len(content)} caracteres")
        tiene_sidebar = 'Sí' if 'sidebar' in content else 'No'
        tiene_humanize = 'Sí' if 'load humanize' in content else 'No'
        tiene_static = 'Sí' if 'load static' in content else 'No'
        print(f"Contiene 'sidebar': {tiene_sidebar}")
        print(f"Contiene load humanize: {tiene_humanize}")
        print(f"Contiene load static: {tiene_static}")
else:
    print(f"❌ {base_path} NO existe")

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 80)
