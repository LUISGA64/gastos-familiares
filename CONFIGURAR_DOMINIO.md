# 🌐 CONFIGURACIÓN DOMINIO gastosweb.com

## 📋 GUÍA COMPLETA DE CONFIGURACIÓN

---

## PASO 1: CONFIGURAR DNS DEL DOMINIO

### En tu proveedor de dominio (donde compraste gastosweb.com):

Agrega estos registros DNS:

```
Tipo    Nombre      Valor               TTL
----    ------      -----               ---
A       @           167.114.2.88        3600
A       www         167.114.2.88        3600
CNAME   www         gastosweb.com       3600
```

**Explicación:**
- `@` = dominio raíz (gastosweb.com)
- `www` = subdominio www (www.gastosweb.com)
- Ambos apuntan a la IP del VPS: `167.114.2.88`

**⏰ IMPORTANTE:** Los cambios DNS pueden tardar de 5 minutos a 48 horas en propagarse.

**Verificar DNS:**
```bash
# En tu computadora local
nslookup gastosweb.com
nslookup www.gastosweb.com

# Debe mostrar: 167.114.2.88
```

---

## PASO 2: ACTUALIZAR CÓDIGO DE DJANGO

### ✅ YA HECHO - Archivo `settings.py` actualizado con:

```python
ALLOWED_HOSTS = [
    'gastosweb.com',
    'www.gastosweb.com',
    '167.114.2.88',
    '192.168.28.93',
    'localhost',
    '127.0.0.1'
]

CSRF_TRUSTED_ORIGINS = [
    'https://gastosweb.com',
    'https://www.gastosweb.com',
    'http://167.114.2.88'
]
```

### Subir cambios al servidor:

```bash
# En tu computadora local
git add DjangoProject/settings.py
git commit -m "feat: Agregar dominio gastosweb.com a ALLOWED_HOSTS"
git push
```

---

## PASO 3: CONFIGURAR NGINX EN EL SERVIDOR

### Conectar al servidor:

```bash
ssh ubuntu@167.114.2.88
```

### Crear configuración de Nginx:

```bash
sudo nano /etc/nginx/sites-available/gastosweb.com
```

### Pegar esta configuración:

```nginx
# HTTP - Redirecciona a HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name gastosweb.com www.gastosweb.com;

    # Certbot validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Configuración principal
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name gastosweb.com www.gastosweb.com;

    # SSL certificates (se configurarán con Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/gastosweb.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gastosweb.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/gastosweb.com.access.log;
    error_log /var/log/nginx/gastosweb.com.error.log;

    # Static files
    location /static/ {
        alias /var/www/gastos-familiares/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/gastos-familiares/media/;
        expires 30d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://unix:/var/www/gastos-familiares/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    # Robots.txt
    location = /robots.txt {
        access_log off;
        log_not_found off;
    }
}
```

### Guardar y salir:
- Presiona `Ctrl + X`
- Presiona `Y`
- Presiona `Enter`

---

## PASO 4: HABILITAR SITIO EN NGINX

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/gastosweb.com /etc/nginx/sites-enabled/

# Verificar configuración (IGNORAR error de SSL por ahora)
sudo nginx -t

# Si todo está OK, continuar
```

**Nota:** Verás error de SSL porque aún no hemos configurado Let's Encrypt. Es normal.

---

## PASO 5: INSTALAR CERTBOT PARA SSL

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

---

## PASO 6: OBTENER CERTIFICADO SSL

**IMPORTANTE:** Asegúrate que el DNS ya esté propagado antes de este paso.

```bash
# Obtener certificado SSL
sudo certbot --nginx -d gastosweb.com -d www.gastosweb.com

# Certbot preguntará:
# Email: [tu email]
# Términos: A (Agree)
# Newsletter: N (No)
# Redirect: 2 (Sí, forzar HTTPS)
```

**Si el DNS no está propagado:**
```
Error: Failed to verify domain ownership

Solución: Espera 1-2 horas y vuelve a intentar
```

**Si el DNS está propagado:**
```
✅ Successfully obtained certificate
✅ Certificate stored at: /etc/letsencrypt/live/gastosweb.com/
```

---

## PASO 7: ACTUALIZAR PROYECTO EN EL SERVIDOR

```bash
# Ir al directorio del proyecto
cd /var/www/gastos-familiares

