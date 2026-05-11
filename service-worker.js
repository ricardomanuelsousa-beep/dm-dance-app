const CACHE_NAME = 'dm-dance-v13';
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
  
  // NÃO interferir com Cloudinary (fotos dos alunos)
  if (url.hostname.includes('cloudinary.com')) {
    return; // deixa o browser tratar
  }
  
  // NÃO interferir com analytics / tracking
  if (url.hostname.includes('google-analytics.com') || url.hostname.includes('googletagmanager.com')) {
    return;
  }
  
  // ===== ESTRATÉGIA: HTML e JSON = Network First =====
  if (event.request.destination === 'document' || url.pathname.endsWith('.json') || url.pathname.endsWith('.txt')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Guarda no cache para offline
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          return response;
        })
        .catch(() => {
          // Se falhar (offline), serve do cache
          return caches.match(event.request)
            .then(cached => cached || caches.match('/dm-dance-app/index.html'));
        })
    );
    return;
  }
  
  // ===== ESTRATÉGIA: Imagens, CSS, JS, Fontes = Cache First =====
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

// ========== Mensagem para atualização ==========
self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});