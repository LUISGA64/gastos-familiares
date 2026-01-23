# 📧 Opciones para Envío de Correos Electrónicos

## 🆓 Opciones GRATUITAS Disponibles

### 1. **Gmail (RECOMENDADO - 100% Gratis)** ⭐

**Ventajas:**
- ✅ Completamente gratis
- ✅ 500 emails/día (más que suficiente)
- ✅ Confiable y rápido
- ✅ Fácil de configurar

**Desventajas:**
- ⚠️ Requiere habilitar "Contraseñas de aplicación"

#### Configuración Paso a Paso:

**A. Habilitar verificación en 2 pasos:**
1. Ir a: https://myaccount.google.com/security
2. Buscar "Verificación en 2 pasos"
3. Activarla (necesaria para contraseñas de app)

**B. Crear contraseña de aplicación:**
1. Ir a: https://myaccount.google.com/apppasswords
2. Seleccionar "Correo" y "Otro dispositivo"
3. Nombrar: "Gastos Familiares"
4. Copiar la contraseña de 16 caracteres

**C. Configurar en `.env`:**
```env
# Email con Gmail (GRATIS)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucorreo@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # Contraseña de app (16 caracteres)
DEFAULT_FROM_EMAIL=Gastos Familiares <tucorreo@gmail.com>
```

---

### 2. **Outlook/Hotmail (Gratis)** 📨

**Ventajas:**
- ✅ Gratis
- ✅ 300 emails/día
- ✅ No requiere contraseña de app

**Configuración en `.env`:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucorreo@outlook.com
EMAIL_HOST_PASSWORD=tu_contraseña_normal
DEFAULT_FROM_EMAIL=Gastos Familiares <tucorreo@outlook.com>
```

---

### 3. **SendGrid (Plan Gratuito)** 📬

**Ventajas:**
- ✅ 100 emails/día gratis
- ✅ API profesional
- ✅ Estadísticas incluidas

**Configuración:**
1. Registrarse en: https://sendgrid.com (Plan Free)
2. Crear API Key
3. Configurar en `.env`:

```env
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=tu-api-key-aqui
DEFAULT_FROM_EMAIL=tucorreo@tudominio.com
```

4. Instalar: `pip install sendgrid-django`

---

### 4. **Mailgun (Plan Sandbox - Gratis)** 📮

**Ventajas:**
- ✅ 100 emails/día gratis
- ✅ API robusta
- ✅ Para emails transaccionales

**Configuración:**
1. Registrarse en: https://www.mailgun.com
2. Obtener API key del dashboard
3. Configurar en `.env`:

```env
EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
MAILGUN_API_KEY=tu-api-key-aqui
MAILGUN_SENDER_DOMAIN=sandboxXXX.mailgun.org
DEFAULT_FROM_EMAIL=tucorreo@sandboxXXX.mailgun.org
```

4. Instalar: `pip install django-anymail`

---

## 🚫 Opción SIN Email (Token en Base de Datos)

**Si prefieres NO usar email**, el sistema ahora incluye una alternativa:

### Funcionalidad Implementada:

1. **Usuario solicita reset** → Se genera token en BD
2. **Sistema muestra el token en pantalla** (solo en DEBUG=True)
3. **Usuario accede directamente con el token**
4. **Token expira después de uso**

### URL directa para reset:
```
https://gastosweb.com/password-reset-token/<token>/
```

**Ventajas:**
- ✅ No requiere configuración de email
- ✅ Funciona inmediatamente
- ✅ Ideal para desarrollo/pruebas

**Desventajas:**
- ⚠️ Menos seguro (el token se muestra en pantalla)
- ⚠️ No es profesional para producción

---

## 📊 Comparación de Opciones

| Servicio | Emails/día | Costo | Dificultad | Recomendado |
|----------|-----------|-------|------------|-------------|
| **Gmail** | 500 | Gratis | Fácil | ⭐⭐⭐⭐⭐ |
| **Outlook** | 300 | Gratis | Muy Fácil | ⭐⭐⭐⭐ |
| **SendGrid** | 100 | Gratis | Media | ⭐⭐⭐ |
| **Mailgun** | 100 | Gratis | Media | ⭐⭐⭐ |
| **Sin Email** | N/A | Gratis | Muy Fácil | ⭐⭐ (solo dev) |

---

## 🎯 Recomendación Final

### Para Producción:
**Usar Gmail** con contraseña de aplicación:
- ✅ Más fácil de configurar
- ✅ Más emails permitidos (500/día)
- ✅ Más confiable
- ✅ 100% gratis

### Para Desarrollo Local:
**Usar Console Backend** (ya configurado):
- ✅ Los emails se muestran en la terminal
- ✅ No requiere configuración
- ✅ Perfecto para testing

---

## 🔧 Configuración Actual del Proyecto

El proyecto ya está configurado para usar el **Console Backend** en desarrollo:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Cómo funciona:**
1. Usuario solicita reset de contraseña
2. El enlace se muestra en la **terminal del servidor**
3. Copias el enlace y lo pegas en el navegador
4. ¡Funciona sin configurar nada!

---

## ✅ Próximos Pasos

### Opción 1: Usar Gmail (Recomendado para producción)
1. Crear cuenta Gmail (o usar una existente)
2. Habilitar verificación en 2 pasos
3. Crear contraseña de aplicación
4. Actualizar archivo `.env` en el servidor
5. Reiniciar gunicorn

### Opción 2: Continuar sin email (Solo desarrollo)
- Ya está funcionando
- El enlace aparece en los mensajes del sistema
- Ideal para pruebas locales

---

## 📝 Archivo de Configuración de Ejemplo

Crear archivo `.env.example` con:

```env
# ============================================
# CONFIGURACIÓN DE EMAIL
# ============================================

# OPCIÓN 1: Gmail (Recomendado)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tucorreo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app-16-caracteres
DEFAULT_FROM_EMAIL=Gastos Familiares <tucorreo@gmail.com>

# OPCIÓN 2: Outlook
# EMAIL_HOST=smtp.office365.com
# EMAIL_HOST_USER=tucorreo@outlook.com
# EMAIL_HOST_PASSWORD=tu-contraseña

# OPCIÓN 3: Desarrollo (consola)
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

**💡 Consejo:** Usa Gmail con contraseña de aplicación. Es la opción más fácil, confiable y completamente gratis para proyectos pequeños y medianos.
