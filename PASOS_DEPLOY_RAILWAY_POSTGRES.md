# 🚀 Guía Paso a Paso - Deploy en Railway con PostgreSQL

## ✅ CONFIGURACIÓN COMPLETADA
Tu proyecto ya está preparado para Railway con PostgreSQL:
- ✅ `requirements.txt` con psycopg2-binary
- ✅ `settings.py` configurado con dj-database-url
- ✅ `Procfile` con gunicorn
- ✅ `railway.json` con build y deploy commands
- ✅ WhiteNoise para archivos estáticos

---

## 📋 PASOS PARA EL DEPLOY

### 1️⃣ GENERAR SECRET_KEY NUEVA (OBLIGATORIO)
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**Guarda el resultado**, lo necesitarás en el paso 5.

---

### 2️⃣ PREPARAR REPOSITORIO GIT (si aún no lo has hecho)

```powershell
# Verificar si ya tienes git inicializado
git status

# Si no está inicializado, crear .gitignore primero
# Luego inicializar git
git init
git add .
git commit -m "Preparado para deploy en Railway con PostgreSQL"
```

---

### 3️⃣ SUBIR A GITHUB

**Si ya tienes un repositorio:**
```powershell
git add .
git commit -m "Configuración Railway PostgreSQL lista"
git push origin main
```

**Si es un repositorio nuevo:**
1. Ve a GitHub.com y crea un nuevo repositorio
2. NO agregues README, .gitignore ni LICENSE (ya los tienes)
3. Copia la URL del repositorio
4. Ejecuta:
```powershell
git remote add origin https://github.com/TU_USUARIO/gastos-familiares.git
git branch -M main
git push -u origin main
```

---

### 4️⃣ CREAR PROYECTO EN RAILWAY

1. Ve a https://railway.app/
2. Haz clic en **"Login"** y conecta con GitHub
3. Clic en **"New Project"**
4. Selecciona **"Deploy from GitHub repo"**
5. Busca y selecciona tu repositorio `gastos-familiares`
6. Railway comenzará el primer build (fallará porque faltan variables)

---

### 5️⃣ AGREGAR BASE DE DATOS POSTGRESQL

1. En tu proyecto de Railway, clic en **"+ New"** (arriba a la derecha)
2. Selecciona **"Database"**
3. Selecciona **"Add PostgreSQL"**
4. Espera 30-60 segundos mientras se provisiona
5. ✅ Railway automáticamente creará la variable `DATABASE_URL` en tu servicio Django

---

### 6️⃣ CONFIGURAR VARIABLES DE ENTORNO

1. Clic en tu servicio **Django** (no en PostgreSQL)
2. Ve a la pestaña **"Variables"**
3. Clic en **"New Variable"** y agrega las siguientes:

```
SECRET_KEY=la-secret-key-que-generaste-en-paso-1
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
AI_PROVIDER=groq
GROQ_API_KEY=tu-groq-api-key-de-console.groq.com
```

**Notas:**
- `DATABASE_URL` ya está configurada automáticamente por Railway
- `PORT` también la configura Railway automáticamente
- Reemplaza el valor de `GROQ_API_KEY` con tu clave real de https://console.groq.com/

4. Después de agregar las variables, Railway **redesplegará automáticamente**

---

### 7️⃣ MONITOREAR EL DEPLOY

1. Ve a la pestaña **"Deployments"**
2. Verás el progreso:
   - 🔨 **Building**: Instalando dependencias
   - 📦 **collectstatic**: Recopilando archivos estáticos
   - 🗄️ **migrate**: Creando tablas en PostgreSQL
   - 🚀 **Starting**: Iniciando gunicorn
3. Espera 3-5 minutos
4. Si todo va bien, verás **"SUCCESS"** en verde ✅

---

### 8️⃣ GENERAR DOMINIO PÚBLICO

1. En tu servicio Django > **"Settings"**
2. Baja hasta **"Networking"** > **"Public Networking"**
3. Clic en **"Generate Domain"**
4. Railway te dará un dominio como:
   ```
   gastos-familiares-production.up.railway.app
   ```
5. ✅ Copia esta URL

---

### 9️⃣ CREAR SUPERUSUARIO

1. Ve a tu servicio Django > **"Settings"**
2. Baja hasta **"Service"**
3. Junto a "Deploy Logs", clic en **"..."** > **"Create Shell"**
4. En la terminal que se abre, ejecuta:
```bash
python manage.py createsuperuser
```
5. Ingresa:
   - Username: `admin`
   - Email: `admin@gastos.com` (o el que prefieras)
   - Password: (tu contraseña segura)
   - Confirmar password

