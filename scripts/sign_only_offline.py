from pathlib import Path
import re

idx = Path('index.html')
s = idx.read_text(encoding='utf-8')

# ----- UI: sign-only, no facial-expression/privacy controls -----
s = s.replace(
'''  <div class="top"><div class="brand"><h1>✋ <span>SilentVoice X</span></h1><p>AI that turns signs into speech</p></div><button id="headerOfflineBtn" class="btn primary">📴 Offline Setup</button></div>''',
'''  <div class="top"><div class="brand"><h1>✋ <span>SilentVoice X</span></h1><p>Offline AI that turns hand signs into speech</p></div><button id="headerOfflineBtn" class="btn primary">📴 Offline Setup</button></div>''')

old_main = '''        <div id="cameraWrap" class="cameraWrap privacy">
          <video id="video" autoplay playsinline muted></video><canvas id="canvas"></canvas><div class="privacyTag">🔒 FACE PRIVACY • LOCAL ONLY</div>
        </div>
        <div class="statusRow"><span id="camStatus" class="pill">● Camera off</span><span id="handStatus" class="pill">● Waiting for hand</span><span id="modelStatus" class="pill">● Model not trained</span><span id="expressionStatus" class="pill">🙂 Expression waiting</span><span id="offlineStatus" class="pill">📴 Offline checking</span><span id="facePrivacyStatus" class="pill on">🙂 Face privacy ON</span><span class="pill on">🚫 No camera upload</span><span id="autoSpeakStatus" class="pill on">🔊 Auto-speak ≥80%</span></div>
        <div class="controls"><button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost">🙂 Face Privacy ON</button><button id="expressionToggleBtn" class="btn ghost">🙂 Expression ON</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="clearBtn" class="btn ghost">Clear</button></div><div class="note" style="margin-top:8px">Face Privacy ON hides the raw camera preview and shows landmarks only. OFF shows a local live preview. Face images/video are never uploaded or saved by SilentVoiceX.</div>'''
new_main = '''        <div id="cameraWrap" class="cameraWrap">
          <video id="video" autoplay playsinline muted></video><canvas id="canvas"></canvas>
        </div>
        <div class="statusRow"><span id="camStatus" class="pill">● Camera off</span><span id="handStatus" class="pill">● Waiting for hand</span><span id="modelStatus" class="pill">● Model not trained</span><span id="offlineStatus" class="pill">📴 Offline checking</span><span class="pill on">✋ Sign-only mode</span><span class="pill on">🚫 No camera upload</span><span id="autoSpeakStatus" class="pill on">🔊 Auto-speak ≥80%</span></div>
        <div class="controls"><button id="startBtn" class="btn primary">Start Camera</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="clearBtn" class="btn ghost">Clear</button></div><div class="note" style="margin-top:8px">Hand landmarks are processed on this device. SilentVoiceX does not upload or save camera video.</div>'''
if old_main not in s:
    raise SystemExit('main camera block not found')
s = s.replace(old_main, new_main)

expr_card = '''<div class="sentence" style="margin-top:10px"><div class="seq">FACIAL EXPRESSION CUE</div><div id="expressionCue" class="natural">—</div><div id="expressionStrength" class="note">Local landmark analysis • not a measure of inner emotion</div></div>'''
s = s.replace(expr_card, '')

old_train = '''          <div id="trainCameraWrap" class="cameraWrap privacy">
            <video id="trainVideo" autoplay playsinline muted></video>
            <canvas id="trainCanvas"></canvas>
            <div class="privacyTag">🔒 FACE PRIVACY • LOCAL ONLY</div>
            <div id="recordOverlay" class="recordOverlay">Camera off — tap Start Camera</div>
          </div>
          <div class="statusRow">
            <span id="trainCamStatus" class="pill">● Camera off</span>
            <span id="trainHandStatus" class="pill">● Waiting for hand</span>
            <span id="trainFaceStatus" class="pill">🙂 Waiting for face</span>
          </div>
          <div class="controls"><button id="trainStartBtn" class="btn primary">Start Camera</button><button id="trainPrivacyBtn" class="btn ghost">🙂 Face Privacy ON</button><button id="trainExpressionToggleBtn" class="btn ghost">🙂 Expression ON</button></div><div class="note" style="margin-top:8px">Face frames are processed in memory only when Expression is ON. Turn Expression OFF to stop facial-expression inference. SilentVoiceX does not upload or save face images/video.</div>'''
new_train = '''          <div id="trainCameraWrap" class="cameraWrap">
            <video id="trainVideo" autoplay playsinline muted></video>
            <canvas id="trainCanvas"></canvas>
            <div id="recordOverlay" class="recordOverlay">Camera off — tap Start Camera</div>
          </div>
          <div class="statusRow">
            <span id="trainCamStatus" class="pill">● Camera off</span>
            <span id="trainHandStatus" class="pill">● Waiting for hand</span>
            <span class="pill on">✋ Hand data only</span>
          </div>
          <div class="controls"><button id="trainStartBtn" class="btn primary">Start Camera</button></div><div class="note" style="margin-top:8px">Only normalized hand-landmark sequences are stored for training. No facial data is collected.</div>'''
