const CACHE_NAME = 'dm-dance-v3';
const urlsToCache = [
  '/dm-dance-app/',
  '/dm-dance-app/index.html',
  '/dm-dance-app/manifest.json',
  '/dm-dance-app/dados_app.json',
  '/dm-dance-app/icon-192x192.png',
  '/dm-dance-app/icon-512x512.png'
];

// Forçar ativação imediata
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  const url = event.request.url;
  
  // NÃO fazer cache de imagens externas (Cloudinary, Supabase)
  if (url.includes('cloudinary.com') || url.includes('supabase.co')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // Para outros, tentar cache
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

// Limpar caches antigas
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