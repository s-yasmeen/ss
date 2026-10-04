from pathlib import Path

p = Path('index.html')
s = p.read_text()

s = s.replace('🔊 Auto-speak ≥80%', '🔊 Auto-speak once')
s = s.replace('BUILD 15 • AUTO SPEAK 80%', 'PRE-FACE BUILD • AUTO-SPEAK ONCE')

old_no_hand = ''' } else {
   $("handStatus").textContent="● Waiting for hand";$("handStatus").classList.remove("on");
   $("trainHandStatus").textContent="● Waiting for hand";$("trainHandStatus").classList.remove("on");
 }
 const f=featureFrom(r);'''
new_no_hand = ''' } else {
   $("handStatus").textContent="● Waiting for hand";$("handStatus").classList.remove("on");
   $("trainHandStatus").textContent="● Waiting for hand";$("trainHandStatus").classList.remove("on");
   // A real hand removal starts a new sign episode.
   liveBuffer=[];
   autoSpeakArmed=true;
   autoSpeakLastLabel="";
   if(currentPrediction!=="READY"){
     currentPrediction="READY";
     currentConfidence=0;
     $("word").textContent="READY";
     $("conf").textContent=model&&labels.length?"Show a trained sign":"Train the AI first";
     $("ringText").textContent="0%";
     $("ring").style.background="conic-gradient(#45e6ff 0deg,#16304a 0)";
   }
 }
 const f=featureFrom(r);'''
if old_no_hand not in s:
    raise SystemExit('No-hand block not found')
s = s.replace(old_no_hand, new_no_hand)

old_auto = ''' // Auto-speak only for a confident accepted sign.
 if(name!=="READY" && name!=="UNKNOWN" && conf>=0.80){
   if(autoSpeakArmed || autoSpeakLastLabel!==name){
     autoSpeakLastLabel=name;
     autoSpeakArmed=false;
     speakText(name);
   }
 }else if(conf<0.70 || name==="UNKNOWN" || name==="READY"){
   // Re-arm after the user changes/removes the gesture.
   autoSpeakArmed=true;
 }
}'''
new_auto = ''' // Speak automatically once as soon as the model accepts a sign.
 // The recognition threshold itself decides whether a sign is accepted.
 if(name!=="READY" && name!=="UNKNOWN"){
   if(autoSpeakArmed || autoSpeakLastLabel!==name){
     autoSpeakLastLabel=name;
     autoSpeakArmed=false;
     speakText(name);
   }
 }
}'''
if old_auto not in s:
    raise SystemExit('Auto-speak block not found')
s = s.replace(old_auto, new_auto)

p.write_text(s)

sw = Path('sw.js')
if sw.exists():
    t = sw.read_text()
    t = t.replace("silentvoicex-pre-face-restore-v2", "silentvoicex-pre-face-autospeak-v3")
    sw.write_text(t)

# Validate the important contract text exists.
assert '🔊 Auto-speak once' in s
assert 'speakText(name);' in s
assert 'autoSpeakArmed=true;' in s
