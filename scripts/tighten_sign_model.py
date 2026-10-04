from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

rep('<meta name="apple-mobile-web-app-title" content="SilentVoiceX">\n<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js"></script>',
    '<meta name="apple-mobile-web-app-title" content="SilentVoiceX">\n<meta name="theme-color" content="#07111f">\n<link rel="manifest" href="./manifest.webmanifest">\n<link rel="icon" href="./icon.svg" type="image/svg+xml">\n<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js"></script>',
    'manifest links')

rep('<div class="top"><div class="brand"><h1>✋ <span>SilentVoice X</span></h1><p>AI that turns signs into speech</p></div></div>',
    '<div class="top"><div class="brand"><h1>✋ <span>SilentVoice X</span></h1><p>AI that turns signs into speech</p></div><button id="headerOfflineBtn" class="btn primary">📴 Offline Setup</button></div>',
    'header offline button')

rep('<div class="controls"><button id="startBtn" class="btn primary">Start Camera</button><button id="privacyBtn" class="btn ghost" disabled>🔒 Privacy ON</button><button id="clearBtn" class="btn ghost">Clear</button></div>',
    '<div class="controls"><button id="startBtn" class="btn primary">Start Camera</button><button id="offlineBtn" class="btn ghost">📴 Offline Setup</button><button id="privacyBtn" class="btn ghost" disabled>🔒 Privacy ON</button><button id="clearBtn" class="btn ghost">Clear</button></div>',
    'translate offline button')

rep('<div class="field"><label>Sign label</label><input id="label" value="HELLO" maxlength="24"></div>',
    '<div class="field"><label>Sign label</label><input id="label" value="HELLO" maxlength="24" list="signVocabulary"><datalist id="signVocabulary"><option value="HELLO"><option value="THANK YOU"><option value="YES"><option value="NO"><option value="PLEASE"><option value="HELP"><option value="STOP"><option value="GOOD"><option value="LOVE"><option value="WATER"><option value="FOOD"><option value="HOME"></datalist></div>',
    'sign vocabulary')

rep('<div class="field"><label>Unknown threshold</label><input id="threshold" type="number" min=".5" max=".99" step=".01" value=".75"></div>',
    '<div class="field"><label>Recognition threshold</label><input id="threshold" type="number" min=".5" max=".99" step=".01" value=".80"></div>',
    'threshold default')

rep('<p class="note"><b>Important:</b> every participant should record the <b>same sign labels</b>. Example: P001 records HELLO, GOOD, HEART; P002 records HELLO, GOOD, HEART; P003 records HELLO, GOOD, HEART. Use P003 only as the unseen test signer.</p>',
    '<p class="note"><b>Accuracy rule:</b> train at least <b>3 different signs</b>. Each sign needs at least <b>8 training samples</b> outside the hold-out participant and must be recorded by at least <b>2 training participants</b>. Use the same labels for every participant. The suggested labels above are optional; you can type your own sign label.</p>',
    'accuracy guidance')

rep('<div class="rocket">🚀</div><h2>Train AI in your browser</h2><div class="smallcap" style="margin-bottom:8px">PRE-FACE BUILD • LANDMARKS 0.50 • AUTO-SPEAK ONCE</div><p class="note">No Python. Training runs directly in this browser using a lightweight temporal neural network.</p>',
    '<div class="rocket">🚀</div><h2>Train AI in your browser</h2><div class="smallcap" style="margin-bottom:8px">ACCURACY BUILD • 3+ SIGNS • 8+ SAMPLES/SIGN • OFFLINE</div><p class="note">No Python. Training uses a stronger temporal Conv1D model with stratified validation, dropout, batch normalization and early stopping. More varied samples usually improve signer-independent accuracy.</p>',
    'build label')

rep('let liveBuffer=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true;\nlet selectedRecordIndexes=new Set();\nconst SEQ=24, FEAT=126;',
    'let liveBuffer=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true;\nlet selectedRecordIndexes=new Set();\nconst SEQ=24, FEAT=126, MIN_SIGNS=3, MIN_TRAIN_PER_SIGN=8, MIN_TRAIN_PARTICIPANTS=2;',
    'training constants')

rep('$("startBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));\n$("trainStartBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));',
    '$("startBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));\n$("trainStartBtn").onclick=()=>startCamera().catch(e=>alert("Camera could not start: "+e.message));\n$("headerOfflineBtn").onclick=()=>{location.href="./offline.html"};\n$("offlineBtn").onclick=()=>{location.href="./offline.html"};',
    'offline handlers')

old_model='''function buildModel(n){
 const m=tf.sequential();
 m.add(tf.layers.conv1d({filters:16,kernelSize:3,padding:"same",activation:"relu",inputShape:[SEQ,FEAT]}));
 m.add(tf.layers.maxPooling1d({poolSize:2}));
 m.add(tf.layers.conv1d({filters:24,kernelSize:3,padding:"same",activation:"relu"}));
 m.add(tf.layers.globalAveragePooling1d());
 m.add(tf.layers.dropout({rate:.15}));
 m.add(tf.layers.dense({units:20,activation:"relu"}));
 m.add(tf.layers.dense({units:n,activation:"softmax"}));
 m.compile({optimizer:tf.train.adam(.001),loss:"categoricalCrossentropy",metrics:["accuracy"]});
 return m;
}'''
new_model='''function buildModel(n){
 const m=tf.sequential();
 m.add(tf.layers.conv1d({filters:32,kernelSize:5,padding:"same",activation:"relu",inputShape:[SEQ,FEAT]}));
 m.add(tf.layers.batchNormalization());
 m.add(tf.layers.maxPooling1d({poolSize:2}));
 m.add(tf.layers.conv1d({filters:64,kernelSize:3,padding:"same",activation:"relu"}));
 m.add(tf.layers.batchNormalization());
 m.add(tf.layers.globalAveragePooling1d());
 m.add(tf.layers.dropout({rate:.25}));
 m.add(tf.layers.dense({units:64,activation:"relu"}));
 m.add(tf.layers.dropout({rate:.20}));
 m.add(tf.layers.dense({units:n,activation:"softmax"}));
 m.compile({optimizer:tf.train.adam(.0007),loss:"categoricalCrossentropy",metrics:["accuracy"]});
 return m;
}'''
rep(old_model,new_model,'stronger model')

