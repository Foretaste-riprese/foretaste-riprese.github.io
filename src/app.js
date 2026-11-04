// ---- The guide for clients: each step is filmed with the phone's camera inside the guide (0.5× lens, 4K), without
// leaving the page; the guide sends every video by itself to the owner's Google Drive (through the Apps Script in
// apps-script/), while the client goes on with the next step. Where the camera can't be used here, the step is
// filmed with the Camera app and picked from the gallery, as before. ----
const PROPS = __PROPS__;
PROPS.avviso = 'Nessuno';
document.documentElement.classList.add('aim-live');   // the canvas shows sample warnings; the guide has no sensors for them yet
const CFG = window.GUIDA_CONFIG || {};
const $ = (s) => document.querySelector(s);
const esc = (t) => String(t == null ? '' : t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const AREA = (k) => ROOMS.includes(k) ? 'Ambiente' : STAIRS.includes(k) ? 'Scalinata' : 'Corridoio';
const fmtMB = (b) => (b / 1048576).toLocaleString('it-IT', { maximumFractionDigits: 0 }) + ' MB';
let comp = null;

__FIT__

// ---------- the property: from the link (?casa=Via Roma 12), otherwise asked once ----------
const fromLink = new URLSearchParams(location.search).get('casa');
function casa() {
  if (fromLink && fromLink.trim()) return fromLink.trim();
  try { return localStorage.getItem('guida-casa') || ''; } catch (_) { return ''; }
}
function setCasa(v) { try { localStorage.setItem('guida-casa', v.trim()); } catch (_) {} }
const lsGet = (k) => { try { return localStorage.getItem(k); } catch (_) { return null; } };
const lsSet = (k, v) => { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (_) {} };

// ---------- sending: one video after the other, in 8 MB pieces, picking up again after a dropped connection ----------
const PIECE = 8 * 1024 * 1024;   // a multiple of 256 KiB, as Drive asks
const Q = [];
let busy = false, lock = null;
const pending = () => Q.filter((x) => x.state !== 'ok');
async function call(action, body) {
  const r = await fetch(CFG.scriptUrl, { method: 'POST', body: JSON.stringify(Object.assign({ action }, body)) });
  const j = await r.json();
  if (!j.ok) throw new Error(j.error || 'risposta non valida');
  return j;
}
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
// ---------- problems reported by themselves: what goes wrong on a client's phone lands in «Problemi della guida» ----------
// At most 12 a visit, each one once; kept and sent again when the connection comes back.
const SENT_REP = new Set(), REP_Q = [];
let repCount = 0;
function report(kind, detail) {
  const key = kind + '|' + detail;
  if (!CFG.scriptUrl || SENT_REP.has(key) || repCount >= 12) return;
  SENT_REP.add(key); repCount++;
  REP_Q.push({ kind, detail: String(detail || '').slice(0, 1000), casa: casa(), ua: navigator.userAgent, page: location.pathname + location.search, build: window.GUIDA_BUILD || '' });
  flushReports();
}
async function flushReports() {
  while (REP_Q.length && navigator.onLine !== false) {
    try { await call('report', REP_Q[0]); REP_Q.shift(); } catch (_) { return; }
  }
}
window.addEventListener('online', flushReports);
window.addEventListener('error', (e) => report('Errore della pagina', `${e.message || e} · ${(e.filename || '').split('/').pop()}:${e.lineno || ''}`));
window.addEventListener('unhandledrejection', (e) => report('Errore della pagina', String((e.reason && (e.reason.message || e.reason)) || 'promessa rifiutata')));
// The phone may close the page while the client is in the Camera app: videos not yet in Drive are kept in the
// browser's own storage (the file once, the progress after every piece) and carry on when the page comes back.
const STORE = (() => {
  let dbp = null;
  const open = () => dbp || (dbp = new Promise((res, rej) => {
    const r = indexedDB.open('guida-invii', 1);
    r.onupgradeneeded = () => { r.result.createObjectStore('meta', { keyPath: 'id' }); r.result.createObjectStore('file'); };
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  }));
  const meta = (it) => ({ id: it.id, name: it.name, casa: it.casa, type: it.type, size: it.size, sent: it.sent, location: it.location || null, base: it.base || null, take: it.take || null });
  const write = (stores, fn) => open().then((db) => new Promise((res, rej) => {
    const t = db.transaction(stores, 'readwrite'); fn(t); t.oncomplete = () => res(); t.onerror = t.onabort = () => rej(t.error);
  }));
  return {
    add: (it) => write(['meta', 'file'], (t) => { t.objectStore('file').put(it.file, it.id); t.objectStore('meta').put(meta(it)); }),
    save: (it) => write(['meta'], (t) => t.objectStore('meta').put(meta(it))),
    drop: (id) => write(['meta', 'file'], (t) => { t.objectStore('meta').delete(id); t.objectStore('file').delete(id); }),
    file: (id) => open().then((db) => new Promise((res, rej) => {
      const g = db.transaction(['file'], 'readonly').objectStore('file').get(id);
      g.onsuccess = () => res(g.result || null); g.onerror = () => rej(g.error);
    })),
    all: () => open().then((db) => new Promise((res, rej) => {
      const t = db.transaction(['meta', 'file'], 'readonly'), out = [], m = t.objectStore('meta').getAll();
      m.onsuccess = () => m.result.forEach((x) => { const g = t.objectStore('file').get(x.id); g.onsuccess = () => { if (g.result) out.push(Object.assign(x, { file: g.result })); }; });
      t.oncomplete = () => res(out); t.onerror = () => rej(t.error);
    }))
  };
})();
async function sendOne(it) {
  if (it.resumed && it.location) {
    // back after the page was closed: ask Drive how much of this video it already has
    it.resumed = false;
    try {
      const q = await fetch(it.location, { method: 'PUT', headers: { 'Content-Range': `bytes */${it.size}` } });
      if (q.ok) { it.sent = it.size; return; }
      if (q.status === 308) { const rg = q.headers.get('Range'); it.sent = rg ? Number(rg.split('-')[1]) + 1 : 0; }
      else { it.location = null; it.sent = 0; }
    } catch (_) {}
  }
  if (!it.location) { it.location = (await call('start', { casa: it.casa, name: it.name, type: it.type, size: it.size, origin: location.origin })).location; it.sent = 0; STORE.save(it).catch(() => {}); }
  const size = it.size;
  while (it.sent < size) {
    const end = Math.min(it.sent + PIECE, size);
    let res = null;
    for (let tryN = 0; tryN < 6 && !res; tryN++) {
      try {
        const r = await fetch(it.location, { method: 'PUT', headers: { 'Content-Range': `bytes ${it.sent}-${end - 1}/${size}` }, body: it.file.slice(it.sent, end) });
        if (r.ok || r.status === 308) res = r;
        else if (r.status === 404 || r.status === 410) { it.location = null; it.sent = 0; throw new Error('sessione scaduta'); }
        else await wait(1500 * (tryN + 1));
      } catch (e) {
        if (!it.location) throw e;
        await wait(1500 * (tryN + 1));
        // where did Drive get to? if it says, carry on from there
        try {
          const q = await fetch(it.location, { method: 'PUT', headers: { 'Content-Range': `bytes */${size}` } });
          if (q.ok) { it.sent = size; res = q; break; }
          const rg = q.headers.get('Range');
          if (rg) { it.sent = Number(rg.split('-')[1]) + 1; status(); break; }
        } catch (_) {}
      }
    }
    if (it.sent >= size) break;
    if (!res) throw new Error('connessione');
    const rg = res.headers.get('Range');
    const before = it.sent;
    it.sent = res.ok ? size : rg ? Number(rg.split('-')[1]) + 1 : end;
    speedAdd(it.sent - before);
    STORE.save(it).catch(() => {});
    status();
  }
}
// Three files travel at a time: for small files (photos) the wait to open each one in Drive weighs more than sending it.
const PARALLEL = 3;
let active = 0;
function pump() {
  if (!CFG.scriptUrl || navigator.onLine === false) return;
  let it;
  while (active < PARALLEL && (it = Q.find((x) => x.state === 'wait' && !(x.retryAt > Date.now())))) sendItem(it);
}
async function sendItem(it) {
  active++; busy = true; awake();
  it.state = 'send'; status();
  try { await sendOne(it); it.state = 'ok'; it.file = null; STORE.drop(it.id).catch(() => {}); }
  catch (e) {
    it.state = 'wait'; it.errors = (it.errors || 0) + 1; status(true);
    if (it.errors === 3 && navigator.onLine) report('Invio non riuscito', `${it.name} · ${fmtMB(it.size)} · arrivati ${fmtMB(it.sent)} · ${(e && e.message) || e}`);
    const ms = Math.min(30000, 4000 * it.errors);
    it.retryAt = Date.now() + ms; setTimeout(pump, ms + 50);
  }
  active--; busy = active > 0; awake();
  status(); pump();
}
window.addEventListener('online', pump);
window.addEventListener('beforeunload', (e) => { if (pending().length) { e.preventDefault(); e.returnValue = ''; } });
// The screen stays on while videos travel and while the camera is on (the phone gives the lock back when the page is left).
async function awake() {
  const on = busy || !!(CAM.stream || CAM.rec);
  try {
    if (on && !lock && navigator.wakeLock && !document.hidden) {
      lock = await navigator.wakeLock.request('screen');
      lock.addEventListener('release', () => { lock = null; });
    } else if (!on && lock) { const l = lock; lock = null; await l.release(); }
  } catch (_) {}
}
// How fast the videos travel (the last 30 seconds of pieces), to tell the client how long is left.
const SPEED = [];
function speedAdd(bytes) {
  const now = Date.now();
  if (bytes > 0) SPEED.push([now, bytes]);
  while (SPEED.length && now - SPEED[0][0] > 30000) SPEED.shift();
}
function timeLeft(bytes) {
  speedAdd(0);
  if (SPEED.length < 2) return '';
  const span = (Date.now() - SPEED[0][0]) / 1000, sum = SPEED.reduce((a, x) => a + x[1], 0);
  if (span < 4 || !sum) return '';
  const s = bytes / (sum / span);
  return s < 60 ? ' · meno di un minuto' : ` · ancora ${Math.round(s / 60)} min`;
}
// «12 foto», «1 video», «12 foto e 1 video»
function things(list, cap) {
  const f = list.filter((x) => /^image\//.test(x.type)).length, v = list.length - f;
  const t = [f ? f + ' foto' : '', v ? v + ' video' : ''].filter(Boolean).join(' e ');
  return cap ? t.charAt(0).toUpperCase() + t.slice(1) : t;
}
let hideT = null;
function status(trouble) {
  const el = $('#send'), p = pending();
  clearTimeout(hideT);
  if (!Q.length) { el.hidden = true; document.body.classList.remove('sending'); return; }
  el.hidden = false; document.body.classList.add('sending'); el.classList.toggle('ok', !p.length); el.classList.toggle('err', !!trouble && !navigator.onLine);
  if (!p.length) { $('#send-t').textContent = Q.length === 1 ? 'Arrivato' : `${things(Q, true)}: tutto arrivato`; hideT = setTimeout(() => { el.hidden = true; document.body.classList.remove('sending'); }, 6000); applyUpdate(); return; }
  const tot = p.reduce((a, x) => a + x.size, 0), done = p.reduce((a, x) => a + x.sent, 0);
  const pct = tot ? Math.floor(done / tot * 100) : 0;
  $('#send-t').textContent = !navigator.onLine ? 'Invio in pausa: manca la connessione' : `Invio di ${things(p)} · ${pct}%${timeLeft(tot - done)}`;
}
// One take into the sending queue: a video, or its photos («… · foto 07.jpg»). The same step done again: the earlier
// take is dropped if none of it has left yet; otherwise both arrive and the new one says «ripresa 2».
function enqueueTake(files, sc) {
  const steps = stepsOf(sc.key), st = steps[sc.i];
  const where = AREA(sc.key) + (sc.key === 'corridoio' ? '' : ' ' + SHAPES[sc.key].name);
  const c = casa() || 'Senza nome', base = `${where} · passo ${String(sc.i + 1).padStart(2, '0')} di ${steps.length} · ${st.title}`;
  const same = (x) => x.casa === c && (x.base ? x.base === base : x.name.replace(/( · ripresa \d+)?( · foto \d+)?\.\w+$/, '') === base);
  const takes = {};
  Q.filter(same).forEach((x) => { const k = x.take || x.id; (takes[k] = takes[k] || []).push(x); });
  Object.values(takes).forEach((xs) => {
    if (xs.every((x) => x.state === 'wait' && !x.sent)) xs.forEach((x) => { Q.splice(Q.indexOf(x), 1); STORE.drop(x.id).catch(() => {}); });
  });
  const n = new Set(Q.filter(same).map((x) => x.take || x.id)).size;
  const rip = n ? ` · ripresa ${n + 1}` : '', take = Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
  files.forEach((file, k) => {
    const ext = (file.name.match(/\.\w+$/) || ['.mp4'])[0].toLowerCase();
    const name = base + rip + (files.length > 1 || /^image\//.test(file.type) ? ` · foto ${String(k + 1).padStart(2, '0')}` : '') + ext;
    const it = { id: take + '-' + k, file, name, base, take, casa: c, type: file.type || 'video/mp4', size: file.size, sent: 0, state: 'wait' };
    Q.push(it);
    // once in the browser's storage, the file is read from there: held in memory it could make the phone close the page
    STORE.add(it).then(() => STORE.file(it.id)).then((f) => { if (f && it.file) it.file = f; })
      .catch((e) => report('Archivio del telefono non disponibile', `${it.name} · ${fmtMB(it.size)} · ${(e && (e.name || e.message)) || e}`));
  });
  status(); pump();
}
const enqueue = (file, sc) => enqueueTake([file], sc);

// ---------- the sheet ----------
const OV = { screen: null };
function sheet(html) { $('#sheet').className = 'sheet'; $('#sheet').innerHTML = html; $('#ov').hidden = false; }
function closeSheet() { $('#ov').hidden = true; $('#sheet').innerHTML = ''; OV.screen = null; saveState(); applyUpdate(); }
// Where the client is, kept in the browser's lasting storage: when the phone closes Chrome (or the page) and the client
// comes back, even days later from the same link, the guide opens on the same step.
const KEEP = 'guida-stato:' + (fromLink || ''), KEEP_DAYS = 7;
function saveState() {
  const c = (comp && comp.state) || {};
  const v = JSON.stringify({ scr: c.scr || null, hist: c.hist || [], rec: OV.screen, t: Date.now() });
  lsSet(KEEP, v);
  try { sessionStorage.setItem(KEEP, v); } catch (_) {}
}
function loadState() {
  const read = (t) => { try { return JSON.parse(t || 'null'); } catch (_) { return null; } };
  let s = null;
  try { s = read(sessionStorage.getItem(KEEP)); } catch (_) {}   // this same tab: always good
  let l = read(lsGet(KEEP));
  if (l && Date.now() - (l.t || 0) > KEEP_DAYS * 86400000) l = null;
  return !s || (l && l.t > (s.t || 0)) ? l : s;
}
const X = '<button type="button" class="o-x" data-a="close" aria-label="Chiudi"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg></button>';
const li = (n, t) => `<li style="display: grid; grid-template-columns: 30px 1fr; gap: 6px; padding: 10px 0; border-top: 1px solid var(--line); font-size: 15px; line-height: 1.45"><span style="font-family: var(--display); font-style: italic; font-size: 17px; color: var(--champ)">${n}</span><span>${t}</span></li>`;

// Registra: film the step with the Camera app, then one tap to pick it; the guide sends it and moves on.
function drawRec(err) {
  saveState();
  const sc = OV.screen, steps = stepsOf(sc.key), st = steps[sc.i], ask = !casa();
  sheet(`<div class="o-top"><div style="display: flex; flex-direction: column; gap: 8px"><span class="o-lab">${AREA(sc.key)} · passo ${sc.i + 1} di ${steps.length}</span><h2 class="o-h" id="ov-title">Registra con la <em>Fotocamera</em></h2></div>${X}</div>
    <ol style="list-style: none; margin: 0; padding: 0">
      ${li('i.', 'Apri l’app <strong>Fotocamera</strong>, modalità <strong>Video</strong>, <strong>4K</strong> e lente <strong>0,5×</strong>.')}
      ${li('ii.', esc(st.text))}
      ${li('iii.', 'Ferma la registrazione, torna qui, tocca <strong>Scegli il video</strong> e seleziona il video appena registrato.')}
      ${li('iv.', 'Nel menu tocca <strong>Libreria foto</strong> (o <strong>Raccolta fotografica</strong>), non la voce per fare un nuovo video.')}
    </ol>
    ${ask ? `<div style="display: flex; flex-direction: column; gap: 8px"><label class="o-lab" for="ov-casa" style="color: var(--soft)">Indirizzo dell’immobile</label><input class="o-in" id="ov-casa" autocomplete="street-address" placeholder="Es. Via Roma 12, Bologna"></div>` : ''}
    ${err ? `<p class="o-err">${esc(err)}</p>` : ''}
    ${CFG.scriptUrl ? '' : '<p class="o-err">L’invio dei video non è ancora collegato: per ora la guida va solo avanti.</p>'}
    <div class="o-row"><button type="button" class="o-btn p" data-a="pick">Scegli il video</button></div>`);
}
// The property's address, when the link doesn't carry it: asked once, before the first take, so every video lands in
// the right folder (without it they would go to «Senza nome»).
let afterCasa = null;
function askCasa(then, err) {
  afterCasa = then;
  sheet(`<div class="o-top"><div style="display: flex; flex-direction: column; gap: 8px"><span class="o-lab">Prima di iniziare</span><h2 class="o-h" id="ov-title">Di che <em>casa</em> si tratta?</h2></div></div>
    <p class="o-p">Serve per mettere i video nella cartella giusta. Lo chiediamo una volta sola.</p>
    <div style="display: flex; flex-direction: column; gap: 8px"><label class="o-lab" for="ov-casa" style="color: var(--soft)">Indirizzo dell’immobile</label><input class="o-in" id="ov-casa" autocomplete="street-address" enterkeyhint="done" placeholder="Es. Via Roma 12, Bologna"></div>
    ${err ? `<p class="o-err">${esc(err)}</p>` : ''}
    <div class="o-row"><button type="button" class="o-btn p" data-a="casa">Avanti</button></div>`);
  setTimeout(() => { const c = $('#ov-casa'); if (c) c.focus(); }, 350);
}
// The end: no uploading to do, only to wait for the videos still travelling.
function drawEnd() {
  const p = pending();
  sheet(`<div class="o-top"><div style="display: flex; flex-direction: column; gap: 8px"><span class="o-lab">Alla fine</span><h2 class="o-h" id="ov-title">${p.length ? 'Quasi <em>fatto</em>' : 'Grazie, <em>è tutto</em>'}</h2></div>${X}</div>
    <p class="o-p" style="color: var(--ink)">${p.length
      ? `Stiamo ancora mandando ${things(p)} (${fmtMB(p.reduce((a, x) => a + x.size - x.sent, 0))}). Tieni aperta questa pagina, con il Wi-Fi se puoi, finché in alto compare «tutto arrivato».`
      : Q.length ? `Abbiamo ricevuto tutto: ${things(Q)}. Puoi chiudere la pagina.` : 'Hai finito le riprese.'}</p>
    <div class="o-row"><button type="button" class="o-btn p" data-a="close">${p.length ? 'Va bene' : 'Chiudi'}</button></div>
    <button type="button" class="o-link" data-a="restart">Ricomincia la guida</button>`);
}
$('#gal').addEventListener('change', (e) => {
  const f = e.target.files && e.target.files[0], sc = OV.screen;
  if (!f || !sc) return;
  if (!/^video\//.test(f.type || 'video/')) { report('Scelto un file che non è un video', `${f.name} · ${f.type}`); drawRec('Questo file non è un video: scegli il video del passo.'); return; }
  if (CFG.scriptUrl) enqueue(f, sc);
  closeSheet();
  if (comp) comp.nextStep({ type: 'step', key: sc.key, i: sc.i });
});
$('#sheet').addEventListener('click', (e) => {
  const b = e.target.closest('[data-a]'); if (!b) return;
  const a = b.dataset.a;
  if (a === 'close') closeSheet();
  if (a === 'restart') { closeSheet(); if (comp) comp.enter({ type: 'setup', i: 0 }, []); }
  if (a === 'casa') {
    const c = $('#ov-casa'), v = c ? c.value.trim() : '';
    if (!v) { askCasa(afterCasa, 'Scrivi l’indirizzo: senza, non sappiamo di che casa sono i video.'); return; }
    setCasa(v);
    const then = afterCasa; afterCasa = null;
    closeSheet();
    if (then) then();   // still inside the tap: the phone can ask for its permissions
    return;
  }
  if (a === 'pick') {
    const c = $('#ov-casa');
    if (c) { if (!c.value.trim()) { drawRec('Scrivi l’indirizzo dell’immobile: serve per sapere di che casa sono i video.'); return; } setCasa(c.value); }
    $('#gal').value = ''; $('#gal').click();
  }
});
$('#ov').addEventListener('click', (e) => { if (e.target === $('#ov') && afterCasa === null) closeSheet(); });
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target && e.target.id === 'ov-casa' && afterCasa !== null) { e.preventDefault(); $('#sheet [data-a="casa"]').click(); return; }
  if (e.key === 'Escape' && !$('#ov').hidden && afterCasa === null) closeSheet();
});

// ---------- the camera inside the guide ----------
// The phone's own camera, opened by the page: the 0.5× lens in 4K at 30 fps, kept on from one step to the next, so
// each step is just: go to the point, press the red button, film, press stop. No app to switch to, no gallery,
// no waiting: the take goes straight into the sending queue. The camera is on only on the recording screen.
const CAM = { stream: null, opening: null, video: null, rec: null, t0: 0, tick: null, sc: null, failed: '', errors: 0 };
// Lighter videos, same frames: HEVC (the Camera app's own format, about half the size for the same picture) where
// the phone lets the page record it; otherwise H.264 at 20 Mbit/s (30 made sending too slow: 7 minutes for 3 videos).
const MIME = (() => {
  if (!window.MediaRecorder || !MediaRecorder.isTypeSupported) return '';
  return ['video/mp4;codecs=hvc1', 'video/mp4;codecs=hev1', 'video/mp4;codecs=avc1', 'video/mp4', 'video/webm;codecs=vp9', 'video/webm'].find((t) => MediaRecorder.isTypeSupported(t)) || '';
})();
const HEVC = /hvc1|hev1/.test(MIME);
const BITRATE = HEVC ? 14e6 : 20e6;   // a minute of video: about 105 MB in HEVC, 150 MB in H.264
// Photos, not video: only the frames are used (for the 3D model of the room and as references), and a photo taken
// straight from the camera is sharper than a frame of a compressed video. 4K JPEG, made by a worker so the camera's
// picture never stalls. Where the phone can't (no OffscreenCanvas), a video as before.
const PHOTO = !!(window.createImageBitmap && window.OffscreenCanvas && OffscreenCanvas.prototype.convertToBlob && window.Worker);
const PHOTO_STEP = 15;    // turns: a photo every 15° actually turned (enough overlap between neighbours for the 3D model)
const PHOTO_WALK = 500;   // walks: a photo every half second (about every 25 cm at a slow walk)
const PHOTO_Q = 0.88;     // JPEG quality: about 2 MB a photo in 4K
const camUsable = () => !CAM.failed && !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && (PHOTO || window.MediaRecorder));
const SHOT = { worker: null, n: 0, waiting: new Map(), failed: false };
function shooter() {
  if (SHOT.worker) return SHOT.worker;
  const src = "onmessage = async (e) => { const { id, bmp, q } = e.data; try { const c = new OffscreenCanvas(bmp.width, bmp.height); c.getContext('2d').drawImage(bmp, 0, 0); bmp.close(); const b = await c.convertToBlob({ type: 'image/jpeg', quality: q }); postMessage({ id, b }); } catch (err) { postMessage({ id, err: String((err && err.message) || err) }); } };";
  SHOT.worker = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' })));
  SHOT.worker.onmessage = (e) => { const w = SHOT.waiting.get(e.data.id); if (!w) return; SHOT.waiting.delete(e.data.id); if (e.data.b) w.ok(e.data.b); else w.no(new Error(e.data.err)); };
  return SHOT.worker;
}
async function shoot() {
  const v = CAM.video;
  if (!v || !v.videoWidth) throw new Error('nessuna immagine');
  const bmp = await createImageBitmap(v);
  const id = ++SHOT.n;
  return new Promise((ok, no) => { SHOT.waiting.set(id, { ok, no }); shooter().postMessage({ id, bmp, q: PHOTO_Q }, [bmp]); });
}
// One photo for this take; at most two being made at once (unless it is the last one), so the phone never piles up
function takeShot(r, last) {
  if (!r || (r.making >= 2 && !last)) return false;
  r.making++;
  r.shots.push(shoot().catch((e) => { if (!SHOT.failed) { SHOT.failed = true; report('Foto non riuscita', String((e && e.message) || e)); } return null; })
    .finally(() => { r.making--; }));
  return true;
}
const camWanted = () => !!comp && !document.hidden && (comp.cur().type === 'rec' || (comp.cur().type === 'step' && CAM.granted));
function camFail(e, where) {
  const n = (e && e.name) || '';
  // refused, or no camera: the guide goes back to the Camera app for the rest of the visit
  if (/NotAllowed|NotFound|Security|NotSupported|TypeError/.test(n) || ++CAM.errors >= 3) CAM.failed = n || 'errore';
  report('Fotocamera della guida non disponibile', `${where} · ${n} ${(e && e.message) || e}`);
}
async function camStream() {
  const want = (id) => navigator.mediaDevices.getUserMedia({
    video: Object.assign({ width: { ideal: 3840 }, height: { ideal: 2160 }, frameRate: { ideal: 30 } }, id ? { deviceId: { exact: id } } : { facingMode: { ideal: 'environment' } }),
    audio: false   // only the pictures: the frames are what counts, and the phone asks for the camera alone
  });
  const known = lsGet('guida-lente');
  let s;
  try { s = await want(known); } catch (e) { if (!known || /NotAllowed|Security/.test(e.name)) throw e; lsSet('guida-lente', null); s = await want(null); }
  if (!known) {
    // the first time: look for the 0.5× lens among the cameras (their names are readable once allowed)
    const cams = (await navigator.mediaDevices.enumerateDevices()).filter((d) => d.kind === 'videoinput');
    const wide = cams.find((d) => /ultra/i.test(d.label)) || cams.find((d) => /0[.,]5/.test(d.label));
    const now = s.getVideoTracks()[0].getSettings().deviceId;
    if (wide && wide.deviceId && wide.deviceId !== now) {
      s.getTracks().forEach((t) => t.stop());
      s = await want(wide.deviceId);
    }
    if (wide && wide.deviceId) lsSet('guida-lente', wide.deviceId);
  }
  // Android: the wide lens is often a zoom below 1 on the main camera
  const tr = s.getVideoTracks()[0], caps = tr.getCapabilities ? tr.getCapabilities() : {};
  CAM.ultra = /ultra|0[.,]5/i.test(tr.label || '');
  if (caps.zoom && caps.zoom.min < 1) { try { await tr.applyConstraints({ advanced: [{ zoom: caps.zoom.min }] }); CAM.ultra = true; } catch (_) {} }
  return s;
}
function camOpen() {
  if (CAM.stream) return Promise.resolve(CAM.stream);
  if (!CAM.opening) CAM.opening = camStream().then((s) => {
    CAM.opening = null;
    if (!camWanted()) { s.getTracks().forEach((t) => t.stop()); return null; }   // the client left meanwhile
    CAM.stream = s; CAM.errors = 0; CAM.granted = true; awake();
    // the phone takes the camera away (a call, Control Center, another app): stop cleanly, ready to film again
    s.getVideoTracks()[0].addEventListener('ended', () => { if (CAM.stream === s) { camLost('La fotocamera si è fermata: tocca il tasto rosso per riprendere.'); } });
    camShow();
    return s;
  }, (e) => { CAM.opening = null; throw e; });
  return CAM.opening;
}
function camClose() {
  recCancel();
  if (CAM.stream) CAM.stream.getTracks().forEach((t) => t.stop());
  CAM.stream = null;
  if (CAM.video) { CAM.video.srcObject = null; CAM.video.remove(); }
  document.body.classList.remove('cam-on');
  awake();
}
// The picture under the recording screen (the canvas's sketch stands in for it until the camera is on)
function camShow() {
  const rs = document.querySelector('#board .rec-screen');
  if (!rs || !CAM.stream) return;
  if (!CAM.video) {
    const v = CAM.video = document.createElement('video');
    v.className = 'cam-live'; v.muted = true; v.playsInline = true; v.autoplay = true;
    v.setAttribute('playsinline', ''); v.setAttribute('muted', ''); v.setAttribute('aria-hidden', 'true');
    v.addEventListener('pause', () => { if (CAM.stream && v.isConnected) v.play().catch(() => {}); });
  }
  const v = CAM.video;
  if (v.srcObject !== CAM.stream) v.srcObject = CAM.stream;
  if (v.parentNode !== rs) rs.prepend(v);
  v.play().catch(() => {});
  document.body.classList.add('cam-on');
}
function clock(ms) { const t = Math.floor(ms / 1000); return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0'); }
function recStart(sc) {
  if (CAM.rec || !CAM.stream) return;
  if (PHOTO) return photoStart(sc);
  let r;
  try { r = new MediaRecorder(CAM.stream, Object.assign({ videoBitsPerSecond: BITRATE }, MIME ? { mimeType: MIME } : {})); }
  catch (e) { camFail(e, 'registrazione'); CAM.failed = CAM.failed || 'MediaRecorder'; camClose(); toCameraApp(sc); return; }
  const chunks = [];   // this take's own pieces: the previous take may still be handing over its last ones
  CAM.rec = r; CAM.sc = sc; r.chunks = chunks;
  turnBegin(sc);
  r.ondataavailable = (e) => { if (e.data && e.data.size) chunks.push(e.data); };
  r.onerror = (e) => report('Registrazione interrotta', String((e.error && (e.error.name || e.error.message)) || e));
  r.start(1000);
  CAM.t0 = Date.now();
  // the time ticks in its own text only: redrawing the whole page twice a second could stall the camera's picture
  CAM.tick = setInterval(() => { const el = document.querySelector('#board .rec-clock'); if (el && el.firstChild) el.firstChild.nodeValue = clock(Date.now() - CAM.t0); }, 500);
  if (CAM.video) CAM.video.play().catch(() => {});
  awake();
}
// A take of photos: one at the start, then every 15° turned (see aimLoop) or every half second walking.
function photoStart(sc) {
  const r = CAM.rec = { photo: true, shots: [], making: 0, next: PHOTO_STEP, timer: null };
  CAM.sc = sc;
  turnBegin(sc);
  CAM.t0 = Date.now();
  takeShot(r);
  if (stepsOf(sc.key)[sc.i].kind !== 'turn') r.timer = setInterval(() => takeShot(r), PHOTO_WALK);
  CAM.tick = setInterval(() => { const el = document.querySelector('#board .rec-clock'); if (el && el.firstChild) el.firstChild.nodeValue = `${clock(Date.now() - CAM.t0)} · ${r.shots.length} foto`; }, 500);
  if (CAM.video) CAM.video.play().catch(() => {});
  awake();
}
// Stop the take: with keep, it goes into the sending queue as soon as its photos (or its video) are ready.
function recStop(keep) {
  const r = CAM.rec, sc = CAM.sc, ms = Date.now() - CAM.t0;
  if (!r) return;
  CAM.rec = null; CAM.sc = null; clearInterval(CAM.tick);
  turnEnd();
  if (r.photo) {
    clearInterval(r.timer);
    if (keep) takeShot(r, true);   // the view where the take ends
    Promise.all(r.shots).then((bs) => {
      if (!keep) return;
      const ok = bs.filter((b) => b && b.size);
      if (!ok.length) { report('Nessuna foto', clock(ms)); takeAgain(sc); return; }
      if (CFG.scriptUrl) enqueueTake(ok.map((b) => new File([b], 'foto.jpg', { type: 'image/jpeg' })), sc);
    });
    return;
  }
  r.onstop = () => {
    const chunks = r.chunks; r.chunks = null;
    if (!keep) return;
    const type = (r.mimeType || MIME || 'video/mp4').split(';')[0], ext = /webm/.test(type) ? '.webm' : '.mp4';
    const blob = new Blob(chunks, { type });
    if (!blob.size) { report('Registrazione vuota', `${type} · ${clock(ms)}`); takeAgain(sc); return; }
    if (CFG.scriptUrl) enqueue(new File([blob], 'ripresa' + ext, { type }), sc);
  };
  try { r.stop(); } catch (_) {}
}
// A take that came out empty: back to that step, ready to film it again (unless the client is already filming the next)
function takeAgain(sc) {
  if (!comp || CAM.rec) return;
  const cur = comp.cur();
  let h = comp.hist();
  if (cur.type === 'rec' && cur.key === sc.key && cur.i === sc.i + 1) h = h.slice(0, -1);
  else if (cur.type === 'space' && cur.fatto === sc.key) h = [{ type: 'space' }];
  else return;
  comp.enter({ type: 'rec', key: sc.key, i: sc.i, ready: true, guide: true, note: 'La ripresa non è venuta: rifalla.' }, h);
}
function recCancel() { if (CAM.rec) recStop(false); }
// The take could not go on (the page was left, the camera was taken away): this step is ready to be filmed again.
function camLost(note) {
  const sc = CAM.sc || (comp && comp.cur());
  const was = !!CAM.rec;
  recCancel();
  if (CAM.stream) { CAM.stream.getTracks().forEach((t) => t.stop()); CAM.stream = null; }
  if (comp && sc && sc.type === 'rec' && (was || !sc.ready)) comp.enter({ type: 'rec', key: sc.key, i: sc.i, ready: true, guide: true, note }, comp.hist());
}
// The camera can't be used here: this step (and the next ones) with the Camera app, as before.
function toCameraApp(sc) {
  comp.enter({ type: 'step', key: sc.key, i: sc.i }, comp.hist());
  OV.screen = { type: 'rec', key: sc.key, i: sc.i, guide: true }; drawRec();
}
// Keep the camera in step with the screen: on for the recording screen, recording while it is the "live" one.
function camSync() {
  if (!camWanted()) { if (CAM.stream || CAM.opening || CAM.rec) camClose(); return; }
  const sc = comp.cur();
  camOpen().then((s) => {
    if (!s) return;
    camShow();
    const now = comp.cur();
    if (now.type === 'rec' && !now.ready && !CAM.rec && now.key === sc.key && now.i === sc.i) recStart(now);
  }).catch((e) => {
    camFail(e, 'apertura');
    const now = comp.cur();
    if (now.type !== 'rec') return;
    if (!camUsable()) toCameraApp(now);
    else comp.enter({ type: 'rec', key: now.key, i: now.i, ready: true, guide: true, note: 'La fotocamera non si è accesa: tocca il tasto rosso per riprovare.' }, comp.hist());
  });
}

// ---------- how far the client has turned: the motion sensors ----------
// The gyroscope says how fast the phone turns; turning around the up-down axis (measured against gravity, so it works
// however the phone is tilted) adds up to the degrees turned. The ring on the trail shows it, and when the turn is
// complete the take stops by itself. Without the sensors: the arrow alone, and a sound when it reaches the end.
const MOT = { asked: false, ok: false, on: false, yaw: 0, last: 0, seen: 0, g: null, arc: 0, done: false, check: null, endT: null };
function motionAsk() {   // called inside a tap: the iPhone asks only then
  if (MOT.asked) return;
  MOT.asked = true;
  const D = window.DeviceMotionEvent;
  if (!D) return;
  const on = () => { MOT.ok = true; window.addEventListener('devicemotion', onMotion); };
  if (typeof D.requestPermission === 'function') D.requestPermission().then((r) => { if (r === 'granted') on(); }, () => {});
  else on();
}
function onMotion(e) {
  const now = performance.now();
  const g = e.accelerationIncludingGravity;
  if (g && g.x != null) MOT.g = [g.x, g.y, g.z];
  const r = e.rotationRate;
  if (!r || r.alpha == null) return;
  MOT.seen = now;
  if (!MOT.on) { MOT.last = now; return; }
  const dt = MOT.last ? Math.min(0.1, (now - MOT.last) / 1000) : 0;
  MOT.last = now;
  // Turning around the up-down axis = the phone's rotation measured along gravity. The three numbers come in two orders:
  // the standard one (alpha around z, beta around x, gamma around y) and the iPhone's (alpha around x, beta around y,
  // gamma around z). Both are added up; the one that sees the turn is the right one (the other sees almost nothing).
  const a = r.alpha || 0, b = r.beta || 0, c = r.gamma || 0;
  let rateStd = c, rateIos = b;
  if (MOT.g) {
    const [x, y, z] = MOT.g, n = Math.hypot(x, y, z) || 1;
    rateStd = (b * x + c * y + a * z) / n;
    rateIos = (a * x + b * y + c * z) / n;
  }
  MOT.yawStd += rateStd * dt; MOT.yawIos += rateIos * dt;
  MOT.yaw = Math.abs(MOT.yawIos) > Math.abs(MOT.yawStd) ? MOT.yawIos : MOT.yawStd;
  turnTick();
}
function turnBegin(sc) {
  turnEnd();
  const st = stepsOf(sc.key)[sc.i];
  if (st.kind !== 'turn') return;
  // the arrow starts where the phone points and goes at 15° a second, frame by frame, to the end of the turn
  Object.assign(MOT, { on: true, yaw: 0, yawStd: 0, yawIos: 0, last: 0, arc: st.arc.gradi, done: false, sim: false, ended: false, started: false, t0: Date.now(), tgt: 0, lastF: 0, k: aimK() });
  const w = document.querySelector('#board .aim-world');
  if (w) w.style.setProperty('--len', (MOT.arc * MOT.k).toFixed(0) + 'px');
  if (!aimRaf) aimRaf = requestAnimationFrame(aimLoop);
  // no movement data within a second: no sensors here; the line moves with the arrow (it shows the pace) and a sound
  // marks the end of the turn
  MOT.check = setTimeout(() => { if (performance.now() - MOT.seen >= 1000) MOT.sim = true; }, 1000);
}
function turnTick() {
  if (!MOT.arc || MOT.done) return;
  // done only when both are at the end: the phone has turned the whole way (a few degrees of grace) AND the arrow has
  // arrived. Slower than the arrow: it waits for the phone. Faster: it waits for the arrow.
  if (Math.abs(MOT.yaw) >= MOT.arc - 4 && MOT.tgt >= MOT.arc && Date.now() - CAM.t0 > 1500 && CAM.rec) {
    MOT.done = true;
    chime();
    const sc = comp.cur();
    setTimeout(() => { if (CAM.rec && comp.cur() === sc) comp.afterRec(sc, true); }, 350);
  }
}
// The arrow set in the room, moved once a frame: the layer with the line slides back by the degrees turned, the
// arrow slides forward by the degrees it should be at. Only transforms: the page is not redrawn while filming.
// How many px of the guide's screen one degree of turning moves the room: what the lens sees across the screen
// (0.5×: about 104° on the picture's long side; 1×: about 69°), less what the screen crops of the picture.
function aimK() {
  const v = CAM.video;
  if (!v || !v.videoWidth || !v.clientWidth) return 6;
  const vw = v.videoWidth, vh = v.videoHeight, ew = v.clientWidth, eh = v.clientHeight;
  const long = CAM.ultra ? 104 : 69, rad = Math.PI / 180;
  const across = vw >= vh ? long : 2 * Math.atan(Math.tan(long / 2 * rad) * vw / vh) / rad;   // the picture's width, in degrees
  const shown = ew / (vw * Math.max(ew / vw, eh / vh));                                        // the part of it on screen
  const deg = 2 * Math.atan(Math.tan(across / 2 * rad) * shown) / rad;
  return deg > 10 ? ew / deg : 6;
}
const PACE_TURN = 15;   // degrees a second, as in the design
let aimRaf = 0;
function aimLoop(now) {
  aimRaf = 0;
  if (!MOT.arc) return;
  // the arrow moves on with the frames actually drawn: if the phone stops drawing for a moment, it waits too (no jump)
  const dt = MOT.lastF ? Math.min(0.05, (now - MOT.lastF) / 1000) : 0;
  MOT.lastF = now;
  // the arrow waits in the ring until the phone starts turning (3°), then sets off from there with it: nobody starts
  // behind. Without sensors there is nothing to wait for: it sets off at once.
  if (!MOT.started && !MOT.sim && Math.abs(MOT.yaw) >= 3) { MOT.started = true; MOT.tgt = Math.min(MOT.arc, Math.abs(MOT.yaw)); }
  if (CAM.rec && (MOT.started || MOT.sim)) MOT.tgt = Math.min(MOT.arc, MOT.tgt + PACE_TURN * dt);
  const tgt = MOT.tgt, yaw = MOT.sim ? tgt : Math.min(Math.abs(MOT.yaw), MOT.arc + 30), k = MOT.k || 6;
  const w = document.querySelector('#board .aim-world'), a = document.querySelector('#board .aim-arrow');
  // the arrow never leaves the screen: too far ahead or behind, it waits at the edge on its side
  const off = Math.max(-165, Math.min(165, (tgt - yaw) * k));
  if (w) w.style.transform = `translateX(${(-yaw * k).toFixed(1)}px)`;
  if (a) a.style.transform = `translateX(${(yaw * k + off).toFixed(1)}px)`;
  // a photo every 15° actually turned (without sensors: every 15° of the arrow)
  const r = CAM.rec;
  if (r && r.photo && Math.min(yaw, MOT.arc) >= r.next && takeShot(r)) r.next += PHOTO_STEP;
  // without sensors: a sound when the arrow is at the end
  if (MOT.sim && tgt >= MOT.arc && !MOT.ended) { MOT.ended = true; chime(); say('Fatto. Tocca stop.'); }
  else if (!MOT.sim) turnTick();
  aimRaf = requestAnimationFrame(aimLoop);
}
function turnEnd() {
  MOT.on = false; MOT.arc = 0;
  clearTimeout(MOT.check); clearTimeout(MOT.endT);
  if (aimRaf) { cancelAnimationFrame(aimRaf); aimRaf = 0; }
}

// ---------- the voice and the sounds while filming (the microphone is off: they don't end up in the video) ----------
let AC = null;
function audioUnlock() {   // inside a tap
  try { AC = AC || new (window.AudioContext || window.webkitAudioContext)(); if (AC.state !== 'running') AC.resume(); } catch (_) {}
  try { if (window.speechSynthesis && !audioUnlock.done) { audioUnlock.done = true; const u = new SpeechSynthesisUtterance(' '); u.volume = 0; speechSynthesis.speak(u); } } catch (_) {}
}
// two soft notes, rising: done
function chime() {
  try {
    if (!AC) return;
    const t = AC.currentTime + 0.01;
    [[1046.5, 0], [1568, 0.12]].forEach(([f, d]) => {
      const o = AC.createOscillator(), g = AC.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, t + d); g.gain.exponentialRampToValueAtTime(0.25, t + d + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + d + 0.5);
      o.connect(g).connect(AC.destination); o.start(t + d); o.stop(t + d + 0.55);
    });
  } catch (_) {}
}
let VOICE = null;
function say(t) {
  try {
    const S = window.speechSynthesis;
    if (!S || !t) return;
    if (!VOICE) VOICE = S.getVoices().filter((v) => /^it/i.test(v.lang)).sort((a, b) => (b.localService - a.localService))[0] || null;
    S.cancel();
    const u = new SpeechSynthesisUtterance(t);
    u.lang = 'it-IT'; if (VOICE) u.voice = VOICE; u.rate = 1.02;
    S.speak(u);
  } catch (_) {}
}
// what the voice says: the step's own words, with the red button instead of «Registra»
function sayFor(sc) {
  if (!sc) return;
  if (sc.type === 'space' && sc.fatto) return say('Spazio finito. Scegli il prossimo.');
  if (sc.type !== 'rec') return;
  const st = stepsOf(sc.key)[sc.i];
  if (sc.ready) say((sc.note ? sc.note + ' ' : '') + st.text.replace(/[()]/g, '').replace(/\bpremi Registra\b/g, 'tocca il tasto rosso').replace(/\bPremi Registra\b/g, 'Tocca il tasto rosso'));
  else if (st.kind !== 'turn') say('Cammina piano. Tocca stop quando arrivi.');
  else if (!lsGet('guida-freccia')) { lsSet('guida-freccia', '1'); say('Gira piano e tieni la freccia dentro il cerchio.'); }   // the first turn only
  else say('Segui la freccia.');
}

