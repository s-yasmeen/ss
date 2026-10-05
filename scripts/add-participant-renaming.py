from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')

old_form = '''          <div class="field"><label>Participant ID</label><input id="participant" value="P001"></div>
          <div class="field"><label>Sign label</label><input id="label" value="HELLO" maxlength="24"></div>
          <div class="field"><label>Hold-out participant for final test</label><input id="holdout" value="P003"></div>
          <div class="field"><label>Unknown threshold</label><input id="threshold" type="number" min=".5" max=".99" step=".01" value=".70"></div>
        </div>
        <div class="controls"><button id="recordBtn" class="btn hot">● Record 1 sample</button><button id="deleteSelectedBtn" class="btn ghost">Delete selected sign</button></div>'''

new_form = '''          <div class="field"><label>Participant ID</label><input id="participant" value="P001"></div>
          <div class="field"><label>Sign label</label><input id="label" value="HELLO" maxlength="24"></div>
          <div class="field"><label>Hold-out participant for final test</label><input id="holdout" value="P003"></div>
          <div class="field"><label>Unknown threshold</label><input id="threshold" type="number" min=".5" max=".99" step=".01" value=".70"></div>
          <div class="field"><label>New participant ID for recorded data</label><input id="renameParticipantTo" placeholder="e.g. P004" maxlength="32"></div>
        </div>
        <div class="controls"><button id="recordBtn" class="btn hot">● Record 1 sample</button><button id="deleteSelectedBtn" class="btn ghost">Delete selected sign</button><button id="renameParticipantBtn" class="btn ghost">✎ Rename recorded participant</button></div>
        <p class="note"><b>Correct a participant ID after recording:</b> enter the existing ID in <b>Participant ID</b>, enter the replacement above, then choose <b>Rename recorded participant</b>. All recorded samples for that participant are updated without changing the hand-sign data.</p>'''

if old_form not in text:
    raise SystemExit('Expected participant form block not found')
text = text.replace(old_form, new_form, 1)

old_delete = '''   const del=document.createElement("button");
   del.className="sampleDelete";
   del.textContent="Delete";
   del.onclick=()=>deleteOneSample(index);
   row.appendChild(check); row.appendChild(info); row.appendChild(del); box.appendChild(row);'''

new_delete = '''   const edit=document.createElement("button");
   edit.className="sampleDelete";
   edit.textContent="Edit participant";
   edit.onclick=()=>editOneSampleParticipant(index);
   const del=document.createElement("button");
   del.className="sampleDelete";
   del.textContent="Delete";
   del.onclick=()=>deleteOneSample(index);
   row.appendChild(check); row.appendChild(info); row.appendChild(edit); row.appendChild(del); box.appendChild(row);'''

if old_delete not in text:
    raise SystemExit('Expected sample row delete block not found')
text = text.replace(old_delete, new_delete, 1)

old_after_delete = '''function deleteOneSample(index){
 const s=dataset[index];
 if(!s)return;
 if(confirm("Delete this sample?\\n\\n"+s.participant+" • "+s.label)){
   dataset.splice(index,1);
   selectedRecordIndexes.clear();
   markDatasetChanged();
   logSamples();
 }
}
function updateStats(){'''

new_after_delete = '''function cleanParticipantId(value){
 return String(value||"").replace(/[<>\\r\\n]/g,"").trim().slice(0,32);
}
function editOneSampleParticipant(index){
 const s=dataset[index];
 if(!s)return;
 const next=cleanParticipantId(prompt("Change participant ID for this recorded sample:",s.participant||"P001"));
 if(!next||next===s.participant)return;
 s.participant=next;
 selectedRecordIndexes.clear();
 markDatasetChanged();
 logSamples();
}
function deleteOneSample(index){
 const s=dataset[index];
 if(!s)return;
 if(confirm("Delete this sample?\\n\\n"+s.participant+" • "+s.label)){
   dataset.splice(index,1);
   selectedRecordIndexes.clear();
   markDatasetChanged();
   logSamples();
 }
}
function updateStats(){'''

if old_after_delete not in text:
    raise SystemExit('Expected delete function block not found')
text = text.replace(old_after_delete, new_after_delete, 1)

old_delete_selected = '''$("deleteSelectedBtn").onclick=()=>{
 const participant=$("participant").value.trim();
 const label=$("label").value.trim().toUpperCase();
 const matches=dataset.filter(s=>s.participant===participant&&s.label===label).length;'''

new_delete_selected = '''$("renameParticipantBtn").onclick=()=>{
 const from=cleanParticipantId($("participant").value);
 const to=cleanParticipantId($("renameParticipantTo").value);
 if(!from){alert("Enter the existing participant ID first.");return;}
 if(!to){alert("Enter the new participant ID.");return;}
 if(from===to){alert("The new participant ID is the same as the existing ID.");return;}
 const matches=dataset.filter(s=>s.participant===from).length;
 if(!matches){alert("No recorded samples found for participant "+from+".");return;}
 if(!confirm("Rename participant "+from+" to "+to+" for "+matches+" recorded sample"+(matches===1?"":"s")+"?"))return;
 dataset.forEach(s=>{if(s.participant===from)s.participant=to;});
 if(cleanParticipantId($("holdout").value)===from)$("holdout").value=to;
 $("participant").value=to;
 $("renameParticipantTo").value="";
 selectedRecordIndexes.clear();
 markDatasetChanged();
 logSamples();
 alert("Participant renamed: "+from+" → "+to+". The recorded hand-sign sequences were preserved.");
};
$("deleteSelectedBtn").onclick=()=>{
 const participant=$("participant").value.trim();
 const label=$("label").value.trim().toUpperCase();
 const matches=dataset.filter(s=>s.participant===participant&&s.label===label).length;'''

if old_delete_selected not in text:
    raise SystemExit('Expected delete selected handler not found')
text = text.replace(old_delete_selected, new_delete_selected, 1)

old_merge = '''function mergeSamples(a,b){
 const out=[],seen=new Set();
 for(const raw of [...(a||[]),...(b||[])]){
   if(!sampleIsValid(raw))continue;
   const x={...raw,label:String(raw.label||"").trim().toUpperCase(),participant:String(raw.participant||"P001")};
   const k=x.id?"id:"+x.id:"fp:"+sampleFingerprint(x);
   if(!seen.has(k)){seen.add(k);out.push(x);}
 }
 return out;
}'''

new_merge = '''function mergeSamples(a,b){
 const out=[],positions=new Map();
 for(const raw of [...(a||[]),...(b||[])]){
   if(!sampleIsValid(raw))continue;
   const x={...raw,label:String(raw.label||"").trim().toUpperCase(),participant:cleanParticipantId(raw.participant||"P001")||"P001"};
   const k=x.id?"id:"+x.id:"fp:"+sampleFingerprint(x);
   if(positions.has(k)) out[positions.get(k)]=x;
   else {positions.set(k,out.length);out.push(x);}
 }
 return out;
}'''

if old_merge not in text:
    raise SystemExit('Expected mergeSamples block not found')
text = text.replace(old_merge, new_merge, 1)

index.write_text(text, encoding='utf-8')

sw = Path('sw.js')
sw_text = sw.read_text(encoding='utf-8')
old_cache = "silentvoicex-build15-cloud-sync-autospeak70-v7"
new_cache = "silentvoicex-build15-cloud-sync-participant-edit-v8"
if old_cache not in sw_text:
    raise SystemExit('Expected service worker cache version not found')
sw.write_text(sw_text.replace(old_cache, new_cache, 1), encoding='utf-8')

print('Participant renaming patch applied')
