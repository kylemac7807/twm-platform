/* The review workbench page (work/workbench/plan-v3.md). Plain JavaScript over the JSON service in api.py.
   Everything starts from choosing a contract set. Written for the person working the queue: plain words, one question at a
   time, the system's suggestion pre-selected but labelled, a clear Save, visible progress. Honest screens: the system's own
   reason for asking stays, folded; nothing is saved without the analyst's name and a reason. */
'use strict';

const S = {
  screen: 'sets',
  analyst: localStorage.getItem('twm.analyst') || '',
  tax: null, saved: 0,
  sets: [], setId: localStorage.getItem('twm.set') || null, set: null, setTab: 'review', editingName: false,
  review: { tab: 'titles', groups: [], items: [], selected: [], form: freshForm(), suggest: null, parking: false },
  docs: { docId: null, rows: [], filter: 'all', search: '', rowId: null, showDetail: false },
  rules: { pending: null, picked: new Set() },
};
function freshForm() { return { role: '', band: null, tags: [], scope: 'set', reason: '', confirm: false, cls: null, docType: '', note: '', fromSuggestion: false }; }

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const n = v => (v ?? 0).toLocaleString('en-CA');
const plural = (k, one, many) => `${n(k)} ${k === 1 ? one : many}`;
const short = (s, len = 110) => { s = String(s ?? ''); return s.length > len ? s.slice(0, len).replace(/\s+\S*$/, '') + '…' : s; };
const rateLine = o => { const r = o.rate_as_stated || o.rate_value || ''; const cur = o.currency && !/[£$€]/.test(r) ? ' ' + o.currency : ''; const unit = o.rate_unit ? ' per ' + o.rate_unit : ''; return `${r}${cur}${unit}`; };
const roleName = id => { const r = (S.tax ? S.tax.families.flatMap(f => f.roles) : []).find(x => x.id === id); return r ? r.name : (id || '').replace(/_/g, ' '); };
function plainWhy(d) {
  d = String(d || '');
  if (/ambiguous:/.test(d)) return 'The title names two roles; choose one.';
  if (/no rule match/.test(d)) return /model abstained|below floor/.test(d) ? 'Not in the role framework yet, and the model was not sure.' : 'Not in the role framework yet.';
  if (/place '/.test(d)) return 'A place name the system never classifies on its own.';
  if (/classification/.test(d)) return 'The document type was a guess; confirm it.';
  if (/suggested only/.test(d)) return 'The link to the contract set is a guess; confirm it.';
  return short(d);
}
const STATUS = { ready: 'Ready for review', in_review: 'In review', complete: 'Complete' };
function statusLine(s) {
  if (s.status === 'ready') return `${STATUS.ready} · ${plural(s.questions, 'question', 'questions')}`;
  if (s.status === 'in_review') return `${STATUS.in_review} · ${n(s.answered)} of ${n(s.questions)} answered${s.parked ? `, ${n(s.parked)} parked` : ''}`;
  return STATUS.complete;
}

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) { let d; try { d = (await r.json()).detail; } catch (e) { d = r.statusText; } throw new Error(typeof d === 'string' ? d : JSON.stringify(d)); }
  return r.json();
}
const post = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
let toastTimer;
function toast(msg, ok = true) { const t = $('#toast'); t.textContent = msg; t.classList.toggle('bad', !ok); t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 3000); }

/* ── small renderers ── */
function statusPill(o) {
  if (o.resolution_status === 'resolved' && o.counted) return '<span class="pill ok">in benchmarks</span>';
  if (o.resolution_status === 'resolved') return '<span class="pill neutral">held back</span>';
  return '<span class="pill wait">to review</span>';
}
function bandPill(o) {
  if (!o.canonical_role_id) return '<span class="muted">–</span>';
  return o.twm_band ? `<span class="pill accent">${esc(o.twm_band.replace('_', ' / '))}</span>` : '<span class="pill neutral">not stated</span>';
}
const rate = o => `<span class="mono">${esc(o.rate_as_stated || o.rate_value || '')}</span>${o.rate_unit ? ` <span class="muted">/ ${esc(o.rate_unit)}</span>` : ''}`;
const kv = pairs => `<table class="kv">${pairs.filter(([, v]) => v !== null && v !== undefined && v !== '').map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('')}</table>`;
const progress = (done, total, label) => `<div class="prog"><div class="bar"><span style="width:${total ? Math.round(100 * done / total) : 0}%"></span></div><div class="lbl">${label}</div></div>`;

/* ── chrome ── */
async function loadSets() { S.sets = await api('/api/sets'); if (S.setId && !S.sets.some(s => s.root_id === S.setId)) S.setId = null; }
async function loadSet() { S.set = S.setId ? await api(`/api/sets/${S.setId}`) : null; }
async function loadTax() { if (!S.tax) S.tax = await api('/api/taxonomy'); }
function showWho() {
  const have = !!S.analyst.trim() && !S.editingWho;
  $('#analyst').hidden = have; $('#who-label').hidden = have; $('#who-set').hidden = !have;
  $('#who-name').textContent = S.analyst.trim();
}
function refreshChrome() {
  showWho();
  const open = S.set ? S.set.open : 0;
  $('#nav-open').textContent = open; $('#nav-open').style.display = open ? '' : 'none';
  $('#foot-saved').textContent = S.saved;
  $('#foot-set').textContent = S.set ? `Contract set: ${S.set.name}` : 'No contract set chosen';
  $('#foot-set').classList.toggle('muted', !S.set);
  $$('#nav button').forEach(b => b.classList.toggle('active', b.dataset.screen === S.screen || (S.screen === 'set' && b.dataset.screen === (S.setTab === 'review' ? 'review' : 'documents'))));
}
function needName() {
  if (S.analyst.trim()) return false;
  toast('Enter your name at the top right first. It is saved with every answer.', false);
  $('#analyst').focus();
  return true;
}

