from pathlib import Path

p=Path('index.html')
s=p.read_text()

def rep(old,new,name):
    global s
    if old not in s:
        raise SystemExit(f'Missing marker: {name}')
    s=s.replace(old,new,1)

# UI should match actual 70% auto-speak threshold.
s=s.replace('BUILD 15 • AUTO SPEAK 80%','BUILD 15 • AUTO SPEAK 70%')

# Add training lock so background sync never competes with TensorFlow training.
rep(
'''let cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null;''',
'''let cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null, trainingBusy=false;''',
'cloud globals')

# Model is only serialized/uploaded after a successful training run. Ordinary sample changes sync data only.
old_push='''async function pushCloudState(baseVersion=cloudVersion){
 if(!navigator.onLine)return false;
 const portableModel=await capturePortableModel().catch(e=>{console.warn("Shared model capture skipped",e);return null});
 let history=[];try{history=JSON.parse(localStorage.getItem("svx-training-history")||"[]")}catch(_){history=[]}
 const body={baseVersion,dataset:dataset.filter(sampleIsValid),trainedLabels:labels,threshold:parseFloat($("threshold").value)||.75,history,model:portableModel};
 const r=await fetch(SYNC_API,{method:"PUT",headers:{"content-type":"application/json"},body:JSON.stringify(body)});
 if(r.status===409){
   const conflict=await r.json();
   const current=conflict.current||{};
   dataset=mergeSamples(current.dataset,dataset);
   localStorage.setItem("svx-data",JSON.stringify(dataset));
   selectedRecordIndexes.clear();logSamples();
   cloudVersion=Number(current.version||0);localStorage.setItem("svx-cloud-version",String(cloudVersion));
   return await pushCloudState(cloudVersion);
 }
 if(!r.ok)throw new Error("sync write "+r.status);
 const saved=await r.json();
 cloudVersion=Number(saved.version||0);localStorage.setItem("svx-cloud-version",String(cloudVersion));
 localStorage.removeItem("svx-cloud-dirty");
 setCloudStatus("☁ Shared AI • synced",true);
 return true;
}'''
new_push='''async function pushCloudState(baseVersion=cloudVersion,retry=0){
 if(!navigator.onLine||trainingBusy)return false;
 const includeModel=localStorage.getItem("svx-cloud-model-dirty")==="1";
 let history=[];try{history=JSON.parse(localStorage.getItem("svx-training-history")||"[]")}catch(_){history=[]}
 const body={baseVersion,dataset:dataset.filter(sampleIsValid),threshold:parseFloat($("threshold").value)||.75};
 if(includeModel){
   body.model=await capturePortableModel().catch(e=>{console.warn("Shared model capture skipped",e);return null});
   body.trainedLabels=labels;
   body.history=history;
 }
 const r=await fetch(SYNC_API,{method:"PUT",headers:{"content-type":"application/json"},body:JSON.stringify(body)});
 if(r.status===409){
   if(retry>=3)throw new Error("sync conflict — will retry shortly");
   const conflict=await r.json();
   const current=conflict.current||{};
   dataset=mergeSamples(current.dataset,dataset);
   localStorage.setItem("svx-data",JSON.stringify(dataset));
   selectedRecordIndexes.clear();logSamples();
   cloudVersion=Number(current.version||0);localStorage.setItem("svx-cloud-version",String(cloudVersion));
   await sleep(150+retry*200);
   return await pushCloudState(cloudVersion,retry+1);
 }
 if(!r.ok)throw new Error("sync write "+r.status);
 const saved=await r.json();
 cloudVersion=Number(saved.version||0);localStorage.setItem("svx-cloud-version",String(cloudVersion));
 localStorage.removeItem("svx-cloud-dirty");
 if(includeModel)localStorage.removeItem("svx-cloud-model-dirty");
 setCloudStatus("☁ Shared AI • synced",true);
 return true;
}'''
rep(old_push,new_push,'cloud push')

