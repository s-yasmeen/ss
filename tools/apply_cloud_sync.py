from pathlib import Path

p = Path('index.html')
s = p.read_text()


def rep(old, new, name):
    global s
    if old not in s:
        raise SystemExit(f'Missing expected marker: {name}')
    s = s.replace(old, new, 1)

# Replace manual sync/import/export controls with passive automatic sync status.
old_controls = '''        <div class="controls"><button id="syncDeviceBtn" class="btn primary">📲 Sync to Device</button><button id="receiveSyncBtn" class="btn ghost">📥 Receive Sync</button><button id="exportBundleBtn" class="btn ghost">⬇ Export Backup</button><button id="importBundleBtn" class="btn ghost">⬆ Import Backup</button><input id="importBundleInput" type="file" accept="application/json,.json" hidden></div>\n        <p class="note"><b>Cross-device + offline:</b> Sync to Device shares the latest cumulative training bundle, including the trained model when available. On the other phone, tablet, or laptop choose Receive Sync and import it. Existing samples are merged, not replaced. Nearby sharing can work without internet when supported by your device.</p>'''
new_controls = '''        <div class="statusRow"><span id="cloudSyncStatus" class="pill">☁ Shared AI • checking…</span></div>\n        <p class="note"><b>Automatic cross-device sync:</b> training and recorded signs are saved locally first, then synchronized over the internet. Open this same SilentVoiceX link on another device and it automatically loads the newest shared training. Offline changes wait locally and sync after reconnection.</p>'''
rep(old_controls, new_controls, 'manual sync controls')

# Cloud constants/state.
rep('const SEQ=24, FEAT=126, PORTABLE_BUNDLE_VERSION=1;', '''const SEQ=24, FEAT=126, PORTABLE_BUNDLE_VERSION=1;\nconst SYNC_API="https://silentvoicex-sync-api-production.up.railway.app/state";\nlet cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null;''', 'sync constants')

# Dataset changes persist offline immediately and schedule cloud sync.
old_mark = '''function markDatasetChanged(){\n try{localStorage.setItem("svx-data",JSON.stringify(dataset));}\n catch(e){alert("This browser storage is full. Export a Training Bundle before recording more samples.");throw e}\n const signCount=new Set(dataset.map(x=>x.label)).size;\n if(model&&labels.length){\n   $("trainText").textContent="Saved "+dataset.length+" cumulative samples across "+signCount+" signs. Previous trained AI is kept until updated training succeeds.";\n   $("modelStatus").textContent="● Previous AI active • update pending";\n   $("modelStatus").classList.add("on");\n }else{\n   $("trainText").textContent="Saved "+dataset.length+" cumulative samples across "+signCount+" signs — train AI when ready.";\n   $("modelStatus").textContent="● Retrain needed";\n   $("modelStatus").classList.remove("on");\n }\n}'''
new_mark = '''function markDatasetChanged(){\n try{localStorage.setItem("svx-data",JSON.stringify(dataset));}\n catch(e){alert("This browser storage is full. Delete unneeded recordings before adding more samples.");throw e}\n localStorage.setItem("svx-cloud-dirty","1");\n scheduleCloudSync();\n const signCount=new Set(dataset.map(x=>x.label)).size;\n if(model&&labels.length){\n   $("trainText").textContent="Saved locally: "+dataset.length+" cumulative samples across "+signCount+" signs. Shared sync is pending.";\n   $("modelStatus").textContent="● Previous AI active • update pending";\n   $("modelStatus").classList.add("on");\n }else{\n   $("trainText").textContent="Saved locally: "+dataset.length+" cumulative samples across "+signCount+" signs — train AI when ready.";\n   $("modelStatus").textContent="● Retrain needed";\n   $("modelStatus").classList.remove("on");\n }\n}'''
rep(old_mark, new_mark, 'dataset change')

