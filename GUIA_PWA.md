# 📱 GUÍA COMPLETA: PWA (Progressive Web App)

## 🎯 ¿QUÉ ES UNA PWA?

Una **Progressive Web App** es una aplicación web que se comporta como una app nativa:

### Ventajas Principales:
- ✅ **Instalable**: Se instala en el dispositivo sin tienda de apps
- ✅ **Funciona Offline**: Usa Service Workers para cachear contenido
- ✅ **Rápida**: Carga instantánea incluso con mala conexión
- ✅ **Actualizaciones automáticas**: Sin pasar por tiendas
- ✅ **Menor tamaño**: No ocupa tanto espacio como apps nativas
- ✅ **Multiplataforma**: Un código para Android, iOS, Desktop
- ✅ **Acceso directo**: Ícono en pantalla de inicio
- ✅ **Notificaciones Push**: (Opcional)

---

## 📦 ARCHIVOS IMPLEMENTADOS

### 1. `manifest.json` - Configuración de la App
```
static/manifest.json
```

**Qué contiene:**
- Nombre de la app
- Íconos en diferentes tamaños
- Colores del tema
- Modo de visualización (standalone)
- Atajos rápidos
- Screenshots (opcional)

### 2. `sw.js` - Service Worker
```
static/sw.js
```

**Qué hace:**
- Cachea archivos para uso offline
- Intercepta peticiones de red
- Sirve contenido cacheado cuando no hay internet
- Se actualiza automáticamente
- Sincroniza datos en segundo plano

### 3. `offline.html` - Página sin conexión
```
templates/offline.html
```

**Qué muestra:**
- Mensaje amigable cuando no hay internet
- Botón para reintentar
- Tips para el usuario
- Auto-recarga cuando vuelve la conexión

### 4. Modificaciones en `base.html`
- Meta tags para PWA
- Link al manifest
- Registro del Service Worker
- Detección de instalación
- Alertas de conexión/desconexión

---

## 🚀 CÓMO FUNCIONA

### Ciclo de Vida de la PWA:

1. **Primera Visita**
   - Usuario accede a la web
   - Service Worker se descarga y registra
   - Archivos se cachean en segundo plano
   - Aparece banner "Instalar App"

2. **Instalación** (Opcional)
   - Usuario hace click en "Instalar"
   - Se agrega ícono a pantalla de inicio
   - App se abre en ventana independiente (sin barra del navegador)

3. **Uso Offline**
   - Usuario pierde conexión
   - Service Worker sirve archivos cacheados
   - App sigue funcionando (parcialmente)
   - Se muestran datos guardados localmente

4. **Reconexión**
   - Internet vuelve
   - Service Worker sincroniza datos
   - Descarga actualizaciones
   - Notifica al usuario

5. **Actualización**
   - Nueva versión disponible
   - Service Worker detecta cambios
   - Descarga nueva versión en background
   - Pregunta al usuario si quiere actualizar

---

## 🛠️ CÓMO PROBAR LA PWA

### Paso 1: Generar Iconos

**Opción A - Online (Recomendado):**
```
1. Ve a: https://realfavicongenerator.net/
2. Sube tu logo (512x512 px)
3. Descarga el paquete
4. Copia a: DjangoProject/static/icons/
```

**Opción B - Crear placeholders:**
```bash
python generar_iconos_pwa.py
```

Luego ejecuta el código Python que te muestra.

### Paso 2: Configurar Django para servir archivos estáticos

En `settings.py`, verifica:
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Paso 3: Ejecutar el servidor

**⚠️ IMPORTANTE: PWA requiere HTTPS en producción**

Para desarrollo local:
```bash
python manage.py runserver
```

Para testing con HTTPS local:
```bash
pip install django-extensions werkzeug pyOpenSSL

python manage.py runserver_plus --cert-file cert.pem
```

### Paso 4: Abrir en Chrome/Edge

```
http://localhost:8000/
```

### Paso 5: Verificar PWA

**Chrome DevTools:**
1. F12 → Pestaña "Application"
2. Sección "Manifest" → Ver configuración
3. Sección "Service Workers" → Ver estado
4. Sección "Cache Storage" → Ver archivos cacheados

**Lighthouse (Auditoría PWA):**
1. F12 → Pestaña "Lighthouse"
2. Seleccionar "Progressive Web App"
3. Click "Analyze page load"
4. Revisar puntuación y recomendaciones

### Paso 6: Instalar la App

**Desktop (Chrome/Edge):**
- Ícono de instalación en barra de direcciones
- O banner en la página
- Click "Instalar"

