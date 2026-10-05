from pathlib import Path

p=Path('index.html')
s=p.read_text()

# Recognition threshold must not block 70% auto-speak.
s=s.replace('id="threshold" type="number" min=".5" max=".99" step=".01" value=".75"',
            'id="threshold" type="number" min=".5" max=".99" step=".01" value=".70"')

# Existing cloud state may carry the previous 0.75 threshold; cap it at 0.70 in this build.
s=s.replace('if(Number.isFinite(Number(remote.threshold)))$("threshold").value=String(remote.threshold);',
            'if(Number.isFinite(Number(remote.threshold)))$("threshold").value=String(Math.min(Number(remote.threshold),0.70));')

s=s.replace('const body={baseVersion,dataset:dataset.filter(sampleIsValid),threshold:parseFloat($("threshold").value)||.75};',
            'const body={baseVersion,dataset:dataset.filter(sampleIsValid),threshold:Math.min(parseFloat($("threshold").value)||.70,0.70)};')

# Restore the known stable Build 15 CPU training backend where possible.
s=s.replace('try{if(!tf.getBackend()){await tf.setBackend("cpu");await tf.ready();}}catch(e){console.warn("Backend setup fallback",e)}',
            'try{if(tf.getBackend()!=="cpu"){await tf.setBackend("cpu");await tf.ready();}}catch(e){console.warn("CPU backend switch skipped",e)}')

# Do not run live neural-network inference while the same device is training.
s=s.replace('if(model && r.landmarks?.length){', 'if(!trainingBusy && model && r.landmarks?.length){', 1)

# Make training state immediately visible before potentially expensive backend work.
s=s.replace('trainingBusy=true;\n   setCloudStatus("☁ Shared AI • training locally…",false);',
            'trainingBusy=true;\n   $("trainBtn").disabled=true;\n   setCloudStatus("☁ Shared AI • training locally…",false);')

# Avoid duplicate assignment later; harmless if absent.
s=s.replace('$("trainBtn").disabled=true;$("bar").style.width="1%";$("resultsLog").textContent="Training updated cumulative model…";await tf.nextFrame();',
            '$("bar").style.width="1%";$("resultsLog").textContent="Training updated cumulative model…";await tf.nextFrame();')

assert 'trainingBusy=false' in s
assert 'conf>=0.70' in s
assert 'BUILD 15 • AUTO SPEAK 70%' in s
assert 'value=".70"' in s
assert 'tf.getBackend()!=="cpu"' in s
assert 'if(!trainingBusy && model && r.landmarks?.length)' in s
assert 'const EPOCHS=15;' in s
assert 'filters:16,kernelSize:3' in s and 'filters:24,kernelSize:3' in s
p.write_text(s)

# Bump cache and make navigation network-first so devices receive fixes instead of staying on stale cached HTML.
sw=Path('sw.js')
w=sw.read_text()
import re
w=re.sub(r"const CACHE='[^']+';", "const CACHE='silentvoicex-build15-cloud-sync-autospeak70-v7';", w, count=1)
old="self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith((async()=>{const c=await caches.match(e.request);if(c)return c;try{const r=await fetch(e.request);if(r&&(r.ok||r.type==='opaque')){const k=await caches.open(CACHE);await k.put(e.request,r.clone())}return r}catch(err){if(e.request.mode==='navigate')return (await caches.match('./index.html'))||(await caches.match('./offline.html'));throw err}})())});"
new="self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith((async()=>{if(e.request.mode==='navigate'){try{const r=await fetch(e.request,{cache:'no-store'});if(r&&r.ok){const k=await caches.open(CACHE);await k.put('./index.html',r.clone())}return r}catch(err){return (await caches.match('./index.html'))||(await caches.match('./offline.html'))}}const c=await caches.match(e.request);if(c)return c;try{const r=await fetch(e.request);if(r&&(r.ok||r.type==='opaque')){const k=await caches.open(CACHE);await k.put(e.request,r.clone())}return r}catch(err){throw err}})())});"
if old in w:
    w=w.replace(old,new,1)
else:
    raise SystemExit('service worker fetch marker not found')
sw.write_text(w)
