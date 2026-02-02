"""
Script de prueba para verificar que el chatbot dashboard funciona
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from gastos.models import Familia
from gastos.views_chatbot import chatbot_dashboard

print("=" * 80)
print("PRUEBA: Chatbot Dashboard")
print("=" * 80)

# Obtener usuario
user = User.objects.first()
if not user:
    print("❌ No hay usuarios en la base de datos")
    exit(1)

print(f"✅ Usuario: {user.username}")

# Obtener familia
familia = Familia.objects.filter(miembros=user).first()
if not familia:
    print("❌ Usuario no tiene familia asignada")
    exit(1)

print(f"✅ Familia: {familia.nombre}")

# Probar directamente la vista
print("\nProbando vista chatbot_dashboard directamente...")
try:
    factory = RequestFactory()
    request = factory.get('/chatbot/')
    request.user = user

    # Simular sesión
    from django.contrib.sessions.middleware import SessionMiddleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session['familia_id'] = familia.id
    request.session.save()

    # Llamar a la vista
    response = chatbot_dashboard(request)

    print(f"✅ Status Code: {response.status_code}")

    if response.status_code == 200:
        print("✅ ¡CHATBOT DASHBOARD FUNCIONA CORRECTAMENTE!")
    else:
        print(f"❌ Error: Status {response.status_code}")

except Exception as e:
    print(f"❌ Error al ejecutar la vista: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIN DE LA PRUEBA")
print("=" * 80)