if old_train not in s:
    raise SystemExit('train camera block not found')
s = s.replace(old_train, new_train)

s = s.replace('value=".75"></div>', 'value=".80"></div>')
s = s.replace('BUILD 24 • OFFLINE SETUP BUTTON', 'BUILD 25 • SIGN-ONLY OFFLINE AI')
s = s.replace('No Python. Training runs directly in this browser using a lightweight temporal neural network.', 'No Python. Hand-sign training and recognition run directly in this browser using a lightweight temporal neural network.')

# ----- JS: remove all face inference/privacy code -----
s = s.replace(
'import {HandLandmarker, FaceLandmarker, FilesetResolver, DrawingUtils} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm";',
'import {HandLandmarker, FilesetResolver, DrawingUtils} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm";')
s = s.replace(
'let handLandmarker,faceLandmarker,stream,ctx,drawing,trainCtx,trainDrawing,model=null,labels=[],dataset=JSON.parse(localStorage.getItem("svx-data")||"[]");',
'let handLandmarker,stream,ctx,drawing,trainCtx,trainDrawing,model=null,labels=[],dataset=JSON.parse(localStorage.getItem("svx-data")||"[]");')
s = s.replace(
'let liveBuffer=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true, lastExpressionAt=0, latestFaceLandmarks=[];',
'let liveBuffer=[], predictionHistory=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true;')
s = s.replace('const SEQ=24, FEAT=126;', 'const SEQ=24, FEAT=126, PRED_WINDOW=3;')

