from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Correct stale training banner/copy.
s=s.replace(
    '<div class="smallcap" style="margin-bottom:8px">STABLE BUILD • 20 EPOCHS • 6+ SAMPLES/SIGN • OFFLINE</div><p class="note">No Python. Training uses a temporal Conv1D model with stratified validation, dropout and batch normalization. It now runs a fixed 20 epochs so training cannot stop itself early. More varied samples usually improve signer-independent accuracy.</p>',
    '<div class="smallcap" style="margin-bottom:8px">STABLE TRAINING • 2+ SIGNS • 4+ SAMPLES/SIGN • OFFLINE</div><p class="note">Training uses a compact temporal Conv1D model and a fixed 20-epoch run. Older incompatible recordings are ignored automatically instead of stopping training.</p>'
)

# Add a strict compatibility check for saved samples from older builds.
anchor='''function tensors(items,labelList){'''
helper='''function isCompatibleSample(item){
 if(!item || !Array.isArray(item.seq) || item.seq.length!==SEQ) return false;
 return item.seq.every(frame=>Array.isArray(frame) && frame.length===FEAT && frame.every(v=>Number.isFinite(v)));
}
function tensors(items,labelList){'''
if anchor in s and 'function isCompatibleSample' not in s:
    s=s.replace(anchor,helper,1)

old='''   labels=[...new Set(dataset.map(x=>x.label))].sort();
   if(labels.length<MIN_SIGNS){alert("Record at least "+MIN_SIGNS+" different sign labels before training. Add more signs first.");return}
   const counts=Object.fromEntries(labels.map(l=>[l,dataset.filter(x=>x.label===l).length]));
   if(Math.min(...Object.values(counts))<MIN_TRAIN_PER_SIGN){alert("Collect at least "+MIN_TRAIN_PER_SIGN+" samples for every sign before training.");return}
   const hold=$("holdout").value.trim();
   const test=hold?dataset.filter(x=>x.participant===hold):[];
   const trainAll=hold?dataset.filter(x=>x.participant!==hold):dataset.slice();'''
new='''   const compatible=dataset.filter(isCompatibleSample);
   const ignored=dataset.length-compatible.length;
   labels=[...new Set(compatible.map(x=>x.label))].sort();
   if(ignored){$("trainText").textContent=ignored+" older incompatible sample"+(ignored===1?"":"s")+" ignored safely.";}
   if(labels.length<MIN_SIGNS){alert("Record at least "+MIN_SIGNS+" different sign labels with compatible hand recordings before training.");return}
   const counts=Object.fromEntries(labels.map(l=>[l,compatible.filter(x=>x.label===l).length]));
   if(Math.min(...Object.values(counts))<MIN_TRAIN_PER_SIGN){alert("Collect at least "+MIN_TRAIN_PER_SIGN+" compatible samples for every sign before training.");return}
   const hold=$("holdout").value.trim();
   const test=hold?compatible.filter(x=>x.participant===hold):[];
   const trainAll=hold?compatible.filter(x=>x.participant!==hold):compatible.slice();'''
if old not in s:
    raise SystemExit('Training preflight block not found')
s=s.replace(old,new,1)

# Make the final completion text mention ignored legacy samples when relevant.
s=s.replace('$("trainText").textContent="✓ Training complete";', '$("trainText").textContent="✓ Training complete"+(ignored?" • "+ignored+" old incompatible sample"+(ignored===1?"":"s")+" ignored":"");',1)

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
t=sw.read_text(encoding='utf-8')
t=re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'silentvoicex-compatible-training-v8';", t, count=1)
sw.write_text(t,encoding='utf-8')