// ---------- hooks into the guide ----------
const _enter = Component.prototype.enter;
Component.prototype.enter = function (screen, h) {
  comp = this;
  // without the camera inside the guide: the step screen, and Registra opens the Camera app sheet, as before
  if (screen && screen.type === 'rec' && !camUsable()) {
    if (screen.ready) { _enter.call(this, { type: 'step', key: screen.key, i: screen.i }, h); saveState(); return; }
    OV.screen = { type: 'rec', key: screen.key, i: screen.i, guide: true }; drawRec(); return;
  }
  // a tap that starts a take: the moment the iPhone allows the motion sensors and the sound
  if (screen && screen.type === 'rec' && !screen.ready) { motionAsk(); audioUnlock(); }
  if (screen && screen.type === 'end') { drawEnd(); return; }
  const was = this.cur();
  // leaving a take any way but Stop (never happens from the buttons): it is not kept
  if (CAM.rec && !(screen && screen.type === 'rec' && !screen.ready && screen.key === was.key && screen.i === was.i)) recCancel();
  _enter.call(this, screen, h);
  saveState();
  if (screen && screen.type === 'rec' && !casa() && $('#ov').hidden) askCasa(() => {});
  if (!(screen && screen.type === 'rec' && !screen.ready) && window.speechSynthesis) speechSynthesis.cancel();
  sayFor(screen);
  queueMicrotask(() => requestAnimationFrame(camSync));
};
const _go = Component.prototype.go;
Component.prototype.go = function (screen, push) {
  if (screen && screen.type === 'perm' && !camUsable()) return _go.call(this, { type: 'space' }, push);   // the Camera app asks for its own permissions
  if (screen && screen.type === 'end') { comp = this; drawEnd(); return; }
  return _go.call(this, screen, push);
};
// Stop: the take is kept (if long enough to be one) and the next step comes up, camera still on.
const _afterRec = Component.prototype.afterRec;
Component.prototype.afterRec = function (sc, recorded) {
  if (recorded) {
    if (!CAM.rec) { this.enter(Object.assign({}, sc, { ready: true, note: '' }), this.hist()); return; }   // stop before the camera started
    if (Date.now() - CAM.t0 < 1500) { recCancel(); this.enter({ type: 'rec', key: sc.key, i: sc.i, ready: true, guide: true, note: 'Troppo breve: tocca il tasto rosso e riprendi il passo.' }, this.hist()); return; }
    recStop(true);
  }
  return _afterRec.call(this, sc, recorded);
};
// The permission screen: the phone asks for the camera (and, on the iPhone, the motion sensors) once, here.
const _allow = Component.prototype.allowCamera;
Component.prototype.allowCamera = function () {
  if (!casa()) { askCasa(() => this.allowCamera()); return; }
  const go = () => _allow.call(this);
  motionAsk(); audioUnlock();
  if (!camUsable()) return go();
  camStream().then((s) => { s.getTracks().forEach((t) => t.stop()); go(); }, (e) => { camFail(e, 'permesso'); go(); });
};
const _fb = Component.prototype.feedbackVals;
Component.prototype.feedbackVals = function () {
  const v = _fb.call(this), fb = (this.state && this.state.fb) || {}, send = v.send;
  v.send = () => {
    if (fb.rating && !fb.sent && CFG.scriptUrl) call('feedback', { rating: fb.rating, text: String(fb.text || '').slice(0, 1000), casa: casa() }).catch((e) => console.warn('feedback non inviato:', e));
    send();
  };
  return v;
};

