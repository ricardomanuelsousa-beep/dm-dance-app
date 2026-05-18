const CACHE_NAME = 'dm-dance-v14';
const urlsToCache = [
  '/dm-dance-app/',
  '/dm-dance-app/manifest.json',
  '/dm-dance-app/icon-192x192.png',
  '/dm-dance-app/icon-512x512.png'
];

// ========== INSTALL ==========
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// ========== FETCH ==========
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // NÃO interferir com Cloudinary
  if (url.hostname.includes('cloudinary.com')) return;
  
  // ===== ESTRATÉGIA PARA HTML: Network First com update automático =====
  if (event.request.destination === 'document') {
    event.respondWith(
      caches.open(CACHE_NAME).then(cache => {
        return fetch(event.request).then(networkResponse => {
          // Atualiza a cache com a nova versão
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        }).catch(() => {
          // Se falhar (offline), serve da cache
          return caches.match(event.request);
        });
      })
    );
    return;
  }
  
  // ===== ESTRATÉGIA PARA DADOS (JSON/TXT): Network First =====
  if (url.pathname.endsWith('.json') || url.pathname.endsWith('.txt')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }
  
  // ===== ESTRATÉGIA PARA IMAGENS, CSS, JS: Cache First =====
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request))
  );
});

// ========== ACTIVATE ==========
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});