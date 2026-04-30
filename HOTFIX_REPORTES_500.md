# 🚨 HOTFIX INMEDIATO - Error 500 en Reportes

## ✅ Problema Resuelto

**Error encontrado:** La variable `familia` se usaba en el contexto de reportes sin haber sido definida

**Fix aplicado:**
1. ✅ Agregar obtención del objeto `Familia` con try/except
2. ✅ Corregir división Decimal/int en distribución equitativa
3. ✅ Código verificado sin errores
4. ✅ Cambios commiteados y pusheados a GitHub

---

## 🚀 Despliegue URGENTE en Producción

### Comandos Rápidos (Copiar y Pegar)

```bash
# 1. Conectar al servidor
ssh usuario@tu-servidor-ovh.com

# 2. Ir al directorio del proyecto
cd /var/www/html/FinanBot

# 3. Pull de cambios
git pull origin main

# 4. Activar entorno virtual (si aplica)
source venv/bin/activate

# 5. Verificar
python manage.py check

# 6. Recargar Gunicorn (SIN DOWNTIME)
sudo systemctl reload gunicorn

# 7. Verificar logs
sudo tail -20 /var/log/gunicorn/error.log

# 8. Test rápido
curl https://tu-dominio.com/reportes/
```

### Verificación Exitosa

```bash
# Deberías ver:
# System check identified no issues (0 silenced).

# Y al visitar /reportes/ debería cargar sin error 500
```

---

## 🔧 Cambios Aplicados

### Archivo: `gastos/views.py` - Función `reportes()`

#### ANTES (causaba error 500):
```python
def reportes(request):
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')
    
    # ...después usaba familia sin definirla
    context = {
        'familia': familia,  # ❌ ERROR: familia no está definida
    }
```

#### DESPUÉS (corregido):
```python
def reportes(request):
    familia_id = request.session.get('familia_id')
    if not familia_id:
        messages.warning(request, 'Debes seleccionar una familia primero.')
        return redirect('seleccionar_familia')

    # ✅ FIX: Obtener objeto familia
    try:
        familia = Familia.objects.get(id=familia_id)
    except Familia.DoesNotExist:
        messages.error(request, 'Familia no encontrada.')
        return redirect('seleccionar_familia')
    
    # ...resto del código
    context = {
        'familia': familia,  # ✅ Ahora familia está definida
    }
```

#### Fix División Decimal (ANTES):
```python
monto_por_aportante = gasto.monto / num_aportantes  # ❌ Decimal / int
```

#### Fix División Decimal (DESPUÉS):
```python
monto_por_aportante = gasto.monto / Decimal(str(num_aportantes))  # ✅
```

---

## ⏱️ Tiempo Estimado de Despliegue

**3-5 minutos total:**
- Git pull: 30 segundos
- Verificación: 30 segundos
- Reload gunicorn: 10 segundos
- Test: 1 minuto
- **Downtime: 0 segundos** (reload sin interrupciones)

---

## ✅ Checklist de Verificación Post-Despliegue

Después de ejecutar los comandos, verifica:

- [ ] `python manage.py check` sin errores
- [ ] Gunicorn recargado: `sudo systemctl status gunicorn` → active (running)
- [ ] Logs sin errores: `sudo tail -20 /var/log/gunicorn/error.log`
- [ ] URL `/reportes/` carga **SIN error 500**
- [ ] Tabla detallada de reportes visible
- [ ] Filtro por mes funciona
- [ ] Exportar a Excel funciona (si tienes plan premium)

---

## 🧪 Test Rápido en Producción

```bash
# Test 1: Verificar que reportes carga
curl -I https://tu-dominio.com/reportes/
# Debe devolver: HTTP/1.1 200 OK (no 500)

# Test 2: Ver logs en tiempo real mientras pruebas
sudo tail -f /var/log/gunicorn/error.log
# Abre /reportes/ en el navegador y mira que no haya errores
```

---

## 📊 Estado Actual

| Item | Estado |
|------|--------|
| Código corregido | ✅ Commit 48353f7 |
| Push a GitHub | ✅ Completado |
| Listo para despliegue | ✅ SÍ |
| Riesgo | 🟢 BAJO (solo fixes) |
| Requiere migraciones | ❌ NO |
| Requiere dependencies | ❌ NO |
| Downtime | ❌ 0 segundos |

---

## 🆘 Si Persiste el Error

Si después del despliegue aún hay error 500:

### 1. Ver logs completos:
```bash
sudo tail -100 /var/log/gunicorn/error.log
```

### 2. Buscar el error específico:
```bash
sudo grep -A 20 "Exception" /var/log/gunicorn/error.log | tail -50
```

### 3. Verificar que el pull se hizo:
```bash
cd /var/www/html/FinanBot
git log --oneline -n 5
# Deberías ver: 48353f7 Hotfix: Error 500 en reportes
```

### 4. Reinicio completo (si reload no funciona):
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 📞 Pasos Siguientes

### Después de desplegar:

1. **Probar inmediatamente:** Ir a `/reportes/` y verificar que funciona
2. **Verificar filtros:** Seleccionar diferentes meses
3. **Probar exportar Excel:** Si tienes plan premium
4. **Monitorear logs:** Durante 5-10 minutos después del despliegue

---

## 🎯 Causa Raíz del Error

**Error original:**
```python
NameError: name 'familia' is not defined
```

**¿Por qué sucedió?**
En la refactorización para agregar los filtros de reportes, se usó la variable `familia` en el contexto del template, pero nunca se obtuvo el objeto `Familia` de la base de datos. Solo se tenía `familia_id`.

**¿Por qué no falló en local?**
Probablemente falló en local también, pero no se probó la vista de reportes después del último cambio, o había un objeto `familia` en el contexto de otra manera.

---

## ✅ Confirmación de Fix

Estos cambios están ahora en GitHub:
- ✅ Commit: `48353f7`
- ✅ Mensaje: "Hotfix: Error 500 en reportes - agregar objeto familia y fix división Decimal"
- ✅ Branch: `main`
- ✅ Hora: 30/04/2026

**LISTO PARA DESPLEGAR** 🚀

---

## 💡 Tip para el Futuro

Siempre probar todas las URLs principales después de un cambio significativo:
```bash
# Test local antes de push
python manage.py runserver

# En el navegador:
# ✓ /dashboard/
# ✓ /gastos/
# ✓ /reportes/
# ✓ /conciliacion/
# ✓ /aportantes/
```

