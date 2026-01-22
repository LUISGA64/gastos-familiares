# 🔌 CONEXIÓN EXTERNA A POSTGRESQL - GUÍA COMPLETA

## ✅ SÍ, PUEDES CONECTARTE DESDE ADMINISTRADORES EXTERNOS

Puedes usar herramientas como:
- **DBeaver** (gratuito, recomendado)
- **pgAdmin** (oficial de PostgreSQL)
- **TablePlus** (Mac/Windows)
- **DataGrip** (JetBrains)
- **Azure Data Studio**
- **HeidiSQL**

---

## 🔒 CONFIGURACIÓN NECESARIA EN EL SERVIDOR

### PASO 1: Configurar PostgreSQL para aceptar conexiones remotas

Ejecuta estos comandos en tu servidor VPS:

```bash
#!/bin/bash
# ===== CONFIGURAR POSTGRESQL PARA CONEXIONES REMOTAS =====

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      CONFIGURACIÓN DE POSTGRESQL PARA ACCESO REMOTO            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "━━━ 1/5: Editando postgresql.conf..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Encontrar la versión de PostgreSQL instalada
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
PG_CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"

echo "PostgreSQL versión detectada: ${PG_VERSION}"
echo "Archivo de configuración: ${PG_CONF}"

# Hacer backup del archivo original
sudo cp ${PG_CONF} ${PG_CONF}.backup

# Configurar PostgreSQL para escuchar en todas las interfaces
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" ${PG_CONF}
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" ${PG_CONF}

echo "✅ postgresql.conf configurado para aceptar conexiones remotas"
echo ""

echo "━━━ 2/5: Editando pg_hba.conf..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"

# Hacer backup
sudo cp ${PG_HBA} ${PG_HBA}.backup

# Agregar regla para permitir conexiones con contraseña desde cualquier IP
echo "" | sudo tee -a ${PG_HBA}
echo "# Permitir conexiones remotas (agregado por script)" | sudo tee -a ${PG_HBA}
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a ${PG_HBA}

echo "✅ pg_hba.conf configurado"
echo ""

echo "━━━ 3/5: Configurando Firewall (UFW)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Permitir puerto PostgreSQL (5432)
sudo ufw allow 5432/tcp comment 'PostgreSQL'

echo "✅ Firewall configurado para permitir PostgreSQL (puerto 5432)"
echo ""

echo "━━━ 4/5: Reiniciando PostgreSQL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sudo systemctl restart postgresql

if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL reiniciado correctamente"
else
    echo "❌ Error al reiniciar PostgreSQL"
    sudo systemctl status postgresql
    exit 1
fi
echo ""

echo "━━━ 5/5: Verificando configuración..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar que PostgreSQL está escuchando en el puerto 5432
if sudo netstat -tuln | grep -q ":5432"; then
    echo "✅ PostgreSQL escuchando en puerto 5432"
else
    echo "⚠️  Verificar manualmente: sudo netstat -tuln | grep 5432"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ CONFIGURACIÓN COMPLETADA                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 DATOS DE CONEXIÓN:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Host:     167.114.2.88"
echo "Puerto:   5432"
echo "Database: gastos_familiares"
echo "Usuario:  gastos_user"
echo "Password: Gastos2026Familia"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 IMPORTANTE:"
echo "   - Cambia la contraseña por una más segura"
echo "   - Considera usar túnel SSH para mayor seguridad"
echo ""
```

---

## 📊 DATOS DE CONEXIÓN

### Configuración estándar:
```
Tipo:       PostgreSQL
Host:       167.114.2.88
Puerto:     5432
Database:   gastos_familiares
Usuario:    gastos_user
Contraseña: Gastos2026Familia
SSL:        Disabled (opcional: require)
```

---

## 🔒 OPCIÓN MÁS SEGURA: CONEXIÓN VÍA TÚNEL SSH

En lugar de exponer PostgreSQL a internet, puedes usar un túnel SSH:

### Configuración con Túnel SSH:
```
SSH Host:       167.114.2.88
SSH User:       ubuntu
SSH Port:       22
SSH Key/Pass:   Tu contraseña SSH

Database Host:  localhost (o 127.0.0.1)
Database Port:  5432
Database:       gastos_familiares
Usuario:        gastos_user
Contraseña:     Gastos2026Familia
```

**Ventajas del túnel SSH:**
- ✅ No expones PostgreSQL a internet
- ✅ Más seguro (usa encriptación SSH)
- ✅ No necesitas abrir puerto 5432 en firewall

---

## 🖥️ CONFIGURACIÓN POR HERRAMIENTA

### DBeaver (Recomendado - Gratuito)

**Descarga:** https://dbeaver.io/download/

**Configuración:**
1. Nuevo Connection → PostgreSQL
2. Datos:
   - Host: `167.114.2.88`
   - Port: `5432`
   - Database: `gastos_familiares`
   - Username: `gastos_user`
   - Password: `Gastos2026Familia`
3. Test Connection → Finish

**Con túnel SSH:**
1. Nuevo Connection → PostgreSQL
2. Pestaña "Main":
   - Host: `localhost`
   - Port: `5432`
   - Database: `gastos_familiares`
   - Username: `gastos_user`
   - Password: `Gastos2026Familia`
3. Pestaña "SSH":
   - ✅ Use SSH Tunnel
   - Host: `167.114.2.88`
   - Port: `22`
   - User: `ubuntu`
   - Authentication: Password o Private key
4. Test Connection → Finish

---

### pgAdmin 4

**Descarga:** https://www.pgadmin.org/download/

**Configuración:**
1. Add New Server
2. General Tab:
   - Name: `Gastos Familiares OVH`
