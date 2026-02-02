"""
Script para generar clave de encriptación
"""
from cryptography.fernet import Fernet

# Generar clave
key = Fernet.generate_key().decode()

print("=" * 80)
print("CLAVE DE ENCRIPTACIÓN GENERADA")
print("=" * 80)
print("\nAgrega esta línea a tu archivo .env:")
print("-" * 80)
print(f"ENCRYPTION_KEY={key}")
print("-" * 80)
print("\n⚠️  IMPORTANTE:")
print("   • Guarda esta clave en un lugar seguro")
print("   • NO la subas a GitHub (el .env ya está en .gitignore)")
print("   • Si pierdes esta clave, NO podrás desencriptar los datos")
print("   • En producción, usa una clave diferente")
print("\n" + "=" * 80)
