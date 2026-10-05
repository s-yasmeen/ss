from pathlib import Path

p = Path('index.html')
s = p.read_text()

replacements = [
    ('BUILD 15 • AUTO SPEAK 80%', 'BUILD 15 • AUTO SPEAK 70%'),
    ('if(name!=="READY" && name!=="UNKNOWN" && conf>=0.80){', 'if(name!=="READY" && name!=="UNKNOWN" && conf>=0.70){'),
    ('}else if(conf<0.70 || name==="UNKNOWN" || name==="READY"){', '}else if(conf<0.60 || name==="UNKNOWN" || name==="READY"){'),
]

for old, new in replacements:
    if old not in s:
        raise SystemExit(f'Missing expected marker: {old}')
    s = s.replace(old, new, 1)

# Guardrails: do not alter the stable Build 15 model/training architecture.
assert 'filters:16,kernelSize:3' in s
assert 'filters:24,kernelSize:3' in s
assert 'const EPOCHS=15;' in s
assert 'minHandDetectionConfidence:.5,minHandPresenceConfidence:.5,minTrackingConfidence:.5' in s
assert 'BUILD 15 • AUTO SPEAK 70%' in s
assert 'conf>=0.70' in s
assert 'conf<0.60' in s

p.write_text(s)