---

### 🔟 VERIFICAR QUE TODO FUNCIONA

Visita tu dominio de Railway:
```
https://tu-dominio.up.railway.app
```

**Verifica:**
- ✅ La página de login carga correctamente
- ✅ Los estilos CSS se ven bien
- ✅ Puedes registrar un usuario nuevo
- ✅ Puedes iniciar sesión
- ✅ El admin funciona: `/admin/`
- ✅ Dashboard funciona

---

## 🎉 DEPLOY AUTOMÁTICO ACTIVADO

Ahora cada vez que hagas:
```powershell
git add .
git commit -m "Mi cambio"
git push
```

Railway **automáticamente**:
1. Detecta el push
2. Hace build
3. Ejecuta collectstatic y migrate
4. Despliega la nueva versión

---

## 🔍 VERIFICAR BASE DE DATOS POSTGRESQL

Si quieres ver tu base de datos:

1. Clic en el servicio **PostgreSQL** (no Django)
2. Ve a **"Variables"**
3. Copia el valor de `DATABASE_URL`
4. Úsalo con una herramienta como:
   - **pgAdmin** (desktop)
   - **TablePlus** (desktop)
   - **psql** (CLI)

**Formato de DATABASE_URL:**
```
postgresql://postgres:contraseña@host.railway.app:puerto/railway
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Bad Request (400)"
**Causa:** ALLOWED_HOSTS no incluye tu dominio Railway

**Solución:**
1. Ve a Variables
2. Actualiza `ALLOWED_HOSTS` con tu dominio real:
```
ALLOWED_HOSTS=tu-dominio.up.railway.app,*.railway.app
```

---

### ❌ Error: "Static files not found"
**Causa:** collectstatic no se ejecutó correctamente

**Solución:**
1. Abre Shell en Railway
2. Ejecuta:
```bash
python manage.py collectstatic --noinput
```

---

### ❌ Error: "Module not found"
**Causa:** Falta una dependencia en requirements.txt

**Solución:**
```powershell
# En local:
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Fix dependencies"
git push
```

---

### ❌ Error: "relation does not exist"
**Causa:** Las tablas no se crearon en PostgreSQL

**Solución:**
1. Abre Shell en Railway
2. Ejecuta:
```bash
python manage.py migrate
```

---

### 🔍 Ver logs detallados

1. Ve a **"Deployments"**
2. Clic en el deploy activo
3. Verás todos los logs
4. Los errores aparecen en **rojo**
5. Los warnings en **amarillo**
6. Los éxitos en **verde**

---

## 📊 VENTAJAS DE POSTGRESQL vs SQLite

✅ **Mejor rendimiento** con múltiples usuarios concurrentes
✅ **Más robusto** para producción
✅ **Backups automáticos** por Railway
✅ **Escalable** a millones de registros
✅ **Tipos de datos avanzados**
✅ **Transacciones ACID** completas

---

## 🎯 COMANDOS ÚTILES EN RAILWAY SHELL

```bash
# Ver migraciones pendientes
python manage.py showmigrations

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estructura de base de datos
python manage.py dbshell

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py createsuperuser

# Verificar configuración
python manage.py check

# Shell interactivo de Django
python manage.py shell
```

---

## 📞 RECURSOS

- **Railway Docs:** https://docs.railway.app/
- **Railway PostgreSQL:** https://docs.railway.app/databases/postgresql
- **Django + PostgreSQL:** https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes
- **Soporte Railway:** https://help.railway.app/

---

## ✅ CHECKLIST FINAL

Antes de considerar el deploy exitoso, verifica:

- [ ] Dominio Railway generado y funcional
- [ ] Login/Registro funcionan
- [ ] Superusuario creado
- [ ] Admin panel accesible (`/admin/`)
- [ ] Dashboard carga sin errores
- [ ] Estilos CSS se ven correctamente
- [ ] Puedes crear gastos
- [ ] Puedes crear familias
- [ ] PostgreSQL conectado (verifica en Railway > PostgreSQL > Metrics)
- [ ] Variables de entorno configuradas
- [ ] GROQ_API_KEY funciona (prueba el chatbot)

---

## 🎊 ¡FELICITACIONES!

Tu aplicación de Gastos Familiares está ahora en producción con PostgreSQL.

**Próximos pasos recomendados:**
1. Configurar un dominio personalizado (opcional)
2. Configurar email SMTP para notificaciones
3. Configurar backups automáticos adicionales
4. Monitorear uso de recursos en Railway

---

**¿Necesitas ayuda?** Revisa los logs en Railway o contacta soporte.

