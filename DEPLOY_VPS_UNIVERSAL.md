# 🖥️ DEPLOY EN SERVIDOR VPS - GUÍA UNIVERSAL

## ✅ ¿Qué es un VPS?
Un **VPS (Virtual Private Server)** es un servidor virtual donde tienes control total del sistema operativo y puedes instalar lo que necesites. Tu proyecto Django está **100% listo** para deploy en cualquier VPS.

---

## 🌐 OPCIONES DE PROVEEDORES VPS

### Recomendados (más populares)

| Proveedor | Precio Mensual | RAM/CPU | Región | Facilidad |
|-----------|---------------|---------|--------|-----------|
| **Digital Ocean** | $6-24 USD | 1-4GB / 1-2 vCPUs | Global | ⭐⭐⭐⭐⭐ |
| **Vultr** | $6-24 USD | 1-4GB / 1-2 vCPUs | Global | ⭐⭐⭐⭐⭐ |
| **Linode (Akamai)** | $5-24 USD | 1-4GB / 1-2 vCPUs | Global | ⭐⭐⭐⭐⭐ |
| **AWS Lightsail** | $5-20 USD | 1-4GB / 1-2 vCPUs | Global | ⭐⭐⭐⭐ |
| **Contabo** | €5-15 EUR | 4-8GB / 4-6 vCPUs | Europa | ⭐⭐⭐⭐ |
| **Hetzner** | €4-20 EUR | 2-8GB / 2-4 vCPUs | Europa | ⭐⭐⭐⭐⭐ |
| **OVH** | €4-15 EUR | 2-8GB / 2-4 vCPUs | Europa/USA | ⭐⭐⭐⭐ |

### Opciones Latinoamérica

| Proveedor | Precio Mensual | Región | Notas |
|-----------|---------------|--------|-------|
| **DigitalOcean** | $6-24 USD | São Paulo, Brasil | ⭐ Mejor para LATAM |
| **AWS EC2** | Variable | São Paulo | Pago por uso |
| **Azure** | Variable | Brasil | Pago por uso |
| **Hostinger VPS** | $5-30 USD | Brasil | Soporte español |
| **Hostgator VPS** | $20-80 USD | USA/Brasil | Soporte español |

---

## 🚀 PASOS UNIVERSALES PARA CUALQUIER VPS

### 📋 Requisitos Mínimos Recomendados
- **RAM:** 2GB (mínimo 1GB)
- **CPU:** 1 vCPU (2 recomendado)
- **Disco:** 25GB SSD
- **SO:** Ubuntu 22.04 LTS o Ubuntu 20.04 LTS
- **Ancho de banda:** 1TB/mes

### 1️⃣ CREAR VPS Y CONECTAR

#### OVHcloud (Recomendado) ⭐
```powershell
# 1. Ir a https://www.ovhcloud.com/es/vps/
# 2. Pedir > VPS (Starter, Value o Essential)
# 3. Seleccionar Ubuntu 22.04 LTS
# 4. Seleccionar datacenter (Europa, América, Asia)
# 5. Completar pedido
# 6. Recibir credenciales por email
# 7. Obtener IP pública
```

#### Digital Ocean / Vultr / Linode
```powershell
# 1. Crear cuenta en el proveedor
# 2. Create > Droplet/Instance
# 3. Seleccionar Ubuntu 22.04 LTS
# 4. Seleccionar plan (2GB RAM recomendado)
# 5. Crear SSH key o usar password
# 6. Obtener IP pública
```

#### AWS Lightsail
```powershell
# 1. Ir a aws.amazon.com/lightsail
# 2. Create instance
# 3. Linux/Unix > OS Only > Ubuntu 22.04
# 4. Seleccionar plan $10-20/mes
# 5. Descargar SSH key
# 6. Obtener IP pública
```

#### Conectar por SSH (todos los proveedores)
```powershell
# Desde PowerShell o terminal
ssh root@TU_IP_AQUI

# O si usas SSH key:
ssh -i ruta/a/tu/clave.pem root@TU_IP_AQUI
```

---

### 2️⃣ INSTALACIÓN EN EL SERVIDOR (Universal)

Una vez conectado al VPS, ejecuta estos comandos **sin importar el proveedor**:

#### Actualizar sistema
```bash
apt update && apt upgrade -y
```

#### Instalar dependencias
```bash
# Python y herramientas (usa la versión disponible en tu sistema)
apt install -y python3 python3-venv python3-pip

# Base de datos PostgreSQL
apt install -y postgresql postgresql-contrib

# Servidor web Nginx
apt install -y nginx

# Control de versiones
apt install -y git

# SSL/HTTPS (opcional pero recomendado)
apt install -y certbot python3-certbot-nginx

# Herramientas útiles
apt install -y curl wget htop ufw

# Verificar versión de Python instalada
python3 --version
# Debería mostrar Python 3.10 o superior (tu servidor tiene 3.13.3 - ¡Perfecto!)
```

---

