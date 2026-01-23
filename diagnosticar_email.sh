#!/bin/bash
# Script para verificar configuración de email en el servidor

echo "=========================================="
echo "  DIAGNÓSTICO DE CONFIGURACIÓN DE EMAIL"
echo "=========================================="
echo ""

cd /var/www/gastos-familiares
source venv/bin/activate

echo "1️⃣ Verificando variables de entorno del .env..."
echo ""
if [ -f .env ]; then
    echo "✅ Archivo .env existe"
    echo ""
    echo "Configuración de EMAIL en .env:"
    grep -E "EMAIL_|DEFAULT_FROM" .env || echo "❌ No hay configuración de EMAIL en .env"
else
    echo "❌ Archivo .env NO existe"
fi

echo ""
echo "=========================================="
echo "2️⃣ Verificando configuración en Django..."
echo ""

python << 'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from django.conf import settings

print(f"EMAIL_BACKEND actual: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NO CONFIGURADO')}")
print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NO CONFIGURADO')}")
print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NO CONFIGURADO')}")
print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NO CONFIGURADO')}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("")
    print("⚠️  PROBLEMA ENCONTRADO:")
    print("   El backend es 'console' - Los emails se muestran en logs, NO se envían")
    print("")
    print("✅ SOLUCIÓN:")
    print("   Cambiar EMAIL_BACKEND en settings.py o .env")
PYEOF

echo ""
echo "=========================================="
echo "3️⃣ Verificando settings.py..."
echo ""

grep -A 5 "EMAIL_BACKEND" DjangoProject/settings.py | head -10

echo ""
echo "=========================================="
echo "✅ DIAGNÓSTICO COMPLETADO"
echo "=========================================="
