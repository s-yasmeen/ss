from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Keep the most recent facial landmarks so the privacy-safe face mesh stays visible
# between the lower-frequency facial-expression inference passes.
s=s.replace(
    'autoSpeakLastLabel="", autoSpeakArmed=true, lastExpressionAt=0;',
    'autoSpeakLastLabel="", autoSpeakArmed=true, lastExpressionAt=0, latestFaceLandmarks=[];',
    1
)

# Add a visible face-detection status to the training preview.
if 'id="trainFaceStatus"' not in s:
    anchor='<span id="trainHandStatus" class="pill">● Waiting for hand</span>'
    replacement=anchor+'\n            <span id="trainFaceStatus" class="pill">🙂 Waiting for face</span>'
    if anchor not in s:
        raise SystemExit('Missing train hand status anchor')
    s=s.replace(anchor,replacement,1)

old=''' if(faceLandmarker && now-lastExpressionAt>220){
   lastExpressionAt=now;
   try{updateExpression(faceLandmarker.detectForVideo($("video"),now));}
   catch(err){console.warn("Expression inference error",err)}
 }
 ctx.clearRect(0,0,$("canvas").width,$("canvas").height);
 trainCtx.clearRect(0,0,$("trainCanvas").width,$("trainCanvas").height);'''
new=''' if(faceLandmarker && now-lastExpressionAt>220){
   lastExpressionAt=now;
   try{
     const faceResult=faceLandmarker.detectForVideo($("video"),now);
     latestFaceLandmarks=faceResult?.faceLandmarks?.[0]||[];
     updateExpression(faceResult);
     if(latestFaceLandmarks.length){
       $("expressionStatus").textContent="🙂 Face detected";
       $("expressionStatus").classList.add("on");
       if($("trainFaceStatus")){
         $("trainFaceStatus").textContent="🙂 Face detected";
         $("trainFaceStatus").classList.add("on");
       }
     }else{
       $("expressionStatus").textContent="🙂 Waiting for face";
       $("expressionStatus").classList.remove("on");
       if($("trainFaceStatus")){
         $("trainFaceStatus").textContent="🙂 Waiting for face";
         $("trainFaceStatus").classList.remove("on");
       }
     }
   }catch(err){console.warn("Expression inference error",err)}
 }
 ctx.clearRect(0,0,$("canvas").width,$("canvas").height);
 trainCtx.clearRect(0,0,$("trainCanvas").width,$("trainCanvas").height);
 if(latestFaceLandmarks.length){
   // Privacy-safe visualization: landmark points only; raw face pixels remain hidden.
   drawing.drawLandmarks(latestFaceLandmarks,{color:"#a78bfa",radius:1.25});
   trainDrawing.drawLandmarks(latestFaceLandmarks,{color:"#a78bfa",radius:1.25});
 }'''
if old not in s:
    raise SystemExit('Missing face inference loop anchor')
s=s.replace(old,new,1)

# Make the privacy purpose explicit on screen.
s=s.replace('🔒 PRIVACY MODE</div>','🔒 PRIVACY MODE • FACE MESH</div>',1)
s=s.replace('🔒 PRIVACY MODE</div>','🔒 PRIVACY MODE • FACE MESH</div>',1)

for old_build in [
    'BUILD 20 • CONFIDENCE 80–100%',
    'BUILD 19 • OFFLINE + EXPRESSION'
]:
    if old_build in s:
        s=s.replace(old_build,'BUILD 21 • PRIVACY FACE MESH',1)
        break

p.write_text(s,encoding='utf-8')

# Refresh the offline application shell so installed phones receive the face-mesh UI.
swp=Path('sw.js')
sw=swp.read_text(encoding='utf-8')
for old_cache in ['silentvoicex-offline-v3','silentvoicex-offline-v4']:
    sw=sw.replace(old_cache,'silentvoicex-offline-v5')
swp.write_text(sw,encoding='utf-8')
