from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Add compact quick-sign UI styles.
style_anchor = '.selectionStatus{font-size:12px;color:#9bb0c9;font-weight:800}'
style_add = style_anchor + '.quickSignPanel{margin:14px 0;padding:12px;border:1px solid #23445f;border-radius:16px;background:#081727}.quickSignButtons{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.quickSign{border:1px solid #31577a;background:#0c2035;color:#d9f6ff;border-radius:999px;padding:8px 11px;font-weight:900;cursor:pointer}.quickSign:hover,.quickSign.active{border-color:#45e6ff;background:#12324a;box-shadow:0 0 18px #45e6ff22}'
if style_anchor in s and '.quickSignPanel{' not in s:
    s = s.replace(style_anchor, style_add, 1)

# Expand the datalist only; these are labels, not fabricated training samples.
old_list = '<datalist id="signVocabulary"><option value="HELLO"><option value="THANK YOU"><option value="YES"><option value="NO"><option value="PLEASE"><option value="HELP"><option value="STOP"><option value="GOOD"><option value="LOVE"><option value="WATER"><option value="FOOD"><option value="HOME"></datalist>'
new_list = '<datalist id="signVocabulary"><option value="HELLO"><option value="THANK YOU"><option value="YES"><option value="NO"><option value="PLEASE"><option value="HELP"><option value="STOP"><option value="GOOD"><option value="LOVE"><option value="WATER"><option value="FOOD"><option value="HOME"><option value="SORRY"><option value="FRIEND"><option value="SCHOOL"><option value="DOCTOR"><option value="EMERGENCY"><option value="BATHROOM"></datalist>'
if old_list in s:
    s = s.replace(old_list, new_list, 1)

# Insert quick-select starter vocabulary after the form grid.
anchor = '        </div>\n        <div class="controls"><button id="recordBtn" class="btn hot">● Record 1 sample</button><button id="deleteSelectedBtn" class="btn ghost">Delete this participant + sign</button></div>'
panel = '''        </div>\n        <div class="quickSignPanel">\n          <div class="smallcap">STARTER SIGN LABELS</div>\n          <div class="quickSignButtons">\n            <button type="button" class="quickSign" data-sign="HELLO">HELLO</button>\n            <button type="button" class="quickSign" data-sign="THANK YOU">THANK YOU</button>\n            <button type="button" class="quickSign" data-sign="YES">YES</button>\n            <button type="button" class="quickSign" data-sign="NO">NO</button>\n            <button type="button" class="quickSign" data-sign="PLEASE">PLEASE</button>\n            <button type="button" class="quickSign" data-sign="HELP">HELP</button>\n            <button type="button" class="quickSign" data-sign="STOP">STOP</button>\n            <button type="button" class="quickSign" data-sign="GOOD">GOOD</button>\n            <button type="button" class="quickSign" data-sign="LOVE">LOVE</button>\n            <button type="button" class="quickSign" data-sign="WATER">WATER</button>\n            <button type="button" class="quickSign" data-sign="FOOD">FOOD</button>\n            <button type="button" class="quickSign" data-sign="HOME">HOME</button>\n            <button type="button" class="quickSign" data-sign="SORRY">SORRY</button>\n            <button type="button" class="quickSign" data-sign="FRIEND">FRIEND</button>\n            <button type="button" class="quickSign" data-sign="SCHOOL">SCHOOL</button>\n            <button type="button" class="quickSign" data-sign="DOCTOR">DOCTOR</button>\n            <button type="button" class="quickSign" data-sign="EMERGENCY">EMERGENCY</button>\n            <button type="button" class="quickSign" data-sign="BATHROOM">BATHROOM</button>\n          </div>\n          <div class="note" style="margin-top:8px">Tap a label, then record your real hand sign. These are vocabulary labels only; SilentVoiceX does not fabricate landmark samples.</div>\n        </div>\n        <div class="controls"><button id="recordBtn" class="btn hot">● Record 1 sample</button><button id="deleteSelectedBtn" class="btn ghost">Delete this participant + sign</button></div>'''
if anchor in s and 'STARTER SIGN LABELS' not in s:
    s = s.replace(anchor, panel, 1)

# Add quick-select behavior.
js_anchor = 'document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>{document.querySelectorAll(".tab,.page").forEach(x=>x.classList.remove("active"));b.classList.add("active");$(b.dataset.page).classList.add("active");updateStats()});'
js_add = js_anchor + '''\n\ndocument.querySelectorAll(".quickSign").forEach(btn=>{\n  btn.onclick=()=>{\n    $("label").value=btn.dataset.sign;\n    document.querySelectorAll(".quickSign").forEach(x=>x.classList.toggle("active",x===btn));\n    $("recordOverlay").textContent="Selected "+btn.dataset.sign+" — start camera and record 6 varied samples";\n  };\n});'''
if js_anchor in s and 'Selected "+btn.dataset.sign+' not in s:
    s = s.replace(js_anchor, js_add, 1)

# Update the visible build description without changing model behavior.
s = s.replace('ACCURACY BUILD • STABLE EARLY STOP • 6+ SAMPLES/SIGN • OFFLINE', 'ACCURACY BUILD • STARTER SIGNS • 6+ SAMPLES/SIGN • OFFLINE')

p.write_text(s, encoding='utf-8')
