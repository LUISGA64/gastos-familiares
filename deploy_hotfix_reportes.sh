#!/bin/bash
# Script de despliegue rápido para hotfix reportes
# Ejecutar en el servidor OVH

echo "🚀 Iniciando despliegue de hotfix..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Ir al directorio del proyecto
echo "📂 Cambiando al directorio del proyecto..."
cd /var/www/html/FinanBot

# 2. Verificar estado actual
echo ""
echo "🔍 Estado actual de Git:"
git log --oneline -n 3

# 3. Pull de cambios
echo ""
echo "📥 Descargando cambios desde GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Pull exitoso${NC}"
else
    echo -e "${RED}❌ Error en pull. Verifica tu conexión.${NC}"
    exit 1
fi

# 4. Activar entorno virtual
echo ""
echo "🐍 Activando entorno virtual..."
source venv/bin/activate

# 5. Verificar código
echo ""
echo "✅ Verificando código Django..."
python manage.py check

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Código verificado sin errores${NC}"
else
    echo -e "${RED}❌ Error en verificación. Revisar código.${NC}"
    exit 1
fi

# 6. Recargar Gunicorn
echo ""
echo "🔄 Recargando Gunicorn (sin downtime)..."
sudo systemctl reload gunicorn

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Gunicorn recargado exitosamente${NC}"
else
    echo -e "${YELLOW}⚠️  Reload falló, intentando restart...${NC}"
    sudo systemctl restart gunicorn
fi

# 7. Verificar estado de servicios
echo ""
echo "🔍 Verificando estado de servicios..."
echo "Gunicorn:"
sudo systemctl is-active gunicorn
echo "Nginx:"
sudo systemctl is-active nginx

# 8. Ver últimos logs
echo ""
echo "📋 Últimos logs de Gunicorn:"
sudo tail -20 /var/log/gunicorn/error.log

# 9. Test básico
echo ""
echo "🧪 Realizando test básico..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/reportes/)

if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "302" ]; then
    echo -e "${GREEN}✅ Test exitoso: HTTP $RESPONSE${NC}"
else
    echo -e "${RED}❌ Test falló: HTTP $RESPONSE${NC}"
    echo "Revisar logs arriba para más detalles"
fi

# 10. Resumen
echo ""
echo "========================================"
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO${NC}"
echo "========================================"
echo ""
echo "📊 Siguiente paso: Verificar en el navegador:"
echo "   https://tu-dominio.com/reportes/"
echo ""
echo "🔍 Si hay problemas, ver logs en tiempo real:"
echo "   sudo tail -f /var/log/gunicorn/error.log"
echo ""
echo "📝 Commit desplegado:"
git log --oneline -n 1
echo ""

