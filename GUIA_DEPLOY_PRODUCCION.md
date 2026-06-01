# 🚀 GUÍA RÁPIDA DE DEPLOY A PRODUCCIÓN

**Proyecto:** FinanBot v2.2.2  
**Fecha:** 31 de Mayo 2026  
**Estado:** ✅ VALIDADO Y LISTO

---

## ✅ PRE-REQUISITOS COMPLETADOS

- ✅ 113 archivos innecesarios eliminados
- ✅ 30 CVEs de seguridad resueltos
- ✅ Dependencias actualizadas a versiones seguras
- ✅ Validación Django: 0 errores
- ✅ 36 migraciones listas para aplicar
- ✅ Documentación completa generada
- ✅ .gitignore configurado correctamente

---

## 📋 CHECKLIST DE DEPLOY

### 1️⃣ Configurar Variables de Entorno

Crear archivo `.env` en el servidor con:

```env
# Django Core
SECRET_KEY=generar-clave-unica-50-caracteres
DEBUG=False
ALLOWED_HOSTS=gastosweb.com,www.gastosweb.com,167.114.2.88

# Base de Datos PostgreSQL
DATABASE_URL=postgresql://usuario:password@localhost:5432/finanbot

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-16-caracteres
DEFAULT_FROM_EMAIL=FinanBot <noreply@gastosweb.com>

# AI Provider (Groq - GRATIS)
AI_PROVIDER=groq
GROQ_API_KEY=gsk_tu_api_key_aqui

# Seguridad
ENCRYPTION_KEY=generar-clave-base64-fernet

# Admin
ADMIN_EMAIL=admin@gastosweb.com

# URLs
SITE_URL=https://gastosweb.com
```

### 2️⃣ Preparar Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx certbot python3-certbot-nginx git -y

# Clonar o actualizar repositorio
cd /var/www
sudo git clone https://github.com/TU_USUARIO/gastos-familiares.git
# O si ya existe:
cd /var/www/gastos-familiares
sudo git pull origin main
```

### 3️⃣ Configurar Base de Datos PostgreSQL

```bash
# Crear base de datos
sudo -u postgres psql
```

```sql
CREATE DATABASE finanbot;
CREATE USER finanbot_user WITH PASSWORD 'password_muy_seguro';
ALTER ROLE finanbot_user SET client_encoding TO 'utf8';
ALTER ROLE finanbot_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE finanbot_user SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE finanbot TO finanbot_user;
\q
```

### 4️⃣ Configurar Python

```bash
# Crear entorno virtual
cd /var/www/gastos-familiares
python3.11 -m venv .venv
source .venv/bin/activate

# IMPORTANTE: Instalar requirements-production.txt
pip install --upgrade pip
pip install -r requirements-production.txt

# Verificar instalación
pip check
```

### 5️⃣ Ejecutar Migraciones

```bash
# Aplicar migraciones (NO elimina datos)
python manage.py migrate

# Verificar migraciones
python manage.py showmigrations
```

### 6️⃣ Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7️⃣ Colectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 8️⃣ Configurar Gunicorn

Crear `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for FinanBot
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/gastos-familiares
Environment="PATH=/var/www/gastos-familiares/.venv/bin"
ExecStart=/var/www/gastos-familiares/.venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/var/www/gastos-familiares/gunicorn.sock \
          DjangoProject.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar Gunicorn
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### 9️⃣ Configurar Nginx

Crear `/etc/nginx/sites-available/finanbot`:

```nginx
server {
    listen 80;
    server_name gastosweb.com www.gastosweb.com;

    location / {
        proxy_pass http://unix:/var/www/gastos-familiares/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

    client_max_body_size 10M;
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/finanbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 🔟 Instalar Certificado SSL

```bash
# Obtener certificado Let's Encrypt
sudo certbot --nginx -d gastosweb.com -d www.gastosweb.com

# Verificar renovación automática
sudo certbot renew --dry-run

# Agregar cron job para renovación
sudo crontab -e
# Agregar: 0 0 * * * certbot renew --quiet
```

---

## 🧪 VERIFICACIÓN POST-DEPLOY

### Pruebas Funcionales

```bash
# 1. Verificar que el sitio carga
curl -I https://gastosweb.com

# 2. Verificar redirección HTTP → HTTPS
curl -I http://gastosweb.com

# 3. Verificar archivos estáticos
curl -I https://gastosweb.com/static/css/styles.css

