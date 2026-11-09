'use strict';
const $ = s => document.querySelector(s), view = $('#view');
const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const store = {
  get: (k, d) => { try { return JSON.parse(localStorage.getItem('axe_' + k)) ?? d; } catch { return d; } },
  set: (k, v) => { try { localStorage.setItem('axe_' + k, JSON.stringify(v)); } catch {} }
};
let P = [], tab = 'buscar', favs = new Set(store.get('favs', [])), list = [], idx = 0, wake = null;
let q = '', catSel = null, tipoSel = '';
const hoje = () => new Date().toISOString().slice(0, 10);
let gira = store.get('gira', null);
if (!gira || gira.dia !== hoje()) gira = { dia: hoje(), linhas: [], feitos: [] };

const ORDEM_TIPO = ['defumação', 'despacho', 'firmeza', 'saudação', 'chamada', 'louvação', 'demanda', 'magia', 'ponto', 'subida'];
const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

function item(p, extra = '') {
  return `<div class="item ${extra}" data-id="${p.id}"><div class="t"><b>${esc(p.titulo)}</b>
  <small>${esc(p.cat)}${p.ent ? ' · ' + esc(p.ent) : ''} · ${p.tipo}</small></div>
  <button class="star" data-fav="${p.id}">${favs.has(p.id) ? '★' : '☆'}</button></div>`;
}
function bindList(arr) {
  view.querySelectorAll('.item').forEach(el => el.onclick = e => {
    if (e.target.dataset.fav) return;
    list = arr; idx = arr.findIndex(p => p.id == el.dataset.id); openReader();
  });
  view.querySelectorAll('[data-fav]').forEach(b => b.onclick = e => {
    e.stopPropagation(); toggleFav(+b.dataset.fav); b.textContent = favs.has(+b.dataset.fav) ? '★' : '☆';
    if (tab === 'favs') render();
  });
}
function toggleFav(id) { favs.has(id) ? favs.delete(id) : favs.add(id); store.set('favs', [...favs]); }

function buscar() {
  view.innerHTML = `<input type="search" id="q" placeholder="Buscar ponto, entidade ou trecho…" value="${esc(q)}"><div id="res"></div>`;
  const run = () => {
    const toks = norm(q).split(/\s+/).filter(Boolean);
    let r = [];
    if (toks.length) {
      for (const p of P) {
        let sc = 0, ok = true;
        for (const t of toks) {
          let s = 0;
          if (p._t.includes(t)) s += 5;
          if (p._e.includes(t)) s += 3;
          if (p._x.includes(t)) s += 1;
          if (!s) { ok = false; break; } sc += s;
        }
        if (ok) r.push([sc, p]);
      }
      r.sort((a, b) => b[0] - a[0]);
      r = r.slice(0, 80).map(x => x[1]);
    }
    $('#res').innerHTML = toks.length
      ? (r.length ? r.map(p => item(p)).join('') : '<p class="muted">Nada encontrado.</p>')
      : `<p class="muted">${P.length} pontos disponíveis offline. Digite parte do nome, da entidade ou de um verso.</p>`;
    bindList(r);
  };
  $('#q').oninput = e => { q = e.target.value; run(); };
  run();
}

function cats() {
  if (!catSel) {
    const grupos = {};
    P.forEach(p => { ((grupos[p.grupo] ||= {})[p.cat] ||= 0); grupos[p.grupo][p.cat]++; });
    view.innerHTML = Object.entries(grupos).map(([g, c]) => `<h3>${g}</h3><div class="chips">` +
      Object.entries(c).map(([n, k]) => `<button class="chip" data-cat="${esc(n)}">${esc(n)} (${k})</button>`).join('') + '</div>').join('');
    view.querySelectorAll('[data-cat]').forEach(b => b.onclick = () => { catSel = b.dataset.cat; tipoSel = ''; render(); });
    return;
  }
  const all = P.filter(p => p.cat === catSel);
  const tipos = [...new Set(all.map(p => p.tipo))].sort((a, b) => ORDEM_TIPO.indexOf(a) - ORDEM_TIPO.indexOf(b));
  const arr = all.filter(p => !tipoSel || p.tipo === tipoSel);
  view.innerHTML = `<button class="chip" id="back">← Categorias</button><h3>${esc(catSel)}</h3>
  <div class="chips"><button class="chip ${tipoSel ? '' : 'on'}" data-tp="">Todos</button>` +
    tipos.map(t => `<button class="chip ${tipoSel === t ? 'on' : ''}" data-tp="${t}">${t}</button>`).join('') + '</div>' +
    arr.map(p => item(p)).join('');
  $('#back').onclick = () => { catSel = null; render(); };
  view.querySelectorAll('[data-tp]').forEach(b => b.onclick = () => { tipoSel = b.dataset.tp; render(); });
  bindList(arr);
}

function favsView() {
  const arr = P.filter(p => favs.has(p.id));
  view.innerHTML = arr.length ? arr.map(p => item(p)).join('') : '<p class="muted">Toque na ☆ de um ponto para guardá-lo aqui.</p>';
  bindList(arr);
}

