from pathlib import Path

p = Path('index.html')
s = p.read_text()

replacements = {
    'minHandDetectionConfidence:.55': 'minHandDetectionConfidence:.5',
    'minHandPresenceConfidence:.55': 'minHandPresenceConfidence:.5',
    'minTrackingConfidence:.55': 'minTrackingConfidence:.5',
}
for old, new in replacements.items():
    s = s.replace(old, new)

required = [
    'minHandDetectionConfidence:.5',
    'minHandPresenceConfidence:.5',
    'minTrackingConfidence:.5',
]
for token in required:
    if token not in s:
        raise SystemExit(f'Missing expected landmark threshold: {token}')

# Keep the trained-sign classification threshold separate.
s = s.replace('PRE-FACE BUILD • AUTO-SPEAK ONCE', 'PRE-FACE BUILD • LANDMARKS 0.50 • AUTO-SPEAK ONCE')
p.write_text(s)

sw = Path('sw.js')
text = sw.read_text()
text = text.replace("silentvoicex-pre-face-autospeak-v3", "silentvoicex-pre-face-landmarks-v4")
sw.write_text(text)
