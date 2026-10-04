from pathlib import Path

# Merge PWA/offline support into the main SilentVoiceX interface.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

# PWA metadata on the main page.
if '<link rel="manifest" href="./manifest.webmanifest">' not in s:
    anchor = '<meta name="apple-mobile-web-app-title" content="SilentVoiceX">'
    addition = anchor + '\n<meta name="theme-color" content="#07111f">\n<link rel="manifest" href="./manifest.webmanifest">\n<link rel="icon" href="./icon.svg" type="image/svg+xml">'
    if anchor not in s:
        raise SystemExit('Missing app title metadata anchor')
    s = s.replace(anchor, addition, 1)

# Visible offline state on the Translate screen.
if 'id="offlineStatus"' not in s:
    anchor = '<span id="expressionStatus" class="pill">🙂 Expression waiting</span>'
    replacement = anchor + '<span id="offlineStatus" class="pill">📴 Offline checking</span>'
    if anchor not in s:
        raise SystemExit('Missing expression status anchor')
    s = s.replace(anchor, replacement, 1)

# One-click access to offline preparation.
if 'id="offlineBtn"' not in s:
    old = '<button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost" disabled>🔒 Privacy ON</button><button id="clearBtn" class="btn ghost">Clear</button>'
    new = '<button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost" disabled>🔒 Privacy ON</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="clearBtn" class="btn ghost">Clear</button>'
    if old not in s:
        raise SystemExit('Missing Translate controls anchor')
    s = s.replace(old, new, 1)

# Register/update the service worker directly from the main app and report status.
if 'function updateOfflineStatus()' not in s:
    anchor = 'const SEQ=24, FEAT=126;'
    block = '''const SEQ=24, FEAT=126;

function updateOfflineStatus(){
 const el=$("offlineStatus");
 if(!el)return;
 const prepared=localStorage.getItem("svx-offline-prepared-v3")==="1";
 if(!navigator.onLine){
   el.textContent="📴 Running offline";
   el.classList.add("on");
 }else if(prepared){
   el.textContent="✓ Offline ready";
   el.classList.add("on");
 }else{
   el.textContent="📴 Offline not prepared";
   el.classList.remove("on");
 }
}
if("serviceWorker" in navigator){
 navigator.serviceWorker.register("./sw.js",{scope:"./"}).then(()=>updateOfflineStatus()).catch(err=>console.warn("Offline worker unavailable",err));
}
window.addEventListener("online",updateOfflineStatus);
window.addEventListener("offline",updateOfflineStatus);
updateOfflineStatus();'''
    if anchor not in s:
        raise SystemExit('Missing SEQ anchor')
    s = s.replace(anchor, block, 1)

if '$(' + '"offlineBtn"' + ').onclick' not in s:
    anchor = '$("startBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));'
    addition = anchor + '\n$("offlineBtn").onclick=()=>{location.href="./offline.html"};'
    if anchor not in s:
        raise SystemExit('Missing start button handler')
    s = s.replace(anchor, addition, 1)

for old_build in ['BUILD 18 • EXPRESSION CUES','BUILD 17 • OFFLINE','BUILD 16 • AUTO SPEAK 80%','BUILD 15 • AUTO SPEAK 80%']:
    if old_build in s:
        s = s.replace(old_build, 'BUILD 19 • OFFLINE + EXPRESSION', 1)
        break

p.write_text(s, encoding='utf-8')

# Force an updated cache so old installations do not remain on the pre-merge UI.
swp = Path('sw.js')
sw = swp.read_text(encoding='utf-8')
for old in ["silentvoicex-offline-v1", "silentvoicex-offline-v2"]:
    sw = sw.replace(old, "silentvoicex-offline-v3")
swp.write_text(sw, encoding='utf-8')

# Update the setup page so the expression model is explicitly part of offline readiness.
offp = Path('offline.html')
off = offp.read_text(encoding='utf-8')
face = "  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',\n"
hand = "  'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',\n"
if face not in off:
    if hand not in off:
        raise SystemExit('Missing hand model in offline assets')
    off = off.replace(hand, hand + face, 1)

off = off.replace(
    'Prepare the sign-to-speech app for use without Wi‑Fi or mobile data. Your recorded samples and trained model stay on this device.',
    'Prepare sign recognition, facial-expression cues, and speech support for use without Wi‑Fi or mobile data. Your recorded samples and trained model stay on this device.'
)
off = off.replace("localStorage.setItem('svx-offline-prepared','1');", "localStorage.setItem('svx-offline-prepared-v3','1');")
off = off.replace("localStorage.getItem('svx-offline-prepared')==='1'", "localStorage.getItem('svx-offline-prepared-v3')==='1'")
off = off.replace(
    '✓ Offline core ready. Open SilentVoiceX and start the camera once while online.',
    '✓ Offline sign + expression AI ready. Open SilentVoiceX and test once before Airplane Mode.'
)
off = off.replace(
    'For the most reliable exhibition demo, prepare while online, then open SilentVoiceX and start the camera once. After that, test again with Airplane Mode enabled.',
    'For the most reliable exhibition demo, prepare while online. This caches both hand-sign AI and facial-expression AI. Then open SilentVoiceX once and test again with Airplane Mode enabled.'
)
offp.write_text(off, encoding='utf-8')
