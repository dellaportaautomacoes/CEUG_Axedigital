'use strict';
const $ = s => document.querySelector(s), view = $('#view');
const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const store = {
  get: (k, d) => { try { return JSON.parse(localStorage.getItem('axe_' + k)) ?? d; } catch { return d; } },
  set: (k, v) => { try { localStorage.setItem('axe_' + k, JSON.stringify(v)); } catch {} }
};
let P = [], FN = {}, outras = store.get('outras', false), guia = [], tab = 'buscar', favs = new Set(store.get('favs', [])), list = [], idx = 0, wake = null;
let q = '', catSel = null, tipoSel = '';
const hoje = () => new Date().toISOString().slice(0, 10);
let gira = store.get('gira', null);
if (!gira || gira.dia !== hoje()) gira = { dia: hoje(), linhas: [], feitos: [] };

const vis = () => P.filter(p => p.fonte === 'ceug' || p.fonte === 'recebido' || outras);
const SHORT = { terreiro: 'Apostila terreiro', t1540: '1.540 pontos', jurema: 'Jurema', recebido: 'Recebido', p3333: '3333 (OCR)' };
const ORDEM_TIPO = ['defumação', 'despacho', 'firmeza', 'saudação', 'chamada', 'louvação', 'demanda', 'magia', 'ponto', 'subida'];
const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

