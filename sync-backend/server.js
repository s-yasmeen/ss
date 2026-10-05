import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';

const PORT = Number(process.env.PORT || 3000);
const DATA_DIR = process.env.DATA_DIR || '/data';
const STATE_FILE = path.join(DATA_DIR, 'state.json');
const DEVICES_FILE = path.join(DATA_DIR, 'devices.json');
const ALLOWED_ORIGIN = 'https://s-yasmeen.github.io';

const emptyState = () => ({
  version: 0,
  updatedAt: null,
  dataset: [],
  trainedLabels: [],
  threshold: 0.75,
  history: [],
  model: null
});

async function ensureStore() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  try { await fs.access(STATE_FILE); }
  catch { await fs.writeFile(STATE_FILE, JSON.stringify(emptyState()), 'utf8'); }
}

async function readState() {
  await ensureStore();
  try {
    return JSON.parse(await fs.readFile(STATE_FILE, 'utf8'));
  } catch {
    const state = emptyState();
    await fs.writeFile(STATE_FILE, JSON.stringify(state), 'utf8');
    return state;
  }
}

async function writeState(state) {
  await ensureStore();
  const tmp = STATE_FILE + '.tmp';
  await fs.writeFile(tmp, JSON.stringify(state), 'utf8');
  await fs.rename(tmp, STATE_FILE);
}

async function readDevices() {
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
  return String(value || '').replace(/[<>\r\n]/g, '').trim().slice(0, max);
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

function corsHeaders(origin) {
  const allow = origin === ALLOWED_ORIGIN ? origin : ALLOWED_ORIGIN;
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type',
    'Cache-Control': 'no-store',
    'Vary': 'Origin'
  };
}

function send(res, status, body, origin) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    ...corsHeaders(origin),
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload)
  });
  res.end(payload);
}

async function readJson(req, limit = 50 * 1024 * 1024) {
  const chunks = [];
  let total = 0;
  for await (const chunk of req) {
    total += chunk.length;
    if (total > limit) throw new Error('payload too large');
    chunks.push(chunk);
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
}

const server = http.createServer(async (req, res) => {
  const origin = req.headers.origin || '';
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

  if (req.method === 'OPTIONS') {
    res.writeHead(204, corsHeaders(origin));
    return res.end();
  }

  if (url.pathname === '/health') {
    return send(res, 200, { ok: true, service: 'SilentVoiceX Sync' }, origin);
  }

  if (url.pathname !== '/state' && url.pathname !== '/devices') {
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

    if (req.method === 'PUT') {
      const incoming = await readJson(req);
      const current = await readState();
      const baseVersion = Number(incoming.baseVersion ?? -1);

      if (baseVersion !== Number(current.version || 0)) {
        return send(res, 409, { error: 'version_conflict', current }, origin);
      }

      const has = key => Object.prototype.hasOwnProperty.call(incoming, key);
      const next = {
        version: Number(current.version || 0) + 1,
        updatedAt: new Date().toISOString(),
        dataset: Array.isArray(incoming.dataset) ? incoming.dataset : (current.dataset || []),
        trainedLabels: has('trainedLabels') && Array.isArray(incoming.trainedLabels) ? incoming.trainedLabels : (current.trainedLabels || []),
        threshold: has('threshold') && Number.isFinite(Number(incoming.threshold)) ? Number(incoming.threshold) : (Number(current.threshold) || 0.75),
        history: has('history') && Array.isArray(incoming.history) ? incoming.history.slice(0, 20) : (current.history || []),
        model: has('model') ? incoming.model : (current.model || null)
      };

      await writeState(next);
      return send(res, 200, next, origin);
    }

    return send(res, 405, { error: 'method_not_allowed' }, origin);
  } catch (error) {
    console.error(error);
    return send(res, 500, { error: 'server_error', detail: error?.message || String(error) }, origin);
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`SilentVoiceX sync listening on ${PORT}`);
});
