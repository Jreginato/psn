const CACHE_NAME = 'personal-trainer-v1';
const RUNTIME_CACHE = 'personal-trainer-runtime';

// Arquivos essenciais para cache durante a instalação
const PRECACHE_URLS = [
  '/',
  '/static/css/sales.css',
  '/static/js/sales.js',
  '/static/manifest.json',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
];

// Instalar service worker e fazer cache dos arquivos essenciais
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Pre-caching offline page');
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => self.skipWaiting())
  );
});

// Ativar service worker e limpar caches antigos
self.addEventListener('activate', event => {
  const currentCaches = [CACHE_NAME, RUNTIME_CACHE];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
    }).then(cachesToDelete => {
      return Promise.all(cachesToDelete.map(cacheToDelete => {
        return caches.delete(cacheToDelete);
      }));
    }).then(() => self.clients.claim())
  );
});

// Estratégia de cache: Network First para HTML, Cache First para assets
self.addEventListener('fetch', event => {
  // Ignorar requisições que não são GET
  if (event.request.method !== 'GET') return;

  // Ignorar requisições para outros domínios (exceto fontes e CDNs conhecidos)
  if (event.request.url.startsWith(self.location.origin) || 
      event.request.url.includes('fonts.googleapis.com') ||
      event.request.url.includes('cdnjs.cloudflare.com')) {
    
    event.respondWith(
      caches.match(event.request).then(cachedResponse => {
        // Para arquivos estáticos (CSS, JS, imagens, fontes), usar cache primeiro
        if (event.request.url.match(/\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/)) {
          return cachedResponse || fetch(event.request).then(response => {
            return caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(event.request, response.clone());
              return response;
            });
          });
        }
        
        // Para HTML e outras requisições, tentar network first
        return fetch(event.request).then(response => {
          // Não fazer cache de respostas inválidas
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }

          // Clonar a resposta
          const responseToCache = response.clone();

          caches.open(RUNTIME_CACHE).then(cache => {
            cache.put(event.request, responseToCache);
          });

          return response;
        }).catch(() => {
          // Se falhar, tentar retornar do cache
          return cachedResponse || caches.match('/');
        });
      })
    );
  }
});

// Mensagens do service worker
self.addEventListener('message', event => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});

// Sincronização em background (para futuras funcionalidades)
self.addEventListener('sync', event => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Implementar lógica de sincronização aqui se necessário
  console.log('[ServiceWorker] Background sync');
}

// Notificações push (para futuras funcionalidades)
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'Nova notificação',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    self.registration.showNotification('Personal Trainer', options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});