// ---------- sound on iPhone ----------
// The iPhone does not let a page change the music's volume (it stays at 1): the guide's fade never reached 0 and so
// never paused. Where the volume cannot be set, the music simply stops at once.
const _fadeTo = Component.prototype.fadeTo;
let fixedVolume = null;
Component.prototype.fadeTo = function (level, pause) {
  const a = this.player();
  if (fixedVolume === null) { const v0 = a.volume; a.volume = v0 === 0.5 ? 0.4 : 0.5; fixedVolume = a.volume === v0; a.volume = v0; }
  if (!fixedVolume) return _fadeTo.call(this, level, pause);
  clearInterval(a._fade);
  if (!level && pause) a.pause();
};
// After the Camera app (or a call, or the lock screen) the iPhone suspends the page's sound and allows it back only
// from a touch: the first touch on the guide brings music and effects back, if the speaker is on.
function wakeSound() {
  if (!comp || !comp._on || comp.cur().type === 'rec') return;
  const c = comp.ctx && comp.ctx();
  if (c && c.state !== 'running') { try { c.resume(); } catch (_) {} }
  const a = window.__guidaMusica;
  if (a && a.paused) comp.startMusic(comp.shared().time);
}
document.addEventListener('pointerdown', (e) => { if (!(e.target.closest && e.target.closest('.snd'))) wakeSound(); }, true);

