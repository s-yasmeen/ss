const CACHE_NAME = 'silentvoicex-offline-v1';

const CORE_ASSETS = [
  './',
  './index.html',
  './offline.html',
  './manifest.webmanifest',
  './icon.svg'
];

const EXTERNAL_ASSETS = [
  'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js',
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm',
  'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_internal.js',
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_internal.wasm',
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_nosimd_internal.js',
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_nosimd_internal.wasm'
];

async function cacheOne(cache, url) {
  try {
    const response = await fetch(url, { cache: 'reload' });
    if (response && (response.ok || response.type === 'opaque')) {
      await cache.put(url, response.clone());
      return true;
    }
  } catch (_) {}
  return false;
}

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    for (const url of [...CORE_ASSETS, ...EXTERNAL_ASSETS]) {
      await cacheOne(cache, url);
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
      const response = await fetch(request);
      if (response && (response.ok || response.type === 'opaque')) {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, response.clone());
      }
      return response;
    } catch (err) {
      if (request.mode === 'navigate') {
        return (await caches.match('./index.html')) || (await caches.match('./offline.html'));
      }
      throw err;
    }
  })());
});
