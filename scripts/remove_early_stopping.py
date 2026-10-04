from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '''   const EPOCHS=35;
   await model.fit(T.x,T.y,{
     epochs:EPOCHS,
     batchSize:Math.min(8,tr.length),
     validationData:[V.x,V.y],
     shuffle:true,
     callbacks:[
       tf.callbacks.earlyStopping({monitor:"val_loss",patience:5,minDelta:0.001}),
       {
         onTrainBegin:async()=>{$("trainText").textContent="Training stronger model…";await tf.nextFrame()},
         onEpochEnd:async(e,l)=>{
           const acc=(l.acc??l.accuracy??0)*100;
           const vacc=(l.val_acc??l.val_accuracy??0)*100;
           $("bar").style.width=((e+1)/EPOCHS*100)+"%";
           $("trainText").textContent="Epoch "+(e+1)+"/"+EPOCHS+" • accuracy "+acc.toFixed(1)+"% • validation "+vacc.toFixed(1)+"%";
           await tf.nextFrame();
         }
       }
     ]
   });'''
new = '''   const EPOCHS=20;
   await model.fit(T.x,T.y,{
     epochs:EPOCHS,
     batchSize:Math.min(8,tr.length),
     validationData:[V.x,V.y],
     shuffle:true,
     callbacks:{
       onTrainBegin:async()=>{$("trainText").textContent="Training model — fixed 20 epochs…";await tf.nextFrame()},
       onEpochEnd:async(e,l)=>{
         const acc=(l.acc??l.accuracy??0)*100;
         const vacc=(l.val_acc??l.val_accuracy??0)*100;
         $("bar").style.width=((e+1)/EPOCHS*100)+"%";
         $("trainText").textContent="Epoch "+(e+1)+"/"+EPOCHS+" • accuracy "+acc.toFixed(1)+"% • validation "+vacc.toFixed(1)+"%";
         await tf.nextFrame();
       },
       onTrainEnd:async()=>{$("bar").style.width="100%";$("trainText").textContent="Training finished — evaluating…";await tf.nextFrame()}
     }
   });'''
if old not in s:
    raise SystemExit('Expected early-stopping training block not found')
s = s.replace(old, new)
s = s.replace('ACCURACY BUILD • STARTER SIGNS • 6+ SAMPLES/SIGN • OFFLINE', 'STABLE BUILD • 20 EPOCHS • 6+ SAMPLES/SIGN • OFFLINE')
s = s.replace('Training uses a stronger temporal Conv1D model with stratified validation, dropout, batch normalization and early stopping.', 'Training uses a temporal Conv1D model with stratified validation, dropout and batch normalization. It now runs a fixed 20 epochs so training cannot stop itself early.')
p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
if sw.exists():
    t = sw.read_text(encoding='utf-8')
    import re
    t = re.sub(r"const CACHE_NAME = '[^']+';", "const CACHE_NAME = 'silentvoicex-fixed-training-v6';", t, count=1)
    sw.write_text(t, encoding='utf-8')
