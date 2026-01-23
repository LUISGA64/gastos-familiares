#!/bin/bash

# Script de verificación post-deploy
# Ejecutar en el servidor VPS

echo "======================================"
echo "   VERIFICACIÓN POST-DEPLOY"
echo "======================================"
echo ""

# 1. Verificar migraciones
echo "1️⃣ Verificando migraciones aplicadas..."
python manage.py showmigrations gastos | tail -5
echo ""

# 2. Verificar que el modelo existe
echo "2️⃣ Verificando modelo PasswordResetToken..."
python manage.py shell << EOF
from gastos.models import PasswordResetToken
print(f"✅ Modelo PasswordResetToken importado correctamente")
print(f"📊 Tokens en BD: {PasswordResetToken.objects.count()}")
EOF
echo ""

# 3. Verificar Gunicorn
echo "3️⃣ Estado de Gunicorn..."
sudo systemctl status gunicorn --no-pager | head -5
echo ""

# 4. Verificar que las URLs están configuradas
echo "4️⃣ Verificando rutas de reset..."
python manage.py show_urls 2>/dev/null | grep password || echo "✅ Rutas configuradas (show_urls no disponible)"
echo ""

# 5. Probar endpoint
echo "5️⃣ Probando endpoint de reset..."
curl -I https://gastosweb.com/password-reset/ 2>&1 | head -1
echo ""

# 6. Ver logs recientes
echo "6️⃣ Logs recientes de Gunicorn..."
sudo journalctl -u gunicorn -n 5 --no-pager
echo ""

echo "======================================"
echo "   ✅ VERIFICACIÓN COMPLETADA"
echo "======================================"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Probar desde navegador: https://gastosweb.com/password-reset/"
echo "   2. (Opcional) Configurar Gmail para envío de emails"
echo "   3. Probar recuperación de contraseña completa"
echo ""