# Remove face privacy + expression toggle state/functions.
s, n = re.subn(r'let facePrivacyEnabled=.*?syncExpressionToggle\(\);\n', '', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('face toggle block not removed')

# Replace landmarker initialization and delete expression helper functions.
pattern = r'async function initLandmarker\(\)\{.*?\n\}\nfunction blendshapeScore\(categories,name\)\{.*?\n\}\nfunction updateExpression\(faceResult\)\{.*?\n\}\nasync function startCamera\(\)\{'
replacement = '''async function initLandmarker(){
 if(handLandmarker)return;
 const vision=await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm");
 handLandmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.55,minHandPresenceConfidence:.55,minTrackingConfidence:.5});
}
async function startCamera(){'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('landmarker/expression block not replaced')

# Remove face inference and mesh drawing from the live loop.
loop_pattern = r' const now=performance\.now\(\),r=handLandmarker\.detectForVideo\(\$\("video"\),now\);.*? handVisible=!!r\.landmarks\?\.length;'
loop_repl = ''' const now=performance.now(),r=handLandmarker.detectForVideo($("video"),now);
 ctx.clearRect(0,0,$("canvas").width,$("canvas").height);
 trainCtx.clearRect(0,0,$("trainCanvas").width,$("trainCanvas").height);
 handVisible=!!r.landmarks?.length;'''
s, n = re.subn(loop_pattern, loop_repl, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('live face inference block not removed')

# Clear temporal buffers when the hand disappears to reduce stale predictions.
s = s.replace(
''' } else {
   $("handStatus").textContent="● Waiting for hand";$("handStatus").classList.remove("on");
   $("trainHandStatus").textContent="● Waiting for hand";$("trainHandStatus").classList.remove("on");
 }
 const f=featureFrom(r);''',
''' } else {
   $("handStatus").textContent="● Waiting for hand";$("handStatus").classList.remove("on");
   $("trainHandStatus").textContent="● Waiting for hand";$("trainHandStatus").classList.remove("on");
   if(liveBuffer.length || predictionHistory.length){
     liveBuffer=[]; predictionHistory=[]; autoSpeakArmed=true;
     currentPrediction="READY"; currentConfidence=0;
     $("word").textContent="READY"; $("conf").textContent="Show a trained hand sign";
     $("ringText").textContent="0%"; $("ring").style.background="conic-gradient(#45e6ff 0deg,#16304a 0)";
   }
 }
 const f=featureFrom(r);''')

# More reliable prediction: require agreement across recent temporal predictions.
old_predict = '''   let idx=0;
   for(let i=1;i<p.length;i++) if(p[i]>p[idx]) idx=i;
   const conf=p[idx];
   const th=parseFloat($("threshold").value)||.75;
   setPrediction(conf>=th?(labels[idx]||"UNKNOWN"):"UNKNOWN",conf);
   inferenceErrors=0;'''
new_predict = '''   let idx=0;
   for(let i=1;i<p.length;i++) if(p[i]>p[idx]) idx=i;
   const conf=p[idx];
   const th=parseFloat($("threshold").value)||.80;
   const candidate=conf>=th?(labels[idx]||"UNKNOWN"):"UNKNOWN";
   if(candidate==="UNKNOWN"){
     predictionHistory=[];
     setPrediction("UNKNOWN",conf);
   }else{
     predictionHistory.push({name:candidate,conf});
     if(predictionHistory.length>PRED_WINDOW) predictionHistory.shift();
     const same=predictionHistory.filter(x=>x.name===candidate);
     if(same.length>=2){
       const avg=same.reduce((a,x)=>a+x.conf,0)/same.length;
       setPrediction(candidate,avg);
     }else{
       currentPrediction="READY"; currentConfidence=conf;
       $("word").textContent="VERIFYING";
       $("conf").textContent="Hold the sign steady • "+(conf*100).toFixed(1)+"%";
       const pct=Math.round(conf*100);
       $("ringText").textContent=pct+"%";
       $("ring").style.background="conic-gradient(#45e6ff "+pct*3.6+"deg,#16304a 0)";
     }
   }
   inferenceErrors=0;'''
if old_predict not in s:
    raise SystemExit('prediction block not found')
s = s.replace(old_predict, new_predict)

# Remove old face-related button handlers and forced privacy hiding.
old_handlers = '''$("startBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));
$("privacyBtn").onclick=toggleFacePrivacy;
$("expressionToggleBtn").onclick=toggleExpression;
$("trainPrivacyBtn").onclick=toggleFacePrivacy;
$("trainExpressionToggleBtn").onclick=toggleExpression;
syncFacePrivacy();
$("offlineBtn").onclick=()=>{location.href="./offline.html"};
if($("headerOfflineBtn")) $("headerOfflineBtn").onclick=()=>{location.href="./offline.html"};
$("trainStartBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));
$("cameraWrap").classList.add("privacy");
$("trainCameraWrap").classList.add("privacy");'''
new_handlers = '''$("startBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));
$("offlineBtn").onclick=()=>{location.href="./offline.html"};
if($("headerOfflineBtn")) $("headerOfflineBtn").onclick=()=>{location.href="./offline.html"};
$("trainStartBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));'''
if old_handlers not in s:
    raise SystemExit('handler block not found')
s = s.replace(old_handlers, new_handlers)
s = s.replace('$("clearBtn").onclick=()=>{phrase=[];autoSpeakArmed=true;autoSpeakLastLabel="";updatePhrase();setPrediction("READY",0)};', '$("clearBtn").onclick=()=>{phrase=[];predictionHistory=[];autoSpeakArmed=true;autoSpeakLastLabel="";updatePhrase();setPrediction("READY",0)};')

# Invalidate the trained model whenever the dataset changes, preventing stale model/data mismatch.
old_mark = '''function markDatasetChanged(){
 localStorage.setItem("svx-data",JSON.stringify(dataset));
 $("trainText").textContent="Dataset changed — retrain AI.";
 $("modelStatus").textContent="● Retrain needed";
 $("modelStatus").classList.remove("on");
}'''
new_mark = '''function markDatasetChanged(){
 localStorage.setItem("svx-data",JSON.stringify(dataset));
 model=null; labels=[]; liveBuffer=[]; predictionHistory=[];
 localStorage.removeItem("svx-labels");
 if(window.tf && tf.io?.removeModel) tf.io.removeModel("indexeddb://silentvoice-x").catch(()=>{});
 $("trainText").textContent="Dataset changed — retrain AI.";
 $("modelStatus").textContent="● Retrain needed";
 $("modelStatus").classList.remove("on");
 $("word").textContent="READY"; $("conf").textContent="Dataset changed — retrain AI";
}'''
if old_mark not in s:
    raise SystemExit('dataset invalidation block not found')
s = s.replace(old_mark, new_mark)

# New offline preparation marker.
s = s.replace('svx-offline-prepared-v3', 'svx-offline-prepared-v4')

idx.write_text(s, encoding='utf-8')

# ----- Service worker: hand-sign assets only -----
sw = Path('sw.js')
w = sw.read_text(encoding='utf-8')
w = re.sub(r"const CACHE_NAME = 'silentvoicex-offline-v\d+';", "const CACHE_NAME = 'silentvoicex-offline-v8';", w)
w = w.replace("  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',\n", '')
sw.write_text(w, encoding='utf-8')

# ----- Offline setup page: sign-only messaging/assets -----
off = Path('offline.html')
o = off.read_text(encoding='utf-8')
o = o.replace('Prepare sign recognition, facial-expression cues, and speech support for use without Wi‑Fi or mobile data. Your recorded samples and trained model stay on this device.', 'Prepare hand-sign recognition and speech support for use without Wi‑Fi or mobile data. Your recorded hand-landmark samples and trained model stay on this device.')
o = o.replace('This caches both hand-sign AI and facial-expression AI.', 'This caches the hand-sign AI and required browser files.')
o = o.replace("  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',\n", '')
o = o.replace("localStorage.setItem('svx-offline-prepared-v3','1');", "localStorage.setItem('svx-offline-prepared-v4','1');")
o = o.replace("statusEl.textContent='✓ Offline sign + expression AI ready. Open SilentVoiceX and test once before Airplane Mode.';", "statusEl.textContent='✓ Offline hand-sign AI ready. Open SilentVoiceX and test once before Airplane Mode.';")
o = o.replace("localStorage.getItem('svx-offline-prepared-v3')==='1'", "localStorage.getItem('svx-offline-prepared-v4')==='1'")
off.write_text(o, encoding='utf-8')

print('SilentVoiceX converted to sign-only offline build with temporal prediction confirmation.')
