from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Add confidence scale styling.
if '.confidenceScale{' not in s:
    anchor = '.sentence .natural{font-size:21px;font-weight:900;margin-top:7px}'
    addition = anchor + '.confidenceScale{margin:4px 0 16px;padding:12px 14px;border-radius:16px;background:#071321;border:1px solid #1d3855}.confidenceScaleHead{display:flex;align-items:center;justify-content:space-between;gap:10px;color:#dff8ff;font-size:13px;font-weight:900}.confidenceScale input[type=range]{width:100%;margin:10px 0 4px;accent-color:#45e6ff}.confidenceTicks{display:flex;justify-content:space-between;color:#7f98b2;font-size:11px;font-weight:850}'
    if anchor not in s:
        raise SystemExit('Missing sentence style anchor')
    s = s.replace(anchor, addition, 1)

# Make the auto-speak status dynamic.
old_status = '<span class="pill on">🔊 Auto-speak ≥80%</span>'
new_status = '<span id="autoSpeakStatus" class="pill on">🔊 Auto-speak ≥80%</span>'
if old_status in s:
    s = s.replace(old_status, new_status, 1)

# Add visible 80-100 confidence control after the confidence ring.
if 'id="autoSpeakSlider"' not in s:
    ring = '<div style="position:relative;width:98px"><div id="ring" class="ring"></div><div id="ringText" class="ringText" style="inset:38px 0;text-align:center">0%</div></div>'
    scale = ring + '<div class="confidenceScale"><div class="confidenceScaleHead"><span>AUTO-SPEAK CONFIDENCE</span><strong id="autoSpeakValue">80%</strong></div><input id="autoSpeakSlider" type="range" min="80" max="100" step="1" value="80" aria-label="Auto-speak confidence from 80 to 100 percent"><div class="confidenceTicks"><span>80%</span><span>90%</span><span>100%</span></div></div>'
    if ring not in s:
        raise SystemExit('Missing confidence ring anchor')
    s = s.replace(ring, scale, 1)

# Add persistent threshold state and slider wiring.
if 'let autoSpeakThreshold=' not in s:
    anchor = 'const SEQ=24, FEAT=126;'
    block = '''const SEQ=24, FEAT=126;\nlet autoSpeakThreshold=Math.min(1,Math.max(.80,parseFloat(localStorage.getItem("svx-auto-speak-threshold")||".80")));\nfunction syncAutoSpeakScale(){\n const pct=Math.round(autoSpeakThreshold*100);\n const slider=$("autoSpeakSlider");\n if(slider)slider.value=String(pct);\n if($("autoSpeakValue"))$("autoSpeakValue").textContent=pct+"%";\n if($("autoSpeakStatus"))$("autoSpeakStatus").textContent="🔊 Auto-speak ≥"+pct+"%";\n}\nif($("autoSpeakSlider")){\n $("autoSpeakSlider").oninput=e=>{\n   autoSpeakThreshold=Math.min(1,Math.max(.80,Number(e.target.value)/100));\n   localStorage.setItem("svx-auto-speak-threshold",String(autoSpeakThreshold));\n   autoSpeakArmed=true;\n   syncAutoSpeakScale();\n };\n}\nsyncAutoSpeakScale();'''
    if anchor not in s:
        raise SystemExit('Missing SEQ anchor')
    s = s.replace(anchor, block, 1)

# Use adjustable threshold for auto-speech.
s = s.replace('conf>=0.80', 'conf>=autoSpeakThreshold')
s = s.replace('conf<0.70 || name==="UNKNOWN" || name==="READY"', 'conf<Math.max(0.70,autoSpeakThreshold-0.10) || name==="UNKNOWN" || name==="READY"')

# Update visible build label.
for old in ['BUILD 19 • OFFLINE + EXPRESSION','BUILD 18 • EXPRESSION CUES']:
    if old in s:
        s = s.replace(old, 'BUILD 20 • CONFIDENCE 80–100%', 1)
        break

p.write_text(s, encoding='utf-8')

# Bump offline cache so the new UI is refreshed on installed devices.
swp = Path('sw.js')
sw = swp.read_text(encoding='utf-8')
sw = sw.replace("silentvoicex-offline-v3", "silentvoicex-offline-v4")
swp.write_text(sw, encoding='utf-8')
