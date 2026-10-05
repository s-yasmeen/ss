from pathlib import Path

index = Path('index.html')
server = Path('sync-backend/server.js')

html = index.read_text(encoding='utf-8')
js = server.read_text(encoding='utf-8')

# 1) Add device panel below cloud sync explanation.
marker = '''        <p class="note"><b>Automatic cross-device sync:</b> training and recorded signs are saved locally first, then synchronized over the internet. Open this same SilentVoiceX link on another device and it automatically loads the newest shared training. Offline changes wait locally and sync after reconnection.</p>'''
panel = marker + '''
        <div style="margin-top:14px;padding:14px;border:1px solid #244560;border-radius:16px;background:#091728">
          <div class="smallcap">CONNECTED DEVICES</div>
          <div class="stats" style="grid-template-columns:repeat(2,1fr);margin-top:10px">
            <div class="stat"><div id="activeDeviceCount" class="n">—</div><div class="k">ACTIVE NOW</div></div>
            <div class="stat"><div id="registeredDeviceCount" class="n">—</div><div class="k">REGISTERED DEVICES</div></div>
          </div>
          <div id="deviceList" class="personSummary"><div class="personCard"><div class="pname">Devices</div><div class="pcount" style="font-size:14px">Checking…</div></div></div>
          <p class="note" style="margin-bottom:0">A random browser ID is used to distinguish devices. No location or owner name is stored. “Active now” means the device checked in within the last 2 minutes.</p>
        </div>'''
if 'id="activeDeviceCount"' not in html:
    if marker not in html:
        raise SystemExit('Missing cloud sync panel marker')
    html = html.replace(marker, panel, 1)

# 2) Add device endpoint constants and persistent random browser ID.
marker = '''const SYNC_API="https://silentvoicex-sync-api-production.up.railway.app/state";
let cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null, trainingBusy=false;'''
replacement = '''const SYNC_API="https://silentvoicex-sync-api-production.up.railway.app/state";
const DEVICE_API="https://silentvoicex-sync-api-production.up.railway.app/devices";
const DEVICE_ID_KEY="svx-device-id";
let DEVICE_ID=localStorage.getItem(DEVICE_ID_KEY);
if(!DEVICE_ID){DEVICE_ID=(crypto.randomUUID?crypto.randomUUID():(Date.now().toString(36)+"-"+Math.random().toString(36).slice(2)));localStorage.setItem(DEVICE_ID_KEY,DEVICE_ID);}
let cloudVersion=Number(localStorage.getItem("svx-cloud-version")||0), cloudBusy=false, cloudTimer=null, trainingBusy=false;'''
if 'const DEVICE_API=' not in html:
    if marker not in html:
        raise SystemExit('Missing sync constants marker')
    html = html.replace(marker, replacement, 1)

