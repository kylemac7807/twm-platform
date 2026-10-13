/* The review workbench page (work/workbench/plan-v2.md). Plain JavaScript over the JSON service in api.py.
   Written for the person working the queue: plain words, one question at a time, a clear Save, visible progress.
   Honest screens: the system's own reason for asking; nothing prefilled; the band defaults to unbanded. */
'use strict';

const S = {
  screen: 'home',
  analyst: localStorage.getItem('twm.analyst') || '',
  tax: null, saved: 0, overview: null,
  queue: { tab: 'titles', groups: [], items: [], selected: [], form: freshForm(), dirty: false },
  docs: { sets: [], setId: null, docId: null, rows: [], filter: 'all', search: '', rowId: null, showDetail: false },
  rules: { pending: null, picked: new Set() },
};
function freshForm() { return { role: '', band: null, tech: '', reason: '', confirm: false, cls: null, docType: '' }; }

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const n = v => (v ?? 0).toLocaleString('en-CA');
const plural = (k, one, many) => `${n(k)} ${k === 1 ? one : many}`;
const short = (s, len = 110) => { s = String(s ?? ''); return s.length > len ? s.slice(0, len).replace(/\s+\S*$/, '') + '…' : s; };
const rateLine = o => { const r = o.rate_as_stated || o.rate_value || ''; const cur = o.currency && !/[£$€]/.test(r) ? ' ' + o.currency : ''; const unit = o.rate_unit ? ' per ' + o.rate_unit : ''; return `${r}${cur}${unit}`; };
/* the system's reason, in plain words for the list; the full text stays in the panel */
function plainWhy(d) {
  d = String(d || '');
  if (/ambiguous:/.test(d)) return 'The title names two roles; choose one.';
  if (/no rule match/.test(d)) return /model abstained|below floor/.test(d) ? 'Not in the role framework yet, and the model was not sure.' : 'Not in the role framework yet.';
  if (/place '/.test(d)) return 'A place name the system never classifies on its own.';
  if (/classification/.test(d)) return 'The document type was a guess; confirm it.';
  if (/suggested only/.test(d)) return 'The link to the contract set is a guess; confirm it.';
  return short(d);
}

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) { let d; try { d = (await r.json()).detail; } catch (e) { d = r.statusText; } throw new Error(typeof d === 'string' ? d : JSON.stringify(d)); }
  return r.json();
}
const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
let toastTimer;
function toast(msg, ok = true) { const t = $('#toast'); t.textContent = msg; t.classList.toggle('bad', !ok); t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2800); }

/* ── small renderers ── */
function statusPill(o) {
  if (o.resolution_status === 'resolved' && o.counted) return '<span class="pill ok">in benchmarks</span>';
  if (o.resolution_status === 'resolved') return '<span class="pill neutral">held back</span>';
  return '<span class="pill wait">to review</span>';
}
function bandPill(o) {
  if (!o.canonical_role_id) return '<span class="muted">–</span>';
  return o.twm_band ? `<span class="pill accent">${esc(o.twm_band.replace('_', ' / '))}</span>` : '<span class="pill neutral">unbanded</span>';
}
const rate = o => `<span class="mono">${esc(o.rate_as_stated || o.rate_value || '')}</span>${o.rate_unit ? ` <span class="muted">/ ${esc(o.rate_unit)}</span>` : ''}`;
const kv = pairs => `<table class="kv">${pairs.filter(([, v]) => v !== null && v !== undefined && v !== '').map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('')}</table>`;
const progress = (done, total, label) => `<div class="prog"><div class="bar"><span style="width:${total ? Math.round(100 * done / total) : 0}%"></span></div><div class="lbl">${label}</div></div>`;

/* ── chrome ── */
async function refreshChrome() {
  S.overview = await api('/api/overview');
  $('#nav-open').textContent = S.overview.open_total;
  $('#nav-open').style.display = S.overview.open_total ? '' : 'none';
  $('#foot-saved').textContent = S.saved;
  $('#foot-left').textContent = S.overview.open_total;
  $$('#nav button').forEach(b => b.classList.toggle('active', b.dataset.screen === S.screen));
}
function needName() {
  if (S.analyst.trim()) return false;
  toast('Enter your name at the top right first. It is saved with every decision.', false);
  $('#analyst').focus();
  return true;
}

