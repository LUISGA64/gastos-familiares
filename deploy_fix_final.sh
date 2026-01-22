#!/bin/bash
# ===== SOLUCIÓN DEFINITIVA - BAD REQUEST 400 =====
# Script completo para resolver el problema de ALLOWED_HOSTS

set -e  # Detener si hay errores

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          SOLUCIÓN DEFINITIVA - BAD REQUEST 400                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el directorio correcto
cd /var/www/gastos-familiares

echo "━━━ 1/6: Creando archivo .env LIMPIO..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Eliminar cualquier .env existente
rm -f .env .env.backup

# Crear .env con formato ASCII puro, sin variables ni espacios extras
cat > .env << 'ENVEOF'
SECRET_KEY=p5p-*+zovjzo@hnv(7lrh45v-l9*&&6i%th#mow#a19s(e+i0j
DEBUG=False
ALLOWED_HOSTS=167.114.2.88,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://167.114.2.88
DATABASE_URL=postgresql://gastos_user:Gastos2026Familia@localhost:5432/gastos_familiares
AI_PROVIDER=groq
GROQ_API_KEY=
ENVEOF

# Asegurar permisos correctos
chown ubuntu:ubuntu .env
chmod 644 .env

echo "✅ .env creado correctamente"
echo ""
echo "Contenido verificado:"
cat .env
echo ""

echo "━━━ 2/6: Creando configuración de Nginx OPTIMIZADA..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Crear configuración de Nginx con protección contra ataques
sudo tee /etc/nginx/sites-available/gastos-familiares > /dev/null << 'NGINXEOF'
# Configuración de Gastos Familiares - OVHcloud

server {
    listen 80;
    server_name 167.114.2.88;

    # Configuración de seguridad
    client_max_body_size 20M;
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;

    # Ocultar versión de Nginx
    server_tokens off;

    # Bloquear acceso a archivos sensibles
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Bloquear intentos de ataque comunes
    location ~* /(phpunit|vendor|cgi-bin|\.php|\.asp|\.aspx) {
        return 404;
        access_log off;
    }

    # Favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    # Archivos estáticos
    location /static/ {
        alias /var/www/gastos-familiares/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Archivos de media
    location /media/ {
        alias /var/www/gastos-familiares/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy a Gunicorn
    location / {
        # Headers necesarios para Django
        proxy_pass http://unix:/var/www/gastos-familiares/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Sin redirects
        proxy_redirect off;

        # Buffer settings
        proxy_buffering off;
    }
}
NGINXEOF

echo "✅ Configuración de Nginx creada"
echo ""

echo "━━━ 3/6: Verificando sintaxis de Nginx..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if sudo nginx -t 2>&1; then
    echo "✅ Configuración de Nginx válida"
else
    echo "❌ Error en configuración de Nginx"
    exit 1
fi
echo ""

echo "━━━ 4/6: Asegurando que el sitio esté habilitado..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Crear symlink si no existe
if [ ! -L /etc/nginx/sites-enabled/gastos-familiares ]; then
    sudo ln -s /etc/nginx/sites-available/gastos-familiares /etc/nginx/sites-enabled/
    echo "✅ Sitio habilitado"
else
    echo "✅ Sitio ya estaba habilitado"
fi

# Eliminar configuración default si existe
if [ -L /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
    echo "✅ Sitio default deshabilitado"
fi
echo ""

echo "━━━ 5/6: Reiniciando servicios..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Reiniciar Gunicorn
echo "Reiniciando Gunicorn..."
sudo systemctl restart gunicorn
sleep 2

if systemctl is-active --quiet gunicorn; then
    echo "✅ Gunicorn activo"
else
    echo "❌ Gunicorn falló al iniciar"
    sudo journalctl -u gunicorn -n 20 --no-pager
    exit 1
fi

# Reiniciar Nginx
echo "Reiniciando Nginx..."
sudo systemctl restart nginx
sleep 1

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx activo"
else
    echo "❌ Nginx falló al iniciar"
    sudo systemctl status nginx --no-pager
    exit 1
fi
echo ""

echo "━━━ 6/6: Verificación final..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Estado de servicios:"
systemctl is-active gunicorn && echo "  ✅ Gunicorn: ACTIVO" || echo "  ❌ Gunicorn: INACTIVO"
systemctl is-active nginx && echo "  ✅ Nginx: ACTIVO" || echo "  ❌ Nginx: INACTIVO"
systemctl is-active postgresql && echo "  ✅ PostgreSQL: ACTIVO" || echo "  ❌ PostgreSQL: INACTIVO"
echo ""

echo "Configuración actual (.env):"
echo "  ALLOWED_HOSTS=$(grep ALLOWED_HOSTS .env | cut -d'=' -f2)"
echo "  DEBUG=$(grep DEBUG .env | cut -d'=' -f2)"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ CORRECCIÓN COMPLETADA EXITOSAMENTE             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 INSTRUCCIONES FINALES:"
echo ""
echo "1. Abre tu navegador en MODO INCÓGNITO:"
echo "   - Chrome/Edge: Ctrl + Shift + N"
echo "   - Firefox: Ctrl + Shift + P"
echo ""
echo "2. Accede EXACTAMENTE a esta URL:"
echo ""
echo "   http://167.114.2.88"
echo ""
echo "3. NO incluyas nada más (sin comas, sin duplicados)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Para monitorear logs en tiempo real:"
echo "   sudo journalctl -u gunicorn -f"
echo ""
echo "🔒 Para ver intentos de ataque bloqueados:"
echo "   sudo tail -f /var/log/nginx/access.log | grep 404"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