**Android:**
- Chrome → Menú → "Añadir a pantalla de inicio"
- O banner automático

**iOS (Safari):**
- Safari → Compartir → "Añadir a pantalla de inicio"
- (iOS tiene limitaciones con PWA)

---

## 📊 ESTRATEGIAS DE CACHÉ

El Service Worker implementa **"Network First, fallback to Cache"**:

### 1. Network First (Implementado)
```
Internet → ✅ Servidor → Actualizar cache → Mostrar
           ❌ Sin internet → Buscar en cache → Mostrar
```

**Ventajas:**
- Siempre muestra contenido fresco
- Actualiza cache automáticamente
- Fallback a offline

### 2. Otras Estrategias (Puedes cambiar):

**Cache First:**
```javascript
// Servir cache primero, luego red
caches.match(request) || fetch(request)
```

**Stale While Revalidate:**
```javascript
// Servir cache y actualizar en background
caches.match(request).then(cached => {
  fetch(request).then(response => cache.put(request, response));
  return cached || fetch(request);
});
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### Cambiar Versión del Cache

En `static/sw.js`:
```javascript
const CACHE_VERSION = 'v1.0.1';  // Cambiar aquí
```

Cada vez que cambies esta versión:
- Caches antiguos se eliminan
- Archivos se vuelven a cachear
- Usuario obtiene versión más reciente

### Agregar más archivos al cache

En `static/sw.js`:
```javascript
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/gastos/',           // Agregar nueva ruta
  '/static/mi-css.css', // Agregar nuevo archivo
  // ...
];
```

### Notificaciones Push (Opcional)

El Service Worker ya tiene código para notificaciones.

**Para activarlas:**
1. Registrar servicio de push (Firebase, OneSignal, etc.)
2. Solicitar permisos al usuario
3. Enviar notificaciones desde el servidor

**Ejemplo:**
```javascript
// Solicitar permiso
Notification.requestPermission().then(permission => {
  if (permission === 'granted') {
    console.log('Notificaciones permitidas');
  }
});

// Mostrar notificación
navigator.serviceWorker.ready.then(registration => {
  registration.showNotification('Nuevo gasto', {
    body: 'Se registró un gasto de $50.000',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-96x96.png',
  });
});
```

---

## 📱 TESTING EN DISPOSITIVOS MÓVILES

### Android:

1. **Conectar por red local:**
```bash
# En settings.py
ALLOWED_HOSTS = ['*']  # Solo para desarrollo

# Ejecutar servidor
python manage.py runserver 0.0.0.0:8000

# Desde móvil
http://TU_IP_LOCAL:8000
```

2. **Usar ngrok (HTTPS gratuito):**
```bash
pip install pyngrok

# En otro terminal
ngrok http 8000

# Usar URL HTTPS que te da ngrok
```

### iOS:

⚠️ **Limitaciones de iOS:**
- No soporta notificaciones push
- Service Workers limitados
- Requiere Safari (Chrome no instala PWAs)
- Cache limitado a 50MB
- Se elimina si no se usa por semanas

**Instalación en iOS:**
1. Safari → Página de la app
2. Botón compartir (cuadrado con flecha)
3. "Añadir a pantalla de inicio"
4. Editar nombre
5. "Añadir"

---

## 🎨 PERSONALIZACIÓN

### Cambiar Colores

En `manifest.json`:
```json
{
  "theme_color": "#3498db",      // Color de barra superior
  "background_color": "#2c3e50"  // Color de splash screen
}
```

En `base.html`:
```html
<meta name="theme-color" content="#3498db">
```

### Cambiar Modo de Pantalla

En `manifest.json`:
```json
{
  "display": "standalone"  // Opciones:
}
```

Opciones:
- `standalone` - Sin UI del navegador (Recomendado)
- `fullscreen` - Pantalla completa
- `minimal-ui` - UI mínima del navegador
- `browser` - Pestaña normal del navegador

### Agregar Atajos (Shortcuts)

En `manifest.json`:
```json
{
  "shortcuts": [
    {
      "name": "Nuevo Gasto",
      "url": "/gastos/nuevo/",
      "icons": [...]
    }
  ]
}
```

Aparecen al presionar largo en el ícono (Android).

---

## 🐛 DEBUGGING Y TROUBLESHOOTING

### Problemas Comunes:

**1. Service Worker no se registra**
```
Causa: HTTPS requerido (excepto localhost)
Solución: Usar localhost o configurar HTTPS
```

**2. Archivos no se cachean**
```
Causa: Ruta incorrecta en urlsToCache
Solución: Verificar rutas en DevTools → Network
```

**3. Cache no se actualiza**
```
Causa: Versión del cache no cambió
Solución: Incrementar CACHE_VERSION en sw.js
```

**4. "Add to Home Screen" no aparece**
```
Causa: Falta manifest o iconos
Solución: Verificar en DevTools → Application → Manifest
```

**5. App no funciona offline**
```
Causa: Service Worker no activado o archivos no cacheados
Solución: DevTools → Application → Service Workers
```

### Comandos Útiles de DevTools:

**Limpiar todo:**
```javascript
// En consola del navegador
navigator.serviceWorker.getRegistrations().then(registrations => {
  registrations.forEach(r => r.unregister());
});

