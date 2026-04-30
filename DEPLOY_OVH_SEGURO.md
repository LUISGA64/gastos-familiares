# 🚀 Guía de Despliegue Seguro en OVH

## 📅 Fecha
30 de Abril de 2026

## 🎯 Cambios a Desplegar

### Resumen de Cambios
1. **Fix crítico:** Redirección en conciliación mantiene parámetros mes/año
2. **Mejora:** Tabla detallada de reportes con distribución por aportante
3. **Nueva funcionalidad:** Exportación Excel de reportes con filtros
4. **Mejora UX:** Filtros por mes y aportante en gastos personales

### Archivos Modificados
- `gastos/views.py` - Fix de redirects y filtros de reportes
- `gastos/views_export.py` - Nueva función exportar_reportes_excel
- `gastos/urls.py` - Nueva ruta para export reportes
- `templates/gastos/reportes.html` - Tabla detallada con aportantes
- `templates/gastos/gastos_personales/lista_gastos_personales.html` - Filtros mejorados

### Documentación Nueva
- `FIX_CONCILIACION_REDIRECCION.md` - Documentación del fix
- `MEJORAS_REPORTES_DETALLADOS.md` - Documentación de reportes
- `FILTROS_GASTOS_PERSONALES.md` - Documentación filtros personales

---

## ⚠️ IMPORTANTE: Verificaciones Pre-Despliegue

### ✅ Checklist de Seguridad

- [x] Código probado en local sin errores
- [x] `python manage.py check` ejecutado exitosamente
- [x] NO hay migraciones de base de datos pendientes
- [x] NO hay cambios en modelos
- [x] NO hay nuevas dependencias en requirements.txt
- [x] Cambios NO afectan datos existentes
- [x] Backup de código actual recomendado

---

## 🔧 Procedimiento de Despliegue en OVH

### PASO 1: Conectarse al Servidor

```bash
# Conectar vía SSH
ssh usuario@tu-servidor-ovh.com

# O si tienes clave privada
ssh -i ~/.ssh/id_rsa usuario@tu-servidor-ovh.com
```

### PASO 2: Backup del Código Actual (CRÍTICO)

```bash
# Ir al directorio del proyecto
cd /var/www/html/FinanBot

# Crear backup con timestamp
BACKUP_DIR="/var/www/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp -r /var/www/html/FinanBot $BACKUP_DIR/FinanBot_backup_$TIMESTAMP

# Verificar que el backup se creó
ls -lh $BACKUP_DIR/

echo "✅ Backup creado: $BACKUP_DIR/FinanBot_backup_$TIMESTAMP"
```

**⚠️ IMPORTANTE:** Si algo sale mal, puedes restaurar con:
```bash
# SOLO EN CASO DE EMERGENCIA
rm -rf /var/www/html/FinanBot
cp -r $BACKUP_DIR/FinanBot_backup_$TIMESTAMP /var/www/html/FinanBot
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### PASO 3: Pull de Cambios desde GitHub

```bash
# Asegurarse de estar en el directorio correcto
cd /var/www/html/FinanBot

# Ver estado actual
git status

# IMPORTANTE: Si hay cambios locales no commiteados
git stash  # Guardar cambios locales temporalmente

# Actualizar desde repositorio
git fetch origin main
git pull origin main

# Si usaste stash, puedes recuperar cambios locales
# git stash pop  # Solo si lo necesitas
```

### PASO 4: Verificar Código

```bash
# Activar entorno virtual
source venv/bin/activate  # o el nombre de tu venv

# Verificar que no hay errores
python manage.py check

# Resultado esperado:
# System check identified no issues (0 silenced).
```

**Si hay errores aquí, NO continuar. Revisar logs y corregir.**

### PASO 5: Archivos Estáticos (Si es necesario)

```bash
# Solo si hay cambios en CSS, JS o templates significativos
python manage.py collectstatic --noinput