# Remove all manual file/share functions and replace with cloud-sync implementation.
start = s.index('async function createTrainingBundleFile(){')
end_marker = 'function buildModel(n){'
end = s.index(end_marker, start)
cloud_js = r'''function setCloudStatus(text,on=false){
 const el=$("cloudSyncStatus");if(!el)return;el.textContent=text;el.classList.toggle("on",!!on);
}
function scheduleCloudSync(delay=1200){
 clearTimeout(cloudTimer);cloudTimer=setTimeout(()=>syncCloud().catch(e=>console.warn("Cloud sync",e)),delay);
}
function mergeSamples(a,b){
 const out=[],seen=new Set();
 for(const raw of [...(a||[]),...(b||[])]){
   if(!sampleIsValid(raw))continue;
   const x={...raw,label:String(raw.label||"").trim().toUpperCase(),participant:String(raw.participant||"P001")};
   const k=x.id?"id:"+x.id:"fp:"+sampleFingerprint(x);
   if(!seen.has(k)){seen.add(k);out.push(x);}
 }
 return out;
}
async function fetchCloudState(){
 const r=await fetch(SYNC_API,{method:"GET",cache:"no-store"});
 if(!r.ok)throw new Error("sync read "+r.status);
 return await r.json();
}
async function pushCloudState(baseVersion=cloudVersion){
 if(!navigator.onLine)return false;
 const portableModel=await capturePortableModel().catch(e=>{console.warn("Shared model capture skipped",e);return null});
 let history=[];try{history=JSON.parse(localStorage.getItem("svx-training-history")||"[]")}catch(_){history=[]}
 const body={baseVersion,dataset:dataset.filter(sampleIsValid),trainedLabels:labels,threshold:parseFloat($("threshold").value)||.75,history,model:portableModel};
 const r=await fetch(SYNC_API,{method:"PUT",headers:{"content-type":"application/json"},body:JSON.stringify(body)});
 if(r.status===409){
   const conflict=await r.json();
   const current=conflict.current||{};
   dataset=mergeSamples(current.dataset,dataset);
   localStorage.setItem("svx-data",JSON.stringify(dataset));
   selectedRecordIndexes.clear();logSamples();
   cloudVersion=Number(current.version||0);localStorage.setItem("svx-cloud-version",String(cloudVersion));
   return await pushCloudState(cloudVersion);
 }
 if(!r.ok)throw new Error("sync write "+r.status);
 const saved=await r.json();
 cloudVersion=Number(saved.version||0);localStorage.setItem("svx-cloud-version",String(cloudVersion));
 localStorage.removeItem("svx-cloud-dirty");
 setCloudStatus("☁ Shared AI • synced",true);
 return true;
}
async function applyCloudState(remote){
 const dirty=localStorage.getItem("svx-cloud-dirty")==="1";
 const remoteVersion=Number(remote.version||0);
 if(remoteVersion<=cloudVersion&&!dirty)return;
 const merged=dirty?mergeSamples(remote.dataset,dataset):mergeSamples(remote.dataset,[]);
 dataset=merged;localStorage.setItem("svx-data",JSON.stringify(dataset));selectedRecordIndexes.clear();logSamples();
 if(Number.isFinite(Number(remote.threshold)))$("threshold").value=String(remote.threshold);
 if(Array.isArray(remote.history))localStorage.setItem("svx-training-history",JSON.stringify(remote.history.slice(0,20)));
 cloudVersion=remoteVersion;localStorage.setItem("svx-cloud-version",String(cloudVersion));
 if(!dirty&&remote.model&&Array.isArray(remote.trainedLabels)&&remote.trainedLabels.length){
   try{await restorePortableModel({model:remote.model,trainedLabels:remote.trainedLabels});$("modelStatus").textContent="● Shared AI loaded ("+labels.length+" signs)";}catch(e){console.warn("Shared model restore failed",e)}
 }
 if(dirty)await pushCloudState(cloudVersion);
 else setCloudStatus("☁ Shared AI • up to date",true);
}
async function syncCloud(){
 if(cloudBusy)return;
 if(!navigator.onLine){setCloudStatus("☁ Shared AI • offline, changes saved locally",false);return}
 cloudBusy=true;setCloudStatus("☁ Shared AI • syncing…",false);
 try{
   const remote=await fetchCloudState();
   if(Number(remote.version||0)===0&&dataset.length){await pushCloudState(0);}
   else await applyCloudState(remote);
 }catch(e){console.warn(e);setCloudStatus("☁ Shared AI • will retry",false);}
 finally{cloudBusy=false;}
}
window.addEventListener("online",()=>syncCloud());
window.addEventListener("offline",()=>setCloudStatus("☁ Shared AI • offline, changes saved locally",false));
document.addEventListener("visibilitychange",()=>{if(!document.hidden)syncCloud()});
setInterval(()=>{if(!document.hidden&&navigator.onLine)syncCloud()},15000);

'''
s = s[:start] + cloud_js + s[end:]

# After a successful updated training, immediately publish the new trained model.
success_marker = '$("trainText").textContent="✓ Updated training complete • previous samples preserved • "+labels.length+" signs";'
if success_marker not in s:
    raise SystemExit('Missing training success marker')
s = s.replace(success_marker, success_marker + '\n   localStorage.setItem("svx-cloud-dirty","1");\n   await syncCloud();', 1)

# Startup: load local model first, then reconcile cloud. Service worker preserves offline behavior.
old_tail = '''logSamples();loadSaved();\nif("serviceWorker" in navigator){window.addEventListener("load",()=>navigator.serviceWorker.register("./sw.js").catch(e=>console.warn("Offline worker unavailable",e)));}\n</script>'''
new_tail = '''logSamples();\nloadSaved().finally(()=>syncCloud());\nif("serviceWorker" in navigator){window.addEventListener("load",()=>navigator.serviceWorker.register("./sw.js").catch(e=>console.warn("Offline worker unavailable",e)));}\n</script>'''
rep(old_tail, new_tail, 'startup cloud sync')

# Update restore wording to cloud terminology.
s=s.replace('● Portable AI restored (','● Shared AI restored (').replace('Portable AI restored — start camera','Shared AI restored — start camera')

# Build 15 invariants must remain intact.
assert 'BUILD 15 • AUTO SPEAK 80%' in s
assert 'filters:16,kernelSize:3' in s and 'filters:24,kernelSize:3' in s
assert 'const EPOCHS=15;' in s
assert 'minHandDetectionConfidence:.5,minHandPresenceConfidence:.5,minTrackingConfidence:.5' in s
assert 'Sync to Device' not in s
assert 'Receive Sync' not in s
assert 'Export Backup' not in s
assert 'Import Backup' not in s
assert 'silentvoicex-sync-api-production.up.railway.app/state' in s

p.write_text(s)

sw=Path('sw.js')
sws=sw.read_text().replace('silentvoicex-build15-device-sync-v4','silentvoicex-build15-cloud-sync-v5')
sw.write_text(sws)
