# 🚀 DEPLOY RÁPIDO - Railway con PostgreSQL

## ✅ TU SECRET_KEY GENERADA
```
p5p-*+zovjzo@hnv(7lrh45v-l9*&&6i%th#mow#a19s(e+i0j
```
**⚠️ IMPORTANTE:** Guarda esta clave, la necesitarás en Railway.

---

## 📋 PASOS RÁPIDOS (15 minutos)

### 1️⃣ SUBIR A GITHUB
```powershell
git init
git add .
git commit -m "Deploy Railway con PostgreSQL"
git remote add origin https://github.com/TU_USUARIO/gastos-familiares.git
git branch -M main
git push -u origin main
```

### 2️⃣ CREAR PROYECTO EN RAILWAY
1. Ve a https://railway.app/
2. Login con GitHub
3. **"New Project"** > **"Deploy from GitHub repo"**
4. Selecciona `gastos-familiares`

### 3️⃣ AGREGAR POSTGRESQL
1. En tu proyecto: **"+ New"** > **"Database"** > **"Add PostgreSQL"**
2. Espera 1 minuto ✅

### 4️⃣ CONFIGURAR VARIABLES
En tu servicio Django > **"Variables"** > **"New Variable"**:

```
SECRET_KEY=p5p-*+zovjzo@hnv(7lrh45v-l9*&&6i%th#mow#a19s(e+i0j
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
AI_PROVIDER=groq
GROQ_API_KEY=tu-groq-api-key-aqui
```

**Notas:**
- Reemplaza `GROQ_API_KEY` con tu clave de https://console.groq.com/
- `DATABASE_URL` la agrega Railway automáticamente

### 5️⃣ ESPERAR DEPLOY (3-5 min)
Railway hará automáticamente:
- ✅ Instalar dependencias
- ✅ collectstatic
- ✅ migrate (crear tablas en PostgreSQL)
- ✅ Iniciar gunicorn

### 6️⃣ GENERAR DOMINIO
1. Django service > **"Settings"** > **"Networking"**
2. **"Generate Domain"**
3. Obtendrás: `tu-app.up.railway.app`

### 7️⃣ CREAR SUPERUSUARIO
1. Django service > **"Settings"** > **"..."** > **"Create Shell"**
2. Ejecutar:
```bash
python manage.py createsuperuser
```

### 8️⃣ ¡LISTO! 🎉
Visita: `https://tu-app.up.railway.app`

---

## 🔧 COMANDOS ÚTILES

### Ver logs
Railway > Deployments > Click en deploy activo

### Redeploy manual
Railway > Deployments > **"Redeploy"**

### Acceder a shell
Settings > **"..."** > **"Create Shell"**

### Siguiente deploy automático
```powershell
git add .
git commit -m "Mi cambio"
git push
```

---

## ✅ VERIFICACIÓN

- [ ] Login funciona
- [ ] Admin funciona: `/admin/`
- [ ] Dashboard funciona
- [ ] CSS se ve correctamente
- [ ] PostgreSQL conectado

---

## 🆘 PROBLEMAS COMUNES

### Error 400 (Bad Request)
**Solución:** Actualiza ALLOWED_HOSTS con tu dominio real de Railway

### Static files no cargan
**Solución:** En Shell ejecutar:
```bash
python manage.py collectstatic --noinput
```

### Error de base de datos
**Solución:** En Shell ejecutar:
```bash
python manage.py migrate
```

---

## 📚 DOCUMENTACIÓN COMPLETA
Ver archivo: **PASOS_DEPLOY_RAILWAY_POSTGRES.md**

---

**¡Tu app está lista para producción con PostgreSQL! 🎊**