# Actualizar código
git pull

# Activar entorno virtual
source venv/bin/activate

# Aplicar migraciones (por si acaso)
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
sudo systemctl restart gunicorn

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## PASO 8: VERIFICAR CONFIGURACIÓN

```bash
# Estado de Nginx
sudo systemctl status nginx

# Estado de Gunicorn
sudo systemctl status gunicorn

# Ver logs de Nginx
sudo tail -f /var/log/nginx/gastosweb.com.error.log

# Ver logs de Gunicorn
sudo journalctl -u gunicorn -f
```

---

## PASO 9: PROBAR EL DOMINIO

### En tu navegador:

1. **http://gastosweb.com**
   - Debe redirigir a `https://gastosweb.com`
   - Debe mostrar el aplicativo

2. **http://www.gastosweb.com**
   - Debe redirigir a `https://www.gastosweb.com`
   - Debe mostrar el aplicativo

3. **https://gastosweb.com**
   - Debe mostrar el aplicativo
   - Candado verde de SSL

4. **http://167.114.2.88**
   - Debe seguir funcionando
   - Para acceso directo por IP

### Verificar SSL:

```
https://www.ssllabs.com/ssltest/analyze.html?d=gastosweb.com
```

---

## PASO 10: CONFIGURAR RENOVACIÓN AUTOMÁTICA DE SSL

```bash
# Probar renovación
sudo certbot renew --dry-run

# Certbot ya configura renovación automática
# Verificar cron job
sudo systemctl status certbot.timer

# Debe mostrar: Active (running)
```

---

## PASO 11: ACTUALIZAR ENLACES EN INVITACIONES

Los enlaces de invitación ahora usarán:
- `https://gastosweb.com/registro/ABC12345/`

En lugar de:
- `http://167.114.2.88/registro/ABC12345/`

**Esto se actualiza automáticamente** porque usamos `window.location.origin` en JavaScript.

---

## PASO 12: CONFIGURAR VARIABLES DE ENTORNO (Opcional pero recomendado)

```bash
# Editar .env en el servidor
nano /var/www/gastos-familiares/.env

# Agregar:
ALLOWED_HOSTS=gastosweb.com,www.gastosweb.com,167.114.2.88,localhost
CSRF_TRUSTED_ORIGINS=https://gastosweb.com,https://www.gastosweb.com,http://167.114.2.88
DEBUG=False
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema 1: DNS no propaga

**Síntomas:**
```
ping gastosweb.com
# No responde o IP incorrecta
```

**Solución:**
- Espera 1-24 horas
- Verifica configuración DNS en tu proveedor
- Usa herramienta: https://www.whatsmydns.net/

---

### Problema 2: Error 502 Bad Gateway

**Síntomas:**
```
Nginx muestra: 502 Bad Gateway
```

**Solución:**
```bash
# Verificar Gunicorn
sudo systemctl status gunicorn
sudo systemctl restart gunicorn

# Ver logs
sudo journalctl -u gunicorn -n 50
```

---

### Problema 3: Error SSL

**Síntomas:**
```
Certificado no válido
```

**Solución:**
```bash
# Re-obtener certificado
sudo certbot delete --cert-name gastosweb.com
sudo certbot --nginx -d gastosweb.com -d www.gastosweb.com
```

---

### Problema 4: Página no carga estilos

**Síntomas:**
```
Página sin CSS
```

**Solución:**
```bash
cd /var/www/gastos-familiares
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

---

### Problema 5: CSRF Token Error

**Síntomas:**
```
CSRF verification failed
```

**Solución:**
```python
# Verificar en settings.py:
CSRF_TRUSTED_ORIGINS = [
    'https://gastosweb.com',
    'https://www.gastosweb.com'
]

# Reiniciar
sudo systemctl restart gunicorn
```

---

## 📊 CHECKLIST DE VERIFICACIÓN

### ✅ DNS Configurado
- [ ] Registro A para @ apunta a 167.114.2.88
- [ ] Registro A para www apunta a 167.114.2.88
- [ ] `nslookup gastosweb.com` muestra IP correcta