/* ── home ── */
async function renderHome() {
  await refreshChrome();
  const ov = S.overview, q = ov.queue, c = ov.counts;
  const parts = [];
  if (q.title) parts.push(plural(ov.title_groups, 'job title', 'job titles'));
  if (q.location) parts.push(plural(q.location, 'place name', 'place names'));
  if (q.intake) parts.push(plural(q.intake, 'document', 'documents'));
  const waiting = parts.length ? parts.join(', ').replace(/, ([^,]*)$/, ' and $1') : '';
  $('#page').innerHTML = `
    <h1>Hello${S.analyst.trim() ? ', ' + esc(S.analyst.trim().split(' ')[0]) : ''}</h1>
    ${!S.analyst.trim() ? '<div class="alert"><span class="dot"></span><div>Enter your name at the top right. It is saved with every decision you make.</div></div>' : ''}
    ${waiting
      ? `<div class="hero"><div><div class="hero-t">${esc(waiting)} to review</div><div class="hero-s">The system could not decide these on its own. Each one takes a minute: read the evidence, answer the question, save.</div></div><button class="btn primary big" data-screen="queue">Start reviewing →</button></div>`
      : '<div class="hero done"><div><div class="hero-t">Nothing to review</div><div class="hero-s">Every rate the system could place is placed. New documents will bring new questions.</div></div></div>'}
    <div class="tiles">
      <div class="tile"><div class="k">Rates found</div><div class="v">${n(c.observations_live)}</div><div class="s">from ${plural(c.documents, 'document', 'documents')} in ${plural(ov.sets.length, 'contract set', 'contract sets')}</div></div>
      <div class="tile ok"><div class="k">In benchmarks</div><div class="v">${n(c.counted)}</div><div class="s">${c.observations_live ? Math.round(100 * c.counted / c.observations_live) : 0}% of rates found</div></div>
      <div class="tile wait"><div class="k">Held back</div><div class="v">${n(c.observations_live - c.counted)}</div><div class="s">${n(ov.rows_unlocked)} of them wait on a title you can decide</div></div>
      <div class="tile"><div class="k">Decided by you</div><div class="v">${n(S.saved)}</div><div class="s">this session</div></div>
    </div>
    <div class="cols even">
      <div class="card"><div class="hd"><h2>Up next</h2><span class="sub">largest first: one answer fixes every rate with that title</span></div>
        <div class="bd flush"><table><thead><tr><th>Job title</th><th>Client</th><th class="num">Rates waiting</th></tr></thead><tbody>
          ${(await api('/api/queue/titles')).slice(0, 6).map(g => `<tr class="row" data-screen="queue"><td>${esc(g.title)}<span class="why">${esc(plainWhy(g.details[0]))}</span></td><td>${esc(g.client || '–')}</td><td class="num">${n(g.rows_unlocked)}</td></tr>`).join('') || '<tr><td colspan="3" class="muted">None.</td></tr>'}
        </tbody></table></div></div>
      <div class="card"><div class="hd"><h2>Contract sets</h2><span class="sub">open one to check rates against the page</span></div>
        <div class="bd"><div class="sets" style="grid-template-columns:1fr">${ov.sets.map(s => `<div class="set" data-go="documents" data-set="${esc(s.root_id)}"><div class="t">${esc(s.root_filename)}</div><div class="m">${plural(s.documents, 'document', 'documents')} · ${esc(s.classes.join(', '))}</div><div class="nums"><span><b>${n(s.rows)}</b> rates</span><span><b>${n(s.counted)}</b> in benchmarks</span></div></div>`).join('')}</div></div></div>
    </div>`;
}

