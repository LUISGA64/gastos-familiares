# 🚀 Guía de Despliegue en Railway - Paso a Paso

## 📋 Requisitos Previos

1. ✅ Cuenta en GitHub
2. ✅ Cuenta en Railway (https://railway.app/)
3. ✅ Repositorio Git inicializado en tu proyecto
4. ✅ API Key de Groq (opcional, pero recomendado)

---

## 🔧 PASO 1: Preparar el Proyecto (YA ESTÁ LISTO ✅)

Los siguientes archivos ya han sido creados:

- ✅ `Procfile` - Comando para ejecutar Gunicorn
- ✅ `runtime.txt` - Versión de Python
- ✅ `railway.json` - Configuración específica de Railway
- ✅ `nixpacks.toml` - Build config
- ✅ `requirements.txt` - Actualizado con gunicorn, whitenoise, psycopg2
- ✅ `settings.py` - Configurado para producción
- ✅ `.env.example` - Ejemplo de variables de entorno
- ✅ `.gitignore` - Para no subir archivos sensibles

---

## 🌐 PASO 2: Subir a GitHub

### 2.1 Inicializar Git (si no lo has hecho)
```bash
git init
```

### 2.2 Agregar archivos al repositorio
```bash
git add .
git commit -m "Preparado para deploy en Railway"
```

### 2.3 Crear repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre: `gastos-familiares`
3. Descripción: `Sistema de gestión de gastos familiares`
4. Público o Privado (recomiendo privado)
5. NO inicialices con README (ya tienes uno)
6. Click en "Create repository"

### 2.4 Conectar y subir
```bash
git remote add origin https://github.com/TU_USUARIO/gastos-familiares.git
git branch -M main
git push -u origin main
```

---

## 🚂 PASO 3: Crear Proyecto en Railway

### 3.1 Registrarse/Iniciar sesión
1. Ve a https://railway.app/
2. Click en "Login" o "Start a New Project"
3. Conéctate con GitHub
4. Autoriza Railway a acceder a tus repositorios

### 3.2 Crear nuevo proyecto
1. Click en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca y selecciona `gastos-familiares`
4. Click en el repositorio

### 3.3 Railway detectará automáticamente
- ✅ Que es un proyecto Django
- ✅ El archivo `railway.json`
- ✅ El archivo `nixpacks.toml`
- ✅ Las dependencias de `requirements.txt`

---

## 🗄️ PASO 4: Agregar Base de Datos PostgreSQL

### 4.1 En tu proyecto de Railway
1. Click en "+ New"
2. Selecciona "Database"
3. Selecciona "Add PostgreSQL"
4. Espera a que se provisione (30-60 segundos)

### 4.2 Conectar la base de datos
Railway automáticamente creará la variable `DATABASE_URL` y la conectará a tu aplicación Django. ✅

---

## ⚙️ PASO 5: Configurar Variables de Entorno

### 5.1 Click en tu servicio Django (no en la BD)
1. Ve a la pestaña "Variables"
2. Click en "New Variable"

### 5.2 Agregar las siguientes variables:

#### Variables OBLIGATORIAS:

**SECRET_KEY**
```
tu-secret-key-super-segura-cambiar-esto-por-algo-aleatorio
```
💡 Genera una segura en: https://djecrety.ir/

**DEBUG**
```
False
```

**ALLOWED_HOSTS**
```
*.railway.app
```

**AI_PROVIDER**
```
groq
```

**GROQ_API_KEY**
```
tu-groq-api-key-aqui
```
💡 Obtén tu API key en: https://console.groq.com/

#### Variables OPCIONALES:

**OPENAI_API_KEY** (solo si usarás OpenAI)
```
sk-proj-tu-openai-key
```

### 5.3 Railway ya configuró automáticamente:
- ✅ `DATABASE_URL` - Conexión a PostgreSQL
- ✅ `PORT` - Puerto del servidor
- ✅ `RAILWAY_ENVIRONMENT` - Identificador de ambiente

---

## 🏗️ PASO 6: Deploy Automático

### 6.1 Railway iniciará el build automáticamente
Verás en los logs:
```
✅ Installing dependencies...
✅ pip install -r requirements.txt
✅ Collecting static files...
✅ python manage.py collectstatic --noinput
✅ Running migrations...
✅ python manage.py migrate --noinput
✅ Starting server...
✅ gunicorn DjangoProject.wsgi:application
```

### 6.2 Espera a que termine (2-5 minutos)
- Si todo sale bien, verás "Deployed" ✅
- Si hay errores, revisa los logs en "Deployments"

---

## 👨‍💼 PASO 7: Crear Superusuario

### 7.1 Ejecutar comando en Railway
1. Ve a tu servicio Django
2. Click en la pestaña "Settings"
3. Baja hasta "Service Variables"
4. Click en "Deploy Logs"
5. Click en los 3 puntos "..." 
6. Selecciona "Create Shell"

### 7.2 En la terminal que se abre:
```bash
python manage.py createsuperuser
```

Ingresa:
- Username: `admin`
- Email: `tu_email@gmail.com`
- Password: `tuPasswordSeguro123`

---

## 🌐 PASO 8: Obtener tu URL

### 8.1 Obtener dominio de Railway
1. En tu servicio Django, pestaña "Settings"
2. Sección "Domains"
3. Click en "Generate Domain"
4. Railway te dará algo como: `gastos-familiares-production.up.railway.app`

### 8.2 Actualizar ALLOWED_HOSTS (si es necesario)
Si tu dominio NO termina en `.railway.app`:
1. Ve a "Variables"
2. Edita `ALLOWED_HOSTS`
3. Agrega tu dominio: `tu-dominio.railway.app,*.railway.app`

---

## ✅ PASO 9: Verificar Deploy

### 9.1 Abre tu aplicación
Visita: `https://tu-app.railway.app`

### 9.2 Verifica que funcionen:
- ✅ Página de login carga
- ✅ Puedes registrarte
- ✅ El admin funciona: `/admin/`
- ✅ Los estilos se ven bien (archivos estáticos)
- ✅ Puedes subir imágenes (media files)
- ✅ El chatbot responde (si configuraste Groq)

---

## 🎯 PASO 10: Datos Iniciales (Opcional)

### 10.1 Crear logros, categorías, etc.
Desde el shell de Railway:
```bash
python manage.py shell

# Dentro del shell de Python:
from gastos.management.commands.crear_logros_iniciales import Command as LogrosCommand
LogrosCommand().handle()

# O ejecuta tus scripts de datos de prueba
exec(open('crear_datos_ejemplo.py').read())
```

### 10.2 O desde tu admin:
1. Ve a `https://tu-app.railway.app/admin/`
2. Crea manualmente categorías, familias, etc.

---

## 🔄 PASO 11: Configurar Deploy Automático

### 11.1 Railway ya tiene deploy automático activado ✅
Cada vez que hagas `git push` a tu rama `main`:
1. Railway detectará el cambio
2. Ejecutará build automáticamente
3. Desplegará la nueva versión
4. Sin downtime (Zero-downtime deploy)

### 11.2 Para hacer cambios:
```bash
# Haces tus cambios en archivos
git add .
git commit -m "Descripción de cambios"
git push
```

Railway automáticamente desplegará en 2-3 minutos.

---

## 🐛 Solución de Problemas Comunes

### Error: "Module not found"
**Solución**: Asegúrate de que la dependencia esté en `requirements.txt`
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Actualizar dependencias"
git push
```

### Error: "Static files not found"
**Solución**: Verifica que se ejecutó `collectstatic`
```bash
# En shell de Railway:
python manage.py collectstatic --noinput
```

### Error: "Database connection failed"
**Solución**: Verifica que PostgreSQL esté conectado
1. Ve a tu base de datos PostgreSQL en Railway
2. Copia el valor de `DATABASE_URL`
3. Verifica que esté en las variables de tu servicio Django

### Error: "Bad Request (400)"
**Solución**: Actualiza `ALLOWED_HOSTS`
1. Ve a Variables
2. Agrega tu dominio real a `ALLOWED_HOSTS`

### Logs no muestran errores
**Solución**: Activa DEBUG temporalmente
1. Cambia `DEBUG=True` en variables
2. Ve los errores detallados
3. ❌ NO olvides volver a `DEBUG=False` después

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real:
1. Ve a tu servicio en Railway
2. Pestaña "Deployments"
3. Click en el deploy activo
4. Los logs se actualizan en vivo

### Métricas:
- CPU usage
- Memory usage
- Network traffic
- Build time

---

## 💰 Costos de Railway

### Plan Gratuito:
- ✅ $5 USD de crédito gratis/mes
- ✅ Suficiente para:
  - 1 app Django pequeña
  - 1 base de datos PostgreSQL
  - ~500 horas de ejecución
- ❌ Se duerme después de inactividad

### Plan Pro ($20/mes):
- ✅ Sin límite de horas
- ✅ Sin sleep
- ✅ Mejor performance
- ✅ Custom domains

---

## 🎉 ¡Listo!

Tu aplicación ya está en producción en:
**https://tu-app.railway.app** 🚀

### Siguiente pasos recomendados:
1. 📧 Configurar email SMTP real (Gmail, SendGrid)
2. 🌐 Agregar dominio personalizado (opcional)
3. 📈 Configurar monitoreo (Sentry, LogRocket)
4. 🔒 Configurar SSL/HTTPS (Railway lo hace automático)
5. 💾 Configurar backups de BD
6. 📱 Probar la PWA en móvil

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Railway
2. Verifica las variables de entorno
3. Consulta la documentación: https://docs.railway.app/
4. Contacta: soporte@gastosfamiliares.com

---

**¡Felicidades por tu deploy! 🎊**

*Guía creada para Gestor de Gastos Familiares - 2026*
