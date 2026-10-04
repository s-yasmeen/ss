from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove the Train preview's forced privacy-tag visibility so the toggle can control it.
s=s.replace('<div class="privacyTag" style="display:block">🔒 PRIVACY MODE • FACE MESH</div>', '<div class="privacyTag">🔒 FACE PRIVACY • LOCAL ONLY</div>', 1)
s=s.replace('<div class="privacyTag">🔒 PRIVACY MODE • FACE MESH</div>', '<div class="privacyTag">🔒 FACE PRIVACY • LOCAL ONLY</div>', 1)

# Replace permanent privacy status with an independent face privacy state plus no-upload notice.
old_status='<span class="pill on">🔒 Privacy always on</span><span id="autoSpeakStatus" class="pill on">🔊 Auto-speak ≥80%</span>'
new_status='<span id="facePrivacyStatus" class="pill on">🙂 Face privacy ON</span><span class="pill on">🚫 No camera upload</span><span id="autoSpeakStatus" class="pill on">🔊 Auto-speak ≥80%</span>'
if old_status not in s:
    raise SystemExit('Missing privacy status anchor')
s=s.replace(old_status,new_status,1)

# Enable the existing privacy button and make it explicitly face-specific.
old_button='<button id="privacyBtn" class="btn ghost" disabled>🔒 Privacy ON</button>'
new_button='<button id="privacyBtn" class="btn ghost">🙂 Face Privacy ON</button>'
if old_button not in s:
    raise SystemExit('Missing privacy button anchor')
s=s.replace(old_button,new_button,1)

# Add a matching face-privacy button to the Train page.
old_train='<div class="controls"><button id="trainStartBtn" class="btn primary">Start Camera</button></div>'
new_train='<div class="controls"><button id="trainStartBtn" class="btn primary">Start Camera</button><button id="trainPrivacyBtn" class="btn ghost">🙂 Face Privacy ON</button></div><div class="note" style="margin-top:8px">Face frames are processed in memory only. SilentVoiceX does not upload or save face images/video.</div>'
if old_train not in s:
    raise SystemExit('Missing train controls anchor')
s=s.replace(old_train,new_train,1)

# Add the same local-only privacy explanation on Translate.
translate_controls='<div class="controls"><button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost">🙂 Face Privacy ON</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="clearBtn" class="btn ghost">Clear</button></div>'
translate_replacement=translate_controls+'<div class="note" style="margin-top:8px">Face Privacy ON hides the raw camera preview and shows landmarks only. OFF shows a local live preview. Face images/video are never uploaded or saved by SilentVoiceX.</div>'
if translate_controls not in s:
    raise SystemExit('Missing translate controls anchor')
s=s.replace(translate_controls,translate_replacement,1)

# Add local face-privacy state and synchronization logic. Default is ON.
anchor='const SEQ=24, FEAT=126;'
block='''const SEQ=24, FEAT=126;
let facePrivacyEnabled=localStorage.getItem("svx-face-privacy")!=="off";
function syncFacePrivacy(){
 const main=$("cameraWrap"), train=$("trainCameraWrap");
 if(main) main.classList.toggle("privacy",facePrivacyEnabled);
 if(train) train.classList.toggle("privacy",facePrivacyEnabled);
 const label=facePrivacyEnabled?"🙂 Face Privacy ON":"🙂 Face Privacy OFF";
 const status=$("facePrivacyStatus");
 if(status){
   status.textContent=label;
   status.classList.toggle("on",facePrivacyEnabled);
 }
 const b=$("privacyBtn"), tb=$("trainPrivacyBtn");
 if(b) b.textContent=label;
 if(tb) tb.textContent=label;
 document.querySelectorAll(".privacyTag").forEach(el=>{
   el.textContent="🔒 FACE PRIVACY • LOCAL ONLY";
 });
}
function toggleFacePrivacy(){
 facePrivacyEnabled=!facePrivacyEnabled;
 localStorage.setItem("svx-face-privacy",facePrivacyEnabled?"on":"off");
 syncFacePrivacy();
}
'''
if 'function syncFacePrivacy()' not in s:
    if anchor not in s:
        raise SystemExit('Missing SEQ anchor')
    s=s.replace(anchor,block,1)

# Bind both privacy buttons and initialize after DOM is available.
start_handler='$("startBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));'
if start_handler not in s:
    raise SystemExit('Missing start button handler')
if '$("privacyBtn").onclick=toggleFacePrivacy;' not in s:
    s=s.replace(start_handler,start_handler+'\n$("privacyBtn").onclick=toggleFacePrivacy;\n$("trainPrivacyBtn").onclick=toggleFacePrivacy;\nsyncFacePrivacy();',1)

# Update build marker.
for old_build in ['BUILD 21 • PRIVACY FACE MESH','BUILD 20 • CONFIDENCE 80–100%']:
    if old_build in s:
        s=s.replace(old_build,'BUILD 22 • FACE PRIVACY TOGGLE',1)
        break

p.write_text(s,encoding='utf-8')

# Force installed/offline copies to refresh.
swp=Path('sw.js')
sw=swp.read_text(encoding='utf-8')
for old_cache in ['silentvoicex-offline-v4','silentvoicex-offline-v5']:
    sw=sw.replace(old_cache,'silentvoicex-offline-v6')
swp.write_text(sw,encoding='utf-8')
