from pathlib import Path

p = Path('index.html')
s = p.read_text()

def rep(old, new, name):
    global s
    if old not in s:
        raise SystemExit(f'Missing expected marker: {name}')
    s = s.replace(old, new, 1)

old = '''<div class="controls"><button id="exportBundleBtn" class="btn primary">⬇ Export Training Bundle</button><button id="importBundleBtn" class="btn ghost">⬆ Import Training Bundle</button><input id="importBundleInput" type="file" accept="application/json,.json" hidden></div>
        <p class="note"><b>Portable training:</b> the bundle keeps your cumulative recorded samples and, when available, the trained model. Import it on another device to continue from the same training instead of starting over.</p>'''
new = '''<div class="controls"><button id="syncDeviceBtn" class="btn primary">📲 Sync to Device</button><button id="receiveSyncBtn" class="btn ghost">📥 Receive Sync</button><button id="exportBundleBtn" class="btn ghost">⬇ Export Backup</button><button id="importBundleBtn" class="btn ghost">⬆ Import Backup</button><input id="importBundleInput" type="file" accept="application/json,.json" hidden></div>
        <p class="note"><b>Cross-device + offline:</b> Sync to Device shares the latest cumulative training bundle, including the trained model when available. On the other phone, tablet, or laptop choose Receive Sync and import it. Existing samples are merged, not replaced. Nearby sharing can work without internet when supported by your device.</p>'''
rep(old, new, 'device sync controls')

old_func = '''async function exportTrainingBundle(){
 try{
   $("exportBundleBtn").disabled=true;
   const portableModel=await capturePortableModel().catch(e=>{console.warn("Model export skipped",e);return null});
   let history=[];try{history=JSON.parse(localStorage.getItem("svx-training-history")||"[]")}catch(_){history=[]}
   const bundle={kind:"SilentVoiceXTrainingBundle",version:PORTABLE_BUNDLE_VERSION,exportedAt:new Date().toISOString(),seq:SEQ,feat:FEAT,dataset,trainedLabels:labels,threshold:parseFloat($("threshold").value)||.75,history,model:portableModel};
   const blob=new Blob([JSON.stringify(bundle)],{type:"application/json"});
   const url=URL.createObjectURL(blob),a=document.createElement("a");
   a.href=url;a.download="SilentVoiceX-training-"+new Date().toISOString().slice(0,10)+".json";document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
   $("trainText").textContent="✓ Portable training bundle exported: "+dataset.length+" samples, "+new Set(dataset.map(x=>x.label)).size+" signs"+(portableModel?" + trained model":"")+".";
 }catch(e){alert("Could not export training bundle: "+e.message)}finally{$("exportBundleBtn").disabled=false;}
}'''
new_func = '''async function createTrainingBundleFile(){
 const portableModel=await capturePortableModel().catch(e=>{console.warn("Model export skipped",e);return null});
 let history=[];try{history=JSON.parse(localStorage.getItem("svx-training-history")||"[]")}catch(_){history=[]}
 const bundle={kind:"SilentVoiceXTrainingBundle",version:PORTABLE_BUNDLE_VERSION,exportedAt:new Date().toISOString(),seq:SEQ,feat:FEAT,dataset,trainedLabels:labels,threshold:parseFloat($("threshold").value)||.75,history,model:portableModel};
 const name="SilentVoiceX-sync-"+new Date().toISOString().replace(/[:.]/g,"-")+".json";
 return {bundle,file:new File([JSON.stringify(bundle)],name,{type:"application/json"}),portableModel};
}
async function exportTrainingBundle(){
 try{
   $("exportBundleBtn").disabled=true;
   const {file,portableModel}=await createTrainingBundleFile();
   const url=URL.createObjectURL(file),a=document.createElement("a");
   a.href=url;a.download=file.name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
   $("trainText").textContent="✓ Backup exported: "+dataset.length+" samples, "+new Set(dataset.map(x=>x.label)).size+" signs"+(portableModel?" + trained model":"")+".";
 }catch(e){alert("Could not export training backup: "+e.message)}finally{$("exportBundleBtn").disabled=false;}
}
async function syncToDevice(){
 try{
   $("syncDeviceBtn").disabled=true;
   const {file,portableModel}=await createTrainingBundleFile();
   if(navigator.share && (!navigator.canShare || navigator.canShare({files:[file]}))){
     await navigator.share({title:"SilentVoiceX Device Sync",text:"Import this SilentVoiceX sync file on the other device using Receive Sync.",files:[file]});
     $("trainText").textContent="✓ Device sync package shared: "+dataset.length+" samples across "+new Set(dataset.map(x=>x.label)).size+" signs"+(portableModel?" + trained model":"")+".";
   }else{
     const url=URL.createObjectURL(file),a=document.createElement("a");a.href=url;a.download=file.name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
     $("trainText").textContent="Share sheet unavailable, so the sync package was saved as a file. Send it to the other device and choose Receive Sync.";
   }
 }catch(e){if(e?.name!=="AbortError")alert("Could not create device sync: "+e.message)}finally{$("syncDeviceBtn").disabled=false;}
}'''
rep(old_func, new_func, 'reusable sync bundle')

old_handlers = '''$("exportBundleBtn").onclick=exportTrainingBundle;
$("importBundleBtn").onclick=()=>$("importBundleInput").click();
$("importBundleInput").onchange=e=>importTrainingBundle(e.target.files?.[0]);'''
new_handlers = '''$("syncDeviceBtn").onclick=syncToDevice;
$("receiveSyncBtn").onclick=()=>$("importBundleInput").click();
$("exportBundleBtn").onclick=exportTrainingBundle;
$("importBundleBtn").onclick=()=>$("importBundleInput").click();
$("importBundleInput").onchange=e=>importTrainingBundle(e.target.files?.[0]);'''
rep(old_handlers, new_handlers, 'device sync handlers')

# Register service worker automatically on the same normal /ss/ URL.
if 'navigator.serviceWorker.register("./sw.js")' not in s:
    rep('logSamples();loadSaved();\n</script>', 'logSamples();loadSaved();\nif("serviceWorker" in navigator){window.addEventListener("load",()=>navigator.serviceWorker.register("./sw.js").catch(e=>console.warn("Offline worker unavailable",e)));}\n</script>', 'service worker registration')

assert 'BUILD 15 • AUTO SPEAK 80%' in s
assert 'filters:16,kernelSize:3' in s and 'filters:24,kernelSize:3' in s
assert 'const EPOCHS=15;' in s
assert 'minHandDetectionConfidence:.5,minHandPresenceConfidence:.5,minTrackingConfidence:.5' in s
assert 'Sync to Device' in s and 'Receive Sync' in s
p.write_text(s)

sw = Path('sw.js')
sws = sw.read_text()
sws = sws.replace('silentvoicex-build15-portable-v3', 'silentvoicex-build15-device-sync-v4')
old_assets = "const ASSETS=['./','./index.html','./offline.html','https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js','https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm','https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'];"
new_assets = "const ASSETS=['./','./index.html','./offline.html','https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js','https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm','https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_internal.js','https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_internal.wasm','https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_nosimd_internal.js','https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm/vision_wasm_nosimd_internal.wasm','https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'];"
if old_assets not in sws:
    raise SystemExit('Missing SW asset marker')
sws = sws.replace(old_assets, new_assets, 1)
sw.write_text(sws)
