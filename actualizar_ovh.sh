#!/bin/bash
#####################################################
# Script de Actualización Automática - FinanBot OVH
# Versión: 2.2.2
# Fecha: 31 de Mayo 2026
#####################################################

set -e  # Detener en caso de error

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
PROJECT_DIR="/var/www/gastos-familiares"
BACKUP_DIR="/backups/finanbot"
DB_NAME="finanbot"
DATE=$(date +%Y%m%d_%H%M%S)

# Función para imprimir con colores
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "========================================================"
    echo "$1"
    echo "========================================================"
    echo ""
}

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root o con sudo"
    exit 1
fi

print_header "🚀 ACTUALIZACIÓN DE FINANBOT EN OVH"

# PASO 1: Verificaciones preliminares
print_header "📋 PASO 1: VERIFICACIONES PRELIMINARES"

# Verificar que el directorio del proyecto existe
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "El directorio del proyecto no existe: $PROJECT_DIR"
    exit 1
fi
print_success "Directorio del proyecto encontrado"

# Verificar que es un repositorio git
cd "$PROJECT_DIR"
if [ ! -d ".git" ]; then
    print_error "No es un repositorio git: $PROJECT_DIR"
    exit 1
fi
print_success "Repositorio git verificado"

# Verificar conexión a Internet
if ! ping -c 1 github.com &> /dev/null; then
    print_error "No hay conexión a Internet"
    exit 1
fi
print_success "Conexión a Internet verificada"

# PASO 2: Crear backups
print_header "💾 PASO 2: CREANDO BACKUPS"

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"
print_success "Directorio de backups listo"

# Backup de base de datos
print_info "Creando backup de PostgreSQL..."
sudo -u postgres pg_dump "$DB_NAME" > "$BACKUP_DIR/backup_$DATE.sql"
gzip "$BACKUP_DIR/backup_$DATE.sql"
print_success "Backup de base de datos creado: backup_$DATE.sql.gz"

# Backup de archivos media
if [ -d "$PROJECT_DIR/media" ]; then
    print_info "Creando backup de archivos media..."
    tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" "$PROJECT_DIR/media/" 2>/dev/null || true
    print_success "Backup de media creado: media_$DATE.tar.gz"
fi

# Backup del .env
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$BACKUP_DIR/.env.backup_$DATE"
    print_success "Backup de .env creado"
fi

# Listar backups
print_info "Backups disponibles:"
ls -lh "$BACKUP_DIR" | tail -n 5

# PASO 3: Detener servicios
print_header "🛑 PASO 3: DETENIENDO SERVICIOS"

print_info "Deteniendo Gunicorn..."
systemctl stop gunicorn
print_success "Gunicorn detenido"

# PASO 4: Actualizar código
print_header "📥 PASO 4: ACTUALIZANDO CÓDIGO DESDE GITHUB"

cd "$PROJECT_DIR"

# Ver commit actual
CURRENT_COMMIT=$(git rev-parse --short HEAD)
print_info "Commit actual: $CURRENT_COMMIT"

# Guardar cambios locales si los hay
if ! git diff-index --quiet HEAD --; then
    print_warning "Hay cambios locales, guardándolos con stash..."
    git stash
fi

# Actualizar código
print_info "Descargando últimos cambios..."
git pull origin main

# Ver nuevo commit
NEW_COMMIT=$(git rev-parse --short HEAD)
print_success "Código actualizado a commit: $NEW_COMMIT"

# Mostrar cambios
print_info "Archivos modificados:"
git diff --stat $CURRENT_COMMIT $NEW_COMMIT | head -n 10

# PASO 5: Actualizar dependencias
print_header "🐍 PASO 5: ACTUALIZANDO DEPENDENCIAS PYTHON"

# Activar entorno virtual
source "$PROJECT_DIR/.venv/bin/activate"

# Actualizar pip
print_info "Actualizando pip..."
pip install --upgrade pip -q

# Instalar dependencias actualizadas
print_info "Instalando dependencias de requirements-production.txt..."
pip install --upgrade -r requirements-production.txt -q

print_success "Dependencias actualizadas"

