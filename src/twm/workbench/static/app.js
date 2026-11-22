/* The review workbench page (work/workbench/plan-v3.md). Plain JavaScript over the JSON service in api.py.
   Everything starts from choosing a contract set. Written for the person working the queue: plain words, one question at a
   time, the system's suggestion pre-selected but labelled, a clear Save, visible progress. Honest screens: the system's own
   reason for asking stays, folded; nothing is saved without the analyst's name and a reason. */
'use strict';

/* The version of this script the browser loaded (the page stamps it on the script's address). An open page that is older than
   the server's script says so and offers a reload, so a change is never missed because a tab was left open. */
const LOADED_VERSION = (() => { try { return new URL(document.currentScript.src).searchParams.get('v'); } catch (e) { return null; } })();
async function checkVersion() {
  if (!LOADED_VERSION || document.getElementById('stale')) return;
  try {
    const v = await (await fetch('/api/version', { cache: 'no-store' })).json();
    if (v.js && v.js !== LOADED_VERSION) {
      const b = document.createElement('div'); b.id = 'stale'; b.className = 'stale';
      b.innerHTML = 'This page has been updated since you opened it. <button class="btn primary sm" onclick="location.reload()">Reload to see the new version</button>';
      document.body.appendChild(b);
    }
  } catch (e) { /* the server is restarting; the next look will tell */ }
}
window.addEventListener('focus', checkVersion);
setInterval(checkVersion, 60000);

