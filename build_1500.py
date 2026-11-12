import json, re, unicodedata
rows=json.load(open('rows_1500.json'))
NICE={'EXÚ&POMBAGIRA':'Exu e Pombagira','PRETOSVELHOS':'Pretos Velhos','POVODOORIENTE':'Povo do Oriente','NANÃBURUQUÊ':'Nanã Buruquê','IBE':'Ibejis (Erês)','YEMANJÁ':'Iemanjá','XANGÔ':'Xangô','OGUM':'Ogum','OXALÁ':'Oxalá','OXUM':'Oxum','IANSÃ':'Iansã','BAIANOS':'Baianos','BOIADEIROS':'Boiadeiros','CIGANOS':'Ciganos','MARINHEIROS':'Marinheiros','DIVERSOS':'Diversos'}
def validtab(t): return t if t in NICE else ''
def nm(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn').lower()
def tipo(s):
    s=nm(s)
    for k,v in [('subida','subida'),('demanda','demanda'),('abertura','abertura'),('louva','louvação'),('sauda','saudação'),('chamada','chamada'),('defuma','defumação'),('polvora','descarrego'),('fechamento','encerramento'),('fim de trabalho','encerramento'),('vibra','vibração')]:
        if k in s: return v
    return 'ponto'
cat='Abertura'; qual=''; cur=None; pts=[]; lastpg=None; lasttop=None
def flush():
    global cur
    if cur and cur['l']: pts.append(cur)
    cur=None
for r in rows:
    if validtab(r['tab']): cat=NICE[r['tab']]
    t=r['t']
    key=(r['pg'],r['fr'],r['col'])
    if r['size']==12 and not t.startswith('Ø'):
        flush(); qual=re.sub(r'^A BERTURA$','Abertura',t); lasttop=None; continue
    if t.startswith('Ø'):
        flush(); h=re.sub(r'^Ø\s*','',t); h=re.sub(r'^\d+\s*\.?\s*','',h).strip()
        cur={'cat':cat,'qual':qual,'titulo':h,'pg':r['pg'],'l':[]}; lasttop=r['top']; continue
    if cur is None: cur={'cat':cat,'qual':qual,'titulo':'','pg':r['pg'],'l':[]}
    if lasttop is not None and r['top']-lasttop>16 and cur['l'] and cur['l'][-1]!='': cur['l'].append('')
    lasttop=r['top']; cur['l'].append(t)
flush()
out=[]
for p in pts:
    ls=[re.sub(r'\s+',' ',l).strip() for l in p['l']]
    while ls and ls[-1]=='': ls.pop()
    if not ls: continue
    out.append({'cat':p['cat'],'sub':p['qual'],'ent':p['titulo'].title() if p['titulo'].isupper() else p['titulo'],
      'tipo':tipo(p['qual']+' '+p['titulo']),'pag':p['pg'],'linhas':ls})
json.dump(out,open('raw_1500.json','w'),ensure_ascii=False)
import collections
print(len(out)); print(collections.Counter(o['cat'] for o in out).most_common())
print(collections.Counter(o['tipo'] for o in out))
for o in out[100:103]+out[900:902]: print(o['cat'],'|',o['sub'],'|',o['ent'],'|',o['linhas'][:3])
