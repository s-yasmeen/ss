from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove quick-sign CSS.
s = re.sub(r'\.quickSignPanel\{.*?\.quickSign:hover,\.quickSign\.active\{.*?\}', '', s, flags=re.S)

# Remove datalist and make sign label a simple free-text field.
s = re.sub(
    r'<div class="field"><label>Sign label</label><input id="label"[^>]*><datalist id="signVocabulary">.*?</datalist></div>',
    '<div class="field"><label>Sign label</label><input id="label" value="" maxlength="24" placeholder="Type sign name, e.g. HELLO"></div>',
    s,
    flags=re.S,
)

# Make hold-out optional and blank by default.
s = re.sub(
    r'<div class="field"><label>Hold-out participant for final test</label><input id="holdout" value="[^"]*"></div>',
    '<div class="field"><label>Hold-out participant (optional)</label><input id="holdout" value="" placeholder="Leave blank for normal training"></div>',
    s,
)

# Remove starter sign panel completely.
s = re.sub(r'\s*<div class="quickSignPanel">.*?</div>\s*<div class="controls"><button id="recordBtn"',
           '\n        <div class="controls"><button id="recordBtn"', s, flags=re.S)

# Replace training guidance / banner.
s = re.sub(
    r'<p class="note"><b>Accuracy rule:</b>.*?</p>',
    '<p class="note"><b>Training rule:</b> record at least <b>2 different signs</b> with at least <b>4 real samples per sign</b>. One participant is enough to train. The hold-out participant is optional and is used only if you want an unseen-signer test.</p>',
    s,
    count=1,
    flags=re.S,
)
s = re.sub(
    r'<div class="smallcap" style="margin-bottom:8px">ACCURACY BUILD.*?</div><p class="note">.*?</p>',
    '<div class="smallcap" style="margin-bottom:8px">STABLE TRAINING • 2+ SIGNS • 4+ SAMPLES/SIGN • OFFLINE</div><p class="note">Training uses a compact temporal Conv1D model designed to run reliably in the browser. Validation is separated from training, and the measured result is shown after all 20 epochs.</p>',
    s,
    count=1,
    flags=re.S,
)

# Remove quick-sign JS handler.
s = re.sub(r'\ndocument\.querySelectorAll\("\.quickSign"\)\.forEach\(btn=>\{.*?\n\}\);\n', '\n', s, flags=re.S)

# Relax dataset requirements.
s = s.replace('const SEQ=24, FEAT=126, MIN_SIGNS=3, MIN_TRAIN_PER_SIGN=6, MIN_TRAIN_PARTICIPANTS=2;',
              'const SEQ=24, FEAT=126, MIN_SIGNS=2, MIN_TRAIN_PER_SIGN=4, MIN_TRAIN_PARTICIPANTS=1;')

# Ensure changed datasets invalidate the active/saved simplified model.
old_mark = '''function markDatasetChanged(){
 localStorage.setItem("svx-data",JSON.stringify(dataset));
 $("trainText").textContent="Dataset changed — retrain AI.";
 $("modelStatus").textContent="● Retrain needed";
 $("modelStatus").classList.remove("on");
}'''
new_mark = '''function markDatasetChanged(){
 localStorage.setItem("svx-data",JSON.stringify(dataset));
 if(model){try{model.dispose()}catch(_){ } model=null;}
 labels=[]; liveBuffer=[];
 localStorage.removeItem("svx-labels");
 if(window.tf && tf.io?.removeModel) tf.io.removeModel("indexeddb://silentvoice-x-simple-v3").catch(()=>{});
 $("trainText").textContent="Dataset changed — retrain AI.";
 $("modelStatus").textContent="● Retrain needed";
 $("modelStatus").classList.remove("on");
 $("word").textContent="READY";
 $("conf").textContent="Saved samples changed • tap Train AI";
}'''
if old_mark in s:
    s = s.replace(old_mark, new_mark)

