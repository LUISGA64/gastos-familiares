# 🚀 GUÍA DE ACTUALIZACIÓN EN OVH

**Proyecto:** FinanBot v2.2.2  
**Servidor:** OVH (gastosweb.com)  
**Fecha:** 31 de Mayo 2026  
**Tipo:** Actualización de proyecto existente

---

## ⚠️ IMPORTANTE - LEER ANTES DE ACTUALIZAR

Este documento es para **actualizar** el proyecto que ya está corriendo en OVH.

**¿Qué incluye esta actualización?**
- ✅ 95 archivos innecesarios eliminados
- ✅ 30 CVEs de seguridad críticos resueltos
- ✅ Dependencias actualizadas (Django 6.0.5, Pillow 12.2.0, etc.)
- ✅ Documentación profesional generada
- ✅ 0 errores en validaciones

**Tiempo estimado:** 15-30 minutos  
**Riesgo:** 🟡 BAJO-MEDIO (cambios en dependencias)  
**Downtime:** ~2-5 minutos

---

## 📋 PRE-REQUISITOS

Antes de comenzar, asegúrate de tener:

- [x] Acceso SSH al servidor OVH
- [x] Usuario con permisos sudo
- [x] El proyecto está en `/var/www/gastos-familiares` (o ruta equivalente)
- [x] Conexión estable a Internet

---

## 🔧 PASO 1: CONECTAR AL SERVIDOR OVH

```bash
# Conectar vía SSH
ssh usuario@gastosweb.com
# O con IP directa
ssh usuario@167.114.2.88

# Verificar que estás en el servidor correcto
hostname
pwd
```

---

## 💾 PASO 2: BACKUP COMPLETO (CRÍTICO)

```bash
# Crear directorio de backups si no existe
sudo mkdir -p /backups/finanbot

# Backup de la base de datos PostgreSQL
sudo -u postgres pg_dump finanbot > /backups/finanbot/backup_$(date +%Y%m%d_%H%M%S).sql

# Comprimir backup
gzip /backups/finanbot/backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de archivos media (si hay uploads importantes)
sudo tar -czf /backups/finanbot/media_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/gastos-familiares/media/

# Verificar backups creados
ls -lh /backups/finanbot/

# Backup del archivo .env (por seguridad)
sudo cp /var/www/gastos-familiares/.env /backups/finanbot/.env.backup_$(date +%Y%m%d_%H%M%S)
```

**✅ VERIFICACIÓN:** Asegúrate de que los backups se crearon correctamente antes de continuar.

---

## 🛑 PASO 3: DETENER SERVICIOS

```bash
# Detener Gunicorn (el sitio quedará temporalmente inaccesible)
sudo systemctl stop gunicorn

# Verificar que se detuvo
sudo systemctl status gunicorn

# Opcional: Mostrar página de mantenimiento en Nginx
# (Si tienes configurada una página de maintenance)
```

---

## 📥 PASO 4: ACTUALIZAR CÓDIGO DESDE GITHUB

```bash
# Ir al directorio del proyecto
cd /var/www/gastos-familiares

# Ver estado actual
git status
git log --oneline -1

# Hacer stash de cambios locales (si los hay)
git stash

# Actualizar código desde GitHub
sudo git pull origin main

# Verificar el último commit
git log --oneline -1
# Deberías ver: 4fda20d 🔒 Validación y limpieza completa para producción...

# Ver archivos que cambiaron
git show --stat

# Si hay conflictos, resolverlos manualmente
# git stash pop (si hiciste stash antes)
```

---

## 🐍 PASO 5: ACTUALIZAR DEPENDENCIAS PYTHON

```bash
# Activar entorno virtual
cd /var/www/gastos-familiares
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# IMPORTANTE: Instalar dependencias actualizadas
pip install --upgrade -r requirements-production.txt

# Verificar versiones instaladas
pip show Django pillow requests gunicorn cryptography

# Deberías ver:
# - Django: 6.0.5
# - Pillow: 12.2.0
# - requests: 2.33.0
# - gunicorn: 22.0.0
# - cryptography: 46.0.6

# Verificar que no hay conflictos
pip check
```

---

## 🔄 PASO 6: APLICAR MIGRACIONES (SI HAY NUEVAS)

```bash
# Verificar si hay migraciones pendientes
python manage.py showmigrations

# Verificar configuración
python manage.py check --deploy

# Aplicar migraciones (NO ELIMINA DATOS)
python manage.py migrate

# Verificar que se aplicaron correctamente
python manage.py showmigrations
```

---

## 📦 PASO 7: COLECTAR ARCHIVOS ESTÁTICOS

```bash
# Colectar archivos estáticos actualizados
python manage.py collectstatic --noinput

# Verificar permisos
sudo chown -R www-data:www-data /var/www/gastos-familiares/staticfiles
sudo chmod -R 755 /var/www/gastos-familiares/staticfiles
```