# 3) Add device detection/heartbeat/render functions before cloud sync helpers.
marker = '''function setCloudStatus(text,on=false){
 const el=$("cloudSyncStatus");if(!el)return;el.textContent=text;el.classList.toggle("on",!!on);
}'''
device_code = '''function detectDeviceType(){
 const ua=navigator.userAgent||"";
 if(/Android/i.test(ua))return /Mobile/i.test(ua)?"Android phone":"Android tablet";
 if(/iPhone/i.test(ua))return "iPhone";
 if(/iPad/i.test(ua))return "iPad";
 if(/Windows/i.test(ua))return "Windows computer";
 if(/Macintosh|Mac OS X/i.test(ua))return "Mac";
 if(/CrOS/i.test(ua))return "Chromebook";
 if(/Linux/i.test(ua))return "Linux computer";
 return "Browser device";
}
function detectBrowser(){
 const ua=navigator.userAgent||"";
 if(/SamsungBrowser/i.test(ua))return "Samsung Internet";
 if(/Edg\//i.test(ua))return "Edge";
 if(/Firefox|FxiOS/i.test(ua))return "Firefox";
 if(/CriOS/i.test(ua))return "Chrome";
 if(/Chrome/i.test(ua))return "Chrome";
 if(/Safari/i.test(ua))return "Safari";
 return "Browser";
}
function relativeSeen(iso){
 const ms=Date.now()-Date.parse(iso||"");
 if(!Number.isFinite(ms)||ms<0)return "just now";
 const s=Math.floor(ms/1000);if(s<45)return "just now";
 const m=Math.floor(s/60);if(m<60)return m+" min ago";
 const h=Math.floor(m/60);if(h<24)return h+" hr"+(h===1?"":"s")+" ago";
 const d=Math.floor(h/24);return d+" day"+(d===1?"":"s")+" ago";
}
function renderDevices(summary){
 const active=$("activeDeviceCount"),registered=$("registeredDeviceCount"),list=$("deviceList");
 if(!active||!registered||!list)return;
 active.textContent=String(summary.activeCount??0);registered.textContent=String(summary.registeredCount??0);
 const devices=Array.isArray(summary.devices)?summary.devices:[];
 list.innerHTML="";
 if(!devices.length){list.innerHTML='<div class="personCard"><div class="pname">Devices</div><div class="pcount" style="font-size:14px">No devices registered yet</div></div>';return;}
 devices.forEach((d,i)=>{
   const card=document.createElement("div");card.className="personCard";
   const mine=d.idSuffix&&DEVICE_ID.endsWith(d.idSuffix);
   const activeNow=!!d.active;
   const title="Device "+(i+1)+(mine?" • THIS DEVICE":"");
   const meta=(d.deviceType||"Browser device")+" • "+(d.browser||"Browser");
   card.innerHTML='<div class="pname">'+title+'</div><div class="pcount" style="font-size:14px">'+meta+'</div><div class="note" style="margin-top:5px;color:'+(activeNow?'#88ffd3':'#9bb0c9')+'">'+(activeNow?'● Active now':'○ Last seen '+relativeSeen(d.lastSeen))+'</div>';
   list.appendChild(card);
 });
}
async function deviceHeartbeat(){
 if(!navigator.onLine)return;
 try{
   const r=await fetch(DEVICE_API,{method:"PUT",headers:{"content-type":"application/json"},body:JSON.stringify({deviceId:DEVICE_ID,deviceType:detectDeviceType(),browser:detectBrowser()})});
   if(!r.ok)throw new Error("device registry "+r.status);
   renderDevices(await r.json());
 }catch(e){console.warn("Device heartbeat",e)}
}
async function refreshDevices(){
 if(!navigator.onLine)return;
 try{const r=await fetch(DEVICE_API,{cache:"no-store"});if(r.ok)renderDevices(await r.json());}catch(e){console.warn("Device list",e)}
}

''' + marker
if 'async function deviceHeartbeat()' not in html:
    if marker not in html:
        raise SystemExit('Missing cloud status function marker')
    html = html.replace(marker, device_code, 1)

# 4) Register device alongside sync lifecycle.
marker = '''window.addEventListener("online",()=>syncCloud());
window.addEventListener("offline",()=>setCloudStatus("☁ Shared AI • offline, changes saved locally",false));
document.addEventListener("visibilitychange",()=>{if(!document.hidden)syncCloud()});
setInterval(()=>{if(!document.hidden&&navigator.onLine)syncCloud()},15000);'''
replacement = '''window.addEventListener("online",()=>{syncCloud();deviceHeartbeat()});
window.addEventListener("offline",()=>setCloudStatus("☁ Shared AI • offline, changes saved locally",false));
document.addEventListener("visibilitychange",()=>{if(!document.hidden){syncCloud();deviceHeartbeat();}});
setInterval(()=>{if(!document.hidden&&navigator.onLine)syncCloud()},15000);
setInterval(()=>{if(!document.hidden&&navigator.onLine)deviceHeartbeat()},30000);
setTimeout(()=>deviceHeartbeat(),800);'''
if 'setInterval(()=>{if(!document.hidden&&navigator.onLine)deviceHeartbeat()},30000);' not in html:
    if marker not in html:
        raise SystemExit('Missing cloud lifecycle marker')
    html = html.replace(marker, replacement, 1)

index.write_text(html, encoding='utf-8')

# --- Backend persistent device registry ---
# Add devices file constant.
marker = "const STATE_FILE = path.join(DATA_DIR, 'state.json');"
replacement = marker + "\nconst DEVICES_FILE = path.join(DATA_DIR, 'devices.json');"
if 'DEVICES_FILE' not in js:
    if marker not in js: raise SystemExit('Missing STATE_FILE marker')
    js = js.replace(marker, replacement, 1)

