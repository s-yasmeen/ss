from pathlib import Path

p = Path('index.html')
s = p.read_text()

s = s.replace('<div id="cameraWrap" class="cameraWrap">\n          <video id="video" autoplay playsinline muted></video><canvas id="canvas"></canvas>\n        </div>',
'''<div id="cameraWrap" class="cameraWrap privacy">\n          <video id="video" autoplay playsinline muted></video><canvas id="canvas"></canvas>\n          <div class="privacyTag">🔒 CAMERA PRIVACY ON • HAND LANDMARKS ONLY</div>\n        </div>''')

s = s.replace('<div id="trainCameraWrap" class="cameraWrap">\n            <video id="trainVideo" autoplay playsinline muted></video>\n            <canvas id="trainCanvas"></canvas>\n            <div id="recordOverlay" class="recordOverlay">Camera off — tap Start Camera</div>\n          </div>',
'''<div id="trainCameraWrap" class="cameraWrap privacy">\n            <video id="trainVideo" autoplay playsinline muted></video>\n            <canvas id="trainCanvas"></canvas>\n            <div class="privacyTag">🔒 CAMERA PRIVACY ON • HAND LANDMARKS ONLY</div>\n            <div id="recordOverlay" class="recordOverlay">Camera off — tap Start Camera</div>\n          </div>''')

s = s.replace('<span class="pill on">✋ Sign-only mode</span><span class="pill on">🚫 No camera upload</span>',
              '<span class="pill on">✋ Sign-only mode</span><span class="pill on">🔒 Camera Privacy ON</span><span class="pill on">🚫 No camera upload</span>')

s = s.replace('Hand landmarks are processed on this device. SilentVoiceX does not upload or save camera video.',
              'Camera Privacy is always ON: raw video is hidden while hand landmarks are processed locally. SilentVoiceX does not upload or save camera video.')

s = s.replace('<span class="pill on">✋ Hand data only</span>',
              '<span class="pill on">✋ Hand data only</span><span class="pill on">🔒 Camera Privacy ON</span>')

s = s.replace('Only normalized hand-landmark sequences are stored for training. No facial data is collected.',
              'Camera Privacy is always ON. Only normalized hand-landmark sequences are stored for training; raw camera video is not saved or uploaded.')

s = s.replace('BUILD 26 • LOCAL OFFLINE SIGN AI', 'BUILD 27 • PRIVATE OFFLINE SIGN AI')

p.write_text(s)

sw = Path('sw.js')
ss = sw.read_text().replace("silentvoicex-offline-v9", "silentvoicex-offline-v10")
sw.write_text(ss)

# Update offline setup text so the privacy behavior is explicit.
off = Path('offline.html')
o = off.read_text()
o = o.replace('✋ SIGN-ONLY • ON-DEVICE • OFFLINE', '✋ SIGN-ONLY • CAMERA-PRIVATE • OFFLINE')
o = o.replace('Prepare the complete hand-sign AI runtime for use without Wi-Fi or mobile data.', 'Prepare the complete hand-sign AI runtime for use without Wi-Fi or mobile data. Camera Privacy stays ON and raw video remains hidden.')
o = o.replace("const CACHE='silentvoicex-offline-v9';", "const CACHE='silentvoicex-offline-v10';")
o = o.replace("./index.html?v=26", "./index.html?v=27")
off.write_text(o)

# Guardrails
final = p.read_text()
assert 'id="cameraWrap" class="cameraWrap privacy"' in final
assert 'id="trainCameraWrap" class="cameraWrap privacy"' in final
assert final.count('CAMERA PRIVACY ON • HAND LANDMARKS ONLY') == 2
assert 'BUILD 27 • PRIVATE OFFLINE SIGN AI' in final