rep('if(labels.length<2){alert("Record at least 2 different sign labels first.");return}',
    'if(labels.length<MIN_SIGNS){alert("Record at least "+MIN_SIGNS+" different sign labels before training. Add more signs first.");return}',
    'minimum signs')

rep('if(Math.min(...Object.values(counts))<4){alert("Collect at least 4 samples for every sign before training.");return}',
    'if(Math.min(...Object.values(counts))<MIN_TRAIN_PER_SIGN){alert("Collect at least "+MIN_TRAIN_PER_SIGN+" samples for every sign before training.");return}',
    'minimum total samples')

rep('const test=dataset.filter(x=>x.participant===hold);\n   const trainLabels=new Set(trainAll.map(x=>x.label));',
    'const test=dataset.filter(x=>x.participant===hold);\n   const trainingParticipants=[...new Set(trainAll.map(x=>x.participant).filter(Boolean))];\n   if(trainingParticipants.length<MIN_TRAIN_PARTICIPANTS){alert("Use at least "+MIN_TRAIN_PARTICIPANTS+" training participants outside the hold-out participant for better generalization.");return}\n   const participantCoverageProblems=labels.filter(l=>new Set(trainAll.filter(x=>x.label===l).map(x=>x.participant)).size<MIN_TRAIN_PARTICIPANTS);\n   if(participantCoverageProblems.length){alert("Each sign must be recorded by at least "+MIN_TRAIN_PARTICIPANTS+" training participants. Add more samples for: "+participantCoverageProblems.join(", "));return}\n   const trainLabels=new Set(trainAll.map(x=>x.label));',
    'participant coverage')

rep('if(Math.min(...Object.values(perLabelTrain))<4){alert("Each sign needs at least 4 training samples outside the hold-out participant.");return}',
    'if(Math.min(...Object.values(perLabelTrain))<MIN_TRAIN_PER_SIGN){alert("Each sign needs at least "+MIN_TRAIN_PER_SIGN+" training samples outside the hold-out participant.");return}',
    'minimum train samples')

rep('const nVal=Math.max(1,Math.floor(items.length*.2));',
    'const nVal=Math.max(2,Math.floor(items.length*.2));',
    'validation size')

rep('const EPOCHS=15;\n   await model.fit(T.x,T.y,{\n     epochs:EPOCHS,\n     batchSize:Math.min(6,tr.length),\n     validationData:[V.x,V.y],\n     shuffle:true,\n     callbacks:{\n       onTrainBegin:async()=>{$("trainText").textContent="Training started…";await tf.nextFrame()},\n       onEpochEnd:async(e,l)=>{\n         const acc=(l.acc??l.accuracy??0)*100;\n         const vacc=(l.val_acc??l.val_accuracy??0)*100;\n         $("bar").style.width=((e+1)/EPOCHS*100)+"%";\n         $("trainText").textContent="Epoch "+(e+1)+"/"+EPOCHS+" • accuracy "+acc.toFixed(1)+"% • validation "+vacc.toFixed(1)+"%";\n         await tf.nextFrame();\n       }\n     }\n   });',
    'const EPOCHS=35;\n   await model.fit(T.x,T.y,{\n     epochs:EPOCHS,\n     batchSize:Math.min(8,tr.length),\n     validationData:[V.x,V.y],\n     shuffle:true,\n     callbacks:[\n       tf.callbacks.earlyStopping({monitor:"val_loss",patience:5,restoreBestWeights:true}),\n       {\n         onTrainBegin:async()=>{$("trainText").textContent="Training stronger model…";await tf.nextFrame()},\n         onEpochEnd:async(e,l)=>{\n           const acc=(l.acc??l.accuracy??0)*100;\n           const vacc=(l.val_acc??l.val_accuracy??0)*100;\n           $("bar").style.width=((e+1)/EPOCHS*100)+"%";\n           $("trainText").textContent="Epoch "+(e+1)+"/"+EPOCHS+" • accuracy "+acc.toFixed(1)+"% • validation "+vacc.toFixed(1)+"%";\n           await tf.nextFrame();\n         }\n       }\n     ]\n   });',
    'training schedule')

# Use a new IndexedDB model key so an older weaker model cannot be mistaken for the tightened model.
s=s.replace('indexeddb://silentvoice-x"','indexeddb://silentvoice-x-accurate-v2"')

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
w=sw.read_text(encoding='utf-8')
import re
w=re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'silentvoicex-accuracy-offline-v5';", w, count=1)
sw.write_text(w,encoding='utf-8')
print('patched accuracy training + offline UI')