# Add helper functions before CORS.
marker = '''function corsHeaders(origin) {'''
helpers = '''async function readDevices() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  try {
    const parsed = JSON.parse(await fs.readFile(DEVICES_FILE, 'utf8'));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    await fs.writeFile(DEVICES_FILE, '[]', 'utf8');
    return [];
  }
}

async function writeDevices(devices) {
  await fs.mkdir(DATA_DIR, { recursive: true });
  const tmp = DEVICES_FILE + '.tmp';
  await fs.writeFile(tmp, JSON.stringify(devices), 'utf8');
  await fs.rename(tmp, DEVICES_FILE);
}

function cleanText(value, max = 48) {
  return String(value || '').replace(/[<>\\r\\n]/g, '').trim().slice(0, max);
}

function deviceSummary(devices) {
  const now = Date.now();
  const activeWindow = 2 * 60 * 1000;
  const sorted = devices.slice().sort((a, b) => Date.parse(a.firstSeen || 0) - Date.parse(b.firstSeen || 0));
  const publicDevices = sorted.map(d => ({
    idSuffix: String(d.deviceId || '').slice(-8),
    deviceType: d.deviceType || 'Browser device',
    browser: d.browser || 'Browser',
    firstSeen: d.firstSeen || null,
    lastSeen: d.lastSeen || null,
    active: now - Date.parse(d.lastSeen || 0) <= activeWindow
  }));
  return {
    activeCount: publicDevices.filter(d => d.active).length,
    registeredCount: publicDevices.length,
    activeWindowSeconds: activeWindow / 1000,
    devices: publicDevices
  };
}

''' + marker
if 'function deviceSummary(devices)' not in js:
    if marker not in js: raise SystemExit('Missing cors marker')
    js = js.replace(marker, helpers, 1)

# Allow /devices route.
old = '''  if (url.pathname !== '/state') {
    return send(res, 404, { error: 'not_found' }, origin);
  }

  if (origin && origin !== ALLOWED_ORIGIN) {
    return send(res, 403, { error: 'origin_not_allowed' }, origin);
  }

  try {
    if (req.method === 'GET') {
      return send(res, 200, await readState(), origin);
    }
'''
new = '''  if (url.pathname !== '/state' && url.pathname !== '/devices') {
    return send(res, 404, { error: 'not_found' }, origin);
  }

  if (origin && origin !== ALLOWED_ORIGIN) {
    return send(res, 403, { error: 'origin_not_allowed' }, origin);
  }

  try {
    if (url.pathname === '/devices') {
      if (req.method === 'GET') {
        const devices = await readDevices();
        return send(res, 200, deviceSummary(devices), origin);
      }
      if (req.method === 'PUT') {
        const incoming = await readJson(req, 16 * 1024);
        const deviceId = cleanText(incoming.deviceId, 100);
        if (!/^[A-Za-z0-9_-]{8,100}$/.test(deviceId)) {
          return send(res, 400, { error: 'invalid_device_id' }, origin);
        }
        const now = new Date().toISOString();
        const ninetyDaysAgo = Date.now() - 90 * 24 * 60 * 60 * 1000;
        let devices = (await readDevices()).filter(d => Date.parse(d.lastSeen || d.firstSeen || 0) >= ninetyDaysAgo);
        const existing = devices.find(d => d.deviceId === deviceId);
        if (existing) {
          existing.lastSeen = now;
          existing.deviceType = cleanText(incoming.deviceType, 48) || existing.deviceType || 'Browser device';
          existing.browser = cleanText(incoming.browser, 48) || existing.browser || 'Browser';
        } else {
          devices.push({
            deviceId,
            deviceType: cleanText(incoming.deviceType, 48) || 'Browser device',
            browser: cleanText(incoming.browser, 48) || 'Browser',
            firstSeen: now,
            lastSeen: now
          });
        }
        await writeDevices(devices);
        return send(res, 200, deviceSummary(devices), origin);
      }
      return send(res, 405, { error: 'method_not_allowed' }, origin);
    }

    if (req.method === 'GET') {
      return send(res, 200, await readState(), origin);
    }
'''
if "url.pathname === '/devices'" not in js:
    if old not in js: raise SystemExit('Missing state route marker')
    js = js.replace(old, new, 1)

server.write_text(js, encoding='utf-8')
print('Device registry patch applied')