# Use a smaller, more reliable model for small browser datasets.
s = re.sub(
    r'function buildModel\(n\)\{.*?\n\}',
    '''function buildModel(n){
 const m=tf.sequential();
 m.add(tf.layers.conv1d({filters:24,kernelSize:5,padding:"same",activation:"relu",inputShape:[SEQ,FEAT]}));
 m.add(tf.layers.maxPooling1d({poolSize:2}));
 m.add(tf.layers.conv1d({filters:32,kernelSize:3,padding:"same",activation:"relu"}));
 m.add(tf.layers.globalAveragePooling1d());
 m.add(tf.layers.dropout({rate:.20}));
 m.add(tf.layers.dense({units:32,activation:"relu"}));
 m.add(tf.layers.dense({units:n,activation:"softmax"}));
 m.compile({optimizer:tf.train.adam(.001),loss:"categoricalCrossentropy",metrics:["accuracy"]});
 return m;
}''',
    s,
    count=1,
    flags=re.S,
)

# Replace the restrictive train/holdout checks with a simple optional hold-out path.
pattern = re.compile(r'''   const counts=Object\.fromEntries\(labels\.map\(l=>\[l,dataset\.filter\(x=>x\.label===l\)\.length\]\)\);.*?   const perLabelTrain=Object\.fromEntries\(labels\.map\(l=>\[l,trainAll\.filter\(x=>x\.label===l\)\.length\]\)\);\n   if\(Math\.min\(\.\.\.Object\.values\(perLabelTrain\)\)<MIN_TRAIN_PER_SIGN\)\{alert\("Each sign needs at least "\+MIN_TRAIN_PER_SIGN\+" training samples outside the hold-out participant\."\);return\}\n''', re.S)
replacement = '''   const counts=Object.fromEntries(labels.map(l=>[l,dataset.filter(x=>x.label===l).length]));
   if(Math.min(...Object.values(counts))<MIN_TRAIN_PER_SIGN){alert("Collect at least "+MIN_TRAIN_PER_SIGN+" samples for every sign before training.");return}
   const hold=$("holdout").value.trim();
   const test=hold?dataset.filter(x=>x.participant===hold):[];
   const trainAll=hold?dataset.filter(x=>x.participant!==hold):dataset.slice();
   if(!trainAll.length){alert("No training samples remain. Clear the hold-out field or choose a different hold-out participant.");return}
   const perLabelTrain=Object.fromEntries(labels.map(l=>[l,trainAll.filter(x=>x.label===l).length]));
   const missingTrain=labels.filter(l=>(perLabelTrain[l]||0)<MIN_TRAIN_PER_SIGN);
   if(missingTrain.length){alert("Need at least "+MIN_TRAIN_PER_SIGN+" training samples for: "+missingTrain.join(", ")+". Clear the hold-out field if those samples were excluded.");return}
'''
s, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit('Could not replace restrictive training checks')

# Use one validation sample per sign so 4-sample classes still have 3 training samples.
s = s.replace('const nVal=Math.max(2,Math.floor(items.length*.2));', 'const nVal=Math.max(1,Math.floor(items.length*.2));')

# Smaller batch for tiny datasets.
s = s.replace('batchSize:Math.min(8,tr.length),', 'batchSize:Math.min(4,tr.length),')

# Improve training copy.
s = s.replace('Training model — fixed 20 epochs…', 'Training model — 20 epochs…')

# Save/load under a fresh model key so an older incompatible model is never mistaken for this one.
s = s.replace('indexeddb://silentvoice-x-accurate-v2', 'indexeddb://silentvoice-x-simple-v3')

# Results wording when hold-out is not used.
s = s.replace('"\\nHeld-out signer: "+hold+" ("+test.length+" samples)',
              '"\\nHeld-out signer: "+(hold||"not used")+" ("+test.length+" samples)')

p.write_text(s, encoding='utf-8')

# Bump cache so phones do not keep serving the old restrictive build.
sw = Path('sw.js')
sw_text = sw.read_text(encoding='utf-8')
sw_text = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'silentvoicex-simple-training-v7';", sw_text, count=1)
sw.write_text(sw_text, encoding='utf-8')
