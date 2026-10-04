from pathlib import Path
p=Path('index.html')
s=p.read_text()
old='tf.callbacks.earlyStopping({monitor:"val_loss",patience:5,restoreBestWeights:true})'
new='tf.callbacks.earlyStopping({monitor:"val_loss",patience:5,minDelta:0.001})'
if old not in s:
    raise SystemExit('early stopping target not found')
s=s.replace(old,new,1)
s=s.replace('ACCURACY BUILD • 3+ SIGNS • 6+ SAMPLES/SIGN • OFFLINE','ACCURACY BUILD • STABLE EARLY STOP • 6+ SAMPLES/SIGN • OFFLINE',1)
p.write_text(s)

sw=Path('sw.js')
if sw.exists():
    t=sw.read_text()
    t=t.replace("silentvoicex-accuracy-offline-v5","silentvoicex-accuracy-offline-v6")
    sw.write_text(t)
print('patched early stopping')
