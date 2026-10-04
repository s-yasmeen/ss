const CACHE_NAME = 'silentvoicex-offline-v10';
const CORE_ASSETS = [
  './',
  './index.html',
  './offline.html',
  './manifest.webmanifest',
  './icon.svg',
  './vendor/tf.min.js',
  './vendor/tasks-vision.mjs',
  './vendor/wasm/vision_wasm_internal.js',
  './vendor/wasm/vision_wasm_internal.wasm',
  './vendor/wasm/vision_wasm_nosimd_internal.js',
  './vendor/wasm/vision_wasm_nosimd_internal.wasm',
  './vendor/models/hand_landmarker.task'
];

self.addEventListener('install', event => {
  event.waitUntil((async()=>{
    const cache=await caches.open(CACHE_NAME);
    await cache.addAll(CORE_ASSETS);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async()=>{
    const names=await caches.keys();
    await Promise.all(names.filter(n=>n!==CACHE_NAME).map(n=>caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const req=event.request;
  if(req.method!=='GET') return;
  if(req.mode==='navigate'){
    event.respondWith((async()=>{
      try{
        const fresh=await fetch(req);
        const cache=await caches.open(CACHE_NAME);
        await cache.put('./index.html',fresh.clone());
        return fresh;
      }catch(_){
        return (await caches.match('./index.html')) || (await caches.match('./offline.html'));
      }
    })());
    return;
  }
  event.respondWith((async()=>{
    const cached=await caches.match(req);
    if(cached) return cached;
    const fresh=await fetch(req);
    if(fresh && fresh.ok){
      const cache=await caches.open(CACHE_NAME);
      await cache.put(req,fresh.clone());
    }
    return fresh;
  })());
});
