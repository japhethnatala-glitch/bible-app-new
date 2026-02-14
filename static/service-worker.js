const CACHE_NAME = 'bible-app-cache-v3';
const urlsToCache = [
  '/',
  '/verses/KJV',
  '/verses/WEB',
  '/static/css/style.css',
  '/static/js/app.js',
  '/offline'   // ✅ offline page route
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      // If request fails, show offline page
      return caches.match(event.request).then(response => {
        return response || caches.match('/offline');
      });
    })
  );
});

// Activate event
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(
        keyList.map(key => {
          if (!cacheWhitelist.includes(key)) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});
