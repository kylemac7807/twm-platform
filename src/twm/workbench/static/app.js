/* The review workbench page (work/workbench/plan-v2.md). Plain JavaScript over the JSON service in api.py.
   Honest screens: the system's own words for why it abstained; nothing prefilled; the band defaults to unbanded. */
'use strict';

const S = {
  screen: 'overview',
  analyst: localStorage.getItem('twm.analyst') || '',
  tax: null, decisions: 0, overview: null,
  queue: { tab: 'titles', groups: [], items: [], selected: [], role: '', band: null, tech: '', reason: '', confirm: false, cls: null, intakeChoice: '' },
  docs: { sets: [], setId: null, rows: [], filter: 'all', search: '', rowId: null, row: null },
  rules: { pending: null, picked: new Set() },
};

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const n = v => (v ?? 0).toLocaleString('en-CA');
const short = (s, len = 120) => { s = String(s ?? ''); return s.length > len ? s.slice(0, len).replace(/\s+\S*$/, '') + '…' : s; };
const rateLine = o => { const r = o.rate_as_stated || o.rate_value || ''; const cur = o.currency && !/[£$€]/.test(r) ? ' ' + o.currency : ''; const unit = o.rate_unit ? ' / ' + o.rate_unit : ''; return `${r}${cur}${unit}`; };

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) { let d; try { d = (await r.json()).detail; } catch (e) { d = r.statusText; } throw new Error(typeof d === 'string' ? d : JSON.stringify(d)); }
  return r.json();
}
const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

let toastTimer;
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2600); }