3. Connection Tab:
   - Host: `167.114.2.88`
   - Port: `5432`
   - Maintenance database: `gastos_familiares`
   - Username: `gastos_user`
   - Password: `Gastos2026Familia`
   - ✅ Save password
4. Save

**Con túnel SSH:**
1. Add New Server
2. Connection Tab:
   - Host: `localhost`
3. SSH Tunnel Tab:
   - ✅ Use SSH tunneling
   - Tunnel host: `167.114.2.88`
   - Tunnel port: `22`
   - Username: `ubuntu`

---

### TablePlus

**Descarga:** https://tableplus.com/

**Configuración:**
1. Create → PostgreSQL
2. Datos:
   - Name: `Gastos Familiares`
   - Host: `167.114.2.88`
   - Port: `5432`
   - User: `gastos_user`
   - Password: `Gastos2026Familia`
   - Database: `gastos_familiares`
3. Test → Connect

**Con túnel SSH:**
1. Over SSH → ✅
2. SSH Settings:
   - Server: `167.114.2.88`
   - Port: `22`
   - User: `ubuntu`
3. Database Settings:
   - Host: `127.0.0.1`
   - Port: `5432`

---

### DataGrip (JetBrains)

**Descarga:** https://www.jetbrains.com/datagrip/

**Configuración:**
1. New → Data Source → PostgreSQL
2. General:
   - Host: `167.114.2.88`
   - Port: `5432`
   - Database: `gastos_familiares`
   - User: `gastos_user`
   - Password: `Gastos2026Familia`
3. SSH/SSL:
   - ✅ Use SSH tunnel
   - Host: `167.114.2.88`
   - User: `ubuntu`
4. Test Connection → OK

---

## 🔒 MEJORAR LA SEGURIDAD

### 1. Cambiar la contraseña de PostgreSQL

```bash
# En el servidor VPS
sudo -u postgres psql

# Dentro de PostgreSQL
ALTER USER gastos_user WITH PASSWORD 'TuNuevaPasswordSuperSegura!2026';
\q

# Actualizar .env
nano /var/www/gastos-familiares/.env
# Cambiar la contraseña en DATABASE_URL

# Reiniciar Gunicorn
sudo systemctl restart gunicorn
```

### 2. Restringir acceso solo a tu IP (Recomendado)

```bash
# Editar pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Cambiar la línea:
# host    all             all             0.0.0.0/0               md5

# Por (reemplaza TU_IP con tu IP pública):
host    all             all             TU_IP/32                md5

# Guardar y reiniciar
sudo systemctl restart postgresql
```

### 3. Usar solo túnel SSH (Más seguro)

```bash
# Remover la regla del firewall para PostgreSQL
sudo ufw delete allow 5432/tcp

# No exponer PostgreSQL a internet
# Usar solo túnel SSH para conectarse
```

---

## 🧪 PROBAR LA CONEXIÓN

### Desde tu computadora local (Windows PowerShell):

```powershell
# Instalar cliente PostgreSQL (si no lo tienes)
# O usar directamente desde DBeaver

# Probar conexión con psql (si lo tienes instalado):
psql -h 167.114.2.88 -p 5432 -U gastos_user -d gastos_familiares
# Ingresar contraseña: Gastos2026Familia
```

### Desde Linux/Mac:

```bash
psql -h 167.114.2.88 -p 5432 -U gastos_user -d gastos_familiares
```

Si te conectas exitosamente, verás el prompt de PostgreSQL:
```
gastos_familiares=>
```

---

## ⚠️ TROUBLESHOOTING

### Error: "connection refused"
**Causa:** PostgreSQL no está escuchando en 0.0.0.0 o firewall bloqueando

**Solución:**
```bash
# Verificar que PostgreSQL escucha en todas las interfaces
sudo netstat -tuln | grep 5432

# Verificar firewall
sudo ufw status | grep 5432

# Verificar logs de PostgreSQL
sudo tail -50 /var/log/postgresql/postgresql-*-main.log
```

### Error: "password authentication failed"
**Causa:** Contraseña incorrecta o usuario no existe

**Solución:**
```bash
# Verificar que el usuario existe
sudo -u postgres psql -c "\du"

# Reiniciar contraseña
sudo -u postgres psql
ALTER USER gastos_user WITH PASSWORD 'Gastos2026Familia';
\q
```

### Error: "no pg_hba.conf entry"
**Causa:** pg_hba.conf no permite conexión desde tu IP

**Solución:**
```bash
# Verificar pg_hba.conf
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep -v "^#" | grep -v "^$"

# Debería mostrar una línea como:
# host    all             all             0.0.0.0/0               md5
```

---

## 📋 RESUMEN

### Para conexión directa (menos segura):
1. ✅ Ejecuta el script de configuración en el servidor
2. ✅ Usa los datos de conexión proporcionados
3. ✅ Abre DBeaver o tu herramienta preferida
4. ✅ Crea nueva conexión PostgreSQL
5. ✅ Conecta y administra tu base de datos

### Para conexión con túnel SSH (más segura) - RECOMENDADO:
1. ✅ NO ejecutes el script (no expongas PostgreSQL)
2. ✅ Usa configuración de túnel SSH en tu herramienta
3. ✅ Conecta a través del túnel encriptado
4. ✅ Mayor seguridad

---

## 🎯 RECOMENDACIÓN

**Usa TÚNEL SSH** en lugar de exponer PostgreSQL directamente. Es mucho más seguro y no requiere abrir el puerto 5432 a internet.

Todas las herramientas modernas (DBeaver, TablePlus, DataGrip, pgAdmin) soportan túnel SSH de forma nativa.

---

**¿Prefieres conexión directa o túnel SSH? Te ayudo a configurar cualquiera de las dos opciones.**
