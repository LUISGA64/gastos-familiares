# 📧 Guía Paso a Paso: Configurar Gmail GRATIS

## 🎯 Objetivo

Configurar Gmail para enviar emails de recuperación de contraseña **sin costo alguno**.

---

## 📋 Requisitos

- ✅ Cuenta de Gmail (crear una si no tienes)
- ✅ 10 minutos de tu tiempo
- ✅ Acceso al servidor VPS (para editar `.env`)

---

## 🔧 Paso 1: Habilitar Verificación en 2 Pasos

### A. Acceder a la configuración de Google

1. **Ir a:** https://myaccount.google.com/security

2. **Buscar:** "Verificación en 2 pasos"

3. **Hacer clic en:** "Verificación en 2 pasos"

4. **Iniciar sesión** con tu cuenta de Gmail

5. **Seguir el asistente:**
   - Ingresar número de teléfono
   - Recibir código de verificación
   - Confirmar el código
   - Activar la verificación en 2 pasos

> **Nota:** Esto es OBLIGATORIO para poder crear contraseñas de aplicación.

---

## 🔑 Paso 2: Crear Contraseña de Aplicación

### B. Generar la contraseña especial

1. **Ir a:** https://myaccount.google.com/apppasswords

   O desde "Seguridad" → "Contraseñas de aplicaciones"

2. **Seleccionar:**
   - **Aplicación:** "Correo"
   - **Dispositivo:** "Otro (nombre personalizado)"

3. **Nombre:** Escribir "Gastos Familiares"

4. **Hacer clic en:** "Generar"

5. **Copiar la contraseña de 16 caracteres** que aparece en pantalla

   Ejemplo: `abcd efgh ijkl mnop`

> **⚠️ IMPORTANTE:** Esta contraseña solo se muestra UNA VEZ. Cópiala ahora.

---

## 💾 Paso 3: Configurar en el Servidor

### C. Editar archivo .env en el VPS

```bash
# Conectar al servidor
ssh ubuntu@167.114.2.88

# Ir al directorio del proyecto
cd /var/www/gastos-familiares

# Editar archivo .env
nano .env
```

### D. Agregar configuración de email

```env
# ============================================
# CONFIGURACIÓN DE EMAIL CON GMAIL
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucorreo@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=Gastos Familiares <tucorreo@gmail.com>
```

**Reemplazar:**
- `tucorreo@gmail.com` → Tu email real
- `abcd efgh ijkl mnop` → La contraseña de 16 caracteres que copiaste

### E. Guardar cambios

```bash
# Guardar en nano
Ctrl + O  (Enter para confirmar)
Ctrl + X  (Salir)
```

---

## 🔄 Paso 4: Reiniciar Servicios

### F. Aplicar cambios

```bash
# Reiniciar Gunicorn
sudo systemctl restart gunicorn

# Verificar que esté corriendo
sudo systemctl status gunicorn

# (Presionar Q para salir)
```

---

## 🧪 Paso 5: Probar el Envío

### G. Probar desde la aplicación

1. **Ir a:** https://gastosweb.com/login/

2. **Hacer clic en:** "¿Olvidaste tu contraseña?"

3. **Ingresar un email registrado**

4. **Hacer clic en:** "Enviar Enlace de Recuperación"

5. **Revisar tu bandeja de entrada:**
   - Debería llegar en segundos
   - Si no aparece, revisar "Spam"

### H. Si hay problemas

**Ver logs del servidor:**
```bash
sudo journalctl -u gunicorn -n 50 --no-pager
```

**Buscar errores de email:**
```bash
cd /var/www/gastos-familiares
tail -f logs/application.log
```

---

## 🔍 Solución de Problemas

### Error: "SMTPAuthenticationError"

**Causa:** Contraseña incorrecta

**Solución:**
1. Verificar que copiaste correctamente la contraseña de app
2. Asegurarte de usar la contraseña de APP (16 caracteres), no la de tu cuenta
3. Generar una nueva contraseña de app si es necesario

---

### Error: "Permission denied"

**Causa:** No tienes permisos para editar .env

**Solución:**
```bash
# Cambiar propietario del archivo
sudo chown ubuntu:ubuntu /var/www/gastos-familiares/.env

# Intentar de nuevo
nano .env
```

---

### Email no llega

**Verificar:**
1. ✅ Email del usuario está correcto en la BD
2. ✅ Email de Gmail configurado correctamente
3. ✅ Revisar carpeta de Spam
4. ✅ Ver logs para errores

**Comando para ver logs:**
```bash
tail -f /var/www/gastos-familiares/logs/application.log | grep -i email
```

---

### "Cuenta menos segura"

**Si Gmail bloquea:**
1. Verificar que usas contraseña de APP (no la de cuenta)
2. Asegurarte que la verificación en 2 pasos está activa
3. Ir a: https://myaccount.google.com/lesssecureapps
4. Activar "Acceso de aplicaciones menos seguras" (si aparece)

---

## 📊 Límites de Gmail

| Concepto | Límite |
|----------|--------|
| Emails por día | 500 |
| Emails por minuto | ~20 |
| Destinatarios por email | 500 |
| Costo | **GRATIS** |

> **Nota:** 500 emails/día es más que suficiente para un proyecto pequeño/mediano

---

## ✅ Verificación Final

### Checklist:

- [ ] Verificación en 2 pasos activada
- [ ] Contraseña de aplicación creada
- [ ] Archivo `.env` editado correctamente
- [ ] Gunicorn reiniciado
- [ ] Email de prueba enviado exitosamente
- [ ] Email recibido en bandeja de entrada

---

## 🎉 ¡Listo!

Ahora tu aplicación puede enviar emails de forma profesional y gratuita usando Gmail.

### Próximos pasos:

1. Probar recuperación de contraseña
2. Verificar que los emails lleguen
3. Personalizar el mensaje si es necesario
4. Monitorear logs por si hay errores

---

## 📞 Soporte

**Si tienes problemas:**
1. Revisar logs: `tail -f logs/application.log`
2. Verificar configuración de Gmail
3. Asegurarte que reiniciaste gunicorn
4. Revisar que el .env no tenga espacios extras

**Archivo de ejemplo completo:**

```env
# .env
DEBUG=False
SECRET_KEY=tu-secret-key-aqui
ALLOWED_HOSTS=gastosweb.com,www.gastosweb.com,167.114.2.88
DATABASE_URL=postgresql://postgres:password@localhost:5432/gastos_familiares

# Email con Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=micorreo@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=Gastos Familiares <micorreo@gmail.com>

# IA
AI_PROVIDER=groq
GROQ_API_KEY=tu-groq-key
```

---

**¡Configuración completada!** 🎊

Tu aplicación ahora puede enviar emails de recuperación de contraseña usando Gmail de forma gratuita y profesional.
