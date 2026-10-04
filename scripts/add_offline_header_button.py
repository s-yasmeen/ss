from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_top = '<div class="top"><div class="brand"><h1>✋ <span>SilentVoice X</span></h1><p>AI that turns signs into speech</p></div></div>'
new_top = '<div class="top"><div class="brand"><h1>✋ <span>SilentVoice X</span></h1><p>AI that turns signs into speech</p></div><button id="headerOfflineBtn" class="btn primary">📴 Offline Setup</button></div>'
if old_top in s:
    s = s.replace(old_top, new_top, 1)

old_bind = '$("offlineBtn").onclick=()=>{location.href="./offline.html"};'
new_bind = '$("offlineBtn").onclick=()=>{location.href="./offline.html"};\nif($("headerOfflineBtn")) $("headerOfflineBtn").onclick=()=>{location.href="./offline.html"};'
if old_bind in s and 'headerOfflineBtn").onclick' not in s:
    s = s.replace(old_bind, new_bind, 1)

s = s.replace('BUILD 23 • EXPRESSION TOGGLE', 'BUILD 24 • OFFLINE SETUP BUTTON')
p.write_text(s, encoding='utf-8')

sw = Path('sw.js')
if sw.exists():
    t = sw.read_text(encoding='utf-8')
    t = t.replace("silentvoicex-offline-v6", "silentvoicex-offline-v7")
    sw.write_text(t, encoding='utf-8')
