const CACHE_NAME = 'dm-dance-v19';
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
  
  // ===== NUNCA fazer cache de .txt ou .json (dados sempre frescos) =====
  if (url.pathname.endsWith('.txt') || url.pathname.endsWith('.json')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // ===== HTML: Network First =====
  if (event.request.destination === 'document') {
    event.respondWith(
      caches.open(CACHE_NAME).then(cache => {
        return fetch(event.request).then(networkResponse => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        }).catch(() => {
          return caches.match(event.request);
        });
      })
    );
    return;
  }
  
  // ===== Imagens, CSS, JS: Cache First =====
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