# Verificar
ls -lh /var/www/html/FinanBot/staticfiles/
```

### PASO 6: Reiniciar Servicios

**Opción A: Reinicio Suave (Recomendado)**
```bash
# Recargar gunicorn sin downtime
sudo systemctl reload gunicorn

# Recargar nginx
sudo systemctl reload nginx

# Verificar estado
sudo systemctl status gunicorn
sudo systemctl status nginx
```

**Opción B: Reinicio Completo (Si Opción A falla)**
```bash
# Reiniciar gunicorn
sudo systemctl restart gunicorn

# Reiniciar nginx
sudo systemctl restart nginx

# Verificar estado
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### PASO 7: Verificación Post-Despliegue

```bash
# Ver logs en tiempo real
sudo tail -f /var/log/gunicorn/error.log

# En otra terminal, hacer prueba
curl https://tu-dominio.com/admin/

# Verificar que responde correctamente
```

---

## 🧪 Pruebas Post-Despliegue

### Test 1: Conciliación con Códigos
1. Ir a `/conciliacion/`
2. Seleccionar un mes pasado (ej: Marzo 2026)
3. Click en "Enviar Códigos de Confirmación"
4. ✅ **Verificar:** Debe mantenerse en Marzo 2026
5. ✅ **Verificar:** Deben aparecer formularios de códigos

### Test 2: Reportes con Filtros
1. Ir a `/reportes/`
2. Seleccionar un mes del dropdown
3. ✅ **Verificar:** Tabla muestra gastos del mes seleccionado
4. ✅ **Verificar:** Columnas por cada aportante visibles
5. ✅ **Verificar:** Totales por aportante correctos

### Test 3: Exportación Excel
1. En `/reportes/`
2. Seleccionar mes
3. Click en "Exportar a Excel"
4. ✅ **Verificar:** Descarga archivo .xlsx
5. ✅ **Verificar:** Archivo contiene datos del mes correcto
6. ✅ **Verificar:** Columnas dinámicas por aportante

### Test 4: Gastos Personales
1. Ir a `/gastos/personales/`
2. Seleccionar mes y aportante
3. ✅ **Verificar:** Filtros funcionan correctamente
4. ✅ **Verificar:** Totales actualizan correctamente

---

## 🔍 Monitoreo Post-Despliegue

### Logs a Vigilar

```bash
# Errores de Gunicorn
sudo tail -f /var/log/gunicorn/error.log

# Errores de Nginx
sudo tail -f /var/log/nginx/error.log

# Accesos de Nginx
sudo tail -f /var/log/nginx/access.log

# Si usas systemd journal
sudo journalctl -u gunicorn -f
```

### Comandos Útiles de Monitoreo

```bash
# Ver procesos de Gunicorn
ps aux | grep gunicorn

# Ver uso de memoria
free -h

# Ver uso de disco
df -h

# Ver procesos más pesados
top
# o
htop  # si está instalado
```

---

## 🚨 Plan de Rollback (En caso de problemas)

### Escenario 1: Errores 500 después del despliegue

```bash
# 1. Ver logs para identificar error
sudo tail -100 /var/log/gunicorn/error.log

# 2. Si no se puede resolver rápido, rollback
cd /var/www/html
sudo rm -rf FinanBot
sudo cp -r /var/www/backups/FinanBot_backup_$TIMESTAMP FinanBot

# 3. Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 4. Verificar
curl https://tu-dominio.com/admin/
```

### Escenario 2: Funcionalidad específica falla

```bash
# Si solo una funcionalidad falla, puede no ser necesario rollback completo
# Revisar logs y hacer fix específico

# Ver últimos 200 errores
sudo tail -200 /var/log/gunicorn/error.log | grep ERROR
```

---

## 📊 Métricas de Éxito

### Después del despliegue, verificar:

- [ ] Website carga sin errores 500/404
- [ ] Login funciona correctamente
- [ ] Dashboard muestra correctamente
- [ ] Conciliación mantiene parámetros de mes
- [ ] Reportes muestran tabla detallada
- [ ] Excel se descarga correctamente
- [ ] Gastos personales con filtros funcionan
- [ ] No hay errores en logs de Gunicorn
- [ ] Tiempo de respuesta normal (<2s)