/* ── to review ── */
async function loadTax() { if (!S.tax) S.tax = await api('/api/taxonomy'); }
const TABS = [['titles', 'Job titles'], ['location', 'Place names'], ['intake', 'Documents'], ['notes', 'Notes']];
async function renderQueue() {
  await refreshChrome(); await loadTax();
  const Q = S.queue, q = S.overview.queue;
  const counts = { titles: S.overview.title_groups, location: q.location || 0, intake: q.intake || 0, notes: (q.extraction || 0) + (q.reading || 0) };
  if (Q.tab === 'titles') Q.groups = await api('/api/queue/titles');
  else if (Q.tab === 'notes') Q.items = [...await api('/api/queue/extraction'), ...await api('/api/queue/reading')];
  else Q.items = await api(`/api/queue/${Q.tab}`);
  const list = Q.tab === 'titles' ? Q.groups : Q.items;
  Q.selected = Q.selected.filter(i => i < list.length);
  if (!Q.selected.length && list.length) Q.selected = [0];
  const total = counts.titles + counts.location + counts.intake;
  $('#page').innerHTML = `
    <div class="titlebar"><div><h1>To review</h1><p class="lede">Pick an item, read the evidence, answer the question, save. It moves to the next one for you.</p></div>
      ${progress(S.saved, S.saved + total, `${n(S.saved)} saved this session · ${n(total)} to go`)}</div>
    <div class="cols">
      <div class="card">
        <div class="tabs">${TABS.map(([k, l]) => `<button data-tab="${k}" class="${Q.tab === k ? 'active' : ''}">${l}<span class="n">${counts[k]}</span></button>`).join('')}</div>
        <div class="bd flush" id="qlist">${Q.tab === 'titles' ? titleTable(Q.groups) : itemTable(Q.items, Q.tab)}</div>
      </div>
      <div class="card panel" id="qpanel">${Q.tab === 'titles' ? titlePanel() : itemPanel()}</div>
    </div>`;
}
function titleTable(groups) {
  if (!groups.length) return '<div class="empty">All job titles are decided. Nothing to do here.</div>';
  return `<table><thead><tr><th></th><th>Job title</th><th>Client</th><th class="num">Rates waiting</th></tr></thead><tbody>
    ${groups.map((g, i) => `<tr class="row ${S.queue.selected.includes(i) ? 'sel' : ''}" data-i="${i}"><td><input type="checkbox" data-check="${i}" ${S.queue.selected.includes(i) ? 'checked' : ''} title="Tick several to give them one answer"></td>
      <td>${esc(g.title)}<span class="why">${esc(plainWhy(g.details[0]))}</span></td><td>${esc(g.client || '–')}</td><td class="num">${n(g.rows_unlocked)}</td></tr>`).join('')}
  </tbody></table><div class="history">Tick more than one title only when they are the same role; one answer then covers all of them.</div>`;
}
function itemTable(items, kind) {
  if (!items.length) return '<div class="empty">Nothing to do here.</div>';
  const decidable = kind === 'location' || kind === 'intake';
  return `<table><thead><tr>${decidable ? '<th></th>' : ''}<th>${kind === 'intake' ? 'Document' : 'Item'}</th>${kind === 'intake' ? '' : '<th>Document</th>'}<th>What the system says</th></tr></thead><tbody>
    ${items.map((it, i) => `<tr class="row ${S.queue.selected.includes(i) ? 'sel' : ''}" data-i="${i}">${decidable ? `<td><input type="checkbox" data-check="${i}" ${S.queue.selected.includes(i) ? 'checked' : ''}></td>` : ''}<td>${esc(it.item)}${it.client ? `<span class="doc">${esc(it.client)}</span>` : ''}</td>${kind === 'intake' ? '' : `<td class="doc">${esc(it.filename || '')}</td>`}<td>${esc(plainWhy(it.detail))}<span class="why">${esc(short(it.detail))}</span></td></tr>`).join('')}
  </tbody></table>${decidable ? '' : '<div class="history">Notes are for information. The fix for them is to run the document again, which is done from the command line for now.</div>'}`;
}
function roleSelect(value) {
  return `<select id="f-role"><option value="">Choose a role…</option>${S.tax.families.map(f => `<optgroup label="${esc(f.family)}">${f.roles.map(r => `<option value="${esc(r.id)}" ${r.id === value ? 'selected' : ''}>${esc(r.name)}</option>`).join('')}</optgroup>`).join('')}</select>`;
}
function bandButtons(current) {
  return `<div class="bands" id="f-bands"><button type="button" class="unb ${current === null ? 'active' : ''}" data-band="">not stated</button>${S.tax.bands.map(b => `<button type="button" class="${current === b ? 'active' : ''}" data-band="${b}">${b.replace('_', ' / ')}</button>`).join('')}</div><div class="hint">Leave "not stated" unless the document says how senior the role is.</div>`;
}
function titlePanel() {
  const Q = S.queue, F = Q.form;
  const sel = Q.selected.map(i => Q.groups[i]).filter(Boolean);
  if (!sel.length) return '<div class="empty">Pick a job title on the left.</div>';
  const g = sel[0], ex = g.examples[0] || {};
  const head = sel.length === 1
    ? `<div class="ev"><div class="step">Step 1 · read the evidence</div><h3>${esc(g.title)}</h3><div class="meta">${esc(g.client || 'no client')} · ${plural(g.rows_affected, 'rate', 'rates')} · ${esc(g.documents.join(', '))}</div>
        <div class="quote">${esc(ex.source_quote || '(no quote stored)')}</div>
        ${kv([['Rate', rateLine(ex)], ['Period', ex.period_raw], ['Location on the card', ex.location_raw], ['Level on the card', ex.level_raw], ['Page', ex.source_page]])}
        ${ex.obs_id ? `<img class="closeup" src="/api/rows/${ex.obs_id}/closeup.png" alt="" onerror="this.remove()">` : ''}
        <details class="more"><summary>Why the system is asking</summary><div class="why-box">${esc(g.details.join(' | '))}</div></details>
        ${g.history.length ? `<details class="more"><summary>Earlier answers</summary>${g.history.map(h => `<div class="why-box">${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (replaced)' : ''}</div>`).join('')}</details>` : ''}</div>`
    : `<div class="ev"><div class="step">Step 1 · check they are the same role</div><h3>${plural(sel.length, 'title', 'titles')} selected</h3>${sel.map(x => `<div>${esc(x.title)} <span class="muted">(${esc(x.client || '–')}, ${plural(x.rows_affected, 'rate', 'rates')})</span></div>`).join('')}</div>`;
  return `${head}
    <div class="form">
      <div class="step">Step 2 · answer</div>
      <label for="f-role">Which role is this?</label>${roleSelect(F.role)}
      <label>How senior?</label>${bandButtons(F.band)}
      <label for="f-tech">Technology, if the title names one <span class="muted">(optional)</span></label><select id="f-tech"><option value="">none</option>${S.tax.tech.map(t => `<option ${t === F.tech ? 'selected' : ''}>${esc(t)}</option>`).join('')}</select>
      <label for="f-reason">Why? <span class="muted">(one line; it is kept with the answer)</span></label><textarea id="f-reason" placeholder="the SOW describes this role as the platform’s operations lead">${esc(F.reason)}</textarea>
      ${sel.length > 1 ? `<label class="confirm"><input type="checkbox" id="f-confirm" ${F.confirm ? 'checked' : ''}> Yes, one answer for all ${sel.length} titles (${plural(sel.reduce((a, x) => a + x.rows_affected, 0), 'rate', 'rates')}).</label>` : ''}
      <div class="err" id="f-err"></div>
      <div class="step">Step 3 · save</div>
      <div class="btns"><button class="btn primary" id="f-record">Save and go to next</button><button class="btn" id="f-flag" title="Records that you could not decide; the title stays on the list of held-back rates">Can’t decide yet</button><button class="btn ghost" id="f-skip">Skip</button></div>
      <div class="hint">Ctrl+Enter saves. Arrow keys move between titles.</div>
    </div>`;
}
function itemPanel() {
  const Q = S.queue, F = Q.form;
  const sel = Q.selected.map(i => Q.items[i]).filter(Boolean);
  if (Q.tab === 'notes') return '<div class="empty">Nothing to answer here.</div>';
  if (!sel.length) return '<div class="empty">Pick an item on the left.</div>';
  const it = sel[0];
  if (Q.tab === 'location') {
    const m = /place '([^']+)'/.exec(it.detail || '');
    return `<div class="ev"><div class="step">Step 1 · read</div><h3>${esc(m ? m[1] : it.item)}</h3><div class="meta">on "${esc(it.item)}" · ${esc(it.client || 'no client')} · ${esc(it.filename || '')}</div>
        <div class="why-box">Is this place onshore, nearshore or offshore <b>for this client</b>? The system never decides a place on its own. Your answer is reused for this client from now on.</div></div>
      <div class="form"><div class="step">Step 2 · answer</div><label>For this client, this place is</label><div class="bands" id="f-cls">${S.tax.locations.map(l => `<button type="button" class="${F.cls === l ? 'active' : ''}" data-cls="${l}">${l}</button>`).join('')}</div>
        <label for="f-reason">Why?</label><textarea id="f-reason" placeholder="Buffalo is a short drive from the client’s Toronto teams">${esc(F.reason)}</textarea>
        <div class="err" id="f-err"></div><div class="step">Step 3 · save</div><div class="btns"><button class="btn primary" id="f-record">Save${sel.length > 1 ? ` for ${sel.length} items` : ''}</button><button class="btn ghost" id="f-skip">Skip</button></div></div>`;
  }
  const isClass = /classification/.test(it.detail || '');
  return `<div class="ev"><div class="step">Step 1 · read</div><h3>${esc(it.item)}</h3><div class="meta">${esc(short(it.detail))}</div></div>
    <div class="form"><div class="step">Step 2 · answer</div>${isClass
      ? `<label for="f-doctype">What kind of document is it?</label><select id="f-doctype"><option value="">Choose…</option>${[['msa', 'Master agreement'], ['sow', 'Statement of work'], ['amendment', 'Amendment'], ['rate_card', 'Rate card or pricing exhibit'], ['sla', 'Service levels'], ['solicitation', 'Solicitation / RFP'], ['template', 'Template'], ['invoice', 'Invoice'], ['timesheet', 'Timesheet'], ['other', 'Other']].map(([v, l]) => `<option value="${v}" ${F.docType === v ? 'selected' : ''}>${l}</option>`).join('')}</select>`
      : `<label>Does this document belong to the contract set it was filed with?</label><div class="bands" id="f-cls">${[['confirm', 'Yes'], ['reject', 'No']].map(([v, l]) => `<button type="button" class="${F.cls === v ? 'active' : ''}" data-cls="${v}">${l}</button>`).join('')}</div>`}
      <label for="f-reason">Why?</label><textarea id="f-reason">${esc(F.reason)}</textarea>
      <div class="err" id="f-err"></div><div class="step">Step 3 · save</div><div class="btns"><button class="btn primary" id="f-record">Save</button><button class="btn ghost" id="f-skip">Skip</button></div></div>`;
}
function readForm() {
  const F = S.queue.form;
  const g = (id, k) => { const el = $(id); if (el) F[k] = el.type === 'checkbox' ? el.checked : el.value; };
  g('#f-role', 'role'); g('#f-tech', 'tech'); g('#f-reason', 'reason'); g('#f-confirm', 'confirm'); g('#f-doctype', 'docType');
  S.queue.dirty = !!(F.role || F.reason.trim() || F.band || F.cls || F.docType);
}
function leaveItem() {
  readForm();
  if (S.queue.dirty && !confirm('You typed an answer but did not save it. Discard it?')) return false;
  S.queue.form = freshForm(); S.queue.dirty = false; return true;
}
function nextAfterSave(removed) {
  const Q = S.queue;
  const list = Q.tab === 'titles' ? Q.groups : Q.items;
  Q.selected = [Math.min(Q.selected[0] ?? 0, Math.max(0, list.length - removed - 1))];
  Q.form = freshForm(); Q.dirty = false;
}
async function saveTitle(cantDecide) {
  const Q = S.queue; readForm(); const F = Q.form;
  if (needName()) return;
  const sel = Q.selected.map(i => Q.groups[i]).filter(Boolean);
  const err = $('#f-err');
  if (!cantDecide && !F.role) { err.textContent = 'Choose a role, or press "Can’t decide yet".'; $('#f-role').focus(); return; }
  if (!F.reason.trim()) { err.textContent = 'Add one line saying why.'; $('#f-reason').focus(); return; }
  if (sel.length > 1 && !F.confirm) { err.textContent = 'Tick the box to confirm one answer for all of them.'; return; }
  const role_id = cantDecide ? null : F.role;
  const btn = $('#f-record'); btn.disabled = true; btn.textContent = 'Saving…';
  try {
    const r = await post('/api/decisions/title', { queue_ids: sel.flatMap(g => g.queue_ids), role_id, band: cantDecide ? null : F.band, technology: cantDecide ? null : (F.tech || null), reason: F.reason, decided_by: S.analyst });
    S.saved += 1;
    const name = role_id ? (S.tax.families.flatMap(f => f.roles).find(x => x.id === role_id) || {}).name || role_id : null;
    toast(role_id ? `Saved: ${sel.map(x => x.title).join(', ')} → ${name}${F.band ? ', ' + F.band.replace('_', ' / ') : ''}. ${r.queue.title ? 'Next one is up.' : 'That was the last one.'}` : 'Saved as "can’t decide yet".');
    nextAfterSave(sel.length);
    await renderQueue();
  } catch (e) { err.textContent = e.message; btn.disabled = false; btn.textContent = 'Save and go to next'; }
}
async function saveItem() {
  const Q = S.queue; readForm(); const F = Q.form;
  if (needName()) return;
  const sel = Q.selected.map(i => Q.items[i]).filter(Boolean);
  const err = $('#f-err');
  if (!F.reason.trim()) { err.textContent = 'Add one line saying why.'; $('#f-reason').focus(); return; }
  try {
    if (Q.tab === 'location') {
      if (!F.cls) { err.textContent = 'Choose onshore, nearshore or offshore.'; return; }
      await post('/api/decisions/location', { queue_ids: sel.map(i => i.id), classification: F.cls, reason: F.reason, decided_by: S.analyst });
    } else {
      const it = sel[0];
      const decision = /classification/.test(it.detail || '') ? { doc_class: F.docType } : { link: F.cls };
      if (!decision.doc_class && !decision.link) { err.textContent = 'Choose an answer first.'; return; }
      await post('/api/decisions/intake', { queue_id: it.id, decision, reason: F.reason, decided_by: S.analyst });
    }
    S.saved += 1; toast('Saved.');
    nextAfterSave(sel.length);
    await renderQueue();
  } catch (e) { err.textContent = e.message; }
}