// ---------- leaving the browser: the music stops (the client is going to the Camera app) and comes back after ----------
document.addEventListener('visibilitychange', () => {
  const a = window.__guidaMusica, v = document.querySelector('#board .prato-video');
  if (document.hidden) {
    if (a && !a.paused) { a.pause(); window.__guidaPausa = true; } if (v) v.pause();
    // the phone stops the camera outside the page: a take cut short is not kept, the step is ready to be filmed again
    if (comp && comp.cur().type === 'rec' && !comp.cur().ready) camLost('La ripresa si è interrotta quando sei uscito: riprendi il passo.');
    camClose();
    return;
  }
  if (v && v.style.visibility !== 'hidden') v.play().catch(() => {});
  if (window.__guidaPausa && comp && comp.musicOn() && comp.cur().type !== 'rec') comp.startMusic(comp.shared().time);
  window.__guidaPausa = false;
  camSync();
});

// ---------- the meadow: with Low Power Mode the phone refuses to start videos by themselves, and shows its own
// play button; then the still photo of the meadow stays, and the wind comes back at the first touch ----------
function meadow() {
  const v = document.querySelector('#board .prato-video');
  if (!v) return;
  v.muted = true; v.playsInline = true;
  const p = v.play();
  if (p && p.catch) p.catch(() => {
    v.style.visibility = 'hidden';
    const wake = () => v.play().then(() => { v.style.visibility = ''; }).catch(() => {});
    document.addEventListener('pointerdown', wake, { once: true, capture: true });
  });
}