### ✅ Django Actualizado
- [ ] ALLOWED_HOSTS incluye gastosweb.com
- [ ] CSRF_TRUSTED_ORIGINS incluye https://gastosweb.com
- [ ] Código subido al repositorio
- [ ] `git pull` ejecutado en servidor

### ✅ Nginx Configurado
- [ ] Archivo `/etc/nginx/sites-available/gastosweb.com` creado
- [ ] Enlace simbólico en `/etc/nginx/sites-enabled/` creado
- [ ] `sudo nginx -t` sin errores
- [ ] Nginx reiniciado

### ✅ SSL Configurado
- [ ] Certbot instalado
- [ ] Certificado obtenido para gastosweb.com y www.gastosweb.com
- [ ] Renovación automática configurada
- [ ] `sudo certbot renew --dry-run` exitoso

### ✅ Aplicativo Funcionando
- [ ] http://gastosweb.com redirige a https
- [ ] https://gastosweb.com carga el aplicativo
- [ ] https://www.gastosweb.com funciona
- [ ] Candado verde de SSL visible
- [ ] CSS y estilos cargan correctamente
- [ ] Login funciona
- [ ] Registro funciona
- [ ] Invitaciones usan nuevo dominio

### ✅ Servicios Activos
- [ ] `sudo systemctl status nginx` = Active
- [ ] `sudo systemctl status gunicorn` = Active
- [ ] `sudo systemctl status certbot.timer` = Active

---

## 🎉 RESULTADO FINAL

Una vez completados todos los pasos:

**URLs Funcionales:**
- ✅ https://gastosweb.com
- ✅ https://www.gastosweb.com
- ✅ http://gastosweb.com (redirige a HTTPS)
- ✅ http://www.gastosweb.com (redirige a HTTPS)
- ✅ http://167.114.2.88 (acceso por IP)

**Características:**
- ✅ SSL/HTTPS habilitado (candado verde)
- ✅ Renovación automática de certificado
- ✅ Redirección automática HTTP → HTTPS
- ✅ Headers de seguridad configurados
- ✅ Cacheo de archivos estáticos
- ✅ Logs separados por dominio

---

## 📱 ACTUALIZAR ENLACES EN INVITACIONES

**Automático:** Los enlaces de invitación ya usan el dominio nuevo:
- JavaScript usa `window.location.origin`
- Detecta automáticamente: `https://gastosweb.com`

**Manual (si necesitas compartir):**
```
Nuevo formato:
https://gastosweb.com/registro/ABC12345/
https://gastosweb.com/familia/unirse/ABC12345/
```

---

## 🔐 SEGURIDAD ADICIONAL (Opcional)

### Firewall:
```bash
# Permitir solo HTTP, HTTPS y SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Fail2ban:
```bash
# Instalar protección contra ataques
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📞 SOPORTE

Si tienes problemas:

1. **Revisa logs:**
   ```bash
   sudo tail -f /var/log/nginx/gastosweb.com.error.log
   sudo journalctl -u gunicorn -f
   ```

2. **Verifica servicios:**
   ```bash
   sudo systemctl status nginx
   sudo systemctl status gunicorn
   ```

3. **Reinicia todo:**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

---

## 🚀 ORDEN DE EJECUCIÓN RÁPIDA

```bash
# 1. Configurar DNS (en proveedor de dominio)
# 2. Esperar propagación DNS (1-24 horas)

# 3. En tu PC local:
git add DjangoProject/settings.py
git commit -m "feat: Agregar dominio gastosweb.com"
git push

# 4. En el servidor:
ssh ubuntu@167.114.2.88

# Crear configuración Nginx
sudo nano /etc/nginx/sites-available/gastosweb.com
# (pegar configuración de arriba)

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/gastosweb.com /etc/nginx/sites-enabled/

# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Obtener SSL
sudo certbot --nginx -d gastosweb.com -d www.gastosweb.com

# Actualizar proyecto
cd /var/www/gastos-familiares
git pull
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 5. Verificar
# Abrir navegador: https://gastosweb.com
```

---

**¡Tu dominio gastosweb.com está listo!** 🎉