---

## 🔄 PASO 8: REINICIAR SERVICIOS

```bash
# Reiniciar Gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn

# Verificar que está corriendo correctamente
sudo systemctl is-active gunicorn

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl status nginx

# Ver logs en tiempo real (Ctrl+C para salir)
sudo journalctl -u gunicorn -f
```

---

## ✅ PASO 9: VERIFICACIÓN POST-ACTUALIZACIÓN

### 9.1 Verificar que el sitio carga

```bash
# Desde el servidor
curl -I https://gastosweb.com

# Debería responder 200 OK

# Verificar redirección HTTP → HTTPS
curl -I http://gastosweb.com
```

### 9.2 Verificar funcionalidad básica

**Desde tu navegador:**
- [ ] https://gastosweb.com carga correctamente
- [ ] Login funciona
- [ ] Dashboard muestra datos
- [ ] Crear gasto funciona
- [ ] Chatbot responde
- [ ] Exportar PDF funciona
- [ ] Exportar Excel funciona

### 9.3 Verificar logs

```bash
# Ver logs de aplicación
tail -n 50 /var/www/gastos-familiares/logs/application.log

# Ver logs de errores
tail -n 50 /var/www/gastos-familiares/logs/errors.log

# Ver logs de Gunicorn
sudo journalctl -u gunicorn --since "10 minutes ago"

# Ver logs de Nginx
sudo tail -n 50 /var/log/nginx/error.log
```

---

## 🔍 PASO 10: VERIFICAR VERSIONES ACTUALIZADAS

```bash
# Desde el servidor, con entorno virtual activado
cd /var/www/gastos-familiares
source .venv/bin/activate

# Verificar versiones de paquetes críticos
python -c "import django; print(f'Django: {django.get_version()}')"
python -c "import PIL; print(f'Pillow: {PIL.__version__}')"
python -c "import requests; print(f'Requests: {requests.__version__}')"
python -c "import cryptography; print(f'Cryptography: {cryptography.__version__}')"

# Verificar que no hay CVEs
pip list --outdated
```

**Versiones esperadas:**
- Django: 6.0.5 ✅
- Pillow: 12.2.0 ✅
- Requests: 2.33.0 ✅
- Gunicorn: 22.0.0 ✅
- Cryptography: 46.0.6 ✅

---

## 🎯 PASO 11: MONITOREO POST-ACTUALIZACIÓN

```bash
# Monitorear logs en tiempo real (10-15 minutos)
sudo journalctl -u gunicorn -f

# En otra terminal, monitorear Nginx
sudo tail -f /var/log/nginx/access.log

# Verificar uso de recursos
top
htop

# Verificar workers de Gunicorn
ps aux | grep gunicorn
```

---

## 🆘 TROUBLESHOOTING

### Error: Gunicorn no inicia después de actualizar

```bash
# Ver logs detallados
sudo journalctl -u gunicorn -n 100 --no-pager

# Verificar sintaxis de Python
cd /var/www/gastos-familiares
source .venv/bin/activate
python manage.py check

# Verificar permisos
sudo chown -R www-data:www-data /var/www/gastos-familiares

# Reintentar
sudo systemctl restart gunicorn
```

### Error: Dependencias no se instalan correctamente

```bash
# Limpiar caché de pip
pip cache purge

# Reinstalar dependencias
pip install --force-reinstall -r requirements-production.txt

# Verificar
pip check
```

### Error: Error 500 en el sitio

```bash
# Ver logs de errores
tail -f /var/www/gastos-familiares/logs/errors.log

# Habilitar DEBUG temporalmente (SOLO PARA DIAGNOSTICAR)
# NO DEJAR DEBUG=True EN PRODUCCIÓN
sudo nano /var/www/gastos-familiares/.env
# Cambiar DEBUG=True temporalmente

sudo systemctl restart gunicorn

# Visitar el sitio y ver el error específico
# Luego VOLVER A DEBUG=False
```

### Error: Migraciones fallan

```bash
# Ver migraciones pendientes
python manage.py showmigrations

# Intentar aplicar manualmente
python manage.py migrate --fake-initial

# Si persiste, revisar base de datos
sudo -u postgres psql finanbot
# \dt para ver tablas
# \q para salir
```

---

## 🔄 ROLLBACK (SI ALGO SALE MAL)

Si algo falla y necesitas volver a la versión anterior:

```bash
# 1. Detener servicios
sudo systemctl stop gunicorn

# 2. Volver al commit anterior
cd /var/www/gastos-familiares
git log --oneline -5
git checkout <commit-anterior>

# 3. Reinstalar dependencias anteriores
source .venv/bin/activate
pip install -r requirements-production.txt

# 4. Restaurar base de datos (si es necesario)
sudo -u postgres psql finanbot < /backups/finanbot/backup_YYYYMMDD_HHMMSS.sql

# 5. Reiniciar servicios
sudo systemctl start gunicorn
sudo systemctl restart nginx
```