### 3️⃣ CONFIGURAR BASE DE DATOS

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Ejecutar dentro de PostgreSQL:
CREATE DATABASE gastos_familiares;
CREATE USER gastos_user WITH PASSWORD 'TuPasswordSuperSeguro123!';
ALTER ROLE gastos_user SET client_encoding TO 'utf8';
ALTER ROLE gastos_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gastos_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gastos_familiares TO gastos_user;
\q
```

---

### 4️⃣ CLONAR PROYECTO

```bash
# Crear directorio
mkdir -p /var/www/gastos-familiares
cd /var/www/gastos-familiares

# Clonar desde GitHub
git clone https://github.com/TU_USUARIO/gastos-familiares.git .

# Crear entorno virtual (usa la versión de Python disponible)
python3 -m venv venv
source venv/bin/activate

# Verificar que el entorno virtual está activo (debería aparecer (venv) en el prompt)
# Verificar versión de Python en el entorno virtual
python --version

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

### 5️⃣ CONFIGURAR VARIABLES DE ENTORNO

```bash
# Crear archivo .env
nano /var/www/gastos-familiares/.env
```

Contenido:
```env
SECRET_KEY=p5p-*+zovjzo@hnv(7lrh45v-l9*&&6i%th#mow#a19s(e+i0j
DEBUG=False
ALLOWED_HOSTS=TU_IP_AQUI,tu-dominio.com,www.tu-dominio.com
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
DATABASE_URL=postgresql://gastos_user:TuPasswordSuperSeguro123!@localhost:5432/gastos_familiares
AI_PROVIDER=groq
GROQ_API_KEY=tu-groq-api-key-aqui
```

Guardar: `Ctrl+X`, luego `Y`, luego `Enter`

---

### 6️⃣ PREPARAR DJANGO

```bash
# Activar entorno virtual si no está activo
source /var/www/gastos-familiares/venv/bin/activate

# Aplicar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py createsuperuser
```

---

### 7️⃣ CONFIGURAR GUNICORN (Servidor WSGI)

```bash
# Crear servicio systemd
nano /etc/systemd/system/gunicorn.service
```

Contenido:
```ini
[Unit]
Description=Gunicorn daemon for Gastos Familiares
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/gastos-familiares
Environment="PATH=/var/www/gastos-familiares/venv/bin"
EnvironmentFile=/var/www/gastos-familiares/.env
ExecStart=/var/www/gastos-familiares/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/gastos-familiares/gunicorn.sock \
          DjangoProject.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar y habilitar Gunicorn
systemctl daemon-reload
systemctl start gunicorn
systemctl enable gunicorn
systemctl status gunicorn
```

---

### 8️⃣ CONFIGURAR NGINX (Servidor Web)

```bash
# Crear configuración
nano /etc/nginx/sites-available/gastos-familiares
```

Contenido:
```nginx
server {
    listen 80;
    server_name TU_IP_AQUI tu-dominio.com www.tu-dominio.com;

    client_max_body_size 20M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/gastos-familiares/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/gastos-familiares/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/gastos-familiares/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

```bash
# Habilitar sitio
ln -s /etc/nginx/sites-available/gastos-familiares /etc/nginx/sites-enabled/

# Verificar configuración
nginx -t

# Reiniciar Nginx
systemctl restart nginx
```

---

### 9️⃣ CONFIGURAR FIREWALL

```bash
# Permitir SSH, HTTP y HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'

# Habilitar firewall
ufw --force enable

# Ver estado
ufw status
```

---

### 🔟 CONFIGURAR SSL/HTTPS (OPCIONAL - Requiere Dominio)

Si tienes un dominio apuntando a tu VPS:

```bash
# Obtener certificado SSL gratis de Let's Encrypt
certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática (Certbot lo hace automáticamente)
systemctl status certbot.timer
```

Si NO tienes dominio:
- Puedes usar la IP: `http://TU_IP_AQUI`
- O usar un servicio gratuito como: `freedns.afraid.org`, `noip.com`, `duckdns.org`

---

## ✅ VERIFICACIÓN FINAL

Visita tu VPS:
- **Sin SSL:** `http://TU_IP_AQUI`
- **Con dominio y SSL:** `https://tu-dominio.com`

Deberías ver tu aplicación funcionando! 🎉

---

## 🔧 COMANDOS ÚTILES DE MANTENIMIENTO

### Ver logs de errores
```bash
# Logs de Gunicorn
journalctl -u gunicorn -f

# Logs de Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Logs de Django
tail -f /var/www/gastos-familiares/logs/django.log
```

### Reiniciar servicios
```bash
# Reiniciar Gunicorn
systemctl restart gunicorn

# Reiniciar Nginx
systemctl restart nginx

# Reiniciar PostgreSQL
systemctl restart postgresql
```

### Actualizar código desde GitHub
```bash
cd /var/www/gastos-familiares
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart gunicorn
```

### Backup de base de datos
```bash
# Crear backup
sudo -u postgres pg_dump gastos_familiares > /root/backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
sudo -u postgres psql gastos_familiares < /root/backup_20260121_120000.sql
```

### Monitoreo del servidor
```bash
# Uso de recursos
htop

# Espacio en disco
df -h

# Memoria
free -h

# Procesos
ps aux | grep gunicorn
```

---

## 🆘 PROBLEMAS COMUNES Y SOLUCIONES