function item(p, extra = '') {
  return `<div class="item ${extra}" data-id="${p.id}"><div class="t"><b>${esc(p.titulo)}</b>
  <small>${esc(p.cat)}${p.ent ? ' · ' + esc(p.ent) : ''} · ${p.tipo}${p.fonte !== 'ceug' ? ' · <i>' + SHORT[p.fonte] + '</i>' : ''}</small></div>
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
      for (const p of vis()) {
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
      : `<p class="muted">${vis().length} pontos disponíveis offline${outras ? ' (todas as fontes)' : ' (apostila do CEUG)'}. Digite parte do nome, da entidade ou de um verso.</p>`;
    bindList(r);
  };
  $('#q').oninput = e => { q = e.target.value; run(); };
  run();
}

function cats() {
  if (!catSel) {
    const grupos = {};
    vis().forEach(p => { ((grupos[p.grupo] ||= {})[p.cat] ||= 0); grupos[p.grupo][p.cat]++; });
    view.innerHTML = Object.entries(grupos).map(([g, c]) => `<h3>${g}</h3><div class="chips">` +
      Object.entries(c).map(([n, k]) => `<button class="chip" data-cat="${esc(n)}">${esc(n)} (${k})</button>`).join('') + '</div>').join('');
    view.querySelectorAll('[data-cat]').forEach(b => b.onclick = () => { catSel = b.dataset.cat; tipoSel = ''; render(); });
    return;
  }
  const all = vis().filter(p => p.cat === catSel);
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
  const ab = vis().filter(p => p.grupo === 'Abertura' && p.fonte === 'ceug');
  const rest = gira.linhas.flatMap(c => vis().filter(p => p.cat === c)
    .sort((a, b) => ORDEM_TIPO.indexOf(a.tipo) - ORDEM_TIPO.indexOf(b.tipo)));
  return [...ab, ...rest];
}
function giraView() {
  const opts = [...new Set(vis().filter(p => p.grupo === 'Orixás' || p.grupo === 'Linhas de trabalho').map(p => p.cat))];
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

function toques() {
  view.innerHTML = '<h3>Guia Prático de Toques</h3><p class="muted">Texto importado por OCR do guia em PDF; pode conter pequenos erros.</p>' +
    guia.slice(1).filter(Boolean).map(t => `<div class="item" style="display:block;cursor:default"><div style="white-space:pre-wrap">${esc(t)}</div></div>`).join('');
}

/* ---------- nuvem (Supabase): login, envio e aprovação ---------- */
const sb = (window.supabase && window.AXE_CFG) ? window.supabase.createClient(window.AXE_CFG.url, window.AXE_CFG.key) : null;
let user = null, papel = 'membro', meus = [], pend = [], msg = '';
const toPonto = r => {
  const g = (P.find(p => p.cat === r.cat && p.fonte !== 'recebido') || {}).grupo || 'Recebidos';
  const texto = r.texto, titulo = (r.titulo || texto.split('\n')[0]).slice(0, 70);
  return { id: 100000 + r.id, fonte: 'recebido', grupo: g, cat: r.cat || 'Recebidos', sub: r.autor ? 'Recebido por ' + r.autor : 'Recebido', ent: r.ent || '', tipo: r.tipo || 'ponto',
    toque: '', pag: 0, titulo, texto, revisar: false, _t: norm(titulo), _e: norm((r.cat || '') + ' ' + (r.ent || '')), _x: norm(texto) };
};
function mergeRec(rows) { P = P.filter(p => p.fonte !== 'recebido').concat((rows || []).map(toPonto)); }
async function loadCloud() {
  if (!sb || !user) { mergeRec([]); return; }
  const a = await sb.from('pontos_enviados').select('*').eq('status', 'aprovado').order('id');
  if (!a.error) store.set('rec', a.data);
  mergeRec(a.error ? store.get('rec', []) : a.data);
  const m = await sb.from('pontos_enviados').select('*').eq('user_id', user.id).order('id', { ascending: false });
  meus = m.data || [];
  if (papel === 'admin') { const q = await sb.from('pontos_enviados').select('*').eq('status', 'pendente').order('id'); pend = q.data || []; }
}
async function setUser(u) {
  user = u || null; papel = 'membro';
  if (user) { const r = await sb.from('perfis').select('papel').eq('user_id', user.id).maybeSingle(); papel = (r.data || {}).papel || 'membro'; }
  await loadCloud(); $('#btnUser').textContent = user ? '👤✔' : '👤';
  if (tab === 'inserir') render();
}
async function decidir(id, status) { await sb.from('pontos_enviados').update({ status }).eq('id', id); await loadCloud(); render(); }
function inserir() {
  if (!sb) { view.innerHTML = '<p class="muted">Recurso indisponível (biblioteca não carregou).</p>'; return; }
  if (!user) {
    view.innerHTML = `<h3>Entrar</h3><p class="muted">Entre para enviar pontos recebidos e ver os pontos aprovados pelos responsáveis.</p>
    <input type="email" id="em" placeholder="e-mail"><input type="password" id="pw" placeholder="senha (mín. 6 caracteres)">
    <div class="chips"><button class="chip on" id="bIn">Entrar</button><button class="chip" id="bUp">Criar conta</button></div><p class="muted" id="mm">${esc(msg)}</p>`;
    const go = async fn => { msg = ''; const r = await fn($('#em').value.trim(), $('#pw').value); msg = r.error ? 'Erro: ' + r.error.message : (r.data.session ? '' : 'Conta criada. Confirme pelo e-mail que você recebeu e depois entre.'); $('#mm').textContent = msg; };
    $('#bIn').onclick = () => go((email, password) => sb.auth.signInWithPassword({ email, password }));
    $('#bUp').onclick = () => go((email, password) => sb.auth.signUp({ email, password }));
    return;
  }
  const cats = [...new Set(P.map(p => p.cat))].sort();
  const st = { pendente: '⏳ aguardando', aprovado: '✅ aprovado', rejeitado: '❌ não aprovado' };
  view.innerHTML = `<h3>Inserir ponto recebido</h3>
  <p class="muted">Será enviado para aprovação do responsável do CEUG antes de aparecer para todos.</p>
  <input id="fT" placeholder="Título (opcional)"><textarea id="fX" rows="7" placeholder="Letra do ponto (uma linha por verso)"></textarea>
  <input id="fC" list="dl" placeholder="Orixá ou linha (ex.: Oxóssi, Pretos-Velhos)"><datalist id="dl">${cats.map(c => `<option value="${esc(c)}">`).join('')}</datalist>
  <input id="fE" placeholder="Entidade (opcional)"><input id="fA" placeholder="Recebido por (nome)">
  <select id="fP">${['ponto', 'chamada', 'louvação', 'subida', 'demanda', 'saudação', 'firmeza'].map(t => `<option>${t}</option>`).join('')}</select>
  <div class="chips"><button class="chip on" id="fS">Enviar para aprovação</button><button class="chip" id="bOut">Sair</button></div><p class="muted" id="mm">${esc(msg)}</p>
  ${papel === 'admin' ? `<h3>Pendentes para aprovar (${pend.length})</h3>` + pend.map(r => `<div class="item" style="display:block;cursor:default"><b>${esc(r.titulo || r.texto.split('\n')[0])}</b><small>${esc(r.cat || '')} · ${esc(r.autor || '')}</small><pre style="white-space:pre-wrap;margin:6px 0">${esc(r.texto)}</pre><button class="chip on" data-ok="${r.id}">Aprovar</button> <button class="chip" data-no="${r.id}">Rejeitar</button></div>`).join('') : ''}
  <h3>Meus envios</h3>` + (meus.length ? meus.map(r => `<div class="item" style="cursor:default"><div class="t"><b>${esc(r.titulo || r.texto.split('\n')[0])}</b><small>${st[r.status]}</small></div></div>`).join('') : '<p class="muted">Nada enviado ainda.</p>');
  $('#bOut').onclick = () => sb.auth.signOut();
  $('#fS').onclick = async () => {
    const texto = $('#fX').value.trim(); if (!texto) { $('#mm').textContent = 'Escreva a letra do ponto.'; return; }
    const r = await sb.from('pontos_enviados').insert({ titulo: $('#fT').value.trim() || null, texto, cat: $('#fC').value.trim() || null, ent: $('#fE').value.trim() || null, autor: $('#fA').value.trim() || null, tipo: $('#fP').value });
    msg = r.error ? 'Erro: ' + r.error.message : 'Enviado! Aguarde a aprovação.'; await loadCloud(); render();
  };
  view.querySelectorAll('[data-ok]').forEach(b => b.onclick = () => decidir(+b.dataset.ok, 'aprovado'));
  view.querySelectorAll('[data-no]').forEach(b => b.onclick = () => decidir(+b.dataset.no, 'rejeitado'));
}
function render() {
  document.querySelectorAll('nav button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  ({ buscar, cats, gira: giraView, favs: favsView, toques, inserir })[tab]();
}

/* leitor */
function openReader() {
  const p = list[idx]; if (!p) return;
  $('#rTitle').textContent = p.titulo;
  $('#rPath').textContent = `${p.cat}${p.sub ? ' › ' + p.sub : ''}${p.toque ? ' · toque: ' + p.toque : ''} · pág. ${p.pag} · ${FN[p.fonte] || ''}`;
  $('#rText').textContent = p.texto + (p.revisar ? '\n\n⚠ Conferir: texto importado automaticamente, pode ter erros.' : '');
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

/* fontes */
const setSrc = () => { $('#btnSrc').textContent = outras ? 'Todas as fontes' : 'Só CEUG'; };
$('#btnSrc').onclick = () => { outras = !outras; store.set('outras', outras); setSrc(); catSel = null; render(); };
setSrc();
/* tema e abas */
const root = document.documentElement;
if (store.get('dark', matchMedia('(prefers-color-scheme: dark)').matches)) root.setAttribute('data-dark', '');
$('#btnDark').onclick = () => { root.toggleAttribute('data-dark'); store.set('dark', root.hasAttribute('data-dark')); };
document.querySelectorAll('nav button').forEach(b => b.onclick = () => { tab = b.dataset.tab; if (tab === 'cats') catSel = null; render(); });

/* início */
$('#btnUser').onclick = () => { tab = 'inserir'; render(); };
Promise.all([fetch('data/pontos.json').then(r => r.json()), fetch('data/guia.json').then(r => r.json())]).then(([d, g]) => {
  guia = g; d.fontes.forEach(f => FN[f.id] = f.nome); FN.recebido = 'Pontos recebidos (aprovados)';
  P = d.pontos.map(p => ({ ...p, _t: norm(p.titulo), _e: norm(p.cat + ' ' + p.ent + ' ' + p.sub), _x: norm(p.texto) }));
  render();
  if (sb) { sb.auth.getSession().then(r => setUser(r.data.session && r.data.session.user)); sb.auth.onAuthStateChange((_e, s) => { if ((s && s.user && s.user.id) !== (user && user.id)) setUser(s && s.user); }); }
}).catch(() => { view.innerHTML = '<p>Não foi possível carregar os pontos.</p>'; });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
