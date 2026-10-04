from pathlib import Path
import re

p = Path('index.html')
s = p.read_text()
s = s.replace('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js', './vendor/tf.min.js')
s = s.replace('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm', './vendor/tasks-vision.mjs')
s = s.replace('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm', './vendor/wasm')
s = s.replace('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', './vendor/models/hand_landmarker.task')
s = s.replace('BUILD 25 • SIGN-ONLY OFFLINE AI', 'BUILD 26 • LOCAL OFFLINE SIGN AI')
s = s.replace('svx-offline-prepared-v4', 'svx-offline-prepared-v5')

old = 'handLandmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"./vendor/models/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.55,minHandPresenceConfidence:.55,minTrackingConfidence:.5});'
new = '''try{\n handLandmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"./vendor/models/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.55,minHandPresenceConfidence:.55,minTrackingConfidence:.5});\n}catch(gpuErr){\n console.warn("GPU hand runtime unavailable; falling back to CPU",gpuErr);\n handLandmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"./vendor/models/hand_landmarker.task"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.55,minHandPresenceConfidence:.55,minTrackingConfidence:.5});\n}'''
if old not in s:
    raise SystemExit('HandLandmarker line not found')
s = s.replace(old, new)
p.write_text(s)

Path('sw.js').write_text("""const CACHE_NAME = 'silentvoicex-offline-v9';
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
""")

Path('offline.html').write_text("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SilentVoiceX Offline Setup</title>
<meta name="theme-color" content="#07111f">
<link rel="manifest" href="./manifest.webmanifest">
<link rel="icon" href="./icon.svg" type="image/svg+xml">
<style>
:root{--bg:#07111f;--card:#0d1b2e;--cyan:#45e6ff;--violet:#8b5cf6;--pink:#ff4fa3;--text:#f7fbff;--muted:#9bb0c9;--good:#3ee6a0}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at 15% 15%,#11284a 0,#07111f 50%,#050a12 100%);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--text);padding:20px}.card{width:min(620px,100%);background:linear-gradient(160deg,#10213aee,#0a1627ee);border:1px solid #1c3a5d;border-radius:26px;padding:24px;box-shadow:0 24px 70px #0007}.logo{width:84px;height:84px;border-radius:22px}.tag{display:inline-flex;padding:7px 10px;border:1px solid #1f7b61;border-radius:999px;color:#88ffd3;font-weight:900;font-size:12px;margin:10px 0}.title{font-size:clamp(34px,7vw,58px);font-weight:950;letter-spacing:-2px;margin:4px 0}.title span{background:linear-gradient(90deg,var(--cyan),#a78bfa,var(--pink));-webkit-background-clip:text;color:transparent}.sub,.note{color:var(--muted);line-height:1.6}.status{margin:18px 0;padding:14px 16px;border-radius:16px;background:#071321;border:1px solid #1d3855;font-weight:850}.bar{height:11px;border-radius:999px;background:#071321;border:1px solid #1b3652;overflow:hidden}.fill{height:100%;width:0;background:linear-gradient(90deg,var(--cyan),var(--violet),var(--pink));transition:.25s}.buttons{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.btn{border:0;border-radius:14px;padding:12px 16px;color:white;font-weight:900;cursor:pointer}.primary{background:linear-gradient(135deg,#0ea5e9,#7c3aed)}.ghost{background:#0b1a2c;border:1px solid #284663}.btn:disabled{opacity:.45}.note{font-size:12px;margin-top:16px}
</style>
</head>
<body><div class="card">
<img class="logo" src="./icon.svg" alt="SilentVoiceX icon">
<div class="tag">✋ SIGN-ONLY • ON-DEVICE • OFFLINE</div>
<div class="title"><span>SilentVoiceX</span></div>
<div class="sub">Prepare the complete hand-sign AI runtime for use without Wi-Fi or mobile data. TensorFlow.js, MediaPipe, WebAssembly files and the hand model are hosted with SilentVoiceX and cached on this device.</div>
<div id="status" class="status">Checking offline runtime…</div>
<div class="bar"><div id="fill" class="fill"></div></div>
<div class="buttons"><button id="prepare" class="btn primary">Prepare Offline Mode</button><button id="open" class="btn ghost">Open SilentVoiceX</button></div>
<div class="note">Prepare once while online. When this page reports “Offline Ready”, open SilentVoiceX, start the camera once, then enable Airplane Mode for the judge demonstration. Speech also requires an offline system voice on the device.</div>
</div>
<script>
const statusEl=document.getElementById('status'),fill=document.getElementById('fill'),prepare=document.getElementById('prepare'),openBtn=document.getElementById('open');
const CACHE='silentvoicex-offline-v9';
const assets=['./','./index.html','./offline.html','./manifest.webmanifest','./icon.svg','./vendor/tf.min.js','./vendor/tasks-vision.mjs','./vendor/wasm/vision_wasm_internal.js','./vendor/wasm/vision_wasm_internal.wasm','./vendor/wasm/vision_wasm_nosimd_internal.js','./vendor/wasm/vision_wasm_nosimd_internal.wasm','./vendor/models/hand_landmarker.task'];
async function ensureWorker(){if(!('serviceWorker' in navigator))throw new Error('Offline mode is not supported in this browser.');await navigator.serviceWorker.register('./sw.js',{scope:'./'});await navigator.serviceWorker.ready;}
async function prepareOffline(){prepare.disabled=true;try{await ensureWorker();const cache=await caches.open(CACHE);let done=0;for(const url of assets){const r=await fetch(url,{cache:'reload'});if(!r.ok)throw new Error('Could not cache '+url);await cache.put(url,r.clone());done++;fill.style.width=Math.round(done/assets.length*100)+'%';statusEl.textContent='Saving offline AI files… '+done+'/'+assets.length;}localStorage.setItem('svx-offline-prepared-v5','1');statusEl.textContent='✓ Offline Ready — all sign-recognition files verified on this device.';fill.style.width='100%';}catch(e){localStorage.removeItem('svx-offline-prepared-v5');statusEl.textContent='Offline setup failed: '+e.message;}finally{prepare.disabled=false;}}
prepare.onclick=prepareOffline;openBtn.onclick=()=>location.href='./index.html?v=26';
(async()=>{try{await ensureWorker();if(localStorage.getItem('svx-offline-prepared-v5')==='1'){statusEl.textContent=navigator.onLine?'✓ Offline Ready':'✓ Running without internet';fill.style.width='100%';}else statusEl.textContent='Tap Prepare Offline Mode while connected to the internet.';}catch(e){statusEl.textContent='Offline setup unavailable: '+e.message;}})();
</script></body></html>
""")

scripts = re.findall(r'<script type="module">(.*?)</script>', s, re.S)
if len(scripts) != 1:
    raise SystemExit('Expected one module script')
Path('/tmp/svx-app.mjs').write_text(scripts[0])