/* ── contract sets (landing) ── */
async function renderSets() {
  await loadSets(); await loadSet(); refreshChrome();
  const q = (S._setSearch || '').toLowerCase();
  const list = S.sets.filter(s => !q || (s.name || '').toLowerCase().includes(q) || (s.root_filename || '').toLowerCase().includes(q));
  const counts = { ready: 0, in_review: 0, complete: 0 };
  S.sets.forEach(s => counts[s.status] = (counts[s.status] || 0) + 1);
  $('#page').innerHTML = `
    <div class="titlebar"><div><h1>Contract sets</h1><p class="lede">Choose the contract you want to work on. A contract set is one contract and the documents that came with it.</p></div>
      <input class="search" id="setsearch" placeholder="find a contract set…" value="${esc(S._setSearch || '')}"></div>
    ${!S.analyst.trim() ? '<div class="alert"><span class="dot"></span><div>Enter your name at the top right. It is saved with every answer you give.</div></div>' : ''}
    <div class="chips" style="margin-bottom:12px"><span class="pill status ready">${n(counts.ready)} ready for review</span><span class="pill status in_review">${n(counts.in_review)} in review</span><span class="pill status complete">${n(counts.complete)} complete</span></div>
    <div class="card setlist"><div class="bd flush"><table><thead><tr><th>Contract set</th><th>Status</th><th class="num">Documents</th><th class="num">Rates</th><th class="num">In benchmarks</th></tr></thead><tbody>
      ${list.map(s => `<tr class="row" data-open="${esc(s.root_id)}"><td><span class="setname">${esc(s.name)}<span class="file">${esc(s.root_filename)}</span></span></td>
        <td><span class="pill status ${s.status}">${esc(statusLine(s))}</span></td><td class="num">${n(s.documents.length)}</td><td class="num">${n(s.rows)}</td><td class="num">${n(s.counted)}</td></tr>`).join('')
        || '<tr><td colspan="5" class="muted">No contract sets match.</td></tr>'}
    </tbody></table></div></div>
    <p class="hint" style="margin-top:10px">Registering new contract sets from this screen comes later; for now they arrive when a contract is run through the engine.</p>`;
}

/* ── one contract set: header, tiles, Review and Documents tabs ── */
async function renderSet() {
  if (!S.setId) { S.screen = 'sets'; return renderSets(); }
  await loadSet(); await loadTax(); refreshChrome();
  $('#page').innerHTML = `<div id="sethead-wrap">${setHeaderHtml()}</div><div id="setbody"></div>`;
  if (S.setTab === 'review') await renderReview(); else await renderDocuments();
}
function setHeaderHtml() {
  const s = S.set;
  const nameBlock = S.editingName
    ? `<div class="namebox"><input id="setname" value="${esc(s.name)}"><button class="btn primary sm" data-savename="1">Save name</button><button class="btn ghost sm" data-cancelname="1">Cancel</button></div>`
    : `<div class="file">${esc(s.root_filename)} <a href="#" data-editname="1">· rename</a></div>`;
  const heldBack = s.rows - s.counted;
  return `
    <p class="crumb"><a href="#" data-screen="sets">Contract sets</a> › ${esc(s.name)}</p>
    <div class="sethead"><div><h1>${esc(s.name)}</h1>${nameBlock}</div><span class="pill status ${s.status}" style="font-size:12px;padding:6px 12px">${esc(statusLine(s))}</span></div>
    <div class="strip"><span><b>${n(s.rows)}</b> rates in ${plural(s.documents, 'document', 'documents')}</span><span class="ok"><b>${n(s.counted)}</b> in benchmarks</span><span class="wait"><b>${n(heldBack)}</b> held back, ${n(s.rows_unlocked)} waiting on a title</span><span><b>${n(s.open)}</b> to answer · ${n(s.answered)} answered · ${n(s.parked)} parked</span></div>
    <div class="subtabs"><button data-settab="review" class="${S.setTab === 'review' ? 'active' : ''}">Review<span class="n">${s.open}</span></button><button data-settab="documents" class="${S.setTab === 'documents' ? 'active' : ''}">Documents<span class="n">${s.documents}</span></button></div>`;
}
/* after a save or park: refresh the numbers in place, re-list, keep the scroll position, show what just happened */
async function afterChange(message) {
  const y = window.scrollY;
  await loadSet(); refreshChrome();
  const w = $('#sethead-wrap'); if (w) w.innerHTML = setHeaderHtml();
  S.review.lastSaved = message;
  await renderReview();
  window.scrollTo(0, y);
  const row = $('#qlist tr.sel'); if (row) row.scrollIntoView({ block: 'nearest' });
}

