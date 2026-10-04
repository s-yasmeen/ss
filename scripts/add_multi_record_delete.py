from pathlib import Path

p = Path('index.html')
s = p.read_text()

# Add compact selection styling.
style_anchor = '.sampleDelete:hover{background:#4a1b37}'
style_extra = '.sampleCheck{width:18px;height:18px;accent-color:#45e6ff;flex:0 0 auto}.recordSelectBar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0}.selectionStatus{font-size:12px;color:#9bb0c9;font-weight:800}'
if '.sampleCheck{' not in s:
    if style_anchor not in s:
        raise SystemExit('Sample delete style anchor not found')
    s = s.replace(style_anchor, style_anchor + style_extra, 1)

# Rename the existing participant+sign group delete so it is not confused with record deletion.
s = s.replace(
    '<button id="deleteSelectedBtn" class="btn ghost">Delete selected sign</button>',
    '<button id="deleteSelectedBtn" class="btn ghost">Delete this participant + sign</button>'
)

# Add bulk record controls above the sample list.
old_log = '<div id="personSummary" class="personSummary"></div><div id="sampleLog" class="log">No samples yet.</div>'
new_log = '''<div id="personSummary" class="personSummary"></div>
        <div class="recordSelectBar">
          <button id="selectAllRecordsBtn" class="btn ghost">☑ Select All</button>
          <button id="clearRecordSelectionBtn" class="btn ghost">Clear Selection</button>
          <button id="deleteRecordsBtn" class="btn ghost" disabled>Delete Selected Records</button>
          <span id="recordSelectionStatus" class="selectionStatus">0 selected</span>
        </div>
        <div id="sampleLog" class="log">No samples yet.</div>'''
if 'id="selectAllRecordsBtn"' not in s:
    if old_log not in s:
        raise SystemExit('Sample log anchor not found')
    s = s.replace(old_log, new_log, 1)

# Add selection state.
state_anchor = 'let liveBuffer=[], currentPrediction="READY", currentConfidence=0, phrase=[], recording=false, recordFrames=[], lastPredict=0, handVisible=false, currentUtterance=null, speechVoices=[], inferenceBusy=false, inferenceErrors=0, autoSpeakLastLabel="", autoSpeakArmed=true;'
if 'selectedRecordIndexes' not in s:
    if state_anchor not in s:
        raise SystemExit('State anchor not found')
    s = s.replace(state_anchor, state_anchor + '\nlet selectedRecordIndexes=new Set();', 1)

# Add selection helper.
log_anchor = 'function logSamples(){'
helper = '''function updateRecordSelectionUI(){
 const n=selectedRecordIndexes.size;
 const status=$("recordSelectionStatus");
 const del=$("deleteRecordsBtn");
 if(status) status.textContent=n+" selected";
 if(del) del.disabled=n===0;
}
function logSamples(){'''
if 'function updateRecordSelectionUI()' not in s:
    if log_anchor not in s:
        raise SystemExit('logSamples anchor not found')
    s = s.replace(log_anchor, helper, 1)

# Keep only valid selected indexes whenever the list is rebuilt.
needle = ''' const box=$("sampleLog");
 const summary=$("personSummary");'''
replace = ''' const box=$("sampleLog");
 const summary=$("personSummary");
 selectedRecordIndexes=new Set([...selectedRecordIndexes].filter(i=>i>=0&&i<dataset.length));
 updateRecordSelectionUI();'''
if 'selectedRecordIndexes=new Set([...selectedRecordIndexes].filter' not in s:
    if needle not in s:
        raise SystemExit('logSamples setup anchor not found')
    s = s.replace(needle, replace, 1)

# Clear stale selection for an empty dataset.
empty_anchor = ''' if(!dataset.length){
   summary.innerHTML='<div class="personCard"><div class="pname">Participants</div><div class="pcount">0 samples</div></div>';'''
empty_replace = ''' if(!dataset.length){
   selectedRecordIndexes.clear();
   updateRecordSelectionUI();
   summary.innerHTML='<div class="personCard"><div class="pname">Participants</div><div class="pcount">0 samples</div></div>';'''
