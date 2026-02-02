"""
Script de prueba para verificar que el chatbot dashboard funciona
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from gastos.models import Familia

print("=" * 80)
print("PRUEBA: Chatbot Dashboard")
print("=" * 80)

# Crear cliente de prueba
client = Client()

# Obtener usuario
user = User.objects.first()
if not user:
    print("❌ No hay usuarios en la base de datos")
    exit(1)

print(f"Usuario: {user.username}")

# Login
client.force_login(user)

# Obtener familia
familia = Familia.objects.filter(miembros=user).first()
if familia:
    print(f"Familia: {familia.nombre}")
    # Simular sesión con familia_id
    session = client.session
    session['familia_id'] = familia.id
    session.save()
else:
    print("⚠️  Usuario no tiene familia asignada")

# Probar chatbot dashboard
print("\nProbando /chatbot/...")
response = client.get('/chatbot/')

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("✅ Chatbot Dashboard funciona correctamente")
elif response.status_code == 500:
    print("❌ Error 500 - Ver detalles en logs/errors.log")
    # Intentar obtener el error
    try:
        print("\nError detectado:")
        print(str(response.content[:500], 'utf-8', errors='ignore'))
    except:
        pass
else:
    print(f"⚠️  Status inesperado: {response.status_code}")

print("\n" + "=" * 80)
