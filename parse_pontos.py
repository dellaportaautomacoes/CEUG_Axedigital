import json, re, unicodedata
rows=json.load(open('rows_pontos.json'))
def nm(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn').lower()
QUAL={'pontos','chefes','geral','especificos','abertura','curumim','caboclos','caboclas','gerais','guias','mirim','especifico'}
_tc=lambda s:' '.join(w.capitalize() if len(w)>2 else w.lower() for w in s.split())
FIX={'Pretos':'Pretos Velhos','Velhos':'Pretos Velhos','a Grande Luz':'A Grande Luz','Malandros':'Malandro','Hino Aos 9 Orixás':'Hino aos 9 Orixás'}
tc=lambda s:FIX.get(_tc(s),_tc(s))
# páginas do sumário e capa ignoradas: começa na página 4
rows=[r for r in rows if r['pg']>=4]

toc=[]
for ln in open('jurema.txt',encoding='utf-8').read().split('\f')[1:3]:
    pass
_t=open('jurema.txt',encoding='utf-8').read().split('\f')
for chunk in _t[:3]:
    for ln in chunk.split('\n'):
        m=re.match(r'^\s*(.*?)\s*\.{3,}\s*(\d+)\s*$',ln)
        if m: toc.append((m.group(1).strip(),int(m.group(2))))
has26={r['pg'] for r in rows if r['size']==26 and r['bold']}
tocpg={}
for tt,p in toc: tocpg.setdefault(p,[]).append(tt)
last_pg=None
pts=[]; cat='Abertura e saudações'; qual=[]; ent=''; cur=None; cat_pg=None
def flush():
    global cur
    if cur and any(l.strip() for l in cur['l']):
        pts.append(cur)
    cur=None
def start(first,pg,title=None):
    global cur
    flush(); cur={'cat':cat,'qual':' '.join(qual),'ent':ent,'pg':pg,'l':[first] if first else []}
pg_titles={}
for r in rows:
    if r['size'] in (20,22) and r['bold']: pg_titles.setdefault(r['pg'],[]).append(r['t'])
seen22=set(); 
for r in rows:
    t=r['t'].strip(); pg=r['pg']
    if not t: continue
    if pg!=last_pg:
        last_pg=pg
        if pg in tocpg and pg not in has26 and pg not in {x['pg'] for x in rows if x['size'] in (20,22) and x['bold']}:
            tt=tocpg[pg][0]; parts=re.split(r'\s+[–-]\s+',tt,1); nc=tc(parts[0]) if tt.strip() else cat
            flush()
            if nc!=cat: cat=nc
            qual=[tc(parts[1])] if len(parts)>1 else []; ent=''
    if r['size'] in (20,22) and r['bold']:
        if pg not in seen22:
            seen22.add(pg); flush(); cat=tc(' '.join(pg_titles[pg])); qual=[]; ent=''
        continue
    if r['size']==26 and r['bold']:
        flush(); base=re.sub(r'^[–\-\s]+','',t); w=nm(base.split()[0]) if base.split() else ''
        if w in QUAL:
            if w=='pontos' or True: qual.append(tc(base))
        else:
            parts=re.split(r'\s*[–-]\s*',base,1); newcat=tc(parts[0])
            cat=newcat; qual=[]; ent=''
            if len(parts)>1 and parts[1]: qual=[tc(parts[1])]
        ent=''; continue
    if t.startswith('~~~~'): flush(); continue
    if re.match(r'^\d+\s*\.\s*\S',t) and r['bold']:
        start(re.sub(r'^\d+\s*\.\s*','',t),pg); continue
    if r['size']==16 and r['bold']:
        flush(); ent=tc(t) if t.isupper() else t; start(None,pg); continue
    if cur is None: start(None,pg)
    cur['l'].append(t)
flush()
# limpeza
out=[]
def tipo(s):
    s=nm(s)
    for k,v in [('subida','subida'),('chamada','chamada'),('abertura','abertura'),('saudac','saudação'),('defuma','defumação'),('firmeza','firmeza'),('pólvora','pólvora'),('polvora','pólvora'),('descarrego','descarrego'),('chefe','chefes'),('hino','hino')]:
        if k in s: return v
    return 'ponto'
for p in pts:
    ls=[re.sub(r'\s*>?\s*(\d+)\s*[xX]\s*$',lambda m:'  ('+m.group(1)+'x)',re.sub(r'^[<\s]+','',l)).replace('>','').strip() for l in p['l']]
    ls=[l for l in ls if l and not re.fullmatch(r'(\d+|Página \d+)',l)]
    if not ls: continue
    out.append({'cat':p['cat'],'sub':' › '.join(x for x in [p['qual'],p['ent']] if x),'ent':p['ent'],
      'tipo':tipo(p['cat']+' '+p['qual']+' '+p['ent']+' '+ls[0]),'pag':p['pg'],'linhas':ls})
json.dump(out,open('raw_pontos.json','w'),ensure_ascii=False,indent=0)
import collections
print(len(out)); print(collections.Counter(o['cat'] for o in out).most_common(40))
print(collections.Counter(len(o['linhas']) for o in out).most_common(8))