# Sync must pause while training is active.
rep(
'''async function syncCloud(){
 if(cloudBusy)return;
 if(!navigator.onLine){setCloudStatus("☁ Shared AI • offline, changes saved locally",false);return}''',
'''async function syncCloud(){
 if(cloudBusy||trainingBusy)return;
 if(!navigator.onLine){setCloudStatus("☁ Shared AI • offline, changes saved locally",false);return}''',
'sync training guard')

# Replace strict all-label blocker with eligible-label training. Pending/incomplete signs no longer block the model.
old_validation='''   const nextLabels=[...new Set(dataset.filter(sampleIsValid).map(x=>x.label))].sort();
   if(nextLabels.length<2){alert("Record at least 2 different sign labels first.");return}
   const counts=Object.fromEntries(nextLabels.map(l=>[l,dataset.filter(x=>sampleIsValid(x)&&x.label===l).length]));
   if(Math.min(...Object.values(counts))<4){alert("Collect at least 4 samples for every sign before training.");return}
   const hold=$("holdout").value.trim();
   const validData=dataset.filter(sampleIsValid);
   const trainAll=validData.filter(x=>x.participant!==hold);
   const test=validData.filter(x=>x.participant===hold);
   const trainLabels=new Set(trainAll.map(x=>x.label));
   const testLabels=new Set(test.map(x=>x.label));
   const missingTrain=nextLabels.filter(l=>!trainLabels.has(l));
   const missingTest=nextLabels.filter(l=>!testLabels.has(l));
   if(missingTrain.length){alert("Training cannot start yet. These signs exist only in the held-out participant: "+missingTrain.join(", ")+". Record them with a training participant too.");return}
   const perLabelTrain=Object.fromEntries(nextLabels.map(l=>[l,trainAll.filter(x=>x.label===l).length]));
   if(Math.min(...Object.values(perLabelTrain))<4){alert("Each sign needs at least 4 training samples outside the hold-out participant.");return}

   $("trainText").textContent="Building updated AI from all "+trainAll.length+" cumulative training samples…";'''
new_validation='''   const hold=$("holdout").value.trim();
   const validData=dataset.filter(sampleIsValid);
   const allLabels=[...new Set(validData.map(x=>x.label))].sort();
   const trainPool=validData.filter(x=>x.participant!==hold);
   const perLabelTrain=Object.fromEntries(allLabels.map(l=>[l,trainPool.filter(x=>x.label===l).length]));
   const nextLabels=allLabels.filter(l=>(perLabelTrain[l]||0)>=4);
   const pendingLabels=allLabels.filter(l=>(perLabelTrain[l]||0)<4);
   if(nextLabels.length<2){
     const detail=allLabels.length?allLabels.map(l=>l+" "+(perLabelTrain[l]||0)+"/4").join(", "):"no signs recorded";
     alert("Training needs at least 2 ready signs. Each ready sign needs 4 samples outside the hold-out participant. Current: "+detail);
     return;
   }
   const readySet=new Set(nextLabels);
   const trainAll=trainPool.filter(x=>readySet.has(x.label));
   const test=validData.filter(x=>x.participant===hold&&readySet.has(x.label));
   const testLabels=new Set(test.map(x=>x.label));
   const missingTest=nextLabels.filter(l=>!testLabels.has(l));

   trainingBusy=true;
   setCloudStatus("☁ Shared AI • training locally…",false);
   $("trainText").textContent="Building updated AI from "+trainAll.length+" ready cumulative training samples"+(pendingLabels.length?" • pending: "+pendingLabels.join(", "):"")+"…";'''
rep(old_validation,new_validation,'training validation')

# Do not force CPU: prefer existing accelerated backend; only fall back to CPU if no backend is ready.
rep(
'''   await tf.ready();
   try{if(tf.getBackend()!=="cpu"){await tf.setBackend("cpu");await tf.ready();}}catch(e){console.warn("Backend switch skipped",e)}''',
'''   await tf.ready();
   try{if(!tf.getBackend()){await tf.setBackend("cpu");await tf.ready();}}catch(e){console.warn("Backend setup fallback",e)}''',
'tensorflow backend')

