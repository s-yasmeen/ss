from pathlib import Path
import re

p = Path('index.html')
s = p.read_text()

# Make the change idempotent because the threshold may already be at 70%.
if 'BUILD 15 • AUTO SPEAK 80%' in s:
    s = s.replace('BUILD 15 • AUTO SPEAK 80%', 'BUILD 15 • AUTO SPEAK 70%', 1)
assert 'BUILD 15 • AUTO SPEAK 70%' in s

if 'if(name!=="READY" && name!=="UNKNOWN" && conf>=0.80){' in s:
    s = s.replace('if(name!=="READY" && name!=="UNKNOWN" && conf>=0.80){', 'if(name!=="READY" && name!=="UNKNOWN" && conf>=0.70){', 1)
assert 'conf>=0.70' in s

if '}else if(conf<0.70 || name==="UNKNOWN" || name==="READY"){' in s:
    s = s.replace('}else if(conf<0.70 || name==="UNKNOWN" || name==="READY"){', '}else if(conf<0.60 || name==="UNKNOWN" || name==="READY"){', 1)
assert 'conf<0.60' in s

if '🔊 Auto-speak ≥80%' in s:
    s = s.replace('🔊 Auto-speak ≥80%', '🔊 Auto-speak ≥70%', 1)
assert '🔊 Auto-speak ≥70%' in s

# Guardrails: preserve the stable Build 15 model/training architecture and cloud sync.
assert 'filters:16,kernelSize:3' in s
assert 'filters:24,kernelSize:3' in s
assert 'const EPOCHS=15;' in s
assert 'minHandDetectionConfidence:.5,minHandPresenceConfidence:.5,minTrackingConfidence:.5' in s
assert 'SYNC_API=' in s
p.write_text(s)

# Force already-installed offline clients to refresh the updated app shell.
sw = Path('sw.js')
sws = sw.read_text()
sws = re.sub(r"const CACHE='[^']+';", "const CACHE='silentvoicex-build15-cloud-sync-autospeak70-v6';", sws, count=1)
sw.write_text(sws)