---

## 📊 VERIFICACIÓN FINAL - CHECKLIST

Una vez completada la actualización, verifica:

### Funcionalidad Core
- [ ] https://gastosweb.com carga sin errores
- [ ] Login funciona correctamente
- [ ] Dashboard Premium muestra datos
- [ ] Crear nuevo gasto funciona
- [ ] Registrar ingreso funciona
- [ ] Conciliación mensual funciona
- [ ] Chatbot IA responde (si está configurado)
- [ ] Exportar PDF genera archivo
- [ ] Exportar Excel genera archivo
- [ ] Sistema de pagos muestra QR
- [ ] Toggle privacidad funciona
- [ ] Gamificación muestra logros

### Seguridad
- [ ] HTTPS funciona (candado verde)
- [ ] Redirección HTTP → HTTPS opera
- [ ] Login seguro (sin warnings)
- [ ] Cookies seguras

### Performance
- [ ] Sitio carga rápido (< 3 segundos)
- [ ] No hay errores en consola del navegador
- [ ] Archivos estáticos cargan correctamente
- [ ] Imágenes se muestran

### Logs
- [ ] No hay errores críticos en logs
- [ ] Gunicorn funciona correctamente
- [ ] Nginx no reporta errores

---

## 📈 MONITOREO CONTINUO (PRÓXIMAS 24 HORAS)

```bash
# Configurar monitoreo de logs
# Ejecutar en segundo plano
nohup sudo journalctl -u gunicorn -f > /tmp/gunicorn_monitor.log 2>&1 &

# Revisar periódicamente
tail -f /tmp/gunicorn_monitor.log

# Verificar métricas del sistema
watch -n 60 'df -h && free -h && ps aux | grep gunicorn | wc -l'
```

---

## 🎊 ACTUALIZACIÓN COMPLETADA

Si todos los checks pasaron, tu actualización fue exitosa:

```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║    ✅  ACTUALIZACIÓN EN OVH COMPLETADA EXITOSAMENTE  ║
║                                                       ║
║    • 30 CVEs resueltos                               ║
║    • Dependencias actualizadas                       ║
║    • 95 archivos innecesarios eliminados             ║
║    • Documentación actualizada                       ║
║    • Sitio funcionando correctamente                 ║
║                                                       ║
║    🚀 Versión: 2.2.2                                 ║
║    🔒 Seguridad: ⭐⭐⭐⭐⭐ Certificado            ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🔐 NOTAS DE SEGURIDAD POST-ACTUALIZACIÓN

### Cambios Importantes en Dependencias

1. **Django 6.0.1 → 6.0.5**
   - 16 vulnerabilidades de seguridad parcheadas
   - Compatibilidad 100% mantenida
   - No se requieren cambios en código

2. **Pillow 10.4.0 → 12.2.0**
   - 5 vulnerabilidades críticas resueltas
   - Verificar procesamiento de imágenes PSD/FITS (si las usas)

3. **Gunicorn 21.2.0 → 22.0.0**
   - Validación mejorada de Transfer-Encoding headers
   - Protección contra request smuggling

---

## 📞 SOPORTE

Si encuentras problemas durante la actualización:

**Email:** soporte@gastosweb.com  
**WhatsApp:** +57 311 700 9855

**Documentación adicional:**
- `ACTUALIZACION_SEGURIDAD_CVEs.md` - Detalles de CVEs
- `VALIDACION_PRODUCCION.md` - Validación completa
- `RESUMEN_VALIDACION_COMPLETA.md` - Resumen ejecutivo

---

## 📝 LOG DE ACTUALIZACIÓN

**Completa este log después de la actualización:**

```
Fecha de actualización: _____________________
Hora inicio: _____________________
Hora fin: _____________________
Duración total: _____________________
Downtime: _____________________
Problemas encontrados: _____________________
Solución aplicada: _____________________
Verificado por: _____________________
Estado final: ☐ EXITOSA  ☐ CON ERRORES  ☐ ROLLBACK
```

---

## 🎯 PRÓXIMA ACTUALIZACIÓN

**Recomendación:** Verificar actualizaciones de seguridad cada mes.

```bash
# Para futuras actualizaciones, repetir este proceso:
# 1. Backup
# 2. Git pull
# 3. Actualizar dependencias
# 4. Migraciones
# 5. Collectstatic
# 6. Reiniciar servicios
# 7. Verificar
```

---

**Última actualización de este documento:** 31 de Mayo 2026  
**Versión de la guía:** 1.0  
**Compatible con:** FinanBot v2.2.2

---

<div align="center">

**Desarrollado con ❤️ en Colombia 🇨🇴**

**FinanBot - Gestión Inteligente de Gastos Familiares**

**OVH Cloud - gastosweb.com**

</div>