---

## 🔐 Consideraciones de Seguridad

### Permisos de Archivos

```bash
# Verificar permisos correctos
cd /var/www/html/FinanBot

# Archivos deben ser propiedad del usuario web
sudo chown -R www-data:www-data .

# Permisos de archivos
sudo find . -type f -exec chmod 644 {} \;

# Permisos de directorios
sudo find . -type d -exec chmod 755 {} \;

# manage.py debe ser ejecutable
sudo chmod +x manage.py
```

### Variables de Entorno

```bash
# Verificar que .env está presente y seguro
ls -la /var/www/html/FinanBot/.env

# Debe tener permisos 600 (solo dueño lee/escribe)
sudo chmod 600 .env

# Verificar que contiene:
# - SECRET_KEY
# - DEBUG=False
# - ALLOWED_HOSTS
# - DATABASE_URL (si aplica)
```

---

## 📞 Contactos de Emergencia

### Si algo sale mal:

1. **Rollback inmediato** (ver sección Plan de Rollback)
2. **Revisar logs** para identificar error
3. **Contactar a soporte OVH** si es problema de infraestructura
4. **Restaurar desde backup** como última opción

---

## 📝 Checklist Final Post-Despliegue

### Verificaciones Técnicas
- [ ] `python manage.py check` sin errores
- [ ] Gunicorn corriendo: `sudo systemctl status gunicorn`
- [ ] Nginx corriendo: `sudo systemctl status nginx`
- [ ] Sin errores en logs
- [ ] Archivos estáticos cargando

### Verificaciones Funcionales
- [ ] Login funciona
- [ ] Dashboard carga
- [ ] Conciliación funciona con códigos
- [ ] Reportes muestran correctamente
- [ ] Excel se descarga
- [ ] Gastos personales filtran bien

### Verificaciones de Performance
- [ ] Tiempo de carga <3 segundos
- [ ] Queries no exceden 100ms
- [ ] Memoria estable
- [ ] CPU normal (<50%)

---

## 🎉 Confirmación de Despliegue Exitoso

Una vez completados todos los pasos:

```bash
echo "✅ Despliegue completado en: $(date)"
echo "✅ Versión: 2.2.1"
echo "✅ Commit: $(git rev-parse --short HEAD)"
echo "✅ Cambios desplegados:"
echo "   - Fix redirección conciliación"
echo "   - Reportes con distribución detallada"
echo "   - Exportación Excel mejorada"
echo "   - Filtros gastos personales"
```

---

## 📚 Documentación Relacionada

- `FIX_CONCILIACION_REDIRECCION.md` - Detalles del fix principal
- `MEJORAS_REPORTES_DETALLADOS.md` - Documentación de reportes
- `DEPLOY_VPS_UNIVERSAL.md` - Guía general de despliegue

---

## ⏱️ Estimación de Tiempo

**Tiempo total estimado:** 15-20 minutos

- Backup: 2 min
- Pull y verificación: 3 min
- Actualizaciones: 5 min
- Reinicio servicios: 2 min
- Pruebas: 5-8 min

**Ventana de mantenimiento:** Mínima o ninguna (hot reload)

---

## 🎯 Notas Importantes

1. ✅ **NO hay migraciones** - Despliegue muy seguro
2. ✅ **NO hay nuevas dependencias** - No requiere pip install
3. ✅ **Cambios solo en lógica** - Bajo riesgo
4. ✅ **Backward compatible** - No rompe funcionalidad existente
5. ✅ **Probado en local** - Sin errores conocidos

**Nivel de Riesgo:** 🟢 BAJO

---

**Preparado por:** FinanBot Development Team  
**Fecha:** 30 de Abril de 2026  
**Versión a desplegar:** 2.2.1  
**Última actualización:** 30/04/2026 - 15:30