function giraSeq() {
  const ab = P.filter(p => p.grupo === 'Abertura');
  const rest = gira.linhas.flatMap(c => P.filter(p => p.cat === c)
    .sort((a, b) => ORDEM_TIPO.indexOf(a.tipo) - ORDEM_TIPO.indexOf(b.tipo)));
  return [...ab, ...rest];
}
function giraView() {
  const opts = [...new Set(P.filter(p => p.grupo === 'Orixás' || p.grupo === 'Linhas de trabalho').map(p => p.cat))];
  const seq = giraSeq();
  view.innerHTML = `<h3>Gira de Hoje · ${new Date().toLocaleDateString('pt-BR')}</h3>
  <p class="muted">Escolha as linhas de hoje. A abertura entra automaticamente; marque ✔ conforme canta (toque longo no ponto).</p>
  <div class="chips">${opts.map(o => `<button class="chip ${gira.linhas.includes(o) ? 'on' : ''}" data-l="${esc(o)}">${esc(o)}</button>`).join('')}</div>
  <div class="chips"><button class="chip" id="gReset">Limpar gira</button></div>` +
    seq.map(p => item(p, gira.feitos.includes(p.id) ? 'done' : '')).join('');
  view.querySelectorAll('[data-l]').forEach(b => b.onclick = () => {
    const l = b.dataset.l; gira.linhas = gira.linhas.includes(l) ? gira.linhas.filter(x => x !== l) : [...gira.linhas, l];
    store.set('gira', gira); render();
  });
  $('#gReset').onclick = () => { gira = { dia: hoje(), linhas: [], feitos: [] }; store.set('gira', gira); render(); };
  bindList(seq);
  view.querySelectorAll('.item').forEach(el => {
    let t; const id = +el.dataset.id;
    const mark = () => { gira.feitos = gira.feitos.includes(id) ? gira.feitos.filter(x => x !== id) : [...gira.feitos, id]; store.set('gira', gira); el.classList.toggle('done'); };
    el.addEventListener('pointerdown', () => t = setTimeout(() => { t = 'L'; mark(); }, 600));
    ['pointerup', 'pointerleave', 'pointermove'].forEach(ev => el.addEventListener(ev, () => { if (t !== 'L') clearTimeout(t); }));
    el.addEventListener('click', e => { if (t === 'L') { e.stopImmediatePropagation(); t = null; } }, true);
  });
}

function render() {
  document.querySelectorAll('nav button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  ({ buscar, cats, gira: giraView, favs: favsView })[tab]();
}

/* leitor */
function openReader() {
  const p = list[idx]; if (!p) return;
  $('#rTitle').textContent = p.titulo;
  $('#rPath').textContent = `${p.cat}${p.sub ? ' › ' + p.sub : ''}${p.toque ? ' · toque: ' + p.toque : ''} · pág. ${p.pag}`;
  $('#rText').textContent = p.texto;
  $('#rFav').textContent = favs.has(p.id) ? '★' : '☆';
  $('#rPrev').disabled = idx <= 0; $('#rNext').disabled = idx >= list.length - 1;
  $('#reader').hidden = false; $('.rbody').scrollTop = 0;
  if (navigator.wakeLock && !wake) navigator.wakeLock.request('screen').then(w => wake = w).catch(() => {});
}
function closeReader() { $('#reader').hidden = true; if (wake) { wake.release(); wake = null; } render(); }
let fs = store.get('fs', 22);
const setFs = n => { fs = Math.max(14, Math.min(48, n)); document.documentElement.style.setProperty('--fs', fs + 'px'); store.set('fs', fs); };
setFs(fs);
$('#rClose').onclick = closeReader;
$('#rPlus').onclick = () => setFs(fs + 2); $('#rMinus').onclick = () => setFs(fs - 2);
$('#rPrev').onclick = () => { idx--; openReader(); }; $('#rNext').onclick = () => { idx++; openReader(); };
$('#rFav').onclick = () => { toggleFav(list[idx].id); openReader(); };
document.addEventListener('keydown', e => {
  if ($('#reader').hidden) return;
  if (e.key === 'Escape') closeReader();
  if (e.key === 'ArrowRight' && idx < list.length - 1) { idx++; openReader(); }
  if (e.key === 'ArrowLeft' && idx > 0) { idx--; openReader(); }
});

/* tema e abas */
const root = document.documentElement;
if (store.get('dark', matchMedia('(prefers-color-scheme: dark)').matches)) root.setAttribute('data-dark', '');
$('#btnDark').onclick = () => { root.toggleAttribute('data-dark'); store.set('dark', root.hasAttribute('data-dark')); };
document.querySelectorAll('nav button').forEach(b => b.onclick = () => { tab = b.dataset.tab; if (tab === 'cats') catSel = null; render(); });

/* início */
fetch('data/pontos.json').then(r => r.json()).then(d => {
  P = d.pontos.map(p => ({ ...p, _t: norm(p.titulo), _e: norm(p.cat + ' ' + p.ent + ' ' + p.sub), _x: norm(p.texto) }));
  render();
}).catch(() => { view.innerHTML = '<p>Não foi possível carregar os pontos.</p>'; });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
