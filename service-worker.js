const CACHE_NAME = 'dm-dance-v12';
const urlsToCache = [
  '/dm-dance-app/',
  '/dm-dance-app/index.html',
  '/dm-dance-app/manifest.json',
  '/dm-dance-app/dados_app.json',
  '/dm-dance-app/icon-192x192.png',
  '/dm-dance-app/icon-512x512.png'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  // NÃO interferir com Cloudinary
  if (event.request.url.includes('cloudinary.com')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match('/dm-dance-app/index.html'))
  );
});

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