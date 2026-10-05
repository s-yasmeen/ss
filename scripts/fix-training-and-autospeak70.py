from pathlib import Path

index = Path('index.html')
s = index.read_text()

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Missing expected marker: {label}')
    s = s.replace(old, new, 1)

# 1) Declare trainingBusy so module-strict training can actually start.
replace_once(
    'let cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null;',
    'let cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null, trainingBusy=false;',
    'trainingBusy declaration'
)

# 2) Make the user-visible unknown/accept threshold default 70%, matching auto-speak.
s = s.replace('id="threshold" type="number" min=".5" max=".99" step=".01" value=".75"',
              'id="threshold" type="number" min=".5" max=".99" step=".01" value=".70"', 1)

# 3) Existing shared state may still contain 0.75. Keep this build at <=70% acceptance
# so auto-speak >=70% is genuinely reachable.
replace_once(
    'if(Number.isFinite(Number(remote.threshold)))$("threshold").value=String(remote.threshold);',
    'if(Number.isFinite(Number(remote.threshold)))$("threshold").value=String(Math.min(Number(remote.threshold),0.70));',
    'cloud threshold clamp'
)

# 4) Keep outgoing shared threshold at 70% or lower.
replace_once(
    'const body={baseVersion,dataset:dataset.filter(sampleIsValid),threshold:parseFloat($("threshold").value)||.75};',
    'const body={baseVersion,dataset:dataset.filter(sampleIsValid),threshold:Math.min(parseFloat($("threshold").value)||.70,.70)};',
    'outgoing threshold'
)

# 5) Restore the known-stable Build 15 CPU training path on mobile/browser devices.
replace_once(
    'try{if(!tf.getBackend()){await tf.setBackend("cpu");await tf.ready();}}catch(e){console.warn("Backend setup fallback",e)}',
    'try{if(tf.getBackend()!=="cpu"){await tf.setBackend("cpu");await tf.ready();}}catch(e){console.warn("CPU backend switch skipped",e)}',
    'stable cpu backend'
)

# Keep exact 70% auto-speak behavior and re-arm at 60%.
assert 'conf>=0.70' in s
assert 'conf<0.60' in s
assert 'BUILD 15 • AUTO SPEAK 70%' in s
assert 'filters:16,kernelSize:3' in s and 'filters:24,kernelSize:3' in s
assert 'const EPOCHS=15;' in s
assert 'trainingBusy=false' in s
index.write_text(s)

# 6) Dataset-only cloud writes must not wipe a previously trained shared model.
server = Path('sync-backend/server.js')
b = server.read_text()
old = '''      const next = {
        version: Number(current.version || 0) + 1,
        updatedAt: new Date().toISOString(),
        dataset: Array.isArray(incoming.dataset) ? incoming.dataset : [],
        trainedLabels: Array.isArray(incoming.trainedLabels) ? incoming.trainedLabels : [],
        threshold: Number(incoming.threshold) || 0.75,
        history: Array.isArray(incoming.history) ? incoming.history.slice(0, 20) : [],
        model: incoming.model || null
      };'''
new = '''      const next = {
        version: Number(current.version || 0) + 1,
        updatedAt: new Date().toISOString(),
        dataset: Array.isArray(incoming.dataset) ? incoming.dataset : current.dataset || [],
        trainedLabels: Array.isArray(incoming.trainedLabels) ? incoming.trainedLabels : current.trainedLabels || [],
        threshold: Number.isFinite(Number(incoming.threshold)) ? Number(incoming.threshold) : Number(current.threshold || 0.70),
        history: Array.isArray(incoming.history) ? incoming.history.slice(0, 20) : current.history || [],
        model: Object.prototype.hasOwnProperty.call(incoming, 'model') ? incoming.model : (current.model || null)
      };'''
if old not in b:
    raise SystemExit('Missing backend state replacement marker')
b = b.replace(old, new, 1)
server.write_text(b)
