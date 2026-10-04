from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Missing expected pattern: {label}')
    s = s.replace(old, new, 1)

replace_once(
    'import {HandLandmarker, FilesetResolver, DrawingUtils} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm";',
    'import {HandLandmarker, FaceLandmarker, FilesetResolver, DrawingUtils} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/+esm";',
    'MediaPipe import'
)

replace_once(
    'let handLandmarker,stream,ctx,drawing,trainCtx,trainDrawing,model=null,labels=[],dataset=JSON.parse(localStorage.getItem("svx-data")||"[]");',
    'let handLandmarker,faceLandmarker,stream,ctx,drawing,trainCtx,trainDrawing,model=null,labels=[],dataset=JSON.parse(localStorage.getItem("svx-data")||"[]");',
    'global detector variables'
)

replace_once(
    'let liveBuffer=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true;',
    'let liveBuffer=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true, lastExpressionAt=0;',
    'state variables'
)

old_status = '<div class="statusRow"><span id="camStatus" class="pill">● Camera off</span><span id="handStatus" class="pill">● Waiting for hand</span><span id="modelStatus" class="pill">● Model not trained</span><span class="pill on">🔒 Privacy always on</span><span class="pill on">🔊 Auto-speak ≥80%</span></div>'
new_status = '<div class="statusRow"><span id="camStatus" class="pill">● Camera off</span><span id="handStatus" class="pill">● Waiting for hand</span><span id="modelStatus" class="pill">● Model not trained</span><span id="expressionStatus" class="pill">🙂 Expression waiting</span><span class="pill on">🔒 Privacy always on</span><span class="pill on">🔊 Auto-speak ≥80%</span></div>'
replace_once(old_status, new_status, 'translate status row')

old_sentence = '<div class="sentence"><div id="seq" class="seq">SIGN SEQUENCE: —</div><div id="natural" class="natural">“Your phrase will appear here.”</div></div>'
new_sentence = '<div class="sentence"><div id="seq" class="seq">SIGN SEQUENCE: —</div><div id="natural" class="natural">“Your phrase will appear here.”</div></div><div class="sentence" style="margin-top:10px"><div class="seq">FACIAL EXPRESSION CUE</div><div id="expressionCue" class="natural">—</div><div id="expressionStrength" class="note">Local landmark analysis • not a measure of inner emotion</div></div>'
replace_once(old_sentence, new_sentence, 'expression display card')

old_init = '''async function initLandmarker(){
 if(handLandmarker)return;
 const vision=await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm");
 handLandmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.55,minHandPresenceConfidence:.55,minTrackingConfidence:.5});
}'''

new_init = '''async function initLandmarker(){
 if(handLandmarker)return;
 const vision=await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm");
 handLandmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.55,minHandPresenceConfidence:.55,minTrackingConfidence:.5});
 try{
   faceLandmarker=await FaceLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numFaces:1,outputFaceBlendshapes:true,minFaceDetectionConfidence:.5,minFacePresenceConfidence:.5,minTrackingConfidence:.5});
   $("expressionStatus").textContent="🙂 Expression ready";
   $("expressionStatus").classList.add("on");
 }catch(err){
   console.warn("Expression module unavailable",err);
   $("expressionStatus").textContent="Expression unavailable";
 }
}
function blendshapeScore(categories,name){
 const item=categories.find(x=>x.categoryName===name);
 return item?item.score:0;
}
function updateExpression(faceResult){
 const sets=faceResult?.faceBlendshapes;
 if(!sets?.length){
   $("expressionCue").textContent="No face";
   $("expressionStrength").textContent="Keep your face visible to the camera • processing stays on-device";
   return;
 }
 const c=sets[0].categories||[];
 const smile=(blendshapeScore(c,"mouthSmileLeft")+blendshapeScore(c,"mouthSmileRight"))/2;
 const frown=(blendshapeScore(c,"mouthFrownLeft")+blendshapeScore(c,"mouthFrownRight"))/2;
 const surprise=Math.min(1,(blendshapeScore(c,"jawOpen")+blendshapeScore(c,"browInnerUp"))/2);
 const candidates=[
   {label:"🙂 Smile cue",score:smile},
   {label:"🙁 Frown cue",score:frown},
   {label:"😮 Surprise cue",score:surprise}
 ];
 candidates.sort((a,b)=>b.score-a.score);
 const best=candidates[0];
 if(best.score<0.38){
   $("expressionCue").textContent="😐 Neutral / no strong cue";
   $("expressionStrength").textContent="No strong facial-expression cue detected • local processing";
 }else{
   $("expressionCue").textContent=best.label;
   $("expressionStrength").textContent="Cue strength "+Math.round(best.score*100)+"% • not a measure of inner emotion";
 }
}'''
replace_once(old_init, new_init, 'landmarker initialization')

old_loop = 'const now=performance.now(),r=handLandmarker.detectForVideo($("video"),now);'
new_loop = '''const now=performance.now(),r=handLandmarker.detectForVideo($("video"),now);
 if(faceLandmarker && now-lastExpressionAt>220){
   lastExpressionAt=now;
   try{updateExpression(faceLandmarker.detectForVideo($("video"),now));}
   catch(err){console.warn("Expression inference error",err)}
 }'''
replace_once(old_loop, new_loop, 'live loop expression inference')

for old_build in ['BUILD 15 • AUTO SPEAK 80%','BUILD 16 • AUTO SPEAK 80%']:
    if old_build in s:
        s = s.replace(old_build,'BUILD 18 • EXPRESSION CUES',1)
        break

p.write_text(s, encoding='utf-8')

swp = Path('sw.js')
sw = swp.read_text(encoding='utf-8')
sw = sw.replace("const CACHE_NAME = 'silentvoicex-offline-v1';", "const CACHE_NAME = 'silentvoicex-offline-v2';")
hand_url = "  'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',\n"
face_url = "  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',\n"
if face_url not in sw:
    if hand_url not in sw:
        raise SystemExit('Could not find hand model entry in sw.js')
    sw = sw.replace(hand_url, hand_url + face_url, 1)
swp.write_text(sw, encoding='utf-8')

offp = Path('offline.html')
off = offp.read_text(encoding='utf-8')
if 'face_landmarker/face_landmarker/float16/1/face_landmarker.task' not in off:
    anchor = "  'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',\n"
    off = off.replace(anchor, anchor + "  'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',\n", 1)
offp.write_text(off, encoding='utf-8')
