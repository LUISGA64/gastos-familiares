// Service Worker para PWA - Gastos Familiares
// Versión del cache - cambiar cuando actualices archivos
const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `gastos-app-${CACHE_VERSION}`;

// Archivos a cachear para funcionamiento offline
const urlsToCache = [
  '/',
  '/static/manifest.json',
  // CSS
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
  // JavaScript
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/sweetalert2@11',
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Instalando...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Cacheando archivos');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] Instalación completada');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[Service Worker] Error en instalación:', error);
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activando...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Eliminar caches antiguos
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Eliminando cache antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Activación completada');
      return self.clients.claim();
    })
  );
});

// Estrategia de Cache: Network First, fallback to Cache
self.addEventListener('fetch', (event) => {
  // Ignorar peticiones POST, PUT, DELETE (solo cachear GET)
  if (event.request.method !== 'GET') {
    return;
  }

  // Ignorar peticiones a dominios externos (excepto CDN)
  const url = new URL(event.request.url);
  const allowedDomains = ['127.0.0.1', 'localhost', 'cdn.jsdelivr.net'];
  if (!allowedDomains.some(domain => url.hostname.includes(domain))) {
    return;
  }

  event.respondWith(
    // Intentar primero la red
    fetch(event.request)
      .then((response) => {
        // Si la respuesta es válida, clonarla y guardarla en cache
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        // Si falla la red, buscar en cache
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            console.log('[Service Worker] Sirviendo desde cache:', event.request.url);
            return cachedResponse;
          }

          // Si no está en cache, mostrar página offline personalizada
          if (event.request.mode === 'navigate') {
            return caches.match('/offline.html');
          }
        });
      })
  );
});

// Sincronización en segundo plano (opcional)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-gastos') {
    console.log('[Service Worker] Sincronizando gastos...');
    event.waitUntil(syncGastos());
  }
});

// Función para sincronizar gastos guardados offline
async function syncGastos() {
  // Aquí iría la lógica para enviar al servidor
  // los gastos que se guardaron mientras estaba offline
  console.log('[Service Worker] Sincronización completada');
}

// Notificaciones Push (opcional)
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push recibido:', event);

  const options = {
    body: event.data ? event.data.text() : 'Nueva notificación',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-96x96.png',
    vibrate: [200, 100, 200],
    tag: 'gastos-notification',
    requireInteraction: false,
  };

  event.waitUntil(
    self.registration.showNotification('Gastos Familiares', options)
  );
});

// Click en notificación
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Click en notificación');

  event.notification.close();

  event.waitUntil(
    clients.openWindow('/')
  );
});

// Mensajes desde la app
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Mensaje recibido:', event.data);

  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }

  if (event.data.action === 'clearCache') {
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => caches.delete(cacheName))
      );
    });
  }
});

console.log('[Service Worker] Archivo cargado, versión:', CACHE_VERSION);

