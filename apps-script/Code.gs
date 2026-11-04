/**
 * Guida alle riprese — riceve nel tuo Google Drive i video e i feedback mandati dalla guida,
 * e le risposte al questionario dopo la prova (foretaste-riprese.github.io/questionario).
 *
 * Per ogni immobile crea una sottocartella nella cartella qui sotto; i video arrivano
 * direttamente dal telefono del cliente a Drive (questo script apre solo il "passaggio"),
 * quindi anche i video in 4K da centinaia di MB vanno bene.
 */

// L'ID della cartella Drive dove arrivano i video: è la parte finale del suo indirizzo,
// https://drive.google.com/drive/folders/QUESTO_È_L_ID
const FOLDER_ID = 'INCOLLA_QUI_L_ID_DELLA_CARTELLA';
// Se insieme all'ID è stato copiato altro dell'indirizzo (…?hl=it, …/view), qui si tiene solo l'ID.
const FOLDER = FOLDER_ID.split(/[?#/]/)[0].trim();

// Gli indirizzi della guida: solo da qui si possono mandare i video.
const ORIGINS = ['https://foretaste-riprese.github.io', 'https://josefmars225.github.io'];

const MAX_SIZE = 4 * 1024 * 1024 * 1024;   // 4 GB per video

function doPost(e) {
  try {
    const req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (req.action === 'start') return out(start(req));
    if (req.action === 'feedback') return out(feedback(req));
    if (req.action === 'report') return out(report(req));
    if (req.action === 'questionario') return out(questionario(req));
    return out({ ok: false, error: 'azione sconosciuta' });
  } catch (err) {
    return out({ ok: false, error: String(err && err.message || err) });
  }
}

// Aprendo l'indirizzo dello script nel browser si vede se è attivo.
function doGet() {
  DriveApp.getFolderById(FOLDER);   // fallisce subito se l'ID è sbagliato
  return out({ ok: true, guida: 'pronta' });
}

// Prepara l'arrivo di un video (o di una risposta a voce del questionario): crea il file in Drive e restituisce l'indirizzo
// a cui il telefono manda il video, a pezzi.
function start(req) {
  const size = Number(req.size);
  if (!(size > 0) || size > MAX_SIZE) throw new Error('dimensione del video non valida');
  // the videos of the guide, and the answers given aloud in the questionnaire
  const t0 = String(req.type || '').split(';')[0].trim();
  const type = /^(video|audio)\/[\w.+-]+$/.test(t0) ? t0 : 'video/mp4';
  const folder = casaFolder(req.casa);
  const res = UrlFetchApp.fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true', {
    method: 'post',
    contentType: 'application/json; charset=UTF-8',
    muteHttpExceptions: true,
    headers: {
      Authorization: 'Bearer ' + ScriptApp.getOAuthToken(),
      'X-Upload-Content-Type': type,
      'X-Upload-Content-Length': String(size),
      Origin: ORIGINS.indexOf(req.origin) >= 0 ? req.origin : ORIGINS[0]   // così il telefono può mandare i pezzi direttamente a Drive
    },
    payload: JSON.stringify({ name: clean(req.name, 'video.mp4'), parents: [folder.getId()] })
  });
  const headers = res.getHeaders();
  const location = headers.Location || headers.location;
  if (res.getResponseCode() !== 200 || !location) throw new Error('Drive non ha accettato il video (' + res.getResponseCode() + ')');
  return { ok: true, location: location };
}

// Un feedback: una riga nel foglio "Feedback della guida", nella stessa cartella.
function feedback(req) {
  const rating = Math.max(1, Math.min(5, Math.round(Number(req.rating) || 0)));
  const sheet = namedSheet('Feedback della guida', ['Quando', 'Immobile', 'Stelle', 'Commento']);
  sheet.appendRow([new Date(), clean(req.casa, ''), rating, String(req.text || '').slice(0, 1000)]);
  return { ok: true };
}