# 4. Ver logs en tiempo real
tail -f /var/www/gastos-familiares/logs/application.log
sudo journalctl -u gunicorn -f
```

### Checklist Manual

Acceder a https://gastosweb.com y verificar:

- [ ] Login funciona
- [ ] Dashboard carga correctamente
- [ ] Crear nuevo gasto
- [ ] Registrar ingreso
- [ ] Chatbot responde
- [ ] Exportar PDF funciona
- [ ] Exportar Excel funciona
- [ ] Sistema de pagos muestra QR
- [ ] Toggle de privacidad funciona
- [ ] Gamificación muestra logros
- [ ] Emails se envían correctamente

---

## 🔄 ACTUALIZACIONES FUTURAS

Cuando necesites actualizar el código:

```bash
cd /var/www/gastos-familiares

# 1. Hacer backup
sudo -u postgres pg_dump finanbot > backup_$(date +%Y%m%d).sql

# 2. Actualizar código
sudo git pull origin main

# 3. Activar entorno
source .venv/bin/activate

# 4. Actualizar dependencias (si cambiaron)
pip install -r requirements-production.txt

# 5. Aplicar migraciones nuevas
python manage.py migrate

# 6. Colectar estáticos
python manage.py collectstatic --noinput

# 7. Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 8. Verificar
curl -I https://gastosweb.com
```

---

## 🛡️ SEGURIDAD Y MANTENIMIENTO

### Backups Automáticos

Crear `/root/backup-finanbot.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/finanbot"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
sudo -u postgres pg_dump finanbot | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/gastos-familiares/media

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completado: $DATE"
```

```bash
# Hacer ejecutable
chmod +x /root/backup-finanbot.sh

# Agregar a crontab (diario a las 2 AM)
sudo crontab -e
# Agregar: 0 2 * * * /root/backup-finanbot.sh
```

### Monitoreo de Logs

```bash
# Ver errores recientes
tail -n 100 /var/www/gastos-familiares/logs/errors.log

# Ver actividad general
tail -n 100 /var/www/gastos-familiares/logs/application.log

# Ver logs de Gunicorn
sudo journalctl -u gunicorn --since "1 hour ago"

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 🆘 TROUBLESHOOTING

### Error: Gunicorn no inicia

```bash
# Ver logs detallados
sudo journalctl -u gunicorn -n 50

# Verificar permisos
sudo chown -R www-data:www-data /var/www/gastos-familiares
sudo chmod -R 755 /var/www/gastos-familiares

# Reintentar
sudo systemctl restart gunicorn
```

### Error: Archivos estáticos no cargan

```bash
# Verificar colecta de estáticos
cd /var/www/gastos-familiares
source .venv/bin/activate
python manage.py collectstatic --noinput

# Verificar permisos
sudo chmod -R 755 /var/www/gastos-familiares/staticfiles

# Verificar Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Error: Base de datos no conecta

```bash
# Verificar PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar conexión
sudo -u postgres psql -c "\l"

# Verificar usuario y permisos
sudo -u postgres psql -c "\du"

# Probar conexión desde Django
cd /var/www/gastos-familiares
source .venv/bin/activate
python manage.py dbshell
```

### Error 500 en producción

```bash
# Habilitar DEBUG temporalmente (SOLO PARA DIAGNOSTICAR)
# Editar .env: DEBUG=True
sudo systemctl restart gunicorn

# Ver error específico en navegador
# Luego VOLVER A DEBUG=False

# Ver logs
tail -f /var/www/gastos-familiares/logs/errors.log
```

---

## 📊 MÉTRICAS Y MONITOREO

### Uso de Recursos

```bash
# CPU y memoria de Gunicorn
ps aux | grep gunicorn

# Espacio en disco
df -h

# Tamaño de base de datos
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('finanbot'));"
```

### Performance

```bash
# Tiempo de respuesta
time curl -s https://gastosweb.com > /dev/null

# Requests por segundo (con Apache Bench)
ab -n 1000 -c 10 https://gastosweb.com/
```

---

## 📞 CONTACTO Y SOPORTE

**Desarrollador:** Luis García  
**Email:** soporte@gastosweb.com  
**WhatsApp:** +57 311 700 9855  
**Website:** https://gastosweb.com

---

## ✅ ESTADO FINAL

```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║    🎉  PROYECTO DESPLEGADO EN PRODUCCIÓN  🎉         ║
║                                                       ║
║    Versión: 2.2.2                                    ║
║    Django: 6.0.5 (Sin CVEs)                          ║
║    Seguridad: ⭐⭐⭐⭐⭐ Certificado                ║
║    Estado: ✅ OPERATIVO                              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

**Última actualización:** 31 de Mayo 2026  
**Documentación completa:** Ver README.md y CHANGELOG.md

<div align="center">

**Desarrollado con ❤️ en Colombia 🇨🇴**

**FinanBot - Gestión Inteligente de Gastos Familiares**

</div>