# Results should explicitly show pending signs that were not included yet.
rep(
'''   $("resultsLog").textContent="Classes: "+labels.join(", ")+"\\nCumulative samples: "+validData.length+"\\nTrain samples: "+tr.length+"\\nValidation samples: "+va.length+"\\nHeld-out signer: "+(hold||"not used")+" ("+test.length+" samples)"+coverage+"\\nFinal validation accuracy: "+(val==null?"not measured":(val*100).toFixed(1)+"%")+"\\nUnseen-signer accuracy: "+(held==null?"not measured":(held*100).toFixed(1)+"%");''',
'''   $("resultsLog").textContent="Classes trained: "+labels.join(", ")+(pendingLabels.length?"\\nPending signs (need 4 training samples): "+pendingLabels.join(", "):"")+"\\nCumulative samples: "+validData.length+"\\nTrain samples: "+tr.length+"\\nValidation samples: "+va.length+"\\nHeld-out signer: "+(hold||"not used")+" ("+test.length+" samples)"+coverage+"\\nFinal validation accuracy: "+(val==null?"not measured":(val*100).toFixed(1)+"%")+"\\nUnseen-signer accuracy: "+(held==null?"not measured":(held*100).toFixed(1)+"%");''',
'results pending labels')

# Successful training must mark both shared data and model for upload.
rep(
'''   localStorage.setItem("svx-cloud-dirty","1");
   await syncCloud();''',
'''   localStorage.setItem("svx-cloud-dirty","1");
   localStorage.setItem("svx-cloud-model-dirty","1");
   trainingBusy=false;
   await syncCloud();''',
'post-training sync')

# Always release the training lock, and retry any pending cloud state after training/failure.
rep(
''' }finally{
   $("trainBtn").disabled=false;if(T){T.x.dispose();T.y.dispose()}if(V){V.x.dispose();V.y.dispose()}
 }''',
''' }finally{
   trainingBusy=false;
   $("trainBtn").disabled=false;if(T){T.x.dispose();T.y.dispose()}if(V){V.x.dispose();V.y.dispose()}
   if(localStorage.getItem("svx-cloud-dirty")==="1")scheduleCloudSync(800);
 }''',
'training finally')

# Guardrails.
assert 'BUILD 15 • AUTO SPEAK 70%' in s
assert 'conf>=0.70' in s
assert 'const EPOCHS=15;' in s
assert 'filters:16,kernelSize:3' in s and 'filters:24,kernelSize:3' in s
assert 'pendingLabels' in s
assert 'svx-cloud-model-dirty' in s
p.write_text(s)

# Backend: ordinary dataset sync must preserve the last successfully trained model.
bp=Path('sync-backend/server.js')
b=bp.read_text()
old='''      const next = {
        version: Number(current.version || 0) + 1,
        updatedAt: new Date().toISOString(),
        dataset: Array.isArray(incoming.dataset) ? incoming.dataset : [],
        trainedLabels: Array.isArray(incoming.trainedLabels) ? incoming.trainedLabels : [],
        threshold: Number(incoming.threshold) || 0.75,
        history: Array.isArray(incoming.history) ? incoming.history.slice(0, 20) : [],
        model: incoming.model || null
      };'''
new='''      const has = key => Object.prototype.hasOwnProperty.call(incoming, key);
      const next = {
        version: Number(current.version || 0) + 1,
        updatedAt: new Date().toISOString(),
        dataset: Array.isArray(incoming.dataset) ? incoming.dataset : (current.dataset || []),
        trainedLabels: has('trainedLabels') && Array.isArray(incoming.trainedLabels) ? incoming.trainedLabels : (current.trainedLabels || []),
        threshold: has('threshold') && Number.isFinite(Number(incoming.threshold)) ? Number(incoming.threshold) : (Number(current.threshold) || 0.75),
        history: has('history') && Array.isArray(incoming.history) ? incoming.history.slice(0, 20) : (current.history || []),
        model: has('model') ? incoming.model : (current.model || null)
      };'''
if old not in b:
    raise SystemExit('Missing backend state marker')
b=b.replace(old,new,1)
bp.write_text(b)
