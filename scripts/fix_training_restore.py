from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '''async function loadSaved(){try{model=await tf.loadLayersModel("indexeddb://silentvoice-x");labels=JSON.parse(localStorage.getItem("svx-labels")||"[]");if(labels.length){$("modelStatus").textContent="● Saved AI loaded ("+labels.length+" signs)";$("modelStatus").classList.add("on");$("word").textContent="READY";$("conf").textContent="AI trained — start camera"}}catch(e){}}'''

new = '''async function loadSaved(){
 const key="indexeddb://silentvoice-x";
 $("modelStatus").textContent="● Checking saved AI…";
 try{
   await tf.ready();
   const models=await tf.io.listModels();
   if(!models[key]){
     model=null; labels=[];
     if(dataset.length){
       const recovered=[...new Set(dataset.map(x=>x.label))].sort();
       $("modelStatus").textContent="● Training data found — retrain AI";
       $("modelStatus").classList.remove("on");
       $("word").textContent="READY";
       $("conf").textContent="Saved samples found • model needs retraining";
       $("trainText").textContent=dataset.length+" saved samples across "+recovered.length+" signs found — tap TRAIN SILENTVOICE X once to restore recognition.";
     }else{
       $("modelStatus").textContent="● Model not trained";
       $("modelStatus").classList.remove("on");
     }
     return;
   }

   model=await tf.loadLayersModel(key);
   let savedLabels=[];
   try{savedLabels=JSON.parse(localStorage.getItem("svx-labels")||"[]")}catch(_){savedLabels=[]}
   const lastLayer=model.layers[model.layers.length-1];
   const outputUnits=Number(lastLayer?.units||0);

   if(!savedLabels.length || (outputUnits && savedLabels.length!==outputUnits)){
     const recovered=[...new Set(dataset.map(x=>x.label))].sort();
     if(recovered.length && (!outputUnits || recovered.length===outputUnits)){
       savedLabels=recovered;
       localStorage.setItem("svx-labels",JSON.stringify(savedLabels));
     }
   }

   if(!savedLabels.length || (outputUnits && savedLabels.length!==outputUnits)){
     if(model){model.dispose();model=null}
     labels=[];
     $("modelStatus").textContent="● Saved AI needs retraining";
     $("modelStatus").classList.remove("on");
     $("conf").textContent="Training labels could not be restored";
     $("trainText").textContent="Your saved samples are still here. Tap TRAIN SILENTVOICE X to rebuild the recognition model.";
     return;
   }

   labels=savedLabels;
   $("modelStatus").textContent="● Saved AI restored ("+labels.length+" signs)";
   $("modelStatus").classList.add("on");
   $("word").textContent="READY";
   $("conf").textContent="AI trained — start camera";
   $("trainText").textContent="✓ Saved training model restored";
 }catch(e){
   console.error("Saved AI restore failed",e);
   model=null; labels=[];
   $("modelStatus").textContent=dataset.length?"● Training data found — retrain AI":"● Model not trained";
   $("modelStatus").classList.remove("on");
   if(dataset.length){
     $("conf").textContent="Saved samples found • tap Train AI";
     $("trainText").textContent=dataset.length+" saved samples are available. Tap TRAIN SILENTVOICE X to rebuild the model.";
   }
 }
}'''

if old not in s:
    raise SystemExit('Expected loadSaved function not found')
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
w = sw.read_text(encoding='utf-8')
w = w.replace("const CACHE_NAME = 'silentvoicex-offline-v1';", "const CACHE_NAME = 'silentvoicex-pre-face-restore-v2';")
sw.write_text(w, encoding='utf-8')

# Validate the browser module separately.
import re
scripts = re.findall(r'<script type="module">(.*?)</script>', s, re.S)
if len(scripts) != 1:
    raise SystemExit('Expected exactly one module script')
Path('/tmp/svx-restore.mjs').write_text(scripts[0], encoding='utf-8')