/* ── review (scoped to the set) ── */
const TABS = [['titles', 'Job titles'], ['location', 'Place names'], ['intake', 'Documents'], ['parked', 'Parked'], ['notes', 'Notes']];
async function renderReview() {
  const R = S.review, s = S.set, q = s.queue || {};
  const counts = { titles: s.title_groups, location: q.location || 0, intake: q.intake || 0, parked: s.parked_items, notes: (q.extraction || 0) + (q.reading || 0) };
  const sid = encodeURIComponent(S.setId);
  if (R.tab === 'titles') R.groups = await api(`/api/queue/titles?set_id=${sid}`);
  else if (R.tab === 'parked') R.groups = await api(`/api/queue/titles?set_id=${sid}&status=parked`);
  else if (R.tab === 'notes') R.items = [...await api(`/api/queue/extraction?set_id=${sid}`), ...await api(`/api/queue/reading?set_id=${sid}`)];
  else R.items = await api(`/api/queue/${R.tab}?set_id=${sid}`);
  const list = (R.tab === 'titles' || R.tab === 'parked') ? R.groups : R.items;
  R.selected = R.selected.filter(i => i < list.length);
  if (!R.selected.length && list.length) R.selected = [0];
  if (R.tab === 'titles' && R.selected.length === 1) await loadSuggestion(R.groups[R.selected[0]]); else R.suggest = null;
  const total = counts.titles + counts.location + counts.intake;
  $('#setbody').innerHTML = `
    <div class="cols review">
      <div class="card rail">
        <div class="tabs">${TABS.map(([k, l]) => `<button data-tab="${k}" class="${R.tab === k ? 'active' : ''}">${l}<span class="n">${counts[k]}</span></button>`).join('')}</div>
        <div class="bd flush" id="qlist">${(R.tab === 'titles' || R.tab === 'parked') ? titleTable(R.groups, R.tab === 'parked') : itemTable(R.items, R.tab)}</div>
      </div>
      <div class="card panel" id="qpanel">${panelNav(list)}${R.lastSaved ? `<div class="saved-note" style="margin:12px 18px 0">${esc(R.lastSaved)}</div>` : ''}${(R.tab === 'titles' || R.tab === 'parked') ? titlePanel() : itemPanel()}</div>
    </div>`;
  R.lastSaved = null;
}
async function loadSuggestion(g) {
  const R = S.review, F = R.form;
  if (!g) { R.suggest = null; return; }
  if (R.suggest && R.suggest.title === g.title) return;
  R.suggest = await api(`/api/suggest?title=${encodeURIComponent(g.title)}&set_id=${encodeURIComponent(S.setId)}${g.vendor ? '&vendor=' + encodeURIComponent(g.vendor) : ''}`);
  const sg = R.suggest;
  if (!F.role && sg.suggestions.length) { F.role = sg.suggestions[0].id; F.fromSuggestion = true; }
  if (F.band === null && sg.band) F.band = sg.band;
  if (!F.tags.length && sg.tech_found.length) F.tags = [...sg.tech_found];
}
function panelNav(list) {
  const R = S.review; if (!list.length) return '';
  const i = R.selected[0] ?? 0;
  const titles = R.tab === 'titles' || R.tab === 'parked';
  const actions = R.tab === 'notes' ? '' : titles
    ? `<button class="btn primary" id="f-record">${R.tab === 'parked' ? 'Save' : 'Save and go to next'}</button>${R.tab === 'parked' ? '<button class="btn" id="f-unpark">Bring back</button>' : '<button class="btn" id="f-park" title="Set it aside with a note; it moves to the Parked tab">Park</button>'}`
    : `<button class="btn primary" id="f-record">Save</button><button class="btn" id="f-park">Park</button>`;
  return `<div class="panelnav"><div class="pos"><button class="btn sm" data-step="-1" ${i <= 0 ? 'disabled' : ''}>‹</button><span>${R.selected.length > 1 ? `${R.selected.length} selected` : `${i + 1} of ${list.length}`}</span><button class="btn sm" data-step="1" ${i >= list.length - 1 ? 'disabled' : ''}>›</button></div>
    <div class="acts">${actions}<span class="hint">Ctrl+Enter saves</span></div></div>
    ${R.parking ? `<div class="parknote bar"><input id="f-note" placeholder="optional note, e.g. need the SOW to decide" value="${esc(R.form.note)}"><button class="btn primary sm" id="f-park-go">Park it</button><button class="btn ghost sm" id="f-park-cancel">Cancel</button></div>` : ''}`;
}
function titleTable(groups, parked) {
  if (!groups.length) return `<div class="empty">${parked ? 'Nothing parked.' : 'All job titles are decided. Nothing to do here.'}</div>`;
  const oneClient = new Set(groups.map(g => g.client)).size === 1;
  return `<table><thead><tr><th></th><th>Job title</th>${oneClient ? '' : '<th>Client</th>'}<th class="num">Rates</th></tr></thead><tbody>
    ${groups.map((g, i) => `<tr class="row ${S.review.selected.includes(i) ? 'sel' : ''}" data-i="${i}"><td><input type="checkbox" data-check="${i}" ${S.review.selected.includes(i) ? 'checked' : ''} title="Tick several to give them one answer"></td>
      <td>${esc(g.title)}${parked && g.history.length ? `<span class="why">${esc(g.history[g.history.length - 1].reason || 'parked')}</span>` : ''}</td>${oneClient ? '' : `<td>${esc(g.client || '–')}</td>`}<td class="num">${n(g.rows_unlocked)}</td></tr>`).join('')}
  </tbody></table>${parked ? '' : '<div class="history">Tick more than one title only when they are the same role; one answer then covers all of them.</div>'}`;
}
function itemTable(items, kind) {
  if (!items.length) return '<div class="empty">Nothing to do here.</div>';
  const decidable = kind === 'location' || kind === 'intake';
  return `<table><thead><tr>${decidable ? '<th></th>' : ''}<th>${kind === 'intake' ? 'Document' : 'Item'}</th>${kind === 'intake' ? '' : '<th>Document</th>'}<th>What the system says</th></tr></thead><tbody>
    ${items.map((it, i) => `<tr class="row ${S.review.selected.includes(i) ? 'sel' : ''}" data-i="${i}">${decidable ? `<td><input type="checkbox" data-check="${i}" ${S.review.selected.includes(i) ? 'checked' : ''}></td>` : ''}<td>${esc(it.item)}${it.client ? `<span class="doc">${esc(it.client)}</span>` : ''}</td>${kind === 'intake' ? '' : `<td class="doc">${esc(it.filename || '')}</td>`}<td>${esc(plainWhy(it.detail))}<span class="why">${esc(short(it.detail))}</span></td></tr>`).join('')}
  </tbody></table>${decidable ? '' : '<div class="history">Notes are for information. The fix for them is to run the document again, which is done from the command line for now.</div>'}`;
}
function roleSelect(value) {
  return `<select id="f-role"><option value="">Choose a role…</option>${S.tax.families.map(f => `<optgroup label="${esc(f.family)}">${f.roles.map(r => `<option value="${esc(r.id)}" ${r.id === value ? 'selected' : ''}>${esc(r.name)}</option>`).join('')}</optgroup>`).join('')}</select>`;
}
function bandButtons(current) {
  return `<div class="bands" id="f-bands"><button type="button" class="unb ${current === null ? 'active' : ''}" data-band="">not stated</button>${S.tax.bands.map(b => `<button type="button" class="${current === b ? 'active' : ''}" data-band="${b}">${b.replace('_', ' / ')}</button>`).join('')}</div><div class="hint">Leave "not stated" unless the document says how senior the role is.</div>`;
}
function tagPicker() {
  const F = S.review.form, sg = S.review.suggest || { tech_found: [], tech_common: [] };
  const shown = [...new Set([...sg.tech_found, ...F.tags, ...sg.tech_common])].slice(0, 10);
  const q = (F._tagq || '').toLowerCase();
  const more = q ? S.tax.tech.filter(t => t.includes(q) && !shown.includes(t)).slice(0, 8) : [];
  return `<div class="tags" id="f-tags">${shown.map(t => `<button type="button" class="${F.tags.includes(t) ? 'on' : ''} ${sg.tech_found.includes(t) ? 'found' : ''}" data-tag="${esc(t)}" title="${sg.tech_found.includes(t) ? 'found in the title' : 'common in this contract set'}">${esc(t)}</button>`).join('')}
    <input class="tagsearch" id="f-tagq" placeholder="other tag…" value="${esc(F._tagq || '')}">${more.map(t => `<button type="button" data-tag="${esc(t)}">${esc(t)}</button>`).join('')}</div>
    <div class="hint">${sg.tech_found.length ? 'Dashed tags were found in the title; the rest are common in this contract set.' : (sg.tech_common && sg.tech_common.length ? 'None named in the title. The chips are the tags common in this contract set; pick one only if the document says so.' : 'None named in the title. Pick one only if the document says so, e.g. "Senior Java Developer" → java.')}</div>`;
}
function scopeButtons(scope) {
  const vendor = (S.set && S.set.vendor) || 'this vendor';
  return `<div class="scope" id="f-scope">
    <button type="button" class="${scope === 'set' ? 'on' : ''}" data-scope="set"><b>This contract set</b>just these documents</button>
    <button type="button" class="${scope === 'vendor' ? 'on' : ''}" data-scope="vendor"><b>This vendor</b>every ${esc(vendor)} contract</button>
    <button type="button" class="${scope === 'everyone' ? 'on' : ''}" data-scope="everyone"><b>Everyone</b>nominate for the shared framework</button></div>`;
}
function titlePanel() {
  const R = S.review, F = R.form, parked = R.tab === 'parked';
  const sel = R.selected.map(i => R.groups[i]).filter(Boolean);
  if (!sel.length) return '<div class="empty">Pick a job title on the left.</div>';
  const g = sel[0], ex = g.examples[0] || {}, sg = R.suggest;
  const head = sel.length === 1
    ? `<div class="ev"><div class="step">Step 1 · read the evidence</div><h3>${esc(g.title)}</h3><div class="meta">${esc(g.client || 'no client')} · ${plural(g.rows_in_set ?? g.rows_affected, 'rate', 'rates')} here${g.rows_affected > (g.rows_in_set ?? g.rows_affected) ? `, ${n(g.rows_affected)} for the client` : ''} · ${esc(g.documents.join(', '))}</div>
        <div class="quote">${esc(ex.source_quote || '(no quote stored)')}</div>
        ${kv([['Rate', rateLine(ex)], ['Period', ex.period_raw], ['Location on the card', ex.location_raw], ['Level on the card', ex.level_raw], ['Page', ex.source_page]])}
        ${ex.obs_id ? `<img class="closeup" src="/api/rows/${ex.obs_id}/closeup.png" alt="" onerror="this.remove()">` : ''}
        <div class="plain"><b>Why you are being asked:</b> ${esc(plainWhy(g.details[0]))}</div>
        <details class="more"><summary>The system's own words</summary><div class="why-box">${esc(g.details.join(' | '))}</div></details>
        ${g.history.length ? `<details class="more"><summary>Earlier answers</summary>${g.history.map(h => `<div class="why-box">${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (replaced)' : ''}</div>`).join('')}</details>` : ''}
        ${sg && sg.saved ? `<div class="saved-note">You answered this title before (${esc(sg.saved.scope === 'set' ? 'this contract set' : sg.saved.scope === 'vendor' ? 'this vendor' : 'everyone')}): ${esc(roleName(sg.saved.canonical_role_id))}${sg.saved.twm_band ? ', ' + esc(sg.saved.twm_band) : ''}. Saving again replaces it.</div>` : ''}</div>`
    : `<div class="ev"><div class="step">Step 1 · check they are the same role</div><h3>${plural(sel.length, 'title', 'titles')} selected</h3>${sel.map(x => `<div>${esc(x.title)} <span class="muted">(${esc(x.client || '–')}, ${plural(x.rows_affected, 'rate', 'rates')})</span></div>`).join('')}</div>`;
  const top = sg && sel.length === 1 && sg.suggestions.length ? sg.suggestions[0] : null;
  const suggestion = top
    ? `<div class="suggested">Suggested: <b>${esc(top.name)}</b> <span class="muted">(${esc(top.why)})</span>. Confirm it, or pick another.${sg.suggestions.length > 1 ? `<div class="alts">${sg.suggestions.slice(1).map(x => `<button type="button" data-alt="${esc(x.id)}" title="${esc(x.why)}">${esc(x.name)}</button>`).join('')}</div>` : ''}</div>`
    : '';
  return `<div class="twocol"><div class="col">${head}</div><div class="col form">
      <div class="step">Step 2 · answer</div>
      <label for="f-role">Which role is this?</label>${suggestion}${roleSelect(F.role)}
      <label>How senior?</label>${bandButtons(F.band)}
      <label>Technology named in the title <span class="muted">(optional)</span></label>${tagPicker()}
      <label>Where does this answer apply?</label>${scopeButtons(F.scope)}
      <label for="f-reason">Why? <span class="muted">(one line; it is kept with the answer)</span></label><textarea id="f-reason" placeholder="the SOW describes this role as the platform’s operations lead">${esc(F.reason)}</textarea>
      ${sel.length > 1 ? `<label class="confirm"><input type="checkbox" id="f-confirm" ${F.confirm ? 'checked' : ''}> Yes, one answer for all ${sel.length} titles (${plural(sel.reduce((a, x) => a + x.rows_affected, 0), 'rate', 'rates')}).</label>` : ''}
      <div class="err" id="f-err"></div>
    </div></div>`;
}
function itemPanel() {
  const R = S.review, F = R.form;
  const sel = R.selected.map(i => R.items[i]).filter(Boolean);
  if (R.tab === 'notes') return '<div class="empty">Nothing to answer here.</div>';
  if (!sel.length) return '<div class="empty">Pick an item on the left.</div>';
  const it = sel[0];
  if (R.tab === 'location') {
    const m = /place '([^']+)'/.exec(it.detail || '');
    return `<div class="twocol"><div class="col"><div class="ev"><div class="step">Step 1 · read</div><h3>${esc(m ? m[1] : it.item)}</h3><div class="meta">on "${esc(it.item)}" · ${esc(it.client || 'no client')} · ${esc(it.filename || '')}</div>
        <div class="plain">Is this place onshore, nearshore or offshore <b>for this client</b>? The system never decides a place on its own. Your answer is reused for this client from now on.</div></div></div>
      <div class="col form"><div class="step">Step 2 · answer</div><label>For this client, this place is</label><div class="bands" id="f-cls">${S.tax.locations.map(l => `<button type="button" class="${F.cls === l ? 'active' : ''}" data-cls="${l}">${l}</button>`).join('')}</div>
        <label for="f-reason">Why?</label><textarea id="f-reason" placeholder="Buffalo is a short drive from the client’s Toronto teams">${esc(F.reason)}</textarea>
        <div class="err" id="f-err"></div><div class="step">Step 3 · save</div><div class="btns"><button class="btn primary" id="f-record">Save${sel.length > 1 ? ` for ${sel.length} items` : ''}</button><button class="btn" id="f-park">Park</button></div>
        ${R.parking ? `<div class="parknote"><input id="f-note" placeholder="optional note" value="${esc(F.note)}"><div class="btns"><button class="btn primary sm" id="f-park-go">Park it</button><button class="btn ghost sm" id="f-park-cancel">Cancel</button></div></div>` : ''}</div>`;
  }
  const isClass = /classification/.test(it.detail || '');
  return `<div class="twocol"><div class="col"><div class="ev"><div class="step">Step 1 · read</div><h3>${esc(it.item)}</h3><div class="meta">${esc(short(it.detail))}</div></div></div>
    <div class="col form"><div class="step">Step 2 · answer</div>${isClass
      ? `<label for="f-doctype">What kind of document is it?</label><select id="f-doctype"><option value="">Choose…</option>${[['msa', 'Master agreement'], ['sow', 'Statement of work'], ['amendment', 'Amendment'], ['rate_card', 'Rate card or pricing exhibit'], ['sla', 'Service levels'], ['solicitation', 'Solicitation / RFP'], ['template', 'Template'], ['invoice', 'Invoice'], ['timesheet', 'Timesheet'], ['other', 'Other']].map(([v, l]) => `<option value="${v}" ${F.docType === v ? 'selected' : ''}>${l}</option>`).join('')}</select>`
      : `<label>Does this document belong to the contract set it was filed with?</label><div class="bands" id="f-cls">${[['confirm', 'Yes'], ['reject', 'No']].map(([v, l]) => `<button type="button" class="${F.cls === v ? 'active' : ''}" data-cls="${v}">${l}</button>`).join('')}</div>`}
      <label for="f-reason">Why?</label><textarea id="f-reason">${esc(F.reason)}</textarea>
      <div class="err" id="f-err"></div><div class="step">Step 3 · save</div><div class="btns"><button class="btn primary" id="f-record">Save</button><button class="btn" id="f-park">Park</button></div>
      ${R.parking ? `<div class="parknote"><input id="f-note" placeholder="optional note" value="${esc(F.note)}"><div class="btns"><button class="btn primary sm" id="f-park-go">Park it</button><button class="btn ghost sm" id="f-park-cancel">Cancel</button></div></div>` : ''}</div>`;
}
function readForm() {
  const F = S.review.form;
  const g = (id, k) => { const el = $(id); if (el) F[k] = el.type === 'checkbox' ? el.checked : el.value; };
  g('#f-role', 'role'); g('#f-reason', 'reason'); g('#f-confirm', 'confirm'); g('#f-doctype', 'docType'); g('#f-note', 'note'); g('#f-tagq', '_tagq');
  const sg = S.review.suggest;
  if (sg && sg.suggestions.length && F.role !== sg.suggestions[0].id) F.fromSuggestion = false;
}
function typed() { const F = S.review.form; return !!(F.reason.trim() || F.cls || F.docType || F.note); }
function leaveItem() {
  readForm();
  if (typed() && !confirm('You typed an answer but did not save it. Discard it?')) return false;
  S.review.form = freshForm(); S.review.suggest = null; S.review.parking = false; return true;
}
function nextAfterChange(removed) {
  const R = S.review;
  const list = (R.tab === 'titles' || R.tab === 'parked') ? R.groups : R.items;
  R.selected = [Math.min(R.selected[0] ?? 0, Math.max(0, list.length - removed - 1))];
  R.form = freshForm(); R.suggest = null; R.parking = false;
}
async function saveTitle() {
  const R = S.review; readForm(); const F = R.form;
  if (needName()) return;
  const sel = R.selected.map(i => R.groups[i]).filter(Boolean);
  const err = $('#f-err');
  if (!F.role) { err.textContent = 'Choose a role, or park it.'; $('#f-role').focus(); return; }
  if (!F.reason.trim()) { err.textContent = 'Add one line saying why.'; $('#f-reason').focus(); return; }
  if (sel.length > 1 && !F.confirm) { err.textContent = 'Tick the box to confirm one answer for all of them.'; return; }
  const btn = $('#f-record'); btn.disabled = true; btn.textContent = 'Saving…';
  try {
    await post('/api/decisions/title', { queue_ids: sel.flatMap(g => g.queue_ids), role_id: F.role, band: F.band, technology: F.tags.join(',') || null, scope: F.scope,
                                         suggested: F.fromSuggestion, reason: F.reason, decided_by: S.analyst });
    S.saved += 1;
    const msg = `Saved: ${sel.map(x => x.title).join(', ')} → ${roleName(F.role)}${F.band ? ', ' + F.band.replace('_', ' / ') : ''} (${F.scope === 'vendor' ? 'this vendor' : F.scope === 'set' ? 'this contract set' : 'everyone'}). Next one is below.`;
    nextAfterChange(sel.length);
    await afterChange(msg);
  } catch (e) { err.textContent = e.message; btn.disabled = false; btn.textContent = 'Save and go to next'; }
}
async function saveItem() {
  const R = S.review; readForm(); const F = R.form;
  if (needName()) return;
  const sel = R.selected.map(i => R.items[i]).filter(Boolean);
  const err = $('#f-err');
  if (!F.reason.trim()) { err.textContent = 'Add one line saying why.'; $('#f-reason').focus(); return; }
  try {
    if (R.tab === 'location') {
      if (!F.cls) { err.textContent = 'Choose onshore, nearshore or offshore.'; return; }
      await post('/api/decisions/location', { queue_ids: sel.map(i => i.id), classification: F.cls, reason: F.reason, decided_by: S.analyst });
    } else {
      const it = sel[0];
      const decision = /classification/.test(it.detail || '') ? { doc_class: F.docType } : { link: F.cls };
      if (!decision.doc_class && !decision.link) { err.textContent = 'Choose an answer first.'; return; }
      await post('/api/decisions/intake', { queue_id: it.id, decision, reason: F.reason, decided_by: S.analyst });
    }
    S.saved += 1;
    nextAfterChange(sel.length);
    await afterChange('Saved. Next one is below.');
  } catch (e) { err.textContent = e.message; }
}
async function parkSelected() {
  const R = S.review; readForm(); const F = R.form;
  if (needName()) return;
  const isTitles = R.tab === 'titles';
  const sel = R.selected.map(i => (isTitles ? R.groups : R.items)[i]).filter(Boolean);
  const ids = isTitles ? sel.flatMap(g => g.queue_ids) : sel.map(i => i.id);
  try {
    await post('/api/queue/park', { queue_ids: ids, note: F.note, decided_by: S.analyst });
    nextAfterChange(sel.length);
    await afterChange(`Parked${F.note ? ': ' + F.note : ''}. Find it under the Parked tab.`);
  } catch (e) { $('#f-err').textContent = e.message; }
}
async function unparkSelected() {
  const R = S.review;
  if (needName()) return;
  const sel = R.selected.map(i => R.groups[i]).filter(Boolean);
  try {
    await post('/api/queue/unpark', { queue_ids: sel.flatMap(g => g.queue_ids), decided_by: S.analyst });
    nextAfterChange(sel.length);
    await afterChange('Back on the list of job titles.');
  } catch (e) { $('#f-err').textContent = e.message; }
}

