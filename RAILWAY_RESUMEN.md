# 🚀 RESUMEN RÁPIDO - Deploy en Railway

## ✅ ARCHIVOS CREADOS
- ✅ Procfile
- ✅ runtime.txt
- ✅ railway.json
- ✅ nixpacks.toml
- ✅ .env.example
- ✅ DEPLOY_RAILWAY.md (guía completa)
- ✅ RAILWAY_COMANDOS.txt (comandos útiles)

## ✅ CONFIGURACIONES ACTUALIZADAS
- ✅ requirements.txt (agregado: gunicorn, whitenoise, dj-database-url, psycopg2-binary)
- ✅ settings.py (configurado para producción con PostgreSQL)
- ✅ WhiteNoise middleware agregado
- ✅ Variables de entorno configuradas

## 📝 PASOS SIGUIENTES (EN ORDEN)

### 1️⃣ GENERAR SECRET_KEY SEGURO
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copia el resultado, lo necesitarás en Railway.

### 2️⃣ SUBIR A GITHUB
```bash
git init
git add .
git commit -m "Preparado para deploy en Railway"
git remote add origin https://github.com/TU_USUARIO/gastos-familiares.git
git branch -M main
git push -u origin main
```

### 3️⃣ CREAR PROYECTO EN RAILWAY
1. Ve a https://railway.app/
2. Login con GitHub
3. "New Project" > "Deploy from GitHub repo"
4. Selecciona tu repositorio

### 4️⃣ AGREGAR POSTGRESQL
1. En tu proyecto: "+ New" > "Database" > "Add PostgreSQL"
2. Espera 1 minuto a que se provisione

### 5️⃣ CONFIGURAR VARIABLES EN RAILWAY
Ve a tu servicio Django > Variables > New Variable:

**OBLIGATORIAS:**
```
SECRET_KEY=la-que-generaste-en-paso-1
DEBUG=False
ALLOWED_HOSTS=*.railway.app
AI_PROVIDER=groq
GROQ_API_KEY=tu-groq-api-key-de-console.groq.com
```

**Railway agrega automáticamente:**
- DATABASE_URL (conexión a PostgreSQL)
- PORT (puerto del servidor)

### 6️⃣ ESPERAR EL DEPLOY (2-5 min)
Railway hará automáticamente:
- ✅ Install dependencies
- ✅ collectstatic
- ✅ migrate
- ✅ start gunicorn

### 7️⃣ GENERAR DOMINIO
1. Tu servicio Django > Settings > Domains
2. "Generate Domain"
3. Obtendrás: `tu-app-production.up.railway.app`

### 8️⃣ CREAR SUPERUSUARIO
1. Tu servicio > Settings > Deploy Logs > ... > Create Shell
2. Ejecutar:
```bash
python manage.py createsuperuser
```

### 9️⃣ VERIFICAR QUE FUNCIONA
Visita: `https://tu-app.railway.app`
- ✅ Login funciona
- ✅ Registro funciona
- ✅ Admin funciona: `/admin/`
- ✅ Estilos se ven bien

### 🔟 DEPLOY AUTOMÁTICO ACTIVADO ✅
Cada `git push` desplegará automáticamente.

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "Bad Request (400)"
**Solución:** Actualiza ALLOWED_HOSTS con tu dominio real de Railway.

### Error: "Static files not found"
**Solución:** 
```bash
# En Railway Shell:
python manage.py collectstatic --noinput
```

### Error: "Module not found"
**Solución:**
```bash
# Local:
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Fix dependencies"
git push
```

### Ver logs detallados
1. Railway > Deployments > Click en deploy activo
2. Los errores aparecen en rojo

---

## 📞 AYUDA
- Documentación Railway: https://docs.railway.app/
- Guía completa: Ver archivo DEPLOY_RAILWAY.md
- Comandos útiles: Ver archivo RAILWAY_COMANDOS.txt

---

**¡Todo listo para deploy! 🎉**

Lee DEPLOY_RAILWAY.md para la guía paso a paso completa.