// ---------- start ----------
// ---------- updating itself: a new version published while the guide is open reaches the client by itself ----------
// The guide looks at version.json now and then and whenever the client comes back to it. When it differs, it waits
// for a quiet moment (no sheet open, no video travelling) and reloads the newest version, past the phone's cache;
// where the client was and any video still to send are kept, as for any reload.
let newer = null;
async function checkUpdate() {
  if (!window.GUIDA_BUILD || location.protocol === 'file:') return;
  try {
    const r = await fetch('version.json?t=' + Date.now(), { cache: 'no-store' });
    const v = r.ok && (await r.json()).v;
    if (v && v !== window.GUIDA_BUILD) { newer = v; applyUpdate(); }
  } catch (_) {}
}
function applyUpdate() {
  if (!newer || !$('#ov').hidden || pending().length || (comp && comp.cur().type === 'rec')) return;
  try {
    // never twice in a row for the same version (the new page may take a minute to be everywhere)
    const last = JSON.parse(sessionStorage.getItem('guida-agg') || '{}');
    if (last.v === newer && Date.now() - last.t < 5 * 60000) return;
    sessionStorage.setItem('guida-agg', JSON.stringify({ v: newer, t: Date.now() }));
  } catch (_) {}
  saveState();
  const u = new URL(location.href);
  u.searchParams.set('v', newer);
  location.replace(u.toString());
}
setTimeout(checkUpdate, 4000);
setInterval(checkUpdate, 3 * 60000);
document.addEventListener('visibilitychange', () => { if (!document.hidden) checkUpdate(); });

comp = DC.mount($('#board'), $('#dc-tpl'), Component, PROPS);
meadow();
const was = loadState();
if (was && was.scr) {
  const s = was.scr.type === 'rec' ? { type: 'step', key: was.scr.key, i: was.scr.i } : was.scr;
  comp.enter(s, was.hist || []);
  if (was.rec) { OV.screen = was.rec; drawRec(); }
}
STORE.all().then((items) => {
  if (!items.length) return;
  items.forEach((x) => Q.push(Object.assign(x, { state: 'wait', resumed: true })));
  status(); pump();
}).catch(() => {});
fit();
new MutationObserver(refit).observe($('#board'), { childList: true, subtree: true });
if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
