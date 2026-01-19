#!/usr/bin/env python
"""
Script para generar un SECRET_KEY seguro para Django.
Úsalo para crear una nueva SECRET_KEY antes de hacer deploy.
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("🔐 SECRET_KEY GENERADO PARA RAILWAY")
    print("="*70)
    print(f"\n{secret_key}\n")
    print("="*70)
    print("📋 Copia este valor y úsalo en Railway:")
    print("   Railway > Tu Servicio > Variables > New Variable")
    print("   Nombre: SECRET_KEY")
    print(f"   Valor: {secret_key}")
    print("="*70 + "\n")
