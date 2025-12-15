// Service Worker для offline підтримки та кешування
const CACHE_NAME = 'velvet-bite-v1';
const STATIC_CACHE = [
    '/',
    '/static/style.css',
    '/static/script.js',
    '/static/performance.js',
    '/static/images/mini.jpg',
];

// Встановлення Service Worker
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Caching static assets');
            return cache.addAll(STATIC_CACHE.map(url => new Request(url, { cache: 'reload' })));
        })
    );
});

// Активація Service Worker
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch стратегія: Network First, fallback to Cache
self.addEventListener('fetch', (event) => {
    // Пропускаємо non-GET запити
    if (event.request.method !== 'GET') {
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Клонуємо відповідь для кешування
                const responseToCache = response.clone();
                
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });
                
                return response;
            })
            .catch(() => {
                // Якщо network недоступний, використовуємо кеш
                return caches.match(event.request).then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    
                    // Fallback для сторінок
                    if (event.request.mode === 'navigate') {
                        return caches.match('/');
                    }
                    
                    return new Response('Network error', {
                        status: 408,
                        headers: { 'Content-Type': 'text/plain' }
                    });
                });
            })
    );
});
