#!/bin/bash
# ===== CONFIGURAR POSTGRESQL PARA CONEXIONES REMOTAS =====
# Script para permitir acceso remoto a PostgreSQL

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      CONFIGURACIÓN DE POSTGRESQL PARA ACCESO REMOTO            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "⚠️  IMPORTANTE: Este script expondrá PostgreSQL a internet."
echo "   Para mayor seguridad, considera usar túnel SSH en su lugar."
echo ""
read -p "¿Continuar con la configuración? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Configuración cancelada."
    exit 0
fi

echo ""
echo "━━━ 1/5: Detectando versión de PostgreSQL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
PG_CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"
PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"

echo "PostgreSQL versión: ${PG_VERSION}"
echo "Archivo postgresql.conf: ${PG_CONF}"
echo "Archivo pg_hba.conf: ${PG_HBA}"
echo ""

echo "━━━ 2/5: Configurando postgresql.conf..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Hacer backup
sudo cp ${PG_CONF} ${PG_CONF}.backup.$(date +%Y%m%d_%H%M%S)

# Configurar PostgreSQL para escuchar en todas las interfaces
if grep -q "^listen_addresses" ${PG_CONF}; then
    sudo sed -i "s/^listen_addresses.*/listen_addresses = '*'/" ${PG_CONF}
else
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" ${PG_CONF}
fi

echo "✅ postgresql.conf configurado para escuchar en todas las interfaces"
echo ""

echo "━━━ 3/5: Configurando pg_hba.conf..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Hacer backup
sudo cp ${PG_HBA} ${PG_HBA}.backup.$(date +%Y%m%d_%H%M%S)

# Verificar si ya existe la regla
if grep -q "# Permitir conexiones remotas" ${PG_HBA}; then
    echo "⚠️  Regla de acceso remoto ya existe, omitiendo..."
else
    # Agregar regla para permitir conexiones con contraseña
    echo "" | sudo tee -a ${PG_HBA} > /dev/null
    echo "# Permitir conexiones remotas (agregado $(date +%Y-%m-%d))" | sudo tee -a ${PG_HBA} > /dev/null
    echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a ${PG_HBA} > /dev/null
    echo "✅ Regla de acceso remoto agregada a pg_hba.conf"
fi
echo ""

echo "━━━ 4/5: Configurando Firewall..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar si la regla ya existe
if sudo ufw status | grep -q "5432"; then
    echo "⚠️  Regla de firewall para PostgreSQL ya existe"
else
    sudo ufw allow 5432/tcp comment 'PostgreSQL remote access'
    echo "✅ Puerto 5432 abierto en firewall"
fi
echo ""

echo "━━━ 5/5: Reiniciando PostgreSQL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo systemctl restart postgresql
sleep 2

if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL reiniciado correctamente"
else
    echo "❌ Error al reiniciar PostgreSQL"
    sudo systemctl status postgresql --no-pager
    exit 1
fi
echo ""

echo "━━━ Verificación final..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar que PostgreSQL está escuchando en 0.0.0.0
if sudo ss -tuln | grep -q "0.0.0.0:5432"; then
    echo "✅ PostgreSQL escuchando en 0.0.0.0:5432 (todas las interfaces)"
else
    echo "⚠️  PostgreSQL no está escuchando en todas las interfaces"
    echo "   Verifica manualmente: sudo ss -tuln | grep 5432"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ CONFIGURACIÓN COMPLETADA                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 DATOS DE CONEXIÓN REMOTA:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Tipo:       PostgreSQL"
echo "Host:       $(hostname -I | awk '{print $1}')"
echo "Puerto:     5432"
echo "Database:   gastos_familiares"
echo "Usuario:    gastos_user"
echo "Contraseña: Gastos2026Familia"
echo "SSL:        Disable (o prefer)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 RECOMENDACIONES DE SEGURIDAD:"
echo ""
echo "1. Cambia la contraseña de PostgreSQL:"
echo "   sudo -u postgres psql"
echo "   ALTER USER gastos_user WITH PASSWORD 'NuevaPasswordSegura';"
echo ""
echo "2. Restringe el acceso solo a tu IP:"
echo "   sudo nano ${PG_HBA}"
echo "   Cambia 0.0.0.0/0 por TU_IP/32"
echo ""
echo "3. O mejor aún, usa túnel SSH y cierra este puerto:"
echo "   sudo ufw delete allow 5432/tcp"
echo ""
echo "📖 Ver guía completa: CONEXION_POSTGRESQL_REMOTA.md"
echo ""