/* ── documents ── */
async function renderDocuments() {
  await refreshChrome();
  const D = S.docs;
  D.sets = await api('/api/sets');
  if (D.setId && !D.sets.some(s => s.root_id === D.setId)) D.setId = null;
  if (!D.setId) {
    $('#page').innerHTML = `<h1>Documents</h1><p class="lede">Each card is one contract and the documents that came with it. Open one to see its rates and check any rate against the page it was read from.</p>
      <div class="sets">${D.sets.map(s => `<div class="set" data-set="${esc(s.root_id)}"><div class="t">${esc(s.root_filename)}</div><div class="m">${plural(s.documents.length, 'document', 'documents')} · ${esc([...new Set(s.documents.map(d => d.doc_class))].join(', '))}</div><div class="nums"><span><b>${n(s.documents.reduce((a, d) => a + d.rows, 0))}</b> rates</span><span><b>${n(s.documents.reduce((a, d) => a + d.counted, 0))}</b> in benchmarks</span>${s.documents.some(d => d.flags.length) ? '<span class="pill wait">needs a look</span>' : ''}</div></div>`).join('')}</div>`;
    return;
  }
  const set = D.sets.find(s => s.root_id === D.setId);
  const withRows = set.documents.filter(d => d.rows);
  if (!D.docId || !set.documents.some(d => d.document_id === D.docId)) D.docId = (withRows[0] || set.documents[0]).document_id;
  const doc = set.documents.find(d => d.document_id === D.docId);
  D.rows = await api(`/api/documents/${D.docId}/rows`);
  let rows = D.rows;
  if (D.filter === 'counted') rows = rows.filter(r => r.counted); else if (D.filter === 'not') rows = rows.filter(r => !r.counted);
  if (D.search) rows = rows.filter(r => (r.observed_title || '').toLowerCase().includes(D.search.toLowerCase()));
  if (D.rowId && !rows.some(r => r.obs_id === D.rowId)) D.rowId = null;
  $('#page').innerHTML = `
    <p class="crumb"><a href="#" data-back="1">Documents</a> › ${esc(set.root_filename)}</p>
    <h1>${esc(set.root_filename.replace(/\.(pdf|html?)$/i, ''))}</h1><p class="lede">${plural(set.documents.length, 'document', 'documents')} in this contract set. Choose a document, then click a rate to see where it came from.</p>
    <div class="card" style="margin-bottom:16px"><div class="hd"><h2>Documents in the set</h2><button class="btn sm" data-detail="1">${D.showDetail ? 'Hide' : 'Show'} how each was identified</button></div>
      <div class="bd flush"><table><thead><tr><th>File</th><th>Kind</th><th class="num">Pages</th><th>Contract number</th><th class="num">Rates</th>${D.showDetail ? '<th class="num">Confidence</th><th>Evidence</th><th>Text</th>' : ''}<th></th></tr></thead><tbody>
      ${set.documents.map(d => `<tr class="row ${d.document_id === D.docId ? 'sel' : ''}" data-doc="${esc(d.document_id)}"><td>${esc(d.filename)}</td><td>${esc(d.doc_class.replace('_', ' '))}</td><td class="num">${d.pages ?? '–'}</td><td>${esc(d.contract_numbers.join(', ')) || '–'}</td><td class="num">${d.rows ? `${n(d.rows)}<span class="why">${n(d.counted)} in benchmarks</span>` : '<span class="muted">none</span>'}</td>${D.showDetail ? `<td class="num">${(d.class_confidence ?? 0).toFixed(2)}</td><td class="muted">${esc(d.evidence)}</td><td>${esc(d.readiness)}${d.extension_mismatch ? ' <span class="pill no">not what its name says</span>' : ''}</td>` : ''}<td>${d.flags.map(f => `<span class="pill wait">${esc(plainWhy(f))}</span>`).join(' ')}</td></tr>`).join('')}
      </tbody></table></div></div>
    <div class="cols">
      <div class="card"><div class="toolbar"><div class="chips">${[['all', 'all'], ['counted', 'in benchmarks'], ['not', 'held back']].map(([k, l]) => `<button class="chip ${D.filter === k ? 'active' : ''}" data-filter="${k}">${l}</button>`).join('')}<span class="muted">${n(rows.length)} of ${plural(D.rows.length, 'rate', 'rates')} in ${esc(doc.filename)}</span></div><input class="search" id="rsearch" placeholder="find a title…" value="${esc(D.search)}"></div>
        <div class="bd flush"><table><thead><tr><th>Title on the document</th><th class="num">Rate</th><th>Period</th><th>Role</th><th>Band</th><th>Status</th></tr></thead><tbody>
        ${rows.map(r => `<tr class="row ${r.obs_id === D.rowId ? 'sel' : ''}" data-row="${r.obs_id}"><td>${esc(r.observed_title)}${r.level_raw ? `<span class="doc">${esc(r.level_raw)}</span>` : ''}</td><td class="num">${rate(r)}</td><td class="muted">${esc(r.period_raw || '')}</td><td>${esc((r.canonical_role_id || '').replace(/_/g, ' '))}</td><td>${bandPill(r)}</td><td>${statusPill(r)}</td></tr>`).join('') || '<tr><td colspan="6" class="muted">No rates match.</td></tr>'}
        </tbody></table></div></div>
      <div class="card panel" id="rpanel">${D.rowId ? '<div class="empty">Loading…</div>' : '<div class="empty">Click a rate to see the page it came from.</div>'}</div>
    </div>`;
  if (D.rowId) renderRowPanel();
}
async function renderRowPanel() {
  const D = S.docs;
  const o = await api(`/api/rows/${D.rowId}`);
  const pos = o.position;
  const img = pos.kind === 'pdf'
    ? `<div class="meta">Page ${pos.page} of ${esc(o.filename)}; the box is where this rate was read.</div><img class="closeup" src="/api/rows/${o.obs_id}/closeup.png" alt="close-up around the row"><img class="pageimg" src="/api/rows/${o.obs_id}/page.png" alt="the page with the row boxed">`
    : `<div class="meta">${esc(o.filename)}: this is a web page, so there is no page image; the quoted cells are the position.</div>`;
  const why = o.counted ? 'in benchmarks' : (o.resolution_status === 'resolved' ? 'held back: the reading was not confident enough (needs 0.90, has ' + o.extraction_confidence + ')' : 'held back: the title is not decided yet');
  $('#rpanel').innerHTML = `
    <div class="ev"><h3>${esc(o.observed_title)}</h3><div class="meta">${esc(o.vendor || '')} → ${esc(o.client || '')}</div><div class="quote">${esc(pos.quote || '(no quote stored)')}</div>${img}</div>
    <div class="ev"><h3 class="h4">What the document says</h3>${kv([['Rate', rateLine(o)], ['Period', o.period_raw], ['Location', o.location_raw], ['Level', o.level_raw], ['Condition', o.qualifier], ['Reading confidence', o.extraction_confidence]])}
      ${o.reporting_value !== null && o.reporting_currency && o.currency !== o.reporting_currency ? kv([[`In ${o.reporting_currency} (converted)`, o.reporting_value], ['Exchange rate', o.fx_rate], ['Rate date', o.fx_date], ['Rate source', o.fx_source]]) : ''}</div>
    <div class="ev"><h3 class="h4">What the system made of it</h3>${kv([['Role', (o.canonical_role_id || 'not decided').replace(/_/g, ' ')], ['Band', o.twm_band ? o.twm_band.replace('_', ' / ') : (o.canonical_role_id ? 'not stated' : '')], ['Band from', o.band_source], ['Technology', o.attr_technology], ['Location', o.attr_location], ['Status', why]])}</div>
    ${o.history.length ? `<div class="history"><b>Answers given on this title</b>${o.history.map(h => `<div>${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (replaced)' : ''}</div>`).join('')}</div>` : ''}`;
}

