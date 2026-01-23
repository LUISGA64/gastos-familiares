# 🔥 FIX CRÍTICO: Emails No Se Envían

## ❌ Problema Encontrado

Los emails se generaban correctamente pero **NO se enviaban**. Solo se mostraban en los logs porque Django estaba usando `console.EmailBackend` en lugar de `smtp.EmailBackend`.

## 🔍 Causa Raíz

En `settings.py` el `EMAIL_BACKEND` estaba **hardcodeado** como:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # ❌ HARDCODEADO
```

Esto ignoraba completamente la configuración de Gmail en el `.env`.

## ✅ Solución Aplicada

Cambié `settings.py` para que **lea las variables del .env**:

```python
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Gastos Familiares <gastos@familia.com>')
```

---

## 🚀 APLICAR EL FIX EN EL SERVIDOR (URGENTE)

Ejecuta estos comandos en tu VPS:

```bash
# 1. Conectar al servidor
ssh ubuntu@167.114.2.88

# 2. Ir al proyecto
cd /var/www/gastos-familiares

# 3. Descargar el fix
git pull origin main

# 4. Verificar que el .env tiene la configuración de Gmail
cat .env | grep EMAIL_

# Deberías ver algo como:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=tucorreo@gmail.com
# EMAIL_HOST_PASSWORD=abcdefghijklmnop
# DEFAULT_FROM_EMAIL=Gastos Familiares <tucorreo@gmail.com>

# 5. Reiniciar Gunicorn para aplicar cambios
sudo systemctl restart gunicorn

# 6. Verificar que se reinició correctamente
sudo systemctl status gunicorn

# 7. Probar envío de email
# Ir a: https://gastosweb.com/password-reset/
# Ingresar email registrado
# ¡Debería llegar a tu bandeja!
```

---

## 🧪 Verificar que el Fix Funciona

### Opción 1: Probar desde la Web

```bash
# En tu navegador:
https://gastosweb.com/password-reset/

# Ingresar: luisgalic64@gmail.com
# Hacer clic en "Enviar Enlace de Recuperación"
# Revisar bandeja de entrada (y spam)
```

### Opción 2: Probar desde el Shell

```bash
cd /var/www/gastos-familiares
source venv/bin/activate
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Verificar configuración cargada
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

# Enviar email de prueba
send_mail(
    subject='✅ TEST - Configuración Correcta',
    message='Este email confirma que la configuración de Gmail está funcionando.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['luisgalic64@gmail.com'],
    fail_silently=False,
)

print("✅ Email enviado. Revisa tu bandeja de entrada.")
```

---

## 📊 Antes vs Después

### ANTES (❌ NO FUNCIONABA):

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Hardcodeado
```

**Resultado:**
- Emails solo en logs
- Gmail ignorado
- Usuarios NO reciben emails

### DESPUÉS (✅ FUNCIONA):

```python
# settings.py
EMAIL_BACKEND = config('EMAIL_BACKEND', ...)  # Lee desde .env
```

**Resultado:**
- Emails enviados vía Gmail
- Configuración desde .env
- Usuarios SÍ reciben emails

---

## 🔍 Verificar Logs Después del Fix

```bash
# Ver logs en tiempo real
sudo journalctl -u gunicorn -f

# Buscar errores de email
sudo journalctl -u gunicorn -n 100 | grep -i email

# Ver logs de aplicación
tail -f /var/www/gastos-familiares/logs/application.log
```

---

## ✅ Lo Que Deberías Ver Ahora

### En los logs del servidor (journalctl):

**ANTES (Console Backend):**
```
Content-Type: text/plain; charset="utf-8"
From: gastos@familia.com
To: luisgalic64@gmail.com
...email completo en logs...
```

**DESPUÉS (SMTP Gmail):**
```
[INFO] Email de recuperación enviado a luisgalic64@gmail.com
```

### En la aplicación web:

**Mensaje:**
```
✅ Se ha enviado un enlace de recuperación a luisgalic64@gmail.com. 
Por favor, revisa tu correo.
```

### En tu bandeja de entrada:

**Email de:**
```
Gastos Familiares <tucorreo@gmail.com>
Asunto: Restablecer Contraseña - Gastos Familiares
```

---

## ⚠️ Si Todavía No Funciona

### 1. Verificar que el .env tiene EMAIL_BACKEND:

```bash
grep EMAIL_BACKEND /var/www/gastos-familiares/.env
```

**Debe decir:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

**NO debe decir:**
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 2. Verificar contraseña de Gmail:

La contraseña debe ser de **16 caracteres** (contraseña de aplicación), no tu contraseña normal.

```bash
grep EMAIL_HOST_PASSWORD /var/www/gastos-familiares/.env
```

Debe ser algo como: `abcdefghijklmnop` (sin espacios)

### 3. Ver errores específicos:

```bash
sudo journalctl -u gunicorn -n 100 --no-pager | grep -A 5 -i "smtp\|email\|error"
```

---

## 📋 Checklist de Verificación

Después de aplicar el fix:

- [ ] Git pull ejecutado
- [ ] Gunicorn reiniciado
- [ ] .env tiene EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
- [ ] .env tiene EMAIL_HOST_USER y EMAIL_HOST_PASSWORD
- [ ] Probar envío desde https://gastosweb.com/password-reset/
- [ ] Email recibido en bandeja de entrada
- [ ] ✅ TODO FUNCIONANDO

---

## 🎯 Resumen del Fix

| Aspecto | Antes | Después |
|---------|-------|---------|
| **EMAIL_BACKEND** | Hardcodeado en settings.py | Lee desde .env |
| **Configuración** | Ignoraba .env | Usa .env |
| **Emails** | Solo en logs | Enviados vía Gmail |
| **Estado** | ❌ Roto | ✅ Funcionando |

---

## 🚀 Comandos Rápidos

```bash
# Todo en uno:
ssh ubuntu@167.114.2.88
cd /var/www/gastos-familiares
git pull origin main
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

Luego probar en: https://gastosweb.com/password-reset/

---

**🔥 ESTE FIX ES CRÍTICO - APLÍCALO AHORA**

El sistema NO puede enviar emails hasta que se aplique este cambio en el servidor.

Commit: Subido a GitHub ✅
Servidor: Pendiente de aplicar ⏳

**Ejecuta los comandos de arriba para que los emails funcionen.** 📧
