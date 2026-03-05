/**
 * VALEO NeuroERP Service Worker
 *
 * Strategies:
 *  - Static assets (JS, CSS, fonts, images): Cache-First with versioned cache name
 *  - API responses: Network-First with stale-while-revalidate fallback
 *  - HTML navigation: Network-First (always fetch fresh shell)
 *
 * The SW_VERSION is bumped at build time (see vite.config.ts).
 * On activation, old caches are purged automatically.
 */

const SW_VERSION = '__SW_VERSION__'
const STATIC_CACHE = `valeo-static-v${SW_VERSION}`
const API_CACHE = `valeo-api-v${SW_VERSION}`

const STATIC_EXTENSIONS = /\.(js|css|woff2?|ttf|eot|png|jpg|jpeg|gif|svg|ico|webp)$/
const API_PATH_PREFIX = '/api/'

self.addEventListener('install', (event) => {
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== API_CACHE)
          .map((key) => caches.delete(key)),
      ),
    ).then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  if (request.method !== 'GET') return

  if (STATIC_EXTENSIONS.test(url.pathname)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE))
    return
  }

  if (url.pathname.startsWith(API_PATH_PREFIX)) {
    event.respondWith(networkFirstWithCache(request, API_CACHE))
    return
  }

  // HTML navigation: network-first, no caching
  event.respondWith(fetch(request).catch(() => caches.match(request)))
})

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request)
  if (cached) return cached

  const response = await fetch(request)
  if (response.ok) {
    const cache = await caches.open(cacheName)
    cache.put(request, response.clone())
  }
  return response
}

async function networkFirstWithCache(request, cacheName) {
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, response.clone())
    }
    return response
  } catch {
    const cached = await caches.match(request)
    if (cached) return cached
    return new Response(JSON.stringify({ error: 'offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