/* ── documents (scoped to the set) ── */
async function renderDocuments() {
  const D = S.docs;
  const set = S.sets.find(s => s.root_id === S.setId) || (await loadSets(), S.sets.find(s => s.root_id === S.setId));
  const withRows = set.documents.filter(d => d.rows);
  if (!D.docId || !set.documents.some(d => d.document_id === D.docId)) D.docId = (withRows[0] || set.documents[0]).document_id;
  const doc = set.documents.find(d => d.document_id === D.docId);
  D.rows = await api(`/api/documents/${D.docId}/rows`);
  let rows = D.rows;
  if (D.filter === 'counted') rows = rows.filter(r => r.counted); else if (D.filter === 'not') rows = rows.filter(r => !r.counted);
  if (D.search) rows = rows.filter(r => (r.observed_title || '').toLowerCase().includes(D.search.toLowerCase()));
  if (D.rowId && !rows.some(r => r.obs_id === D.rowId)) D.rowId = null;
  $('#setbody').innerHTML = `
    <p class="lede">Choose a document, then click a rate to see the page it was read from.</p>
    <div class="card" style="margin-bottom:16px"><div class="hd"><h2>Documents in the set</h2><button class="btn sm" data-detail="1">${D.showDetail ? 'Hide' : 'Show'} how each was identified</button></div>
      <div class="bd flush"><table><thead><tr><th>File</th><th>Kind</th><th class="num">Pages</th><th>Contract number</th><th class="num">Rates</th>${D.showDetail ? '<th class="num">Confidence</th><th>Evidence</th><th>Text</th>' : ''}<th></th></tr></thead><tbody>
      ${set.documents.map(d => `<tr class="row ${d.document_id === D.docId ? 'sel' : ''}" data-doc="${esc(d.document_id)}"><td>${esc(d.filename)}</td><td>${esc(d.doc_class.replace('_', ' '))}</td><td class="num">${d.pages ?? '–'}</td><td>${esc(d.contract_numbers.join(', ')) || '–'}</td><td class="num">${d.rows ? `${n(d.rows)}<span class="why">${n(d.counted)} in benchmarks</span>` : '<span class="muted">none</span>'}</td>${D.showDetail ? `<td class="num">${(d.class_confidence ?? 0).toFixed(2)}</td><td class="muted">${esc(d.evidence)}</td><td>${esc(d.readiness)}${d.extension_mismatch ? ' <span class="pill no">not what its name says</span>' : ''}</td>` : ''}<td>${d.flags.map(f => `<span class="pill wait">${esc(plainWhy(f))}</span>`).join(' ')}</td></tr>`).join('')}
      </tbody></table></div></div>
    <div class="cols">
      <div class="card"><div class="toolbar"><div class="chips">${[['all', 'all'], ['counted', 'in benchmarks'], ['not', 'held back']].map(([k, l]) => `<button class="chip ${D.filter === k ? 'active' : ''}" data-filter="${k}">${l}</button>`).join('')}<span class="muted">${n(rows.length)} of ${plural(D.rows.length, 'rate', 'rates')} in ${esc(doc.filename)}</span></div><input class="search" id="rsearch" placeholder="find a title…" value="${esc(D.search)}"></div>
        <div class="bd flush"><table><thead><tr><th>Title on the document</th><th class="num">Rate</th><th>Period</th><th>Role</th><th>Band</th><th>Status</th></tr></thead><tbody>
        ${rows.map(r => `<tr class="row ${r.obs_id === D.rowId ? 'sel' : ''}" data-row="${r.obs_id}"><td>${esc(r.observed_title)}${r.level_raw ? `<span class="doc">${esc(r.level_raw)}</span>` : ''}</td><td class="num">${rate(r)}</td><td class="muted">${esc(r.period_raw || '')}</td><td>${esc(roleName(r.canonical_role_id))}</td><td>${bandPill(r)}</td><td>${statusPill(r)}</td></tr>`).join('') || '<tr><td colspan="6" class="muted">No rates match.</td></tr>'}
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
    <div class="ev"><h3 class="h4">What the system made of it</h3>${kv([['Role', o.canonical_role_id ? roleName(o.canonical_role_id) : 'not decided'], ['Band', o.twm_band ? o.twm_band.replace('_', ' / ') : (o.canonical_role_id ? 'not stated' : '')], ['Band from', o.band_source], ['Technology', o.attr_technology], ['Location', o.attr_location], ['Status', why]])}</div>
    ${o.history.length ? `<div class="history"><b>Answers given on this title</b>${o.history.map(h => `<div>${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (replaced)' : ''}</div>`).join('')}</div>` : ''}`;
}

