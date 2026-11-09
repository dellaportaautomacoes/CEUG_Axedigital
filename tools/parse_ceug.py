import re, json, unicodedata
txt = open('tools/ceug.txt', encoding='utf-8').read()
pages = txt.split('\f')
def norm(s):
    s = unicodedata.normalize('NFD', s)
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower())

# --- sumário
toc = []
body_start = None
for i, p in enumerate(pages):
    if re.search(r'P\s*[áa]\s*g\s*i\s*n\s*a\s*\|\s*1\s*$', p.strip().split('\n')[0] if p.strip() else ''):
        body_start = i; break
for p in pages[:body_start]:
    for ln in p.split('\n'):
        m = re.match(r'^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*\.{3,}\s*(\d+)\s*$', ln)
        if m: toc.append((m.group(1), m.group(2).strip(), int(m.group(3))))
print('TOC entries', len(toc), 'body_start page idx', body_start)

# --- linhas do corpo com página
lines = []
for p in pages[body_start:]:
    ps = p.split('\n')
    pg = None
    for ln in ps:
        m = re.match(r'^\s*P\s*[áa]\s*g\s*i\s*n\s*a\s*\|\s*(\d+)\s*$', ln)
        if m: pg = int(m.group(1)); continue
        lines.append((pg, ln.rstrip()))
# fix None page (herda)
last = 1
for i,(pg,ln) in enumerate(lines):
    if pg is None: lines[i] = (last, ln)
    else: last = pg

# --- localizar títulos na ordem
pos = []; cur = 0; missing = []
for num, title, pg in toc:
    key = norm(title)[:10]
    found = None
    for j in range(cur, len(lines)):
        m = re.match(r'^\s*' + re.escape(num) + r'\s+(\S.*)$', lines[j][1])
        if m and norm(m.group(1)).startswith(key[:min(len(key),8)]):
            found = (j, m.group(1)); break
    if found:
        pos.append((found[0], num, title, found[1])); cur = found[0] + 1
    else:
        missing.append((num, title))
print('encontrados', len(pos), 'faltando', missing[:20])

def tipo_de(path):
    t = ' '.join(path).lower()
    for k, v in [('subida','subida'),('chamada','chamada'),('louva','louvação'),('sauda','saudação'),
                 ('demanda','demanda'),('magia','magia'),('defuma','defumação'),('batiz','batizado'),
                 ('firmeza','firmeza'),('despach','despacho')]:
        if k in t: return v
    return 'ponto'

def clean_block(blk):
    out = []
    for ln in blk:
        s = ln.rstrip()
        m = re.match(r'^(.*?\S)\s{3,}(\[?\s*(?:\d+\s*x|repetir|bis)\s*\]?)\s*$', s, re.I)
        if m:
            s = m.group(1) + '  (' + re.sub(r'[\[\]\s]', '', m.group(2)).lower() + ')'
        out.append(s)
    ind = min((len(l) - len(l.lstrip()) for l in out if l.strip()), default=0)
    out = [re.sub(r'\s+', ' ', l[ind:]).strip() if True else l for l in out]
    # marcador "2x" sozinho na linha: anexa à anterior
    res = []
    for l in out:
        if re.fullmatch(r'\[?\d+x\]?', l, re.I) and res:
            res[-1] += '  (' + l.strip('[]').lower() + ')'
        else: res.append(l)
    return res

points = []; sections = []
stack = {}
for k, (j, num, title, rest) in enumerate(pos):
    end = pos[k+1][0] if k+1 < len(pos) else len(lines)
    level = num.count('.') + 1
    stack = {l: t for l, t in stack.items() if l < level}
    stack[level] = title
    path = [stack[l] for l in sorted(stack)]
    toque = rest[len(title):].strip() if norm(rest).startswith(norm(title)[:8]) and len(rest) > len(title) else ''
    sections.append({'num': num, 'title': title, 'level': level, 'path': path, 'toque': toque})
    seg = lines[j+1:end]
    # divide em blocos por 2+ linhas em branco (ou virada de página com bloco aberto)
    blocks = []; cur_b = []; blank = 0; pg0 = None; lastpg = None; blank_prev = 0; joined = False
    for pg, ln in seg:
        if not ln.strip():
            blank += 1
            if pg == lastpg: blank_prev += 1
            continue
        cont = False
        if cur_b and pg != lastpg and blank_prev == 0:
            cont = True   # página encheu sem linha em branco: ponto continua
        if blank >= 1 and cur_b and not cont:
            blocks.append((pg0, cur_b, joined)); cur_b = []; joined = False
        if cont: joined = True
        if not cur_b: pg0 = pg
        cur_b.append(ln); blank = 0; blank_prev = 0; lastpg = pg
    if cur_b: blocks.append((pg0, cur_b, joined))
    for n, (pg, b, jn) in enumerate(blocks):
        txt_lines = clean_block(b)
        if not any(txt_lines): continue
        points.append({'num': num, 'path': path, 'tipo': tipo_de(path), 'toque': toque, 'pagina': pg, 'linhas': txt_lines, 'revisar': jn})
json.dump({'sections': sections, 'points': points}, open('tools/raw_ceug.json','w'), ensure_ascii=False, indent=1)
print('seções', len(sections), 'blocos', len(points))
from collections import Counter
print(Counter(len(p['linhas']) for p in points).most_common(8))