const S = {
  screen: 'sets',
  analyst: localStorage.getItem('twm.analyst') || '',
  tax: null, saved: 0,
  sets: [], setId: localStorage.getItem('twm.set') || null, set: null, setTab: 'review', editingName: false,
  review: { tab: 'titles', groups: [], items: [], selected: [], form: freshForm(), suggest: null, parking: false },
  docs: { docId: null, rows: [], filter: 'all', search: '', rowId: null, showDetail: false },
  rules: { pending: null, picked: new Set() },
  terms: { data: null, termId: null, floor: null, filter: 'all', more: {} }, inv: null, vendors: null, dis: null,
};
function freshForm() { return { role: '', band: null, tags: [], scope: 'set', reason: '', confirm: false, cls: null, docType: '', note: '', fromSuggestion: false, cond: '', newName: '', newGroup: '', vendor: '', notVendor: false, basis: '' }; }

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const n = v => (v ?? 0).toLocaleString('en-CA');
const z = v => (v ? n(v) : '');
const KIND_OF = { msa: 'contracts', amendment: 'amendments', sow: 'sows', rate_card: 'rate_cards', invoice: 'invoices', timesheet: 'invoices' };
const KIND_LABEL = { contracts: 'Contracts', amendments: 'Amendments', sows: 'SOWs', rate_cards: 'Rate cards', other: 'Other', invoices: 'Invoices and timesheets' };
const kindOf = cls => KIND_OF[cls] || 'other';
const DOC_KINDS = [['msa', 'Master agreement'], ['sow', 'Statement of work'], ['amendment', 'Amendment'], ['rate_card', 'Rate card or pricing exhibit'], ['sla', 'Service levels'], ['solicitation', 'Solicitation / RFP'], ['template', 'Template'], ['invoice', 'Invoice'], ['timesheet', 'Timesheet'], ['other', 'Other']];
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
async function loadSet() { S.set = S.setId ? await api(`/api/sets/${S.setId}`) : null; S.comp = S.setId ? await api(`/api/sets/${S.setId}/composition`) : null; S.dis = S.setId ? await api(`/api/sets/${S.setId}/disclosure`) : null; }
async function loadInv() { if (!S.inv) S.inv = await api('/api/conditions'); }
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
  $$('#nav button').forEach(b => b.classList.toggle('active', b.dataset.screen === S.screen || (S.screen === 'set' && (b.dataset.screen === S.setTab || ((S.setTab === 'overview' || S.setTab === 'terms') && b.dataset.screen === 'sets')))));
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
    <div class="card setlist"><div class="bd flush"><table><thead><tr><th>Contract set</th><th>Status</th><th class="num">Docs</th><th class="num">Contracts</th><th class="num">Amend-<br>ments</th><th class="num">SOWs</th><th class="num">Rate<br>cards</th><th class="num">Other</th><th class="num gap">Read by<br>the engine</th><th class="num">Rates<br>found</th><th class="num">Questions<br>for you</th></tr></thead><tbody>
      ${list.map(s => { const k = s.kinds || {}, ct = s.composition_total || {}; return `<tr class="row" data-open="${esc(s.root_id)}"><td><span class="setname">${esc(s.name)}<span class="file">${esc(s.root_filename)}</span></span></td>
        <td><span class="pill status ${s.status}">${esc(statusLine(s))}</span></td><td class="num">${n(s.documents.length)}</td><td class="num">${z(k.contracts)}</td><td class="num">${z(k.amendments)}</td><td class="num">${z(k.sows)}</td><td class="num">${z(k.rate_cards)}</td><td class="num">${z((k.other || 0) + (k.invoices || 0))}</td>
        <td class="num gap">${n(ct.read)} of ${n(s.documents.length)}</td><td class="num">${n(ct.rates)}</td><td class="num">${z(s.open)}</td></tr>`; }).join('')
        || '<tr><td colspan="11" class="muted">No contract sets match.</td></tr>'}
    </tbody></table></div></div>
    <p class="hint" style="margin-top:10px">Registering new contract sets from this screen comes later; for now they arrive when a contract is run through the engine.</p>`;
}

/* ── one contract set: header, tiles, Review and Documents tabs ── */
async function renderSet() {
  if (!S.setId) { S.screen = 'sets'; return renderSets(); }
  await loadSet(); await loadTax(); refreshChrome();
  $('#page').innerHTML = `<div id="sethead-wrap">${setHeaderHtml()}</div><div id="setbody"></div>`;
  if (S.setTab === 'review') await renderReview(); else if (S.setTab === 'documents') await renderDocuments(); else if (S.setTab === 'terms') await renderTerms();
}
function setHeaderHtml() {
  const s = S.set;
  const nameBlock = S.editingName
    ? `<div class="namebox"><input id="setname" value="${esc(s.name)}"><button class="btn primary sm" data-savename="1">Save name</button><button class="btn ghost sm" data-cancelname="1">Cancel</button></div>`
    : `<div class="file">${esc(s.root_filename)} <a href="#" data-editname="1">· rename</a></div>`;
  const heldBack = s.rows - s.counted;
  const comp = S.comp || { rows: [], total: {} };
  const inv = comp.rows.find(r => r.kind === 'invoices') || { documents: 0 };
  const T = comp.total;
  const compRow = r => `<tr class="row" data-kind="${r.kind}" title="Show these documents"><td>${esc(r.label)}</td><td class="num">${z(r.documents)}</td>
      <td class="num">${r.documents ? `${n(r.read)} of ${n(r.documents)}` : ''}</td><td class="num">${r.rates ? `${n(r.rates)}<span class="why">${n(r.counted)} in benchmarks</span>` : ''}</td>
      <td class="num">${r.facts || r.conditions ? `${n(r.facts)} facts, ${n(r.conditions)} conditions` : ''}</td><td class="num">${z(r.questions)}</td></tr>`;
  const head = `
    <p class="crumb"><a href="#" data-screen="sets">Contract sets</a> › ${esc(s.name)}</p>
    <div class="sethead"><div><h1>${esc(s.name)}</h1>${nameBlock}</div><span class="pill status ${s.status}" style="font-size:12px;padding:6px 12px">${esc(statusLine(s))}</span></div>`;
  const table = `
    <div class="card comp"><table><thead><tr><th></th><th class="num">Documents</th><th class="num">Read by the engine</th><th class="num">Rates found</th><th class="num">Facts and conditions</th><th class="num">Questions for you</th></tr></thead><tbody>
      ${comp.rows.filter(r => r.kind !== 'invoices').map(compRow).join('')}
      <tr class="later"><td>Invoices and timesheets</td><td class="num">${inv.documents ? n(inv.documents) : 'none yet'}</td><td colspan="4">matched to this contract in a later stage (reconciliation), not here</td></tr>
      <tr class="tot"><td>Total</td><td class="num">${n(T.documents)}</td><td class="num">${n(T.read)} of ${n(T.documents)}</td><td class="num">${n(T.rates)}<span class="why">${n(T.counted)} in benchmarks${heldBack ? `, ${n(heldBack)} held back` : ''}</span></td><td class="num">${T.facts || T.conditions ? `${n(T.facts)} facts, ${n(T.conditions)} conditions` : ''}</td><td class="num">${z(T.questions)}</td></tr>
    </tbody></table></div>
    <div class="btns" style="margin:0 0 14px">${s.open ? `<button class="btn primary" data-settab="review">Start reviewing: ${plural(s.open, 'question', 'questions')} →</button>` : ''}${T.facts || T.conditions ? '<button class="btn" data-settab="terms">Read the contract terms</button>' : ''}<button class="btn" data-settab="documents">Browse the documents and rates</button><span class="hint" style="margin:0">Click a row of the table to see those documents.${T.notes ? ` ${plural(T.notes, 'note', 'notes')} from the engine: see Review.` : ''}</span></div>`;
  const strip = `
    <div class="strip"><span><b>${n(T.documents)}</b> documents, ${n(T.read)} read</span><span class="ok"><b>${n(T.rates)}</b> rates, ${n(T.counted)} in benchmarks</span>${T.facts || T.conditions ? `<span><b>${n(T.facts)}</b> facts, <b>${n(T.conditions)}</b> conditions</span>` : ''}<span class="wait"><b>${n(s.open)}</b> to answer · ${n(s.answered)} answered · ${n(s.parked)} parked</span></div>`;
  const tabs = `
    <div class="subtabs"><button data-settab="overview" class="${S.setTab === 'overview' ? 'active' : ''}">Overview</button><button data-settab="review" class="${S.setTab === 'review' ? 'active' : ''}">Review<span class="n">${s.open}</span></button><button data-settab="terms" class="${S.setTab === 'terms' ? 'active' : ''}">Terms<span class="n">${n((T.facts || 0) + (T.conditions || 0))}</span></button><button data-settab="documents" class="${S.setTab === 'documents' ? 'active' : ''}">Documents<span class="n">${s.documents}</span></button></div>`;
  return head + (S.setTab === 'overview' ? tabs + disclosureLine(S.dis, true) + table : strip + tabs);
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
const TABS = [['titles', 'Job titles'], ['condition', 'Conditions'], ['disclosure', 'Disclosure'], ['vendor', 'Vendor names'], ['location', 'Place names'], ['intake', 'Document types'], ['parked', 'Parked'], ['notes', 'Engine notes']];
const ANSWERABLE = ['titles', 'condition', 'disclosure', 'vendor', 'location', 'intake'];
const isTitles = () => S.review.tab === 'titles' || S.review.tab === 'parked';
const currentList = () => (isTitles() ? S.review.groups : S.review.items);
function panelHtml() {
  const R = S.review;
  return `${panelNav(currentList())}${R.lastSaved ? `<div class="saved-note" style="margin:12px 18px 0">${esc(R.lastSaved)}</div>` : ''}${isTitles() ? titlePanel() : itemPanel()}`;
}
function drawPanel() { const el = $('#qpanel'); if (el) el.innerHTML = panelHtml(); }
async function renderReview() {
  const R = S.review, s = S.set, q = s.queue || {};
  await loadInv();
  const counts = { titles: s.title_groups, condition: q.condition || 0, disclosure: q.disclosure ? 1 : 0, vendor: q.vendor || 0, location: q.location || 0, intake: q.intake || 0, parked: s.parked_items, notes: (q.extraction || 0) + (q.reading || 0) };
  if (!TABS.some(([k]) => k === R.tab)) R.tab = 'titles';
  if (ANSWERABLE.includes(R.tab) && !counts[R.tab]) { const next = ANSWERABLE.find(k => counts[k]); if (next) { R.tab = next; R.selected = []; R.form = freshForm(); } }   // one kind finished: on to the next
  const sid = encodeURIComponent(S.setId);
  R.parkedItems = [];
  if (R.tab === 'titles') R.groups = await api(`/api/queue/titles?set_id=${sid}`);
  else if (R.tab === 'parked') {
    R.groups = await api(`/api/queue/titles?set_id=${sid}&status=parked`);
    for (const k of ['condition', 'disclosure', 'vendor', 'location', 'intake']) R.parkedItems.push(...await api(`/api/queue/${k}?set_id=${sid}&status=parked`));
  }
  else if (R.tab === 'notes') R.items = [...await api(`/api/queue/extraction?set_id=${sid}`), ...await api(`/api/queue/reading?set_id=${sid}`)];
  else if (R.tab === 'condition') R.items = await api(`/api/queue/conditions?set_id=${sid}`);
  else if (R.tab === 'disclosure') { const d = await api(`/api/sets/${sid}/disclosure`); R.items = d.queue_ids.length ? [d] : []; }
  else { R.items = await api(`/api/queue/${R.tab}?set_id=${sid}`); if (R.tab === 'vendor' && !S.vendors) S.vendors = await api('/api/vendors'); }
  const list = currentList();
  R.selected = R.selected.filter(i => i < list.length);
  if (!R.selected.length && list.length) R.selected = [0];
  if (R.tab === 'titles' && R.selected.length === 1) await loadSuggestion(R.groups[R.selected[0]]); else R.suggest = null;
  const shown = TABS.filter(([k]) => counts[k] || k === R.tab);
  const rail = isTitles() ? ((R.tab === 'parked' && !R.groups.length && R.parkedItems.length) ? '' : titleTable(R.groups, R.tab === 'parked')) + (R.tab === 'parked' ? parkedItemsTable() : '') : itemTable(R.items, R.tab);
  $('#setbody').innerHTML = `
    <div class="cols review">
      <div class="card rail">
        <div class="tabs">${shown.map(([k, l]) => `<button data-tab="${k}" class="${R.tab === k ? 'active' : ''}">${l}<span class="n">${counts[k]}</span></button>`).join('')}</div>
        <div class="bd flush" id="qlist">${rail}</div>
      </div>
      <div class="card panel" id="qpanel">${panelHtml()}</div>
    </div>`;
  R.lastSaved = null;
  if (isTitles() && R.selected.length === 1) fillEvidence(R.groups[R.selected[0]]);
}
function parkedItemsTable() {
  const items = S.review.parkedItems || []; if (!items.length) return '';
  const KIND = { condition: 'Condition', disclosure: 'Disclosure', vendor: 'Vendor name', location: 'Place name', intake: 'Document type' };
  return `<table><thead><tr><th>Also parked</th><th></th></tr></thead><tbody>${items.map(it => `<tr><td>${esc(it.item)}<span class="why">${KIND[it.kind] || it.kind} · ${esc(it.filename || '')}</span></td><td><button class="btn sm" data-unpark="${it.id}">Bring back</button></td></tr>`).join('')}</tbody></table>`;
}
function ctxTable(ctx, stated) {
  if (!ctx || ctx.kind !== 'table') return null;
  const cell = (c, tag, hit) => `<${tag}${hit && stated && c.includes(stated) ? ' class="hitcell"' : ''}>${esc(c)}</${tag}>`;
  return `<div class="ctxwrap"><table class="ctx"><thead>${ctx.header.map(r => `<tr>${r.map(c => cell(c, 'th', false)).join('')}</tr>`).join('')}</thead>
    <tbody>${ctx.rows.map(r => `<tr class="${r.hit ? 'hit' : ''}">${r.cells.map(c => cell(c, 'td', r.hit)).join('')}</tr>`).join('')}</tbody></table></div>
    <div class="hint">The row as printed${ctx.page ? ' on page ' + ctx.page : ''}, with its headings and neighbours (${n(ctx.of_rows)} rows in the table).</div>`;
}
function appearHtml(list) {
  if (!list.length) return 'Only in this question; no priced rows found for it.';
  return list.map(a => {
    const where = a.pages.length ? ` · page${a.pages.length > 1 ? 's' : ''} ${a.pages.slice(0, 6).join(', ')}${a.pages.length > 6 ? '…' : ''}` : '';
    const open = `<a href="/api/documents/${a.document_id}/file${a.pages.length ? '#page=' + a.pages[0] : ''}" target="_blank" rel="noopener">open</a>`;
    if (a.how === 'named') return `<div><b>${esc(KIND_LABEL[kindOf(a.doc_class)])}</b> · ${esc(a.filename)}${where} · names ${esc(a.who || 'a person')} under this title · ${open}</div>`;
    const range = a.rate_min === a.rate_max ? `${a.rate_min}` : `${a.rate_min} to ${a.rate_max}`;
    const bits = [plural(a.rates, 'rate', 'rates'), a.periods.length > 1 ? `${a.periods.length} periods (${esc(a.periods[0])} to ${esc(a.periods[a.periods.length - 1])})` : (a.periods[0] ? esc(a.periods[0]) : ''),
      a.locations.length ? esc(a.locations.join(' / ')) : '', a.qualifiers.length ? esc(a.qualifiers.slice(0, 3).join(' / ')) : '', `${esc(range)} ${esc(a.currency || '')}${a.unit ? ' per ' + esc(a.unit) : ''}`].filter(Boolean);
    return `<div><b>${esc(KIND_LABEL[kindOf(a.doc_class)])}</b> · ${esc(a.filename)}${where} · ${open}<span class="why">${bits.join(' · ')}</span></div>`;
  }).join('');
}
async function fillEvidence(g) {
  const ex = g.examples[0] || {};
  const same = () => { const R = S.review; const cur = R.groups[R.selected[0]]; return cur && cur.title === g.title && cur.vendor === g.vendor; };
  if (ex.obs_id) api(`/api/rows/${ex.obs_id}/table`).then(ctx => { const html = ctxTable(ctx, ex.rate_as_stated); const el = $('#tctx'); if (html && el && same()) el.innerHTML = html; }).catch(() => {});
  api(`/api/appearances?title=${encodeURIComponent(g.title)}&set_id=${encodeURIComponent(S.setId)}${g.vendor ? '&vendor=' + encodeURIComponent(g.vendor) : ''}`)
    .then(list => { const el = $('#appear'); if (el && same()) { el.classList.remove('muted'); el.innerHTML = appearHtml(list); } }).catch(() => {});
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
  const titles = isTitles();
  const actions = R.tab === 'notes' ? '' : titles
    ? `<button class="btn primary" id="f-record">${R.tab === 'parked' ? 'Save' : 'Save and go to next'}</button>${R.tab === 'parked' ? '<button class="btn" id="f-unpark">Bring back</button>' : '<button class="btn" id="f-park" title="Set it aside with a note; it moves to the Parked tab">Park</button>'}`
    : `<button class="btn primary" id="f-record">${list.length > 1 ? 'Save and go to next' : 'Save'}</button><button class="btn" id="f-park" title="Set it aside with a note; it moves to the Parked tab">Park</button>`;
  return `<div class="panelnav"><div class="pos"><button class="btn sm" data-step="-1" ${i <= 0 ? 'disabled' : ''}>‹</button><span>${R.selected.length > 1 ? `${R.selected.length} selected` : `${i + 1} of ${list.length}`}</span><button class="btn sm" data-step="1" ${i >= list.length - 1 ? 'disabled' : ''}>›</button></div>
    <div class="acts">${actions}<span class="hint">Ctrl+Enter saves</span></div></div>
    ${R.parking ? `<div class="parknote bar"><input id="f-note" placeholder="optional note, e.g. need the SOW to decide" value="${esc(R.form.note)}"><button class="btn primary sm" id="f-park-go">Park it</button><button class="btn ghost sm" id="f-park-cancel">Cancel</button></div>` : ''}`;
}
function titleTable(groups, parked) {
  if (!groups.length) return `<div class="empty">${parked ? 'Nothing parked.' : 'All job titles are decided. Nothing to do here.'}</div>`;
  const oneClient = new Set(groups.map(g => g.client)).size === 1;
  return `<table><thead><tr><th></th><th>Job title</th>${oneClient ? '' : '<th>Client</th>'}<th class="num" title="How many rates in this contract set are priced under this job title and wait on your answer">Rates under<br>this title</th></tr></thead><tbody>
    ${groups.map((g, i) => `<tr class="row ${S.review.selected.includes(i) ? 'sel' : ''}" data-i="${i}"><td><input type="checkbox" data-check="${i}" ${S.review.selected.includes(i) ? 'checked' : ''} title="Tick several to give them one answer"></td>
      <td>${esc(g.title)}${parked && g.history.length ? `<span class="why">${esc(g.history[g.history.length - 1].reason || 'parked')}</span>` : ''}</td>${oneClient ? '' : `<td>${esc(g.client || '–')}</td>`}<td class="num">${n(g.rows_unlocked)}</td></tr>`).join('')}
  </tbody></table>${parked ? '' : '<div class="history">Tick more than one title only when they are the same role; one answer then covers all of them.</div>'}`;
}
function itemTable(items, kind) {
  if (!items.length) return '<div class="empty">Nothing to do here.</div>';
  const sel = i => (S.review.selected.includes(i) ? 'sel' : '');
  if (kind === 'condition') return `<table><thead><tr><th>What the engine found</th><th class="num">Page</th></tr></thead><tbody>
    ${items.map((it, i) => `<tr class="row ${sel(i)}" data-i="${i}"><td>${esc(it.item)}<span class="why">${esc(it.filename || '')}</span></td><td class="num">${it.term.page ?? ''}</td></tr>`).join('')}</tbody></table>
    <div class="history">Clauses the engine read that fit none of the ${S.inv.total} named conditions. One at a time.</div>`;
  if (kind === 'disclosure') return `<table><tbody><tr class="row sel" data-i="0"><td>Disclosure check<span class="why">${plural(items[0].restricting.length, 'clause restricts', 'clauses restrict')}, ${plural(items[0].clearing.length, 'allows', 'allow')}</span></td></tr></tbody></table>
    <div class="history">One decision for the whole contract set.</div>`;
  if (kind === 'vendor') return `<table><thead><tr><th>Name printed on the document</th></tr></thead><tbody>
    ${items.map((it, i) => `<tr class="row ${sel(i)}" data-i="${i}"><td>${esc(it.item)}<span class="why">${esc(it.filename || '')}</span></td></tr>`).join('')}</tbody></table>`;
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
    ? `<div class="ev"><div class="step">What the document says</div><h3>${esc(g.title)}</h3><div class="meta">${esc(g.client || 'no client')} · ${plural(g.rows_in_set ?? g.rows_affected, 'rate', 'rates')} here${g.rows_affected > (g.rows_in_set ?? g.rows_affected) ? `, ${n(g.rows_affected)} for the client` : ''} · ${esc(g.documents.join(', '))}</div>
        <div id="tctx" class="tctx"><div class="quote">${esc(ex.source_quote || '(no quote stored)')}</div></div>
        ${ex.obs_id ? `<a href="/api/rows/${ex.obs_id}/page.png" target="_blank" rel="noopener" title="See the whole page with this row boxed"><img class="closeup" src="/api/rows/${ex.obs_id}/closeup.png" alt="the row on its page" onerror="this.parentNode.remove()"></a>` : ''}
        <div class="links">${ex.obs_id && ex.source_page ? `<a href="/api/rows/${ex.obs_id}/page.png" target="_blank" rel="noopener">See the whole page</a>` : ''}${ex.document_id ? `<a href="/api/documents/${ex.document_id}/file${ex.source_page ? '#page=' + ex.source_page : ''}" target="_blank" rel="noopener">Open the original document${ex.source_page ? ' at page ' + ex.source_page : ''}</a>` : ''}</div>
        <div class="step" style="margin-top:10px">Where this title appears in the contract set</div><div id="appear" class="appear muted">Looking…</div>
        <div class="plain"><b>Why this needs you:</b> ${esc(plainWhy(g.details[0]))}</div>
        <details class="more"><summary>The system's own words</summary><div class="why-box">${esc(g.details.join(' | '))}</div></details>
        ${g.history.length ? `<details class="more"><summary>Earlier answers</summary>${g.history.map(h => `<div class="why-box">${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (replaced)' : ''}</div>`).join('')}</details>` : ''}
        ${sg && sg.saved ? `<div class="saved-note">You answered this title before (${esc(sg.saved.scope === 'set' ? 'this contract set' : sg.saved.scope === 'vendor' ? 'this vendor' : 'everyone')}): ${esc(roleName(sg.saved.canonical_role_id))}${sg.saved.twm_band ? ', ' + esc(sg.saved.twm_band) : ''}. Saving again replaces it.</div>` : ''}</div>`
    : `<div class="ev"><div class="step">Check they are the same role</div><h3>${plural(sel.length, 'title', 'titles')} selected</h3>${sel.map(x => `<div>${esc(x.title)} <span class="muted">(${esc(x.client || '–')}, ${plural(x.rows_affected, 'rate', 'rates')})</span></div>`).join('')}</div>`;
  const top = sg && sel.length === 1 && sg.suggestions.length ? sg.suggestions[0] : null;
  const suggestion = top
    ? `<div class="suggested">Suggested: <b>${esc(top.name)}</b> <span class="muted">(${esc(top.why)})</span>. Confirm it, or pick another.${sg.suggestions.length > 1 ? `<div class="alts">${sg.suggestions.slice(1).map(x => `<button type="button" data-alt="${esc(x.id)}" title="${esc(x.why)}">${esc(x.name)}</button>`).join('')}</div>` : ''}</div>`
    : '';
  return `<div class="twocol"><div class="col">${head}</div><div class="col form">
      <div class="step">Your answer</div>
      <label for="f-role">Which role is this?</label>${suggestion}${roleSelect(F.role)}
      <label>How senior?</label>${bandButtons(F.band)}
      <label>Technology named in the title <span class="muted">(optional)</span></label>${tagPicker()}
      <label>Where does this answer apply?</label>${scopeButtons(F.scope)}
      <label for="f-reason">Note <span class="muted">(optional)</span></label><textarea id="f-reason" placeholder="anything worth remembering about this answer">${esc(F.reason)}</textarea>
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
  if (R.tab === 'condition') return conditionPanel(it);
  if (R.tab === 'disclosure') return disclosurePanel(it);
  if (R.tab === 'vendor') return vendorPanel(it);
  if (R.tab === 'location') {
    const m = /place '([^']+)'/.exec(it.detail || '');
    return `<div class="twocol"><div class="col"><div class="ev"><div class="step">What the system found</div><h3>${esc(m ? m[1] : it.item)}</h3><div class="meta">on "${esc(it.item)}" · ${esc(it.client || 'no client')} · ${esc(it.filename || '')}</div>
        <div class="plain">Is this place onshore, nearshore or offshore <b>for this client</b>? The system never decides a place on its own. Your answer is reused for this client from now on.</div></div></div>
      <div class="col form"><div class="step">Your answer</div><label>For this client, this place is</label><div class="bands" id="f-cls">${S.tax.locations.map(l => `<button type="button" class="${F.cls === l ? 'active' : ''}" data-cls="${l}">${l}</button>`).join('')}</div>
        <label for="f-reason">Note <span class="muted">(optional)</span></label><textarea id="f-reason" placeholder="e.g. a short drive from the client’s Toronto teams">${esc(F.reason)}</textarea>
        <div class="err" id="f-err"></div></div></div>`;
  }
  const isClass = /classification/.test(it.detail || '');
  return `<div class="twocol"><div class="col"><div class="ev"><div class="step">What the system found</div><h3>${esc(it.item)}</h3><div class="meta">${esc(short(it.detail))}</div></div></div>
    <div class="col form"><div class="step">Your answer</div>${isClass
      ? `<label for="f-doctype">What kind of document is it?</label><select id="f-doctype"><option value="">Choose…</option>${[['msa', 'Master agreement'], ['sow', 'Statement of work'], ['amendment', 'Amendment'], ['rate_card', 'Rate card or pricing exhibit'], ['sla', 'Service levels'], ['solicitation', 'Solicitation / RFP'], ['template', 'Template'], ['invoice', 'Invoice'], ['timesheet', 'Timesheet'], ['other', 'Other']].map(([v, l]) => `<option value="${v}" ${F.docType === v ? 'selected' : ''}>${l}</option>`).join('')}</select>`
      : `<label>Does this document belong to the contract set it was filed with?</label><div class="bands" id="f-cls">${[['confirm', 'Yes'], ['reject', 'No']].map(([v, l]) => `<button type="button" class="${F.cls === v ? 'active' : ''}" data-cls="${v}">${l}</button>`).join('')}</div>`}
      <label for="f-reason">Note <span class="muted">(optional)</span></label><textarea id="f-reason">${esc(F.reason)}</textarea>
      <div class="err" id="f-err"></div></div></div>`;
}
function condOptions(value) {
  return S.inv.groups.map(g => `<optgroup label="${g.letter} · ${esc(g.name)}">${g.conditions.map(c => `<option value="${c.key}" ${c.key === value ? 'selected' : ''}>${esc(short(c.label + ': ' + c.meaning, 95))}</option>`).join('')}</optgroup>`).join('');
}
const condOf = key => S.inv.groups.flatMap(g => g.conditions).find(c => c.key === key);
function conditionPanel(it) {
  const F = S.review.form, t = it.term;
  const inv = F.cond && !F.cond.startsWith('__') ? condOf(F.cond) : null;
  return `<div class="twocol"><div class="col"><div class="ev"><div class="step">What the contract says</div><h3>${esc(it.item)}</h3>
      <div class="meta">${esc(it.filename || '')} · page ${t.page ?? '–'} · the heading is the engine's description; the clause itself is below</div>
      <div class="quote">${esc(t.value)}</div>
      <a href="/api/terms/${t.term_id}/page.png" target="_blank" rel="noopener" title="See the whole page with this clause boxed"><img class="closeup" src="/api/terms/${t.term_id}/closeup.png" alt="the clause on its page" onerror="this.parentNode.remove()"></a>
      <div class="links"><a href="/api/terms/${t.term_id}/page.png" target="_blank" rel="noopener">See the whole page</a><a href="/api/documents/${it.document_id}/file${t.page ? '#page=' + t.page : ''}" target="_blank" rel="noopener">Open the original document${t.page ? ' at page ' + t.page : ''}</a></div>
      <div class="plain"><b>Why this needs you:</b> The engine read a clause that may change what a rate costs, and none of the ${S.inv.total} named conditions fits it.</div></div></div>
    <div class="col form"><div class="step">Your answer</div>
      <label for="f-cond">Which condition is this?</label>
      ${it.closest.length ? `<div class="suggested">Closest by wording:<div class="alts">${it.closest.map(c => `<button type="button" class="${F.cond === c.key ? 'on' : ''}" data-cond="${c.key}" title="${esc(c.meaning)}">${esc(c.label)}</button>`).join('')}</div></div>` : ''}
      <select id="f-cond"><option value="">Choose…</option><option value="__new" ${F.cond === '__new' ? 'selected' : ''}>None of these: propose a new condition</option><option value="__not" ${F.cond === '__not' ? 'selected' : ''}>This is not a rate condition</option>${condOptions(F.cond)}</select>
      ${inv ? `<div class="hint">${esc(inv.meaning)}.</div>` : ''}
      ${F.cond === '__new' ? `<label for="f-newname">A short name for it</label><input type="text" id="f-newname" placeholder="e.g. capacity shortfall credit" value="${esc(F.newName)}">
        <label for="f-newgroup">Which group does it belong to?</label><select id="f-newgroup"><option value="">Choose…</option>${S.inv.groups.map(g => `<option value="${g.letter}" ${F.newGroup === g.letter ? 'selected' : ''}>${g.letter} · ${esc(g.name)}</option>`).join('')}</select>
        <div class="hint">Recorded for this contract at once and listed under Global Framework Updates. It joins the inventory only after it is confirmed there.</div>` : ''}
      ${F.cond === '__not' ? '<div class="hint">The clause is kept and set aside; nothing relies on it.</div>' : ''}
      <label>Where does this answer apply?</label>${scopeButtons(F.scope)}
      <label for="f-reason">Note <span class="muted">(optional)</span></label><textarea id="f-reason" placeholder="anything worth remembering about this answer">${esc(F.reason)}</textarea>
      <div class="err" id="f-err"></div></div></div>`;
}
const BASES = ['It is a public record', 'The client confirmed in writing', 'A clause in the contract allows it'];
function disclosurePanel(d) {
  const F = S.review.form;
  const clause = c => `<div class="clause"><b>${esc(c.label)}</b> <span class="muted">· ${esc(c.filename)} · page ${c.page ?? '–'} · <a href="/api/terms/${c.term_id}/page.png" target="_blank" rel="noopener">see the page</a></span><div class="quote">${esc(c.value)}</div></div>`;
  return `<div class="twocol"><div class="col"><div class="ev"><div class="step">What the contract says</div><h3>Disclosure check</h3><div class="meta">Read first, before anything from this contract set is benchmarked or contributed.</div>
      ${d.restricting.length ? `<div class="step" style="margin-top:8px">${d.restricting.length === 1 ? 'The clause that restricts' : `The ${d.restricting.length} clauses that restrict`}</div>${d.restricting.map(clause).join('')}` : '<div class="plain">No disclosure or benchmarking clause was found on the pages read.</div>'}
      ${d.clearing.length ? `<div class="step" style="margin-top:10px">${d.clearing.length === 1 ? 'The clause that allows' : `Clauses that allow (${d.clearing.length})`}</div>${d.clearing.slice(0, 3).map(clause).join('')}${d.clearing.length > 3 ? `<div class="hint">${d.clearing.length - 3} more under the Terms tab.</div>` : ''}` : ''}</div></div>
    <div class="col form"><div class="step">Your answer</div><label>May this contract set be benchmarked and contributed?</label>
      <div class="bands" id="f-cls">${[['cleared', 'Yes, it is cleared'], ['restricted', 'No, keep it restricted']].map(([v, l]) => `<button type="button" class="${F.cls === v ? 'active' : ''}" data-cls="${v}">${l}</button>`).join('')}</div>
      ${F.cls === 'cleared' ? `<label for="f-basis">On what basis?</label><div class="alts">${BASES.map(b => `<button type="button" class="${F.basis === b ? 'on' : ''}" data-basis="${esc(b)}">${esc(b)}</button>`).join('')}</div><input type="text" id="f-basis" style="margin-top:6px" placeholder="or say what" value="${esc(F.basis)}">` : ''}
      <label for="f-reason">Note <span class="muted">(optional)</span></label><textarea id="f-reason" placeholder="e.g. who confirmed it and when">${esc(F.reason)}</textarea>
      <div class="hint">One decision for the whole contract set, recorded with your name. It can be changed later.</div><div class="err" id="f-err"></div></div></div>`;
}
function vendorPanel(it) {
  const F = S.review.form;
  return `<div class="twocol"><div class="col"><div class="ev"><div class="step">What the document says</div><h3>${esc(it.item)}</h3><div class="meta">${esc(it.filename || '')}</div><div class="quote">${esc(short(it.detail, 260))}</div>
      <div class="links"><a href="/api/documents/${it.document_id}/file" target="_blank" rel="noopener">Open the original document</a></div>
      <div class="plain"><b>Why this needs you:</b> The system never guesses who the vendor is. Your answer is kept, so this printed name is recognised from now on.</div></div></div>
    <div class="col form"><div class="step">Your answer</div><label for="f-vendor">Which vendor is this printed name?</label>
      ${(S.vendors || []).length ? `<div class="suggested">Vendors already known:<div class="alts">${S.vendors.map(v => `<button type="button" data-vendor="${esc(v)}">${esc(v)}</button>`).join('')}</div></div>` : ''}
      <input type="text" id="f-vendor" placeholder="the vendor's name as you want it shown" value="${esc(F.vendor)}">
      <label class="confirm"><input type="checkbox" id="f-notvendor" ${F.notVendor ? 'checked' : ''}> It is not the vendor (the client, or another party)</label>
      <label for="f-reason">Note <span class="muted">(optional)</span></label><textarea id="f-reason">${esc(F.reason)}</textarea>
      <div class="err" id="f-err"></div></div></div>`;
}
function readForm() {
  const F = S.review.form;
  const g = (id, k) => { const el = $(id); if (el) F[k] = el.type === 'checkbox' ? el.checked : el.value; };
  g('#f-role', 'role'); g('#f-reason', 'reason'); g('#f-confirm', 'confirm'); g('#f-doctype', 'docType'); g('#f-note', 'note'); g('#f-tagq', '_tagq');
  g('#f-cond', 'cond'); g('#f-newname', 'newName'); g('#f-newgroup', 'newGroup'); g('#f-vendor', 'vendor'); g('#f-notvendor', 'notVendor'); g('#f-basis', 'basis');
  const sg = S.review.suggest;
  if (sg && sg.suggestions.length && F.role !== sg.suggestions[0].id) F.fromSuggestion = false;
}
function typed() { const F = S.review.form; return !!(F.reason.trim() || F.cls || F.docType || F.note || F.cond || F.newName.trim() || F.vendor.trim() || F.notVendor); }
function leaveItem() {
  readForm();
  if (typed() && !confirm('You typed an answer but did not save it. Discard it?')) return false;
  S.review.form = freshForm(); S.review.suggest = null; S.review.parking = false; return true;
}
function nextAfterChange(removed) {
  const R = S.review;
  const list = currentList();
  R.selected = [Math.min(R.selected[0] ?? 0, Math.max(0, list.length - removed - 1))];
  R.form = freshForm(); R.suggest = null; R.parking = false;
}
async function saveTitle() {
  const R = S.review; readForm(); const F = R.form;
  if (needName()) return;
  const sel = R.selected.map(i => R.groups[i]).filter(Boolean);
  const err = $('#f-err');
  if (!F.role) { err.textContent = 'Choose a role, or park it.'; $('#f-role').focus(); return; }
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
  try {
    if (R.tab === 'condition') {
      const it = sel[0], body = { queue_ids: [it.id], scope: F.scope, reason: F.reason, decided_by: S.analyst };
      if (F.cond === '__new') { if (!F.newName.trim() || !F.newGroup) { err.textContent = 'Give the new condition a short name and a group.'; return; } body.proposed_name = F.newName; body.proposed_group = F.newGroup; }
      else if (F.cond === '__not') body.not_a_condition = true;
      else if (F.cond) body.condition_key = F.cond;
      else { err.textContent = 'Choose a condition, propose a new one, or park it.'; return; }
      await post('/api/decisions/condition', body);
      S.saved += 1; nextAfterChange(1);
      return await afterChange(`Saved: "${short(it.item, 60)}" → ${F.cond === '__new' ? F.newName.trim() + ' (proposed)' : F.cond === '__not' ? 'not a rate condition' : condOf(F.cond).label}. Next one is below.`);
    }
    if (R.tab === 'disclosure') {
      if (!F.cls) { err.textContent = 'Choose cleared or restricted.'; return; }
      if (F.cls === 'cleared' && !F.basis.trim()) { err.textContent = 'Say on what basis it is cleared.'; return; }
      await post(`/api/sets/${encodeURIComponent(S.setId)}/disclosure`, { outcome: F.cls, basis: F.cls === 'cleared' ? F.basis : '', reason: F.reason, decided_by: S.analyst });
      S.saved += 1; nextAfterChange(1);
      return await afterChange(`Saved: disclosure check ${F.cls === 'cleared' ? 'cleared (' + F.basis.trim() + ')' : 'kept restricted'}.`);
    }
    if (R.tab === 'vendor') {
      if (!F.notVendor && !F.vendor.trim()) { err.textContent = 'Name the vendor, or tick "not the vendor".'; return; }
      await post('/api/decisions/vendor', { queue_ids: [sel[0].id], vendor: F.notVendor ? null : F.vendor, not_the_vendor: !!F.notVendor, reason: F.reason, decided_by: S.analyst });
      S.saved += 1; S.vendors = null; nextAfterChange(1);
      return await afterChange(`Saved: ${sel[0].item} → ${F.notVendor ? 'not the vendor' : F.vendor.trim()}.`);
    }
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
  const sel = R.selected.map(i => currentList()[i]).filter(Boolean);
  const ids = sel.flatMap(x => x.queue_ids || [x.id]);
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
  await loadSets();
  const set = S.sets.find(s => s.root_id === S.setId);
  const shown = D.kind ? set.documents.filter(d => kindOf(d.doc_class) === D.kind) : set.documents;
  const pool = shown.length ? shown : set.documents;
  const withRows = pool.filter(d => d.rows);
  if (!D.docId || !pool.some(d => d.document_id === D.docId)) D.docId = (withRows[0] || pool[0]).document_id;
  const doc = set.documents.find(d => d.document_id === D.docId);
  D.rows = await api(`/api/documents/${D.docId}/rows`);
  let rows = D.rows;
  if (D.filter === 'counted') rows = rows.filter(r => r.counted); else if (D.filter === 'not') rows = rows.filter(r => !r.counted);
  if (D.search) rows = rows.filter(r => (r.observed_title || '').toLowerCase().includes(D.search.toLowerCase()));
  if (D.rowId && !rows.some(r => r.obs_id === D.rowId)) D.rowId = null;
  $('#setbody').innerHTML = `
    <div class="card" style="margin-bottom:16px"><div class="hd"><h2>${D.kind ? esc(KIND_LABEL[D.kind]) + ' in this contract set' : 'Documents in the set'}${D.kind ? ' <a href="#" data-clearkind="1" style="font-size:12px;font-weight:400">· show all kinds</a>' : ''}</h2><button class="btn sm" data-detail="1">${D.showDetail ? 'Hide' : 'Show'} how each was identified</button></div>
      <div class="bd flush"><table><thead><tr><th>File</th><th>Kind</th><th class="num">Pages</th><th>Contract number</th><th class="num">Rates</th>${D.showDetail ? '<th class="num">Confidence</th><th>Evidence</th><th>Text</th>' : ''}<th></th></tr></thead><tbody>
      ${pool.map(d => `<tr class="row ${d.document_id === D.docId ? 'sel' : ''}" data-doc="${esc(d.document_id)}"><td>${esc(d.filename)} <a class="open" href="/api/documents/${esc(d.document_id)}/file" target="_blank" rel="noopener" title="Open the original document">open</a></td><td>${D.kindEdit === d.document_id
        ? `<select id="k-new">${DOC_KINDS.map(([v, l]) => `<option value="${v}" ${v === d.doc_class ? 'selected' : ''}>${l}</option>`).join('')}</select> <button class="btn primary sm" data-kindsave="${esc(d.document_id)}">Save</button> <button class="btn ghost sm" data-kindedit="">Cancel</button>`
        : `${esc(KIND_LABEL[kindOf(d.doc_class)])}<span class="doc"> · ${esc((DOC_KINDS.find(k => k[0] === d.doc_class) || [0, d.doc_class.replace('_', ' ')])[1].toLowerCase())}</span> <a href="#" class="open" data-kindedit="${esc(d.document_id)}" title="Say what kind of document this really is">change</a>`}</td><td class="num">${d.pages ?? '–'}</td><td>${esc(d.contract_numbers.join(', ')) || '–'}</td><td class="num">${d.rows ? `${n(d.rows)}<span class="why">${n(d.counted)} in benchmarks</span>` : '<span class="muted">none</span>'}</td>${D.showDetail ? `<td class="num">${(d.class_confidence ?? 0).toFixed(2)}</td><td class="muted">${esc(d.evidence)}</td><td>${esc(d.readiness)}${d.extension_mismatch ? ' <span class="pill no">not what its name says</span>' : ''}</td>` : ''}<td>${d.flags.map(f => `<span class="pill wait">${esc(plainWhy(f))}</span>`).join(' ')}</td></tr>`).join('')}
      </tbody></table></div></div>
    <div class="cols">
      <div class="card"><div class="toolbar"><div class="chips">${[['all', 'all'], ['counted', 'in benchmarks'], ['not', 'held back']].map(([k, l]) => `<button class="chip ${D.filter === k ? 'active' : ''}" data-filter="${k}">${l}</button>`).join('')}<span class="muted">${n(rows.length)} of ${plural(D.rows.length, 'rate', 'rates')} in ${esc(doc.filename)}</span></div><input class="search" id="rsearch" placeholder="find a title…" value="${esc(D.search)}"></div>
        <div class="bd flush"><table><thead><tr><th>Title on the document</th><th class="num">Rate</th><th>Period</th><th>Role</th><th>Band</th><th>Status</th></tr></thead><tbody>
        ${rows.slice(0, 300).map(r => `<tr class="row ${r.obs_id === D.rowId ? 'sel' : ''}" data-row="${r.obs_id}"><td>${esc(r.observed_title)}${r.level_raw || r.location_raw ? `<span class="doc">${esc([r.level_raw, r.location_raw, r.qualifier].filter(Boolean).join(' · '))}</span>` : ''}</td><td class="num">${rate(r)}</td><td class="muted">${esc(r.period_raw || '')}</td><td>${esc(roleName(r.canonical_role_id))}</td><td>${bandPill(r)}</td><td>${statusPill(r)}</td></tr>`).join('') || '<tr><td colspan="6" class="muted">No rates match.</td></tr>'}
        </tbody></table>${rows.length > 300 ? `<div class="history">Showing the first 300 of ${n(rows.length)} rates. Use "find a title" to narrow it.</div>` : ''}</div></div>
      <div class="card panel" id="rpanel">${D.rowId ? '<div class="empty">Loading…</div>' : '<div class="empty">Click a rate to see the page it came from.</div>'}</div>
    </div>`;
  if (D.rowId) renderRowPanel();
}
async function renderRowPanel() {
  const D = S.docs;
  const o = await api(`/api/rows/${D.rowId}`);
  const pos = o.position;
  const original = `<a href="/api/documents/${o.document_id}/file${pos.page ? '#page=' + pos.page : ''}" target="_blank" rel="noopener">Open the original document${pos.page ? ' at page ' + pos.page : ''}</a>`;
  const img = pos.kind === 'pdf'
    ? `<div class="meta">Page ${pos.page} of ${esc(o.filename)}; the box is where this rate was read.</div><div class="links">${original}</div><a href="/api/rows/${o.obs_id}/page.png" target="_blank" rel="noopener"><img class="closeup" src="/api/rows/${o.obs_id}/closeup.png" alt="close-up around the row"></a><a href="/api/rows/${o.obs_id}/page.png" target="_blank" rel="noopener"><img class="pageimg" src="/api/rows/${o.obs_id}/page.png" alt="the page with the row boxed"></a>`
    : `<div class="meta">${esc(o.filename)}: a web page, so there is no page image; the table below is the position.</div><div class="links">${original}</div>`;
  const why = o.counted ? 'in benchmarks' : (o.resolution_status === 'resolved' ? 'held back: the reading was not confident enough (needs 0.90, has ' + o.extraction_confidence + ')' : 'held back: the title is not decided yet');
  $('#rpanel').innerHTML = `
    <div class="ev"><h3>${esc(o.observed_title)}</h3><div class="meta">${esc(o.vendor || '')} → ${esc(o.client || '')}</div><div id="rctx" class="tctx"><div class="quote">${esc(pos.quote || '(no quote stored)')}</div></div>${img}</div>
    <div class="ev"><h3 class="h4">What the document says</h3>${kv([['Rate', rateLine(o)], ['Period', o.period_raw], ['Location', o.location_raw], ['Level', o.level_raw], ['Condition', o.qualifier], ['Reading confidence', o.extraction_confidence]])}
      ${o.reporting_value !== null && o.reporting_currency && o.currency !== o.reporting_currency ? kv([[`In ${o.reporting_currency} (converted)`, o.reporting_value], ['Exchange rate', o.fx_rate], ['Rate date', o.fx_date], ['Rate source', o.fx_source]]) : ''}</div>
    <div class="ev"><h3 class="h4">What the system made of it</h3>${kv([['Role', o.canonical_role_id ? roleName(o.canonical_role_id) : 'not decided'], ['Band', o.twm_band ? o.twm_band.replace('_', ' / ') : (o.canonical_role_id ? 'not stated' : '')], ['Band from', o.band_source], ['Technology', o.attr_technology], ['Location', o.attr_location], ['Status', why]])}</div>
    ${o.history.length ? `<div class="history"><b>Answers given on this title</b>${o.history.map(h => `<div>${esc(h.decided_at.slice(0, 10))} ${esc(h.decided_by)}: ${esc(h.decision_json)} — ${esc(h.reason)}${h.superseded_by ? ' (replaced)' : ''}</div>`).join('')}</div>` : ''}`;
  api(`/api/rows/${o.obs_id}/table`).then(ctx => { const html = ctxTable(ctx, o.rate_as_stated); const el = $('#rctx'); if (html && el && S.docs.rowId === o.obs_id) el.innerHTML = html; }).catch(() => {});
}

/* ── terms (scoped to the set): the disclosure check first, then facts, then conditions by group ── */
const GATE = { restricted: ['no', 'Restricted'], cleared: ['ok', 'Cleared'], unchecked: ['wait', 'Not checked'] };
const SHOWN = { recorded: ['neutral', 'recorded'], to_review: ['wait', 'to review'], unnamed: ['wait', 'not yet named'], set_aside: ['neutral', 'set aside'] };
function disclosureLine(d, withLink) {
  if (!d) return '';
  const [cls, word] = GATE[d.status];
  let why;
  if (d.decided) why = `${d.decided.outcome === 'cleared' ? 'Cleared' : 'Kept restricted'} by ${esc(d.decided.decided_by)} on ${esc(d.decided.decided_at.slice(0, 10))}${d.decided.basis ? ': ' + esc(d.decided.basis.toLowerCase()) : ''}.`;
  else if (!d.read) why = 'No contract text has been read for this set, so there is nothing to check yet. Confirm with the client before it is benchmarked.';
  else if (d.status === 'restricted') why = `${d.restricting.length === 1 ? 'A clause limits' : d.restricting.length + ' clauses limit'} disclosure or use of the data. It needs your decision before this set is benchmarked or contributed.`;
  else if (d.status === 'cleared') why = `Nothing bars it, and ${d.clearing.length === 1 ? 'a clause allows' : d.clearing.length + ' clauses allow'} it (${[...new Set(d.clearing.map(c => c.label.toLowerCase()))].join(', ')}).`;
  else why = 'No disclosure or benchmarking clause was found on the pages read. Confirm with the client before it is benchmarked.';
  return `<div class="gate"><span class="pill ${cls}">Disclosure check: ${word}</span><span>${why}</span>${withLink && d.queue_ids.length && !d.decided ? '<button class="btn sm" data-goreview="disclosure">Decide →</button>' : ''}</div>`;
}
async function renderTerms() {
  const T = S.terms, sid = encodeURIComponent(S.setId);
  await loadInv();
  const d = T.data = await api(`/api/sets/${sid}/terms${T.floor != null ? '?floor=' + T.floor : ''}`);
  const c = d.counts;
  if (!c.facts && !c.conditions) {
    $('#setbody').innerHTML = `${disclosureLine(d.disclosure, true)}<div class="card"><div class="empty">The engine has read this set's rates but no contract text, so there are no facts or conditions to show. They appear once a contract, amendment or SOW in the set is read.</div></div>`;
    return;
  }
  const termRow = v => `<tr class="row ${v.term_id === T.termId ? 'sel' : ''}" data-term="${v.term_id}"><td title="${esc(v.meaning || '')}">${esc(v.label)}${v.by_analyst ? '<span class="why">named or confirmed by you</span>' : ''}</td><td>${esc(short(v.value, 130))}<span class="why">${esc(v.filename)} · page ${v.page ?? '–'}</span></td><td><span class="pill ${SHOWN[v.shown][0]}">${SHOWN[v.shown][1]}</span></td></tr>`;
  const groups = d.groups.map(g => {
    const rows = T.filter === 'review' ? g.conditions.filter(x => x.shown === 'to_review') : g.conditions;
    return rows.length ? `<tr class="grp"><td colspan="3">${g.letter} · ${esc(g.name)}<span class="n">${rows.length}</span></td></tr>${rows.map(termRow).join('')}` : '';
  }).join('');
  const factRow = f => {
    const all = T.more[f.type], vals = all ? f.values : f.values.slice(0, 3);
    return `<tr><td class="flabel">${esc(f.label)}</td><td>${vals.map(v => `<a href="#" class="fact ${v.term_id === T.termId ? 'sel' : ''}" data-term="${v.term_id}" title="${esc(v.filename)} · page ${v.page ?? ''}">${esc(short(v.value, 70))}${v.times > 1 ? ` <span class="muted">×${v.times}</span>` : ''}</a>`).join('')}${f.values.length > 3 ? `<a href="#" class="morelink" data-more="${f.type}">${all ? 'show fewer' : `+${f.values.length - 3} more`}</a>` : ''}</td></tr>`;
  };
  $('#setbody').innerHTML = `
    ${disclosureLine(d.disclosure, true)}
    ${d.summary ? `<div class="oneline"><b>In one line</b> <span class="muted">· draft wording, built only from the conditions recorded below</span><div>${esc(d.summary)}</div></div>` : ''}
    <div class="cols">
      <div>
        <div class="card" style="margin-bottom:16px"><div class="hd"><h2>Facts</h2><span class="sub">${n(c.facts)} read · click one to see it on its page</span></div><div class="bd flush"><table class="facts"><tbody>${d.facts.map(factRow).join('')}</tbody></table></div></div>
        <div class="card"><div class="toolbar"><div class="chips"><b style="font-size:14px;margin-right:4px">Conditions</b><button class="chip ${T.filter === 'all' ? 'active' : ''}" data-tfilter="all">all ${n(c.recorded + c.to_review)}</button><button class="chip ${T.filter === 'review' ? 'active' : ''}" data-tfilter="review">to review ${n(c.to_review)}</button></div>${c.unnamed ? `<button class="btn sm" data-goreview="condition">${plural(c.unnamed, 'clause', 'clauses')} not yet named: name them in Review →</button>` : ''}</div>
          <div class="bd flush"><table><thead><tr><th>Condition</th><th>What the contract says</th><th>Status</th></tr></thead><tbody>${groups || '<tr><td colspan="3" class="muted">Nothing to review at this setting.</td></tr>'}</tbody></table>
          <div class="history">A condition is shown as "to review" when the engine's confidence in its type is below <select id="t-floor">${[0.5, 0.6, 0.7, 0.75, 0.8, 0.9].map(f => `<option ${f === d.floor ? 'selected' : ''}>${f}</option>`).join('')}</select>. Changing this re-sorts the list; it rewrites nothing.${c.set_aside ? ` ${plural(c.set_aside, 'clause', 'clauses')} set aside by you as not a rate condition.` : ''}${c.named_people ? ` ${plural(c.named_people, 'named person was', 'named people were')} also read (key personnel); names stay in the client's environment.` : ''}</div></div></div>
      </div>
      <div class="card panel" id="tpanel"><div class="empty">Click a fact or a condition to see the clause on its page.</div></div>
    </div>`;
  if (T.termId) renderTermPanel();
}
async function renderTermPanel() {
  const T = S.terms, id = T.termId;
  let v;
  try { v = await api(`/api/terms/${id}${T.floor != null ? '?floor=' + T.floor : ''}`); } catch (e) { $('#tpanel').innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
  if (T.termId !== id || !$('#tpanel')) return;
  const pos = v.position, fact = v.kind === 'fact';
  const g = S.inv.groups.find(x => x.letter === v.group);
  const factLabel = ((T.data.facts.find(f => f.type === v.term_type) || {}).label) || v.term_type;
  const original = `<a href="/api/documents/${v.document_id}/file${v.page ? '#page=' + v.page : ''}" target="_blank" rel="noopener">Open the original document${v.page ? ' at page ' + v.page : ''}</a>`;
  const img = pos.kind === 'pdf'
    ? `<div class="links"><a href="/api/terms/${id}/page.png" target="_blank" rel="noopener">See the whole page</a>${original}</div><a href="/api/terms/${id}/page.png" target="_blank" rel="noopener"><img class="closeup" src="/api/terms/${id}/closeup.png" alt="the clause on its page"></a><a href="/api/terms/${id}/page.png" target="_blank" rel="noopener"><img class="pageimg" src="/api/terms/${id}/page.png" alt="the page with the clause boxed"></a>`
    : `<div class="links">${original}</div><div class="hint">${esc(pos.note || '')}</div>`;
  const act = !fact && v.shown === 'to_review'
    ? `<div class="confirmbox"><b>The engine was not sure of the type.</b> Is "${esc(v.label)}" right?<div class="btns"><button class="btn primary sm" id="t-confirm">Yes, confirm</button><select id="t-change"><option value="">or change it to…</option>${condOptions('')}</select><button class="btn sm" id="t-change-go">Save change</button></div><div class="err" id="t-err"></div></div>`
    : (v.shown === 'unnamed' ? '<div class="confirmbox">Not yet named. <button class="btn sm" data-goreview="condition">Name it in Review →</button></div>' : '');
  $('#tpanel').innerHTML = `
    <div class="ev"><div class="step">What the contract says</div><h3>${esc(fact ? factLabel : v.label)}</h3><div class="meta">${esc(v.filename)} · page ${v.page ?? '–'}</div><div class="quote">${esc(v.value)}</div>${act}</div>
    <div class="ev"><h3 class="h4">What the system made of it</h3>${kv(fact
      ? [['Fact', factLabel], ['Reading confidence', v.confidence], ['Status', SHOWN[v.shown][1]]]
      : [['Condition', v.label], ['Means', v.meaning], ['Group', g ? `${g.letter} · ${g.name}` : ''], ["The engine's note", v.note], ['Confidence in the type', v.confidence], ['Status', SHOWN[v.shown][1] + (v.by_analyst ? ' (named or confirmed by you)' : '')], ['Disclosure check', v.gate === 'restricts' ? 'this clause restricts' : (v.gate === 'clears' ? 'this clause allows' : '')]])}</div>
    <div class="ev">${img}</div>`;
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
    ${section('conditions', 'Rate conditions nominated for the inventory', ['what', 'name', 'group_name', 'quote', 'decided_by'], ['What', 'Condition', 'Group', 'The clause (stays here)', 'Decided by'], 'A proposed condition is already recorded for its own contract set. It joins the shared inventory of named conditions only after it is confirmed here. The download carries the name and group only: never the clause, the client or the vendor.')}
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
async function openSet(id) { S.setId = id; localStorage.setItem('twm.set', id); S.screen = 'set'; S.setTab = 'overview'; S.docs.kind = null; S.terms.termId = null; S.terms.filter = 'all'; S.terms.more = {}; S.review.tab = 'titles'; S.review.selected = []; S.review.form = freshForm(); S.review.suggest = null; S.docs.rowId = null; S.docs.docId = null; await renderSet(); window.scrollTo(0, 0); }

document.addEventListener('click', async e => {
  const t = e.target.closest('#who-change,[data-kind],[data-clearkind],[data-step],[data-screen],[data-open],[data-settab],[data-tab],[data-i],[data-check],[data-band],[data-cls],[data-tag],[data-alt],[data-scope],[data-doc],[data-row],[data-filter],[data-pick],[data-applied],[data-detail],[data-editname],[data-cancelname],[data-savename],[data-confirmname],[data-kindedit],[data-kindsave],[data-cond],[data-basis],[data-vendor],[data-unpark],[data-term],[data-tfilter],[data-more],[data-goreview],#t-confirm,#t-change-go,#f-record,#f-park,#f-park-go,#f-park-cancel,#f-unpark');
  if (!t) return;
  if (t.id === 'who-change') { e.preventDefault(); S.editingWho = true; showWho(); $('#analyst').focus(); return; }
  if (t.dataset.screen) { e.preventDefault(); return go(t.dataset.screen); }
  if (t.dataset.open) return openSet(t.dataset.open);
  if (t.dataset.settab) { if (S.setTab === 'review' && !leaveItem()) return; S.setTab = t.dataset.settab; return renderSet(); }
  if (t.dataset.tab) { if (!leaveItem()) return; S.review.tab = t.dataset.tab; S.review.selected = []; return renderReview(); }
  if (t.dataset.step) { const R = S.review; const list = currentList(); const next = Math.max(0, Math.min(list.length - 1, (R.selected[0] ?? 0) + (+t.dataset.step))); if (!leaveItem()) return; R.selected = [next]; await renderReview(); const row = $('#qlist tr.sel'); if (row) row.scrollIntoView({ block: 'nearest' }); return; }
  if (t.dataset.check !== undefined) { const i = +t.dataset.check; const sel = S.review.selected; readForm(); S.review.selected = t.checked ? [...sel, i].sort((a, b) => a - b) : sel.filter(x => x !== i); S.review.suggest = null; return renderReview(); }
  if (t.dataset.i !== undefined) { if (S.review.selected.length === 1 && S.review.selected[0] === +t.dataset.i) return; if (!leaveItem()) return; S.review.selected = [+t.dataset.i]; return renderReview(); }
  if (t.dataset.band !== undefined) { S.review.form.band = t.dataset.band || null; $$('#f-bands button').forEach(b => b.classList.toggle('active', b === t)); return; }
  if (t.dataset.cls) { S.review.form.cls = t.dataset.cls; $$('#f-cls button').forEach(b => b.classList.toggle('active', b === t)); if (S.review.tab === 'disclosure') { readForm(); drawPanel(); } return; }
  if (t.dataset.cond) { readForm(); S.review.form.cond = t.dataset.cond; return drawPanel(); }
  if (t.dataset.basis) { readForm(); S.review.form.basis = t.dataset.basis; return drawPanel(); }
  if (t.dataset.vendor) { readForm(); S.review.form.vendor = t.dataset.vendor; S.review.form.notVendor = false; return drawPanel(); }
  if (t.dataset.unpark) { if (needName()) return; try { await post('/api/queue/unpark', { queue_ids: [+t.dataset.unpark], decided_by: S.analyst }); await afterChange('Back on its list.'); } catch (err) { toast(err.message, false); } return; }
  if (t.dataset.goreview) { S.setTab = 'review'; S.review.tab = t.dataset.goreview; S.review.selected = []; S.review.form = freshForm(); await renderSet(); window.scrollTo(0, 0); return; }
  if (t.dataset.term) { e.preventDefault(); S.terms.termId = +t.dataset.term; $$('[data-term]').forEach(r => r.classList.toggle('sel', +r.dataset.term === S.terms.termId)); $('#tpanel').innerHTML = '<div class="empty">Loading…</div>'; return renderTermPanel(); }
  if (t.dataset.tfilter) { S.terms.filter = t.dataset.tfilter; return renderTerms(); }
  if (t.dataset.more) { e.preventDefault(); S.terms.more[t.dataset.more] = !S.terms.more[t.dataset.more]; return renderTerms(); }
  if (t.id === 't-confirm' || t.id === 't-change-go') {
    if (needName()) return;
    const key = t.id === 't-change-go' ? $('#t-change').value : null;
    if (t.id === 't-change-go' && !key) { $('#t-err').textContent = 'Choose the condition it should be.'; return; }
    try { await post(`/api/terms/${S.terms.termId}/confirm`, { condition_key: key, decided_by: S.analyst }); S.saved += 1; toast(key ? 'Changed and recorded.' : 'Confirmed.'); refreshChrome(); return renderTerms(); } catch (err) { $('#t-err').textContent = err.message; }
    return;
  }
  if (t.dataset.scope) { S.review.form.scope = t.dataset.scope; $$('#f-scope button').forEach(b => b.classList.toggle('on', b === t)); return; }
  if (t.dataset.tag !== undefined) { readForm(); const F = S.review.form; const tag = t.dataset.tag; F.tags = F.tags.includes(tag) ? F.tags.filter(x => x !== tag) : [...F.tags, tag]; F._tagq = ''; $('#f-tags').outerHTML = tagPicker().split('<div class="hint">')[0]; return; }
  if (t.dataset.alt) { readForm(); S.review.form.role = t.dataset.alt; S.review.form.fromSuggestion = true; $('#f-role').value = t.dataset.alt; return; }
  if (t.id === 'f-record') return isTitles() ? saveTitle() : saveItem();
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
  if (t.dataset.kind) { if (S.setTab === 'review' && !leaveItem()) return; S.docs.kind = t.dataset.kind; S.docs.docId = null; S.docs.rowId = null; S.setTab = 'documents'; return renderSet(); }
  if (t.dataset.clearkind) { e.preventDefault(); S.docs.kind = null; S.docs.docId = null; return renderSet(); }
  if (t.dataset.kindedit !== undefined) { e.preventDefault(); S.docs.kindEdit = t.dataset.kindedit || null; return renderDocuments(); }
  if (t.dataset.kindsave) {
    if (needName()) return;
    try { await post(`/api/documents/${t.dataset.kindsave}/kind`, { doc_class: $('#k-new').value, decided_by: S.analyst }); S.docs.kindEdit = null; S.docs.kind = null; toast('Saved. The contract set is regrouped.'); return renderSet(); } catch (err) { toast(err.message, false); }
    return;
  }
  if (e.target.closest('a.open') || e.target.closest('#k-new')) return;
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
  if (e.target.id === 'f-cond') { readForm(); drawPanel(); const el = $('#f-newname'); if (el) el.focus(); }
  if (e.target.id === 'f-notvendor') { readForm(); if (S.review.form.notVendor) { S.review.form.vendor = ''; drawPanel(); } }
  if (e.target.id === 't-floor') { S.terms.floor = +e.target.value; renderTerms(); }
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
  const list = currentList();
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