/* ── small renderers ── */
function statusPill(o) {
  if (o.resolution_status === 'resolved' && o.counted) return '<span class="pill ok">counted</span>';
  if (o.resolution_status === 'resolved') return '<span class="pill wait">not counted</span>';
  if (o.resolution_status === 'ambiguous') return '<span class="pill wait">ambiguous</span>';
  return '<span class="pill wait">needs a decision</span>';
}
function bandPill(o) {
  if (!o.canonical_role_id) return '<span class="muted">–</span>';
  return o.twm_band ? `<span class="pill accent">${esc(o.twm_band)}</span>` : '<span class="pill neutral">unbanded</span>';
}
const rate = o => `<span class="mono">${esc(o.rate_as_stated || o.rate_value || '')}</span>${o.rate_unit ? ` <span class="muted">/ ${esc(o.rate_unit)}</span>` : ''}`;
const kv = pairs => `<table class="kv">${pairs.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v === null || v === undefined || v === '' ? '<span class="muted">–</span>' : esc(v)}</td></tr>`).join('')}</table>`;

/* ── chrome ── */
async function refreshChrome() {
  S.overview = await api('/api/overview');
  $('#nav-open').textContent = S.overview.open_total;
  $('#foot-left').textContent = S.overview.title_groups;
  $('#foot-ledger').textContent = `ledger: ${S.overview.ledger}`;
  $('#foot-decisions').textContent = S.decisions;
  $$('#nav button').forEach(b => b.classList.toggle('active', b.dataset.screen === S.screen));
}
function needName() {
  if (S.analyst.trim()) return false;
  toast('Type your name first: every decision is recorded with the analyst’s name.');
  $('#analyst').focus();
  return true;
}

/* ── overview ── */
async function renderOverview() {
  await refreshChrome();
  const ov = S.overview;
  const groups = await api('/api/queue/titles');
  const q = ov.queue;
  const parts = [];
  if (q.title) parts.push(`<b>${n(ov.title_groups)} title${ov.title_groups === 1 ? '' : 's'}</b> (${n(ov.rows_unlocked)} ledger rows not counted until decided)`);
  if (q.location) parts.push(`<b>${n(q.location)} place name${q.location === 1 ? '' : 's'}</b>`);
  if (q.intake) parts.push(`<b>${n(q.intake)} document${q.intake === 1 ? '' : 's'}</b> to confirm`);
  const alert = parts.length
    ? `<div class="alert"><span class="dot"></span><div>Waiting on you: ${parts.join(', ')}. The system abstained on each one and says why. <a href="#" data-go="queue">Open the queue →</a></div></div>`
    : `<div class="alert ok"><span class="dot"></span><div>Nothing waits on you. Every row the system could decide is decided; the rest is counted.</div></div>`;
  const c = ov.counts;
  $('#page').innerHTML = `
    <h1>Overview</h1>
    <p class="lede">What the ledger holds, and what needs a person. Rates are stored as the documents state them; a row counts toward benchmarks only when its title is resolved and its extraction confidence is at or above 0.90.</p>
    ${alert}
    <div class="tiles">
      <div class="tile"><div class="k">Rows in the ledger</div><div class="v">${n(c.observations_live)}</div><div class="s">${n(c.observations_superseded)} superseded by re-runs, kept</div></div>
      <div class="tile ok"><div class="k">Counted toward benchmarks</div><div class="v">${n(c.counted)}</div><div class="s">${c.observations_live ? Math.round(100 * c.counted / c.observations_live) : 0}% of live rows</div></div>
      <div class="tile wait"><div class="k">Waiting on you</div><div class="v">${n(ov.open_total)}</div><div class="s">${n(ov.title_groups)} titles · ${n(q.location || 0)} places · ${n(q.intake || 0)} documents</div></div>
      <div class="tile"><div class="k">Contract sets</div><div class="v">${n(ov.sets.length)}</div><div class="s">${n(c.documents)} documents registered</div></div>
    </div>
    <div class="cols even">
      <div class="card"><div class="hd"><h2>What needs you first</h2><span class="sub">one decision resolves every row with that title for that client</span></div>
        <div class="bd flush"><table><thead><tr><th>Title</th><th>Client</th><th class="num">Rows unlocked</th></tr></thead><tbody>
          ${groups.slice(0, 8).map(g => `<tr class="row" data-go="queue"><td>${esc(g.title)}<span class="why">${esc(short(g.details.join(' | ')))}</span></td><td>${esc(g.client || '–')}</td><td class="num">${n(g.rows_unlocked)}</td></tr>`).join('')
          || '<tr><td colspan="3" class="muted">No titles waiting.</td></tr>'}
        </tbody></table>${groups.length > 8 ? `<div class="history">and ${groups.length - 8} more in the queue</div>` : ''}</div></div>
      <div>
        <div class="card" style="margin-bottom:14px"><div class="hd"><h2>Contract sets</h2><span class="sub">as intake linked them</span></div>
          <div class="bd"><div class="sets" style="grid-template-columns:1fr">${ov.sets.map(s => `<div class="set" data-go="documents" data-set="${esc(s.root_id)}"><div class="t">${esc(s.root_filename)}</div><div class="m">${n(s.documents)} document${s.documents === 1 ? '' : 's'} · ${esc(s.classes.join(', '))}</div><div class="nums"><span><b>${n(s.rows)}</b> rates</span><span><b>${n(s.counted)}</b> counted</span></div></div>`).join('')}</div></div></div>
        <div class="card"><div class="hd"><h2>Other open items</h2><span class="sub">in the system’s words</span></div>
          <div class="bd flush"><table><tbody>${ov.items.filter(i => i.kind !== 'title').map(i => `<tr><td><span class="pill neutral">${esc(i.kind)}</span></td><td>${esc(i.item)}<span class="why">${esc(short(i.detail))}</span></td></tr>`).join('') || '<tr><td class="muted">None.</td></tr>'}</tbody></table></div></div>
      </div>
    </div>`;
}

/* ── queue ── */
async function loadTax() { if (!S.tax) S.tax = await api('/api/taxonomy'); }
function roleSelect(value) {
  return `<select id="f-role"><option value="">Choose a role…</option><option value="__flag">No role: leave flagged (recorded)</option>${S.tax.families.map(f => `<optgroup label="${esc(f.family)}">${f.roles.map(r => `<option value="${esc(r.id)}" ${r.id === value ? 'selected' : ''}>${esc(r.name)}</option>`).join('')}</optgroup>`).join('')}</select>`;
}
function bandButtons(current) {
  return `<div class="bands" id="f-bands"><button type="button" class="unb ${current === null ? 'active' : ''}" data-band="">unbanded</button>${S.tax.bands.map(b => `<button type="button" class="${current === b ? 'active' : ''}" data-band="${b}">${b.replace('_', ' / ')}</button>`).join('')}</div><div class="hint">Unbanded unless the document gives seniority evidence.</div>`;
}
async function renderQueue() {
  await refreshChrome(); await loadTax();
  const Q = S.queue;
  const q = S.overview.queue;
  const tabs = [['titles', 'Titles', S.overview.title_groups], ['location', 'Places', q.location || 0], ['intake', 'Intake', q.intake || 0], ['extraction', 'Extraction', q.extraction || 0], ['reading', 'Reading', q.reading || 0]];
  if (Q.tab === 'titles') Q.groups = await api('/api/queue/titles'); else Q.items = await api(`/api/queue/${Q.tab}`);
  const list = Q.tab === 'titles' ? Q.groups : Q.items;
  Q.selected = Q.selected.filter(i => i < list.length);
  if (!Q.selected.length && list.length) Q.selected = [0];
  $('#page').innerHTML = `
    <h1>Queue</h1>
    <p class="lede">Every place the system abstained, with its reason. Decide once, with a reason, and every row waiting on that answer is updated. Arrow keys move; Enter jumps to the reason.</p>
    <div class="cols">
      <div class="card">
        <div class="tabs">${tabs.map(([k, l, c]) => `<button data-tab="${k}" class="${Q.tab === k ? 'active' : ''}">${l}<span class="n">${c}</span></button>`).join('')}</div>
        <div class="bd flush" id="qlist">${Q.tab === 'titles' ? titleTable(Q.groups) : itemTable(Q.items, Q.tab)}</div>
      </div>
      <div class="card panel" id="qpanel">${Q.tab === 'titles' ? titlePanel() : itemPanel()}</div>
    </div>`;
}
function titleTable(groups) {
  if (!groups.length) return '<div class="empty" style="padding:30px;text-align:center" class="muted">No titles waiting.</div>';
  return `<table><thead><tr><th></th><th>Title</th><th>Client</th><th class="num">Rows unlocked</th></tr></thead><tbody>
    ${groups.map((g, i) => `<tr class="row ${S.queue.selected.includes(i) ? 'sel' : ''}" data-i="${i}"><td><input type="checkbox" data-check="${i}" ${S.queue.selected.includes(i) ? 'checked' : ''}></td>
      <td>${esc(g.title)}<span class="why">${esc(short(g.details.join(' | ')))}</span><span class="doc">${esc(g.documents.join(', '))}</span></td><td>${esc(g.client || '–')}</td><td class="num">${n(g.rows_unlocked)}<span class="why">${n(g.rows_affected)} rows</span></td></tr>`).join('')}
  </tbody></table>`;
}
function itemTable(items, kind) {
  if (!items.length) return `<div style="padding:30px;text-align:center" class="muted">Nothing waiting here.</div>`;
  const decidable = kind === 'location' || kind === 'intake';
  return `<table><thead><tr>${decidable ? '<th></th>' : ''}<th>Item</th><th>Document</th><th>Why</th></tr></thead><tbody>
    ${items.map((it, i) => `<tr class="row ${S.queue.selected.includes(i) ? 'sel' : ''}" data-i="${i}">${decidable ? `<td><input type="checkbox" data-check="${i}" ${S.queue.selected.includes(i) ? 'checked' : ''}></td>` : ''}<td>${esc(it.item)}${it.client ? `<span class="doc">${esc(it.client)}</span>` : ''}</td><td class="doc">${esc(it.filename || '')}</td><td>${esc(it.detail)}</td></tr>`).join('')}
  </tbody></table>${decidable ? '' : '<div class="history">These notes are information for the analyst; the action for them is a re-run of the document, which is not started from here yet.</div>'}`;
}
function titlePanel() {
  const Q = S.queue;
  const sel = Q.selected.map(i => Q.groups[i]).filter(Boolean);
  if (!sel.length) return '<div class="empty">Pick a title to see its evidence and decide.</div>';
  const g = sel[0];
  const ex = g.examples[0] || {};
  const evidence = sel.length === 1
    ? `<div class="ev"><h3>${esc(g.title)}</h3><div class="meta">${esc(g.client || 'no client')} · ${n(g.rows_affected)} row${g.rows_affected === 1 ? '' : 's'} · ${esc(g.documents.join(', '))}</div>
        <div class="quote">${esc(ex.source_quote || '(no quote stored)')}</div>
        ${kv([['rate', rateLine(ex)], ['period', ex.period_raw], ['location label', ex.location_raw], ['level label', ex.level_raw], ['page', ex.source_page]])}
        ${ex.obs_id ? `<img class="closeup" src="/api/rows/${ex.obs_id}/closeup.png" alt="" onerror="this.remove()">` : ''}
        <div class="why-box"><b>Why the system abstained:</b> ${esc(g.details.join(' | '))}</div></div>
       ${g.history.length ? `<div class="history"><b>Earlier decisions</b>${g.history.map(h => `<div>${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (superseded)' : ''}</div>`).join('')}</div>` : ''}`
    : `<div class="ev"><h3>${sel.length} titles selected</h3><div class="meta">${n(sel.reduce((a, x) => a + x.rows_affected, 0))} rows in all</div>${sel.map(x => `<div>${esc(x.title)} <span class="muted">(${esc(x.client || '–')}, ${n(x.rows_affected)})</span></div>`).join('')}
        <div class="why-box">One decision for all of them: pick several only when they are the same role.</div></div>`;
  return `${evidence}
    <div class="form">
      <label for="f-role">Role</label>${roleSelect(Q.role)}
      <label>Band</label>${bandButtons(Q.band)}
      <label for="f-tech">Technology tag <span class="muted">(optional)</span></label><select id="f-tech"><option value="">none</option>${S.tax.tech.map(t => `<option ${t === Q.tech ? 'selected' : ''}>${esc(t)}</option>`).join('')}</select>
      <label for="f-reason">Reason <span class="muted">(required; it becomes part of the rule)</span></label><textarea id="f-reason" placeholder="e.g. the SOW describes this role as the platform’s operations lead">${esc(Q.reason)}</textarea>
      ${sel.length > 1 ? `<label class="confirm"><input type="checkbox" id="f-confirm" ${Q.confirm ? 'checked' : ''}> Apply this one decision to ${sel.length} titles, ${sel.reduce((a, x) => a + x.queue_ids.length, 0)} queue items, ${n(sel.reduce((a, x) => a + x.rows_affected, 0))} ledger rows.</label>` : ''}
      <div class="err" id="f-err"></div>
      <div class="btns"><button class="btn primary" id="f-record">Record and next</button><button class="btn" id="f-flag">Leave flagged</button></div>
    </div>`;
}
function itemPanel() {
  const Q = S.queue;
  const sel = Q.selected.map(i => Q.items[i]).filter(Boolean);
  if (Q.tab !== 'location' && Q.tab !== 'intake') return '<div class="empty">Nothing to decide on this tab.</div>';
  if (!sel.length) return '<div class="empty">Pick an item to decide.</div>';
  const it = sel[0];
  if (Q.tab === 'location') {
    return `<div class="ev"><h3>${esc(it.item)}</h3><div class="meta">${esc(it.client || 'no client')} · ${esc(it.filename || '')}</div><div class="why-box"><b>Why:</b> ${esc(it.detail)}</div>
        <div class="why-box">The platform never classifies a place name. Your answer is for this client only; once codified, later occurrences are lookups.</div></div>
      <div class="form"><label>Classification for this client</label><div class="bands" id="f-cls">${S.tax.locations.map(l => `<button type="button" class="${Q.cls === l ? 'active' : ''}" data-cls="${l}">${l}</button>`).join('')}</div>
        <label for="f-reason">Reason <span class="muted">(required)</span></label><textarea id="f-reason">${esc(Q.reason)}</textarea>
        <div class="err" id="f-err"></div><div class="btns"><button class="btn primary" id="f-record">Record${sel.length > 1 ? ` for ${sel.length} items` : ''}</button></div></div>`;
  }
  const isClass = /classification/.test(it.detail || '');
  return `<div class="ev"><h3>${esc(it.item)}</h3><div class="meta">${esc(it.filename || '')}</div><div class="why-box"><b>Why:</b> ${esc(it.detail)}</div></div>
    <div class="form">${isClass
      ? `<label for="f-intake">Document type</label><select id="f-intake"><option value="">Choose…</option>${['msa', 'sow', 'amendment', 'rate_card', 'sla', 'solicitation', 'template', 'invoice', 'timesheet', 'other'].map(c => `<option ${Q.intakeChoice === c ? 'selected' : ''}>${c}</option>`).join('')}</select>`
      : `<label>Suggested contract-set link</label><div class="bands" id="f-cls">${['confirm', 'reject'].map(l => `<button type="button" class="${Q.cls === l ? 'active' : ''}" data-cls="${l}">${l}</button>`).join('')}</div>`}
      <label for="f-reason">Reason <span class="muted">(required)</span></label><textarea id="f-reason">${esc(Q.reason)}</textarea>
      <div class="err" id="f-err"></div><div class="btns"><button class="btn primary" id="f-record">Record</button></div></div>`;
}
function readForm() {
  const Q = S.queue;
  const role = $('#f-role'); if (role) Q.role = role.value;
  const tech = $('#f-tech'); if (tech) Q.tech = tech.value;
  const reason = $('#f-reason'); if (reason) Q.reason = reason.value;
  const conf = $('#f-confirm'); Q.confirm = conf ? conf.checked : false;
  const intake = $('#f-intake'); if (intake) Q.intakeChoice = intake.value;
}
async function recordTitle(leaveFlagged) {
  const Q = S.queue; readForm();
  if (needName()) return;
  const sel = Q.selected.map(i => Q.groups[i]).filter(Boolean);
  const err = $('#f-err');
  if (!leaveFlagged && (!Q.role || Q.role === '__flag')) { if (Q.role !== '__flag') { err.textContent = 'Choose a role, or leave it flagged.'; return; } }
  if (!Q.reason.trim()) { err.textContent = 'A decision needs a reason.'; return; }
  if (sel.length > 1 && !Q.confirm) { err.textContent = 'Tick the confirmation to apply one decision to several titles.'; return; }
  const role_id = leaveFlagged || Q.role === '__flag' ? null : Q.role;
  try {
    const r = await post('/api/decisions/title', { queue_ids: sel.flatMap(g => g.queue_ids), role_id, band: Q.band, technology: Q.tech || null, reason: Q.reason, decided_by: S.analyst });
    S.decisions += r.decision_ids.length;
    toast(role_id ? `Recorded for ${sel.length} title${sel.length === 1 ? '' : 's'}: ${role_id}${Q.band ? ' / ' + Q.band : ' (unbanded)'}` : 'Recorded: left flagged');
    const keep = Math.min(Q.selected[0], Math.max(0, Q.groups.length - sel.length - 1));
    Q.selected = [keep]; Q.role = ''; Q.band = null; Q.tech = ''; Q.reason = ''; Q.confirm = false;
    await renderQueue();
  } catch (e) { err.textContent = e.message; }
}
async function recordItem() {
  const Q = S.queue; readForm();
  if (needName()) return;
  const sel = Q.selected.map(i => Q.items[i]).filter(Boolean);
  const err = $('#f-err');
  if (!Q.reason.trim()) { err.textContent = 'A decision needs a reason.'; return; }
  try {
    let r;
    if (Q.tab === 'location') {
      if (!Q.cls) { err.textContent = 'Choose onshore, nearshore or offshore.'; return; }
      r = await post('/api/decisions/location', { queue_ids: sel.map(i => i.id), classification: Q.cls, reason: Q.reason, decided_by: S.analyst });
    } else {
      const it = sel[0];
      const decision = /classification/.test(it.detail || '') ? { doc_class: Q.intakeChoice } : { link: Q.cls };
      if (!decision.doc_class && !decision.link) { err.textContent = 'Choose an answer first.'; return; }
      r = await post('/api/decisions/intake', { queue_id: it.id, decision, reason: Q.reason, decided_by: S.analyst });
    }
    S.decisions += r.decision_ids.length; toast('Recorded.');
    Q.selected = [0]; Q.reason = ''; Q.cls = null; Q.intakeChoice = '';
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
    $('#page').innerHTML = `<h1>Documents</h1><p class="lede">Every document the pipeline registered, grouped into contract sets: the documents that belong to one contract, linked by the contract number printed on their pages. Open a set to see its rates and trace any one to its page.</p>
      <div class="sets">${D.sets.map(s => `<div class="set" data-set="${esc(s.root_id)}"><div class="t">${esc(s.root_filename)}</div><div class="m">${n(s.documents.length)} document${s.documents.length === 1 ? '' : 's'} · ${esc([...new Set(s.documents.map(d => d.doc_class))].join(', '))}</div><div class="nums"><span><b>${n(s.documents.reduce((a, d) => a + d.rows, 0))}</b> rates</span><span><b>${n(s.documents.reduce((a, d) => a + d.counted, 0))}</b> counted</span>${s.documents.some(d => d.flags.length) ? '<span class="pill wait">flags</span>' : ''}</div></div>`).join('')}</div>`;
    return;
  }
  const set = D.sets.find(s => s.root_id === D.setId);
  const withRows = set.documents.filter(d => d.rows);
  if (!D.docId || !set.documents.some(d => d.document_id === D.docId)) D.docId = (withRows[0] || set.documents[0]).document_id;
  D.rows = await api(`/api/documents/${D.docId}/rows`);
  let rows = D.rows;
  if (D.filter === 'counted') rows = rows.filter(r => r.counted); else if (D.filter === 'not') rows = rows.filter(r => !r.counted);
  if (D.search) rows = rows.filter(r => (r.observed_title || '').toLowerCase().includes(D.search.toLowerCase()));
  if (D.rowId && !rows.some(r => r.obs_id === D.rowId)) D.rowId = null;
  $('#page').innerHTML = `
    <h1>Contract set: ${esc(set.root_filename)}</h1><p class="lede"><a href="#" data-back="1">← All contract sets</a></p>
    <div class="card" style="margin-bottom:16px"><div class="hd"><h2>Documents</h2><span class="sub">type, confidence and the evidence intake used, verbatim</span></div>
      <div class="bd flush"><table><thead><tr><th>File</th><th>Type</th><th class="num">Confidence</th><th>Evidence</th><th>Readiness</th><th class="num">Pages</th><th>Contract numbers</th><th class="num">Rates</th><th>Flags</th></tr></thead><tbody>
      ${set.documents.map(d => `<tr class="row ${d.document_id === D.docId ? 'sel' : ''}" data-doc="${esc(d.document_id)}"><td>${esc(d.filename)}<span class="doc">${esc(d.role)}</span></td><td>${esc(d.doc_class)}</td><td class="num">${(d.class_confidence ?? 0).toFixed(2)}</td><td class="muted">${esc(d.evidence)}</td><td>${esc(d.readiness)}${d.extension_mismatch ? ' <span class="pill no">extension lies</span>' : ''}</td><td class="num">${d.pages ?? '–'}</td><td>${esc(d.contract_numbers.join(', ')) || '–'}</td><td class="num">${n(d.rows)}<span class="why">${n(d.counted)} counted</span></td><td>${d.flags.map(f => `<span class="pill wait">${esc(f)}</span>`).join(' ')}</td></tr>`).join('')}
      </tbody></table></div></div>
    <div class="cols">
      <div class="card"><div class="toolbar"><div class="chips">${[['all', 'all rows'], ['counted', 'counted'], ['not', 'not counted']].map(([k, l]) => `<button class="chip ${D.filter === k ? 'active' : ''}" data-filter="${k}">${l}</button>`).join('')}<span class="muted">${n(rows.length)} of ${n(D.rows.length)} rows in ${esc((set.documents.find(d => d.document_id === D.docId) || {}).filename || '')}</span></div><input class="search" id="rsearch" placeholder="title contains…" value="${esc(D.search)}"></div>
        <div class="bd flush"><table><thead><tr><th>Title</th><th class="num">Rate</th><th>Period</th><th>Role</th><th>Band</th><th>Status</th><th class="num">Page</th></tr></thead><tbody>
        ${rows.map(r => `<tr class="row ${r.obs_id === D.rowId ? 'sel' : ''}" data-row="${r.obs_id}"><td>${esc(r.observed_title)}${r.level_raw ? `<span class="doc">${esc(r.level_raw)}</span>` : ''}</td><td class="num">${rate(r)}</td><td class="muted">${esc(r.period_raw || '')}</td><td>${esc(r.canonical_role_id || '')}</td><td>${bandPill(r)}</td><td>${statusPill(r)}</td><td class="num">${r.source_page ?? '–'}</td></tr>`).join('') || '<tr><td colspan="7" class="muted">No rows.</td></tr>'}
        </tbody></table></div></div>
      <div class="card panel" id="rpanel">${D.rowId ? '<div class="empty">Loading…</div>' : '<div class="empty">Pick a rate to trace it to the page it came from.</div>'}</div>
    </div>`;
  if (D.rowId) renderRowPanel();
}
async function renderRowPanel() {
  const D = S.docs;
  const o = await api(`/api/rows/${D.rowId}`);
  const pos = o.position;
  const img = pos.kind === 'pdf'
    ? `<div class="meta">Page ${pos.page} of ${esc(o.filename)}, box (${pos.bbox.map(v => v.toFixed(1)).join(', ')}) in PDF points</div><img class="closeup" src="/api/rows/${o.obs_id}/closeup.png" alt="close-up around the row"><img class="pageimg" src="/api/rows/${o.obs_id}/page.png" alt="the page with the row boxed">`
    : `<div class="meta">${esc(o.filename)}: ${esc(pos.note)}</div>`;
  const fx = o.reporting_value !== null && o.reporting_currency && o.currency !== o.reporting_currency
    ? kv([[`in ${o.reporting_currency} (derived)`, o.reporting_value], ['exchange rate', o.fx_rate], ['rate date', o.fx_date], ['rate source', o.fx_source]]) : '';
  $('#rpanel').innerHTML = `
    <div class="ev"><h3>${esc(o.observed_title)}</h3><div class="meta">row ${o.obs_id} · ${esc(o.vendor || '')} → ${esc(o.client || '')}</div>
      <div class="quote">${esc(pos.quote || '(no quote stored)')}</div>${img}</div>
    <div class="ev"><h3 style="font-size:13px">As stated on the page</h3>${kv([['rate', o.rate_as_stated], ['currency', o.currency], ['unit', o.rate_unit], ['period', o.period_raw], ['location label', o.location_raw], ['level label', o.level_raw], ['qualifier', o.qualifier], ['extraction confidence', o.extraction_confidence], ['scan quality', o.scan_quality]])}${fx}</div>
    <div class="ev"><h3 style="font-size:13px">Resolution</h3>${kv([['role', o.canonical_role_id], ['band', o.twm_band || (o.canonical_role_id ? 'unbanded: no seniority evidence' : '')], ['band from', o.band_source], ['technology', o.attr_technology], ['location', o.attr_location], ['status', o.resolution_status], ['confidence', o.resolution_confidence], ['counted toward benchmarks', o.counted ? 'yes' : 'no']])}</div>
    ${o.history.length ? `<div class="history"><b>Decisions on this title</b>${o.history.map(h => `<div>${esc(h.decided_at.slice(0, 16))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (superseded)' : ''}</div>`).join('')}</div>` : ''}`;
}

/* ── rules ── */
async function renderRules() {
  await refreshChrome();
  const R = S.rules;
  R.pending = await api('/api/rules/pending');
  const section = (kind, title, cols) => {
    const rows = R.pending[kind];
    return `<div class="card" style="margin-bottom:16px"><div class="hd"><h2>${title}</h2><span class="sub">${n(rows.length)} waiting</span></div>
      ${rows.length ? `<div class="toolbar"><div class="chips"><a class="btn sm" href="/api/rules/pending.csv?kind=${kind}">Download CSV to append</a><button class="btn sm" data-applied="${kind}">Mark selected as applied</button></div></div>
      <div class="bd flush"><table><thead><tr><th></th>${cols.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>
        ${rows.map(r => `<tr><td><input type="checkbox" data-pick="${r.decision_id}" ${R.picked.has(r.decision_id) ? 'checked' : ''}></td>${cols.map(c => `<td>${esc(r[c] ?? '')}</td>`).join('')}</tr>`).join('')}
      </tbody></table></div>` : '<div class="bd muted">Nothing waiting.</div>'}</div>`;
  };
  $('#page').innerHTML = `<h1>Rules to codify</h1><p class="lede">A decision becomes a permanent rule only when it is appended to the taxonomy files, which the workbench never writes. Download the rows, append them (the taxonomy-change procedure regenerates the acceptance report), then mark them applied.</p>
    ${section('title_mappings', 'Title mappings', ['observed_title', 'source', 'canonical_role_id', 'twm_band', 'attr_technology', 'reviewer'])}
    ${section('location_rules', 'Location rules', ['client_key', 'place', 'classification', 'decided_by', 'decided_on', 'reason'])}`;
}

/* ── routing and events ── */
const RENDER = { overview: renderOverview, queue: renderQueue, documents: renderDocuments, rules: renderRules };
async function go(screen) { S.screen = screen; await RENDER[screen](); window.scrollTo(0, 0); }

document.addEventListener('click', async e => {
  const t = e.target.closest('[data-screen],[data-go],[data-tab],[data-i],[data-check],[data-band],[data-cls],[data-set],[data-back],[data-doc],[data-row],[data-filter],[data-pick],[data-applied],#f-record,#f-flag');
  if (!t) return;
  if (t.dataset.screen) return go(t.dataset.screen);
  if (t.dataset.go) { e.preventDefault(); if (t.dataset.set) S.docs.setId = t.dataset.set; return go(t.dataset.go); }
  if (t.dataset.tab) { S.queue.tab = t.dataset.tab; S.queue.selected = []; S.queue.reason = ''; S.queue.cls = null; return renderQueue(); }
  if (t.dataset.check !== undefined) { const i = +t.dataset.check; const sel = S.queue.selected; readForm(); S.queue.selected = t.checked ? [...sel, i].sort((a, b) => a - b) : sel.filter(x => x !== i); return renderQueue(); }
  if (t.dataset.i !== undefined) { readForm(); S.queue.selected = [+t.dataset.i]; return renderQueue(); }
  if (t.dataset.band !== undefined) { readForm(); S.queue.band = t.dataset.band || null; $$('#f-bands button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.dataset.cls) { S.queue.cls = t.dataset.cls; $$('#f-cls button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.id === 'f-record') return S.queue.tab === 'titles' ? recordTitle(false) : recordItem();
  if (t.id === 'f-flag') return recordTitle(true);
  if (t.dataset.set) { S.docs.setId = t.dataset.set; S.docs.rowId = null; S.docs.docId = null; return renderDocuments(); }
  if (t.dataset.back) { e.preventDefault(); S.docs.setId = null; S.docs.rowId = null; return renderDocuments(); }
  if (t.dataset.doc) { S.docs.docId = t.dataset.doc; S.docs.rowId = null; return renderDocuments(); }
  if (t.dataset.row) { S.docs.rowId = +t.dataset.row; $$('tr[data-row]').forEach(r => r.classList.toggle('sel', +r.dataset.row === S.docs.rowId)); $('#rpanel').innerHTML = '<div class="empty">Loading…</div>'; return renderRowPanel(); }
  if (t.dataset.filter) { S.docs.filter = t.dataset.filter; return renderDocuments(); }
  if (t.dataset.pick !== undefined) { const id = +t.dataset.pick; if (t.checked) S.rules.picked.add(id); else S.rules.picked.delete(id); return; }
  if (t.dataset.applied) {
    const ids = [...S.rules.picked]; if (!ids.length) return toast('Pick the rows that were appended first.');
    try { const r = await post('/api/rules/applied', { decision_ids: ids }); S.rules.picked.clear(); toast(`${r.marked} decision row${r.marked === 1 ? '' : 's'} marked applied.`); return renderRules(); } catch (err) { toast(err.message); }
  }
});
document.addEventListener('input', e => {
  if (e.target.id === 'analyst') { S.analyst = e.target.value; localStorage.setItem('twm.analyst', S.analyst); }
  if (e.target.id === 'rsearch') { S.docs.search = e.target.value; clearTimeout(S._st); S._st = setTimeout(renderDocuments, 250); }
});
document.addEventListener('keydown', e => {
  if (S.screen !== 'queue' || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
  const list = S.queue.tab === 'titles' ? S.queue.groups : S.queue.items;
  if (!list.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault(); readForm();
    const cur = S.queue.selected[0] ?? -1;
    S.queue.selected = [Math.max(0, Math.min(list.length - 1, cur + (e.key === 'ArrowDown' ? 1 : -1)))];
    renderQueue();
  } else if (e.key === 'Enter') { const r = $('#f-reason'); if (r) { e.preventDefault(); r.focus(); } }
});

$('#analyst').value = S.analyst;
go('overview').catch(err => { $('#page').innerHTML = `<div class="alert"><span class="dot"></span><div>Could not read the ledger: ${esc(err.message)}</div></div>`; });