// Un problema visto dalla guida sul telefono di un cliente: una riga nel foglio "Problemi della guida".
function report(req) {
  const sheet = namedSheet('Problemi della guida', ['Quando', 'Immobile', 'Cosa', 'Dettagli', 'Telefono e browser', 'Pagina', 'Versione']);
  const text = (v, n) => String(v || '').replace(/[\u0000-\u001f]+/g, ' ').slice(0, n);
  sheet.appendRow([new Date(), clean(req.casa, ''), text(req.kind, 80), text(req.detail, 1000), text(req.ua, 300), text(req.page, 300), text(req.build, 20)]);
  return { ok: true };
}

// Il questionario dopo la prova: una riga per persona nel foglio "Questionario della prova", con una colonna
// per domanda. La pagina manda tutta la riga a ogni risposta: la stessa persona (stesso codice) aggiorna la sua riga.
function questionario(req) {
  const id = String(req.id || '').replace(/[^\w-]/g, '').slice(0, 40);
  if (!id) throw new Error('questionario senza codice');
  const domande = (Array.isArray(req.domande) ? req.domande : []).slice(0, 80).map((d) => cell(d, 400));
  const risposte = (Array.isArray(req.risposte) ? req.risposte : []).slice(0, 80).map((r) => cell(r, 5000));
  const header = ['Codice', 'Iniziato', 'Aggiornato', 'Stato', 'Nome', 'Alloggio', 'Risposte date'].concat(domande);
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);   // due invii della stessa persona insieme: una sola riga
  try {
    const sheet = namedSheet('Questionario della prova', header);
    sheet.getRange(1, 1, 1, header.length).setValues([header]).setFontWeight('bold');
    const found = sheet.getRange(1, 1, Math.max(1, sheet.getLastRow()), 1).createTextFinder(id).matchEntireCell(true).findNext();
    const row = found ? found.getRow() : sheet.getLastRow() + 1;
    const started = found ? sheet.getRange(row, 2).getValue() : new Date();
    const date = risposte.filter((r) => r.trim()).length;
    const vals = [id, started, new Date(), req.finito ? 'Completato' : 'In corso', cell(clean(req.nome, ''), 140), cell(clean(req.casa, ''), 140), date + ' di ' + domande.length].concat(risposte);
    while (vals.length < header.length) vals.push('');
    sheet.getRange(row, 1, 1, vals.length).setValues([vals]);
    sheet.getRange(row, 8, 1, Math.max(1, risposte.length)).setWrap(true).setVerticalAlignment('top');
  } finally {
    lock.releaseLock();
  }
  return { ok: true };
}

// Un testo scritto da un cliente, così com'è: mai preso per una formula del foglio.
function cell(v, n) {
  const t = String(v == null ? '' : v).replace(/[\u0000-\u0008\u000b-\u001f]+/g, ' ').slice(0, n);
  return /^[=+\-@]/.test(t) ? "'" + t : t;
}

function casaFolder(name) {
  const root = DriveApp.getFolderById(FOLDER);
  const title = clean(name, 'Senza nome');
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);   // due video della stessa casa insieme: una sola cartella
  try {
    const found = root.getFoldersByName(title);
    return found.hasNext() ? found.next() : root.createFolder(title);
  } finally {
    lock.releaseLock();
  }
}

// Il foglio con questo nome nella cartella dei video; la prima volta lo crea, con la riga dei titoli.
function namedSheet(name, header) {
  const root = DriveApp.getFolderById(FOLDER);
  const files = root.getFilesByName(name);
  if (files.hasNext()) return SpreadsheetApp.open(files.next()).getSheets()[0];
  const ss = SpreadsheetApp.create(name);
  DriveApp.getFileById(ss.getId()).moveTo(root);
  const sheet = ss.getSheets()[0];
  sheet.appendRow(header);
  sheet.setFrozenRows(1);
  return sheet;
}

function clean(s, fallback) {
  const t = String(s || '').replace(/[\\/:*?"<>|\u0000-\u001f]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 140);
  return t || fallback;
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