/* ── global framework updates ── */
async function renderRules() {
  await loadSet(); refreshChrome();
  const R = S.rules;
  R.pending = await api('/api/rules/pending');
  const section = (kind, title, cols, labels, blurb) => {
    const rows = R.pending[kind];
    return `<div class="card" style="margin-bottom:16px"><div class="hd"><h2>${title}</h2><span class="sub">${rows.length ? plural(rows.length, 'answer', 'answers') + ' waiting' : 'nothing waiting'}</span></div>
      <div class="bd" style="padding-bottom:${rows.length ? 0 : 16}px"><div class="plain" style="margin:0 0 10px">${blurb}</div></div>
      ${rows.length ? `<div class="toolbar"><div class="chips"><a class="btn sm" href="/api/rules/pending.csv?kind=${kind}">1 · Download</a><button class="btn sm" data-applied="${kind}">2 · Mark the ticked rows as done</button></div></div>
      <div class="bd flush"><table><thead><tr><th></th>${labels.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>
        ${rows.map(r => `<tr><td><input type="checkbox" data-pick="${r.decision_id}" ${R.picked.has(r.decision_id) ? 'checked' : ''}></td>${cols.map(c => `<td>${esc(c === 'canonical_role_id' ? roleName(r[c]) : String(r[c] ?? '').replace(/_/g, ' '))}</td>`).join('')}</tr>`).join('')}
      </tbody></table></div>` : ''}</div>`;
  };
  $('#page').innerHTML = `<h1>Global Framework Updates</h1><p class="lede">Answers you marked <b>Everyone</b> are nominations to the role framework TWM shares across clients. They do not change the framework by themselves: Claude checks each one and adds it, and the framework's acceptance report is regenerated. Download the rows, hand them over, then tick them off here. Answers for this client or this contract set never come here; they already apply.</p>
    ${section('title_mappings', 'Job titles nominated for everyone', ['observed_title', 'source', 'canonical_role_id', 'twm_band', 'attr_technology', 'reviewer'], ['Title', 'Client', 'Role', 'Band', 'Technology', 'Decided by'], 'Each row becomes a permanent mapping from a vendor’s title to a role, for every future document from any client.')}
    ${section('location_rules', 'Place names for this client’s rulebook', ['client_key', 'place', 'classification', 'decided_by', 'reason'], ['Client', 'Place', 'Answer', 'Decided by', 'Why'], 'Place names are always per client. These rows go into this client’s location rulebook so the next document for the same client does not ask again.')}`;
}

/* ── routing and events ── */
async function go(screen) {
  if (S.screen === 'set' && S.setTab === 'review' && !leaveItem()) return;
  if (screen === 'review' || screen === 'documents') {
    if (!S.setId) { S.screen = 'sets'; await renderSets(); toast('Choose a contract set first.', false); return; }
    S.screen = 'set'; S.setTab = screen; await renderSet();
  } else { S.screen = screen; await (screen === 'sets' ? renderSets() : renderRules()); }
  window.scrollTo(0, 0);
}
async function openSet(id) { S.setId = id; localStorage.setItem('twm.set', id); S.screen = 'set'; S.setTab = 'review'; S.review.selected = []; S.review.form = freshForm(); S.review.suggest = null; S.docs.rowId = null; S.docs.docId = null; await renderSet(); window.scrollTo(0, 0); }

document.addEventListener('click', async e => {
  const t = e.target.closest('#who-change,[data-step],[data-screen],[data-open],[data-settab],[data-tab],[data-i],[data-check],[data-band],[data-cls],[data-tag],[data-alt],[data-scope],[data-doc],[data-row],[data-filter],[data-pick],[data-applied],[data-detail],[data-editname],[data-cancelname],[data-savename],[data-confirmname],#f-record,#f-park,#f-park-go,#f-park-cancel,#f-unpark');
  if (!t) return;
  if (t.id === 'who-change') { e.preventDefault(); S.editingWho = true; showWho(); $('#analyst').focus(); return; }
  if (t.dataset.screen) { e.preventDefault(); return go(t.dataset.screen); }
  if (t.dataset.open) return openSet(t.dataset.open);
  if (t.dataset.settab) { if (S.setTab === 'review' && !leaveItem()) return; S.setTab = t.dataset.settab; return renderSet(); }
  if (t.dataset.tab) { if (!leaveItem()) return; S.review.tab = t.dataset.tab; S.review.selected = []; return renderReview(); }
  if (t.dataset.step) { const R = S.review; const list = (R.tab === 'titles' || R.tab === 'parked') ? R.groups : R.items; const next = Math.max(0, Math.min(list.length - 1, (R.selected[0] ?? 0) + (+t.dataset.step))); if (!leaveItem()) return; R.selected = [next]; await renderReview(); const row = $('#qlist tr.sel'); if (row) row.scrollIntoView({ block: 'nearest' }); return; }
  if (t.dataset.check !== undefined) { const i = +t.dataset.check; const sel = S.review.selected; readForm(); S.review.selected = t.checked ? [...sel, i].sort((a, b) => a - b) : sel.filter(x => x !== i); S.review.suggest = null; return renderReview(); }
  if (t.dataset.i !== undefined) { if (S.review.selected.length === 1 && S.review.selected[0] === +t.dataset.i) return; if (!leaveItem()) return; S.review.selected = [+t.dataset.i]; return renderReview(); }
  if (t.dataset.band !== undefined) { S.review.form.band = t.dataset.band || null; $$('#f-bands button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.dataset.cls) { S.review.form.cls = t.dataset.cls; $$('#f-cls button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.dataset.scope) { S.review.form.scope = t.dataset.scope; $$('#f-scope button').forEach(b => b.classList.toggle('on', b === t)); return; }
  if (t.dataset.tag !== undefined) { readForm(); const F = S.review.form; const tag = t.dataset.tag; F.tags = F.tags.includes(tag) ? F.tags.filter(x => x !== tag) : [...F.tags, tag]; F._tagq = ''; $('#f-tags').outerHTML = tagPicker().split('<div class="hint">')[0]; return; }
  if (t.dataset.alt) { readForm(); S.review.form.role = t.dataset.alt; S.review.form.fromSuggestion = true; $('#f-role').value = t.dataset.alt; return; }
  if (t.id === 'f-record') return (S.review.tab === 'titles' || S.review.tab === 'parked') ? saveTitle() : saveItem();
  if (t.id === 'f-park') { readForm(); S.review.parking = true; return renderReview(); }
  if (t.id === 'f-park-cancel') { readForm(); S.review.parking = false; return renderReview(); }
  if (t.id === 'f-park-go') return parkSelected();
  if (t.id === 'f-unpark') return unparkSelected();
  if (t.dataset.editname) { e.preventDefault(); S.editingName = true; return renderSet(); }
  if (t.dataset.cancelname) { S.editingName = false; return renderSet(); }
  if (t.dataset.savename || t.dataset.confirmname) {
    if (needName()) return;
    const name = t.dataset.savename ? $('#setname').value : S.set.name;
    try { await post(`/api/sets/${encodeURIComponent(S.setId)}/name`, { name, decided_by: S.analyst }); S.editingName = false; toast('Name saved.'); return renderSet(); } catch (err) { toast(err.message, false); }
    return;
  }
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
  if (e.target.id === 'f-note' || e.target.id === 'f-reason') readForm();
  if (e.target.id === 'rsearch') { S.docs.search = e.target.value; clearTimeout(S._st); S._st = setTimeout(renderDocuments, 250); }
  if (e.target.id === 'setsearch') { S._setSearch = e.target.value; clearTimeout(S._ss); S._ss = setTimeout(renderSets, 200); }
  if (e.target.id === 'f-tagq') { readForm(); $('#f-tags').outerHTML = tagPicker().split('<div class="hint">')[0]; const q = $('#f-tagq'); q.focus(); q.setSelectionRange(q.value.length, q.value.length); }
  if (e.target.id === 'f-role') { const F = S.review.form; F.role = e.target.value; const sg = S.review.suggest; F.fromSuggestion = !!(sg && sg.suggestions.some(x => x.id === F.role)); }
});
document.addEventListener('keydown', e => {
  if (e.target.id === 'analyst' && (e.key === 'Enter' || e.key === 'Tab')) { S.editingWho = false; showWho(); if (S.screen === 'sets') renderSets(); return; }
  if (S.screen !== 'set' || S.setTab !== 'review') return;
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); const b = $('#f-record'); if (b) b.click(); return; }
  if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
  const R = S.review;
  const list = (R.tab === 'titles' || R.tab === 'parked') ? R.groups : R.items;
  if (!list.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    const cur = R.selected[0] ?? -1;
    const next = Math.max(0, Math.min(list.length - 1, cur + (e.key === 'ArrowDown' ? 1 : -1)));
    if (next === cur || !leaveItem()) return;
    R.selected = [next]; renderReview();
  }
});

$('#analyst').value = S.analyst;
$('#analyst').addEventListener('blur', () => { if (S.analyst.trim()) { S.editingWho = false; showWho(); } });
(S.setId ? openSet(S.setId) : go('sets')).catch(err => { $('#page').innerHTML = `<div class="alert"><span class="dot"></span><div>Could not open the ledger: ${esc(err.message)}</div></div>`; });
