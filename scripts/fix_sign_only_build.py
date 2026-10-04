from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove the two leftover lines from the retired facial-expression toggle block.
s=s.replace('const SEQ=24, FEAT=126, PRED_WINDOW=3;\n}\nsyncExpressionToggle();\n', 'const SEQ=24, FEAT=126, PRED_WINDOW=3;\n')

# Defensive cleanup: no retired face-control identifiers should remain in the app logic/UI.
for token in ['FaceLandmarker','faceLandmarker','expressionToggleBtn','trainExpressionToggleBtn','privacyBtn','trainPrivacyBtn','trainFaceStatus','expressionCue','expressionStrength','facePrivacyStatus','syncExpressionToggle','toggleExpression','syncFacePrivacy','toggleFacePrivacy']:
    if token in s:
        raise SystemExit(f'Unexpected retired face token remains: {token}')

# Validate module-script syntax with Node after writing a temporary module file.
p.write_text(s,encoding='utf-8')
module=re.search(r'<script type="module">(.*?)</script>',s,re.S)
if not module:
    raise SystemExit('module script not found')
Path('/tmp/svx-app.mjs').write_text(module.group(1),encoding='utf-8')

print('Sign-only build cleanup complete.')
