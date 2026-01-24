#!/bin/bash
# Script de Despliegue Automatizado para gastosweb.com
# Ejecutar en el servidor de producción

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   DESPLIEGUE AUTOMATIZADO${NC}"
echo -e "${GREEN}   gastosweb.com - Sistema de Privacidad${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. Verificar que estamos en el directorio correcto
echo -e "${YELLOW}[1/9] Verificando directorio...${NC}"
if [ ! -f "manage.py" ]; then
    echo -e "${RED}ERROR: No se encontró manage.py. ¿Estás en el directorio del proyecto?${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Directorio correcto${NC}"
echo ""

# 2. Hacer backup de la base de datos
echo -e "${YELLOW}[2/9] Creando backup de base de datos...${NC}"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump $DATABASE_NAME > $BACKUP_FILE
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backup creado: $BACKUP_FILE${NC}"
else
    echo -e "${RED}ERROR: No se pudo crear backup${NC}"
    exit 1
fi
echo ""

# 3. Actualizar código desde GitHub
echo -e "${YELLOW}[3/9] Actualizando código desde GitHub...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudo actualizar el código${NC}"
    echo -e "${YELLOW}Restaurando backup...${NC}"
    psql $DATABASE_NAME < $BACKUP_FILE
    exit 1
fi
echo -e "${GREEN}✓ Código actualizado${NC}"
echo ""

# 4. Activar entorno virtual
echo -e "${YELLOW}[4/9] Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# 5. Instalar/actualizar dependencias
echo -e "${YELLOW}[5/9] Instalando dependencias...${NC}"
pip install -r requirements-production.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudieron instalar las dependencias${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# 6. Aplicar migraciones
echo -e "${YELLOW}[6/9] Aplicando migraciones...${NC}"
python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Falló la migración${NC}"
    echo -e "${YELLOW}Restaurando backup...${NC}"
    python manage.py migrate gastos 0013  # Revertir a migración anterior
    psql $DATABASE_NAME < $BACKUP_FILE
    exit 1
fi
echo -e "${GREEN}✓ Migraciones aplicadas${NC}"
echo ""

# 7. Recolectar archivos estáticos
echo -e "${YELLOW}[7/9] Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Archivos estáticos actualizados${NC}"
echo ""

# 8. Verificar que no hay errores
echo -e "${YELLOW}[8/9] Verificando configuración...${NC}"
python manage.py check --deploy
if [ $? -ne 0 ]; then
    echo -e "${RED}ADVERTENCIA: Hay problemas de configuración${NC}"
    read -p "¿Continuar de todos modos? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi
echo -e "${GREEN}✓ Verificación completada${NC}"
echo ""

# 9. Reiniciar servidor
echo -e "${YELLOW}[9/9] Reiniciando servidor...${NC}"
if command -v systemctl &> /dev/null; then
    sudo systemctl restart gunicorn
    echo -e "${GREEN}✓ Gunicorn reiniciado${NC}"
elif command -v supervisorctl &> /dev/null; then
    sudo supervisorctl restart djangoproject
    echo -e "${GREEN}✓ Supervisor reiniciado${NC}"
else
    echo -e "${YELLOW}⚠ Reinicia manualmente el servidor${NC}"
fi
echo ""

# Resumen
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✓ DESPLIEGUE COMPLETADO${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Backup guardado en: ${GREEN}$BACKUP_FILE${NC}"
echo -e "Sitio: ${GREEN}https://gastosweb.com${NC}"
echo ""
echo -e "${YELLOW}Verificaciones recomendadas:${NC}"
echo "1. Acceder a https://gastosweb.com/"
echo "2. Verificar login funciona"
echo "3. Probar toggle de privacidad en dashboard"
echo "4. Verificar formato de moneda: \$1.000.000"
echo ""
echo -e "${YELLOW}Para ver logs:${NC}"
echo "tail -f /var/log/gunicorn/error.log"
echo "tail -f /var/log/nginx/error.log"
echo ""
echo -e "${YELLOW}Para revertir si hay problemas:${NC}"
echo "python manage.py migrate gastos 0013"
echo "psql \$DATABASE_NAME < $BACKUP_FILE"
echo "sudo systemctl restart gunicorn"