caches.keys().then(keys => {
  keys.forEach(key => caches.delete(key));
});
```

**Forzar actualización:**
```javascript
navigator.serviceWorker.ready.then(registration => {
  registration.update();
});
```

**Simular offline:**
```
DevTools → Network → Throttling → Offline
```

---

## 📊 MÉTRICAS Y AUDITORÍA

### Lighthouse PWA Checklist:

✅ **Instalabilidad:**
- Manifest válido
- Service Worker registrado
- HTTPS (producción)
- Iconos de 192px y 512px

✅ **Confiabilidad:**
- Responde con 200 offline
- Página offline personalizada
- Service Worker controla página

✅ **Optimización:**
- Carga rápida (< 3s)
- Primera pintura con contenido (< 2s)
- Interactivo (< 5s)

### Herramientas de Testing:

1. **Lighthouse** (Chrome DevTools)
2. **PWA Builder** (https://www.pwabuilder.com/)
3. **Web.dev Measure** (https://web.dev/measure/)

---

## 🚀 DESPLIEGUE EN PRODUCCIÓN

### Requisitos:

1. **HTTPS Obligatorio**
   - Certificado SSL/TLS
   - Let's Encrypt gratuito
   - Cloudflare (gratis)

2. **Configurar Django:**
```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

3. **Servir archivos estáticos:**
```bash
python manage.py collectstatic
```

4. **Configurar servidor web (Nginx):**
```nginx
location /static/ {
    alias /path/to/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location /sw.js {
    alias /path/to/static/sw.js;
    add_header Cache-Control "no-cache";
}
```

---

## 💡 PRÓXIMOS PASOS

### Funcionalidades Avanzadas:

1. **Background Sync**
   - Guardar gastos offline
   - Sincronizar cuando hay internet

2. **Notificaciones Push**
   - Alertas de presupuesto
   - Recordatorios de gastos

3. **Compartir API**
   - Compartir gastos a la app desde otras apps

4. **Shortcuts**
   - Accesos rápidos desde ícono

5. **Share Target**
   - Recibir compartidos de otras apps

---

## 📚 RECURSOS

### Documentación Oficial:
- MDN PWA: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps
- Google PWA: https://web.dev/progressive-web-apps/
- Service Workers: https://developers.google.com/web/fundamentals/primers/service-workers

### Herramientas:
- PWA Builder: https://www.pwabuilder.com/
- Workbox (Google): https://developers.google.com/web/tools/workbox
- Favicon Generator: https://realfavicongenerator.net/

### Testing:
- Lighthouse: Chrome DevTools
- PWA Testing Tool: https://www.pwabuilder.com/
- ngrok (HTTPS): https://ngrok.com/

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Manifest.json creado
- [x] Service Worker implementado
- [x] Página offline diseñada
- [x] Meta tags PWA agregados
- [x] Registro de SW en base.html
- [x] Detección de instalación
- [x] Alertas de conexión
- [ ] Generar iconos (pendiente)
- [ ] Testing en móvil
- [ ] Auditoría Lighthouse
- [ ] Configurar HTTPS producción
- [ ] Optimizar cache
- [ ] Implementar Background Sync (opcional)
- [ ] Notificaciones Push (opcional)

---

## 🎊 CONCLUSIÓN

**¡Tu app ya tiene PWA implementada!**

### Lo que ya funciona:
✅ Manifest configurado
✅ Service Worker activo
✅ Cache offline
✅ Detección de instalación
✅ Página offline
✅ Alertas de conexión
✅ Actualización automática

### Para activarla completamente:
1. Genera los iconos
2. Prueba en Chrome
3. Instala la app
4. Desconecta internet y verifica offline
5. Ejecuta Lighthouse para optimizar

**¡Tu aplicación ahora puede competir con apps nativas!** 📱✨

---

_Documento creado: 2026-01-14_
_Versión PWA: 1.0.0_

