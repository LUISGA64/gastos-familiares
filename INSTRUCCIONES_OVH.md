# 📝 INSTRUCCIONES RÁPIDAS - ACTUALIZACIÓN EN OVH

**Servidor:** gastosweb.com (167.114.2.88)  
**Versión actual:** 2.2.1  
**Versión nueva:** 2.2.2  
**Fecha:** 31 de Mayo 2026

---

## ⚡ OPCIÓN 1: SCRIPT AUTOMATIZADO (RECOMENDADO)

### Pasos:

```bash
# 1. Conectar al servidor OVH
ssh usuario@gastosweb.com

# 2. Ir al directorio del proyecto
cd /var/www/gastos-familiares

# 3. Actualizar código desde GitHub
sudo git pull origin main

# 4. Ejecutar script de actualización
sudo bash actualizar_ovh.sh

# 5. Verificar que todo funciona
# Visitar: https://gastosweb.com
```

**Tiempo estimado:** 15-30 minutos  
**Downtime:** ~2-5 minutos

---

## 📖 OPCIÓN 2: MANUAL (PASO A PASO)

Seguir las instrucciones detalladas en: **ACTUALIZACION_OVH.md**

---

## ✅ QUÉ HACE EL SCRIPT AUTOMATIZADO

1. ✓ Verifica el estado del sistema
2. ✓ Crea backup de PostgreSQL
3. ✓ Crea backup de archivos media
4. ✓ Crea backup del archivo .env
5. ✓ Detiene Gunicorn
6. ✓ Actualiza código desde GitHub
7. ✓ Actualiza dependencias Python
8. ✓ Aplica migraciones de Django
9. ✓ Colecta archivos estáticos
10. ✓ Reinicia Gunicorn y Nginx
11. ✓ Verifica que el sitio funciona
12. ✓ Muestra resumen de la actualización

---

## 📊 CAMBIOS QUE SE APLICARÁN

| Categoría | Cambios |
|-----------|---------|
| **Limpieza** | 95 archivos innecesarios eliminados |
| **Seguridad** | 30 CVEs críticos resueltos |
| **Django** | 6.0.1 → 6.0.5 (16 CVEs) |
| **Pillow** | 10.4.0 → 12.2.0 (5 CVEs) |
| **Requests** | 2.31.0 → 2.33.0 (3 CVEs) |
| **Gunicorn** | 21.2.0 → 22.0.0 (2 CVEs) |
| **Cryptography** | 42.0.5 → 46.0.6 (4 CVEs) |

---

## ⚠️ IMPORTANTE

- **El script hace backup automático** antes de cualquier cambio
- **Monitorear logs** después de actualizar
- **Verificar funcionalidad** en https://gastosweb.com
- **Si algo falla**, el script muestra cómo hacer rollback

---

## 🔍 VERIFICACIÓN POST-ACTUALIZACIÓN

```bash
# Ver logs de Gunicorn
sudo journalctl -u gunicorn -f

# Ver logs de aplicación
tail -f /var/www/gastos-familiares/logs/application.log

# Ver logs de errores
tail -f /var/www/gastos-familiares/logs/errors.log

# Verificar estado de servicios
sudo systemctl status gunicorn
sudo systemctl status nginx
```

---

## 🆘 EN CASO DE PROBLEMAS

### Si el sitio no carga:

```bash
# Ver logs detallados
sudo journalctl -u gunicorn -n 100

# Verificar configuración
cd /var/www/gastos-familiares
source .venv/bin/activate
python manage.py check
```

### Si necesitas hacer rollback:

```bash
# Ver commits recientes
git log --oneline -5

# Volver al commit anterior
git checkout <commit-anterior>

# Reinstalar dependencias anteriores
pip install -r requirements-production.txt

# Restaurar base de datos si es necesario
sudo -u postgres psql finanbot < /backups/finanbot/backup_YYYYMMDD_HHMMSS.sql.gz
```

### Contacto de soporte:
- **Email:** soporte@gastosweb.com
- **WhatsApp:** +57 311 700 9855

---

## 📂 ARCHIVOS DISPONIBLES EN EL REPOSITORIO

```
gastos-familiares/
├── ACTUALIZACION_OVH.md          ← Guía detallada paso a paso
├── actualizar_ovh.sh              ← Script automatizado
├── VALIDACION_PRODUCCION.md       ← Validación completa
├── ACTUALIZACION_SEGURIDAD_CVEs.md ← Reporte de CVEs
├── RESUMEN_VALIDACION_COMPLETA.md ← Resumen ejecutivo
└── requirements-production.txt    ← Dependencias actualizadas
```

---

## ✨ RESUMEN

1. **Conectar a OVH vía SSH**
2. **Ejecutar:** `sudo bash actualizar_ovh.sh`
3. **Esperar:** 15-30 minutos
4. **Verificar:** https://gastosweb.com
5. **Monitorear:** Logs durante 1-2 horas

---

**¡Tu proyecto se actualizará a la versión 2.2.2 con todos los CVEs resueltos!**

🔒 Seguridad: ⭐⭐⭐⭐⭐ Certificado  
✅ Estado: Listo para actualizar  
📅 Fecha: 31 de Mayo 2026