### Error 502 Bad Gateway
**Causa:** Gunicorn no está corriendo o hay error en el socket

**Solución:**
```bash
systemctl status gunicorn
journalctl -u gunicorn -n 50
systemctl restart gunicorn
```

### Static files no cargan (CSS/JS)
**Causa:** Permisos o ruta incorrecta

**Solución:**
```bash
chmod -R 755 /var/www/gastos-familiares/staticfiles/
chown -R root:www-data /var/www/gastos-familiares/
python manage.py collectstatic --noinput
systemctl restart nginx
```

### Error de base de datos
**Causa:** Credenciales incorrectas o PostgreSQL no corriendo

**Solución:**
```bash
systemctl status postgresql
sudo -u postgres psql -d gastos_familiares -c "SELECT 1;"
# Verificar .env con las credenciales correctas
```

### Puerto 80 ocupado
**Causa:** Otro servicio usando el puerto

**Solución:**
```bash
# Ver qué usa el puerto 80
lsof -i :80
# Detener Apache si está instalado
systemctl stop apache2
systemctl disable apache2
```

### Memoria insuficiente
**Causa:** VPS con poca RAM

**Solución:**
```bash
# Crear swap (memoria virtual)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 💰 COMPARATIVA DE COSTOS (Estimado)

### Para una app pequeña-mediana (100-1000 usuarios)

| Proveedor | Plan Recomendado | Costo Mensual | Tráfico Incluido |
|-----------|------------------|---------------|------------------|
| **Digital Ocean** | 2GB RAM / 1 vCPU | $12 USD | 2TB |
| **Vultr** | 2GB RAM / 1 vCPU | $12 USD | 2TB |
| **Linode** | 2GB RAM / 1 vCPU | $12 USD | 2TB |
| **AWS Lightsail** | 2GB RAM / 1 vCPU | $10 USD | 3TB |
| **Hetzner** | 2GB RAM / 2 vCPU | €4.5 EUR (~$5) | 20TB |
| **Contabo** | 4GB RAM / 4 vCPU | €5 EUR (~$5.5) | 32TB |

**Recomendación:** Hetzner o Contabo ofrecen mejor relación precio/rendimiento para Europa, Digital Ocean/Vultr para LATAM.

---

## 🌟 VENTAJAS DE USAR VPS vs PaaS (Heroku/Railway)

### ✅ Ventajas VPS
- ✅ **Costo:** Mucho más económico a largo plazo
- ✅ **Control total:** Puedes instalar lo que quieras
- ✅ **Rendimiento:** Recursos dedicados
- ✅ **Sin límites:** No hay restricciones de horas/requests
- ✅ **Escalabilidad:** Puedes upgradear cuando quieras
- ✅ **Aprendizaje:** Conoces la infraestructura real

### ❌ Desventajas VPS
- ❌ Requiere conocimientos de Linux
- ❌ Más tiempo de configuración inicial
- ❌ Tú eres responsable de seguridad y mantenimiento
- ❌ No hay deploy automático desde Git (pero se puede configurar)

---

## 📚 RECURSOS ADICIONALES

### Tutoriales y Documentación
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **Nginx Docs:** https://nginx.org/en/docs/
- **Gunicorn Docs:** https://docs.gunicorn.org/
- **PostgreSQL:** https://www.postgresql.org/docs/

### Videos Recomendados
- Buscar en YouTube: "Django VPS deployment Ubuntu"
- Buscar en YouTube: "Nginx Gunicorn Django production"

### Comunidades
- Reddit: r/django, r/webdev
- Stack Overflow
- Django Discord

---

## 🎯 CHECKLIST FINAL

Antes de considerar tu deploy completo:

- [ ] VPS creado y SSH funciona
- [ ] Dependencias instaladas (Python, PostgreSQL, Nginx)
- [ ] Base de datos creada y configurada
- [ ] Proyecto clonado desde GitHub
- [ ] Variables de entorno configuradas (.env)
- [ ] Migraciones aplicadas
- [ ] Archivos estáticos recolectados
- [ ] Superusuario creado
- [ ] Gunicorn corriendo como servicio
- [ ] Nginx configurado y corriendo
- [ ] Firewall habilitado
- [ ] Aplicación accesible desde navegador
- [ ] Login funciona correctamente
- [ ] CSS/JS cargan correctamente
- [ ] SSL configurado (si tienes dominio)
- [ ] Backup de base de datos configurado

---

## 🚀 CONCLUSIÓN

**¡Tu proyecto Django está 100% listo para cualquier VPS!**

Los pasos son prácticamente idénticos sin importar el proveedor que elijas. La diferencia principal es solo cómo crear el servidor inicial, pero una vez que tienes acceso SSH, todo es igual.

**Tiempo estimado de deploy:** 30-45 minutos
**Nivel de dificultad:** Medio (requiere conocimientos básicos de Linux)

---

**¿Dudas? Consulta:**
- `DEPLOY_RAPIDO.md` - Guía específica para Digital Ocean
- Este archivo - Guía universal para cualquier VPS
- Documentación oficial de Django

**¡Éxito con tu deploy! 🎉**
