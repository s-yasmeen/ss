from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Add expression toggle buttons to Translate and Train controls.
old='<button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost">🙂 Face Privacy ON</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="clearBtn" class="btn ghost">Clear</button>'
new='<button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost">🙂 Face Privacy ON</button><button id="expressionToggleBtn" class="btn ghost">🙂 Expression ON</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="clearBtn" class="btn ghost">Clear</button>'
if old in s and 'id="expressionToggleBtn"' not in s:
    s=s.replace(old,new,1)

old2='<div class="controls"><button id="trainStartBtn" class="btn primary">Start Camera</button><button id="trainPrivacyBtn" class="btn ghost">🙂 Face Privacy ON</button></div>'
new2='<div class="controls"><button id="trainStartBtn" class="btn primary">Start Camera</button><button id="trainPrivacyBtn" class="btn ghost">🙂 Face Privacy ON</button><button id="trainExpressionToggleBtn" class="btn ghost">🙂 Expression ON</button></div>'
if old2 in s and 'id="trainExpressionToggleBtn"' not in s:
    s=s.replace(old2,new2,1)

# Add independent expression-analysis state and UI sync.
anchor='let autoSpeakThreshold=Math.min(1,Math.max(.80,parseFloat(localStorage.getItem("svx-auto-speak-threshold")||".80")));'
if 'let expressionEnabled=' not in s:
    block='''let expressionEnabled=localStorage.getItem("svx-expression-enabled")!=="off";
function syncExpressionToggle(){
 const label=expressionEnabled?"🙂 Expression ON":"🙂 Expression OFF";
 const mainBtn=$("expressionToggleBtn"), trainBtn=$("trainExpressionToggleBtn");
 if(mainBtn)mainBtn.textContent=label;
 if(trainBtn)trainBtn.textContent=label;
 if(!expressionEnabled){
   latestFaceLandmarks=[];
   if($("expressionCue"))$("expressionCue").textContent="OFF";
   if($("expressionStrength"))$("expressionStrength").textContent="Facial-expression analysis disabled • no face inference running";
   if($("expressionStatus")){
     $("expressionStatus").textContent="🙂 Expression OFF";
     $("expressionStatus").classList.remove("on");
   }
   if($("trainFaceStatus")){
     $("trainFaceStatus").textContent="🙂 Expression OFF";
     $("trainFaceStatus").classList.remove("on");
   }
 }else{
   if($("expressionStatus") && $("expressionStatus").textContent==="🙂 Expression OFF")$("expressionStatus").textContent="🙂 Expression waiting";
   if($("trainFaceStatus") && $("trainFaceStatus").textContent==="🙂 Expression OFF")$("trainFaceStatus").textContent="🙂 Waiting for face";
   if($("expressionCue") && $("expressionCue").textContent==="OFF")$("expressionCue").textContent="—";
   if($("expressionStrength") && $("expressionStrength").textContent.includes("disabled"))$("expressionStrength").textContent="Local landmark analysis • not a measure of inner emotion";
 }
}
function toggleExpression(){
 expressionEnabled=!expressionEnabled;
 localStorage.setItem("svx-expression-enabled",expressionEnabled?"on":"off");
 syncExpressionToggle();
}
syncExpressionToggle();
'''+anchor
    if anchor not in s: raise SystemExit('auto-speak anchor missing')
    s=s.replace(anchor,block,1)

# Gate face inference and mesh rendering when expression analysis is disabled.
s=s.replace('if(faceLandmarker && now-lastExpressionAt>220){','if(expressionEnabled && faceLandmarker && now-lastExpressionAt>220){',1)
s=s.replace('if(latestFaceLandmarks.length){\n   // Privacy-safe visualization: landmark points only; raw face pixels remain hidden.','if(expressionEnabled && latestFaceLandmarks.length){\n   // Privacy-safe visualization: landmark points only; raw face pixels remain hidden.',1)

# Hook both toggle buttons.
handler_anchor='$("privacyBtn").onclick=toggleFacePrivacy;'
if '$("expressionToggleBtn").onclick=toggleExpression;' not in s:
    if handler_anchor in s:
        s=s.replace(handler_anchor,handler_anchor+'\n$("expressionToggleBtn").onclick=toggleExpression;',1)
    else:
        # Fallback near offline button handler.
        anchor2='$("offlineBtn").onclick=()=>{location.href="./offline.html"};'
        if anchor2 not in s: raise SystemExit('handler anchor missing')
        s=s.replace(anchor2,'$("expressionToggleBtn").onclick=toggleExpression;\n'+anchor2,1)

handler_anchor2='$("trainPrivacyBtn").onclick=toggleFacePrivacy;'
if '$("trainExpressionToggleBtn").onclick=toggleExpression;' not in s:
    if handler_anchor2 in s:
        s=s.replace(handler_anchor2,handler_anchor2+'\n$("trainExpressionToggleBtn").onclick=toggleExpression;',1)
    else:
        anchor3='$("trainStartBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));'
        if anchor3 not in s: raise SystemExit('train handler anchor missing')
        s=s.replace(anchor3,anchor3+'\n$("trainExpressionToggleBtn").onclick=toggleExpression;',1)

# Update explanatory notes and build marker.
s=s.replace('Face frames are processed in memory only. SilentVoiceX does not upload or save face images/video.','Face frames are processed in memory only when Expression is ON. Turn Expression OFF to stop facial-expression inference. SilentVoiceX does not upload or save face images/video.',1)
s=s.replace('BUILD 22 • FACE PRIVACY TOGGLE','BUILD 23 • EXPRESSION TOGGLE',1)

p.write_text(s,encoding='utf-8')

# Bump offline cache so installed devices receive the new controls.
swp=Path('sw.js')
sw=swp.read_text(encoding='utf-8')
sw=sw.replace('silentvoicex-offline-v6','silentvoicex-offline-v7')
swp.write_text(sw,encoding='utf-8')