/* ── apply decisions ── */
async function renderRules() {
  await refreshChrome();
  const R = S.rules;
  R.pending = await api('/api/rules/pending');
  const section = (kind, title, cols, labels) => {
    const rows = R.pending[kind];
    return `<div class="card" style="margin-bottom:16px"><div class="hd"><h2>${title}</h2><span class="sub">${rows.length ? plural(rows.length, 'answer', 'answers') + ' waiting' : 'nothing waiting'}</span></div>
      ${rows.length ? `<div class="toolbar"><div class="chips"><a class="btn sm" href="/api/rules/pending.csv?kind=${kind}">1 · Download</a><button class="btn sm" data-applied="${kind}">2 · Mark the ticked rows as done</button></div></div>
      <div class="bd flush"><table><thead><tr><th></th>${labels.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>
        ${rows.map(r => `<tr><td><input type="checkbox" data-pick="${r.decision_id}" ${R.picked.has(r.decision_id) ? 'checked' : ''}></td>${cols.map(c => `<td>${esc(String(r[c] ?? '').replace(/_/g, ' '))}</td>`).join('')}</tr>`).join('')}
      </tbody></table></div>` : ''}</div>`;
  };
  $('#page').innerHTML = `<h1>Apply decisions</h1><p class="lede">Your answers take effect in the ledger the moment you save them. They become permanent rules for every future document once Claude adds them to the role framework. Download the rows, hand them over, then tick them off here.</p>
    ${section('title_mappings', 'Job titles', ['observed_title', 'source', 'canonical_role_id', 'twm_band', 'reviewer'], ['Title', 'Client', 'Role', 'Band', 'Decided by'])}
    ${section('location_rules', 'Place names', ['client_key', 'place', 'classification', 'decided_by', 'reason'], ['Client', 'Place', 'Answer', 'Decided by', 'Why'])}`;
}

/* ── routing and events ── */
const RENDER = { home: renderHome, queue: renderQueue, documents: renderDocuments, rules: renderRules };
async function go(screen) { if (S.screen === 'queue' && screen !== 'queue' && !leaveItem()) return; S.screen = screen; await RENDER[screen](); window.scrollTo(0, 0); }

document.addEventListener('click', async e => {
  const t = e.target.closest('[data-screen],[data-go],[data-tab],[data-i],[data-check],[data-band],[data-cls],[data-set],[data-back],[data-doc],[data-row],[data-filter],[data-pick],[data-applied],[data-detail],#f-record,#f-flag,#f-skip');
  if (!t) return;
  if (t.dataset.screen) return go(t.dataset.screen);
  if (t.dataset.go) { e.preventDefault(); if (t.dataset.set) { S.docs.setId = t.dataset.set; S.docs.rowId = null; S.docs.docId = null; } return go(t.dataset.go); }
  if (t.dataset.tab) { if (!leaveItem()) return; S.queue.tab = t.dataset.tab; S.queue.selected = []; return renderQueue(); }
  if (t.dataset.check !== undefined) { const i = +t.dataset.check; const sel = S.queue.selected; readForm(); S.queue.selected = t.checked ? [...sel, i].sort((a, b) => a - b) : sel.filter(x => x !== i); return renderQueue(); }
  if (t.dataset.i !== undefined) { if (S.queue.selected.length === 1 && S.queue.selected[0] === +t.dataset.i) return; if (!leaveItem()) return; S.queue.selected = [+t.dataset.i]; return renderQueue(); }
  if (t.dataset.band !== undefined) { S.queue.form.band = t.dataset.band || null; $$('#f-bands button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.dataset.cls) { S.queue.form.cls = t.dataset.cls; $$('#f-cls button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.id === 'f-record') return S.queue.tab === 'titles' ? saveTitle(false) : saveItem();
  if (t.id === 'f-flag') return saveTitle(true);
  if (t.id === 'f-skip') { if (!leaveItem()) return; const list = S.queue.tab === 'titles' ? S.queue.groups : S.queue.items; S.queue.selected = [((S.queue.selected[0] ?? -1) + 1) % Math.max(1, list.length)]; return renderQueue(); }
  if (t.dataset.set) { S.docs.setId = t.dataset.set; S.docs.rowId = null; S.docs.docId = null; return renderDocuments(); }
  if (t.dataset.back) { e.preventDefault(); S.docs.setId = null; S.docs.rowId = null; return renderDocuments(); }
  if (t.dataset.doc) { S.docs.docId = t.dataset.doc; S.docs.rowId = null; return renderDocuments(); }
  if (t.dataset.detail) { S.docs.showDetail = !S.docs.showDetail; return renderDocuments(); }
  if (t.dataset.row) { S.docs.rowId = +t.dataset.row; $$('tr[data-row]').forEach(r => r.classList.toggle('sel', +r.dataset.row === S.docs.rowId)); $('#rpanel').innerHTML = '<div class="empty">Loading…</div>'; return renderRowPanel(); }
  if (t.dataset.filter) { S.docs.filter = t.dataset.filter; return renderDocuments(); }
  if (t.dataset.pick !== undefined) { const id = +t.dataset.pick; if (t.checked) S.rules.picked.add(id); else S.rules.picked.delete(id); return; }
  if (t.dataset.applied) {
    const ids = [...S.rules.picked]; if (!ids.length) return toast('Tick the rows you have handed over first.', false);
    try { const r = await post('/api/rules/applied', { decision_ids: ids }); S.rules.picked.clear(); toast(`Done: ${plural(r.marked, 'row', 'rows')} ticked off.`); return renderRules(); } catch (err) { toast(err.message, false); }
  }
});
document.addEventListener('input', e => {
  if (e.target.id === 'analyst') { S.analyst = e.target.value; localStorage.setItem('twm.analyst', S.analyst); }
  if (e.target.id === 'rsearch') { S.docs.search = e.target.value; clearTimeout(S._st); S._st = setTimeout(renderDocuments, 250); }
});
document.addEventListener('keydown', e => {
  if (S.screen !== 'queue') return;
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); const b = $('#f-record'); if (b) b.click(); return; }
  if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
  const list = S.queue.tab === 'titles' ? S.queue.groups : S.queue.items;
  if (!list.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    const cur = S.queue.selected[0] ?? -1;
    const next = Math.max(0, Math.min(list.length - 1, cur + (e.key === 'ArrowDown' ? 1 : -1)));
    if (next === cur || !leaveItem()) return;
    S.queue.selected = [next]; renderQueue();
  }
});

$('#analyst').value = S.analyst;
go('home').catch(err => { $('#page').innerHTML = `<div class="alert"><span class="dot"></span><div>Could not open the ledger: ${esc(err.message)}</div></div>`; });