# Verificar versiones críticas
print_info "Versiones instaladas:"
python -c "import django; print(f'  Django: {django.get_version()}')"
python -c "import PIL; print(f'  Pillow: {PIL.__version__}')"
python -c "import requests; print(f'  Requests: {requests.__version__}')"
python -c "import cryptography; print(f'  Cryptography: {cryptography.__version__}')"

# Verificar conflictos
print_info "Verificando conflictos de dependencias..."
if pip check > /dev/null 2>&1; then
    print_success "No hay conflictos de dependencias"
else
    print_warning "Hay conflictos de dependencias (revisar manualmente)"
fi

# PASO 6: Aplicar migraciones
print_header "🔄 PASO 6: APLICANDO MIGRACIONES"

# Verificar configuración
print_info "Verificando configuración de Django..."
python manage.py check --deploy

# Mostrar migraciones pendientes
print_info "Migraciones pendientes:"
python manage.py showmigrations | grep "\[ \]" || print_success "No hay migraciones pendientes"

# Aplicar migraciones
print_info "Aplicando migraciones..."
python manage.py migrate --noinput

print_success "Migraciones aplicadas correctamente"

# PASO 7: Colectar estáticos
print_header "📦 PASO 7: COLECTANDO ARCHIVOS ESTÁTICOS"

print_info "Colectando archivos estáticos..."
python manage.py collectstatic --noinput

# Ajustar permisos
print_info "Ajustando permisos..."
chown -R www-data:www-data "$PROJECT_DIR/staticfiles"
chmod -R 755 "$PROJECT_DIR/staticfiles"

print_success "Archivos estáticos actualizados"

# PASO 8: Reiniciar servicios
print_header "🔄 PASO 8: REINICIANDO SERVICIOS"

# Iniciar Gunicorn
print_info "Iniciando Gunicorn..."
systemctl start gunicorn
sleep 2

if systemctl is-active --quiet gunicorn; then
    print_success "Gunicorn iniciado correctamente"
else
    print_error "Error al iniciar Gunicorn"
    print_info "Ver logs con: sudo journalctl -u gunicorn -n 50"
    exit 1
fi

# Reiniciar Nginx
print_info "Reiniciando Nginx..."
systemctl restart nginx

if systemctl is-active --quiet nginx; then
    print_success "Nginx reiniciado correctamente"
else
    print_warning "Nginx puede tener problemas"
fi

# PASO 9: Verificaciones post-actualización
print_header "✅ PASO 9: VERIFICACIONES POST-ACTUALIZACIÓN"

# Verificar que el sitio responde
print_info "Verificando que el sitio responde..."
sleep 3

if curl -s -o /dev/null -w "%{http_code}" https://gastosweb.com | grep -q "200\|301\|302"; then
    print_success "Sitio respondiendo correctamente"
else
    print_warning "El sitio puede no estar respondiendo correctamente"
fi

# Verificar logs recientes
print_info "Últimas líneas de log de errores:"
if [ -f "$PROJECT_DIR/logs/errors.log" ]; then
    tail -n 5 "$PROJECT_DIR/logs/errors.log" | grep -v "^$" || print_success "No hay errores recientes"
else
    print_info "Archivo de log no encontrado"
fi

# RESUMEN FINAL
print_header "🎊 ACTUALIZACIÓN COMPLETADA"

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║    ✅  ACTUALIZACIÓN EXITOSA                         ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

print_info "Resumen de la actualización:"
echo "  • Commit anterior: $CURRENT_COMMIT"
echo "  • Commit nuevo: $NEW_COMMIT"
echo "  • Backup DB: backup_$DATE.sql.gz"
echo "  • Duración: $(($(date +%s) - $(date -d "$DATE" +%s 2>/dev/null || echo 0))) segundos"
echo ""

print_info "Verificaciones recomendadas:"
echo "  1. Visitar https://gastosweb.com"
echo "  2. Verificar login"
echo "  3. Revisar funcionalidad crítica"
echo "  4. Monitorear logs: sudo journalctl -u gunicorn -f"
echo ""

print_warning "IMPORTANTE: Monitorear el sitio durante las próximas horas"
echo ""

# Log de actualización
echo "$DATE - Actualización de $CURRENT_COMMIT a $NEW_COMMIT - EXITOSA" >> "$BACKUP_DIR/update_history.log"

print_success "Script de actualización completado"
echo ""