if 'selectedRecordIndexes.clear();\n   updateRecordSelectionUI();\n   summary.innerHTML' not in s:
    if empty_anchor not in s:
        raise SystemExit('Empty dataset anchor not found')
    s = s.replace(empty_anchor, empty_replace, 1)

# Insert a checkbox into every rendered sample row.
row_anchor = '''   const info=document.createElement("div");
   info.className="sampleInfo";'''
row_replace = '''   const check=document.createElement("input");
   check.type="checkbox";
   check.className="sampleCheck";
   check.checked=selectedRecordIndexes.has(index);
   check.setAttribute("aria-label","Select record "+(index+1));
   check.onchange=()=>{
     if(check.checked) selectedRecordIndexes.add(index); else selectedRecordIndexes.delete(index);
     updateRecordSelectionUI();
   };
   const info=document.createElement("div");
   info.className="sampleInfo";'''
if 'check.className="sampleCheck"' not in s:
    if row_anchor not in s:
        raise SystemExit('Sample row info anchor not found')
    s = s.replace(row_anchor, row_replace, 1)

append_anchor = '   row.appendChild(info); row.appendChild(del); box.appendChild(row);'
append_replace = '   row.appendChild(check); row.appendChild(info); row.appendChild(del); box.appendChild(row);'
if 'row.appendChild(check);' not in s:
    if append_anchor not in s:
        raise SystemExit('Sample row append anchor not found')
    s = s.replace(append_anchor, append_replace, 1)

# Single delete clears selection to avoid index shifts.
single_anchor = '''   dataset.splice(index,1);
   markDatasetChanged();
   logSamples();'''
single_replace = '''   dataset.splice(index,1);
   selectedRecordIndexes.clear();
   markDatasetChanged();
   logSamples();'''
if 'dataset.splice(index,1);\n   selectedRecordIndexes.clear();' not in s:
    if single_anchor not in s:
        raise SystemExit('Single delete anchor not found')
    s = s.replace(single_anchor, single_replace, 1)

# Add bulk select/delete handlers before the existing participant+sign group delete handler.
group_anchor = '$("deleteSelectedBtn").onclick=()=>{'
bulk_handlers = '''$("selectAllRecordsBtn").onclick=()=>{
 selectedRecordIndexes=new Set(dataset.map((_,i)=>i));
 logSamples();
};
$("clearRecordSelectionBtn").onclick=()=>{
 selectedRecordIndexes.clear();
 logSamples();
};
$("deleteRecordsBtn").onclick=()=>{
 const indexes=[...selectedRecordIndexes].sort((a,b)=>a-b);
 if(!indexes.length)return;
 if(!confirm("Delete "+indexes.length+" selected record"+(indexes.length===1?"":"s")+"?"))return;
 const selected=new Set(indexes);
 dataset=dataset.filter((_,i)=>!selected.has(i));
 selectedRecordIndexes.clear();
 markDatasetChanged();
 logSamples();
};
$("deleteSelectedBtn").onclick=()=>{'''
if '$("selectAllRecordsBtn").onclick' not in s:
    if group_anchor not in s:
        raise SystemExit('Group delete handler anchor not found')
    s = s.replace(group_anchor, bulk_handlers, 1)

# Clear record selection when deleting a participant+sign group.
group_delete_anchor = '''   dataset=dataset.filter(s=>!(s.participant===participant&&s.label===label));
   markDatasetChanged();'''
group_delete_replace = '''   dataset=dataset.filter(s=>!(s.participant===participant&&s.label===label));
   selectedRecordIndexes.clear();
   markDatasetChanged();'''
if 'dataset=dataset.filter(s=>!(s.participant===participant&&s.label===label));\n   selectedRecordIndexes.clear();' not in s:
    if group_delete_anchor not in s:
        raise SystemExit('Group delete body anchor not found')
    s = s.replace(group_delete_anchor, group_delete_replace, 1)

p.write_text(s)
