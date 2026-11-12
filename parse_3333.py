import re, glob, json, unicodedata, difflib, collections
def nm(s): return re.sub(r'[^a-z0-9]','',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn'))
EXU="Firmeza|Chamada|Louvação|Exu Arranca Toco|Exu Bará|Exu Brasa|Exu Calunga|Exu Calunguinha do Mar|Exu Campina|Exu da Capa Preta|Exu Caveira|Exu do Carangola|Exu do Cemitério|Exu Corta-Corta|Exu Curadô|Exu do Fogo|Exu Ganga|Exu Gargalhada|Exu Gira Mundo|Exu João Caveira|Exu Kaminaloá|Exu Lalu|Exu do Lodo|Exu Lonan|Exu Lúcifer|Exu Malê|Exu Mangueira|Exu Marabá|Exu Marabô|Exu Marabô Toquinho|Exu Maré|Exu das Matas|Exu da Meia-Noite|Exu Mirim|Exu Morcego|Exu Mulambo|Exu Pagão|Exu Pedra Negra|Exu Pemba|Exu Pimenta|Exu Pinga Fogo|Exu Poeira|Exu Quebra Galho|Exu Quirombô|Exu Rei|Rei das Sete Encruzilhadas|Exu dos Rios|Exu Serapião|Exu Sete Catacumbas|Exu Sete Chaves|Exu Sete Covas|Exu Sete Cruzes|Exu Sete Encruzas|Exu Sete Montanhas|Exu Sete Pedras|Exu Sete Poeiras|Exu Sete Portas|Exu Sete Porteiras|Exu Sete Sombras|Exu Tatá Caveira|Exu Tira Teima|Exu Tiririf|Exu Tirirí|Exu Toco Preto|Exu Toquinho|Exu Tranca Gira|Exu Tranca Ruas|Tranca Ruas das Almas|Exu Tranca Tudo|Exu Tronqueira|Exu Veludo|Exu dos Ventos|Exu Vira Mundo|Exu Zé Pilintra|Despedida".split('|')
PG="Chamada|Maria Mulambo|Maria Padilha|Maria Padilha dos 7 Cruzeiros da Calunga|Maria Quitéria|Pomba Gira|Pomba Gira das Almas|Pomba Gira de Calunga|Pomba Gira Cigana|Pomba Gira Menina|Pomba Gira da Praia|Pomba Gira Rainha|Pomba Gira Rainha do Cruzeiro|Pomba Gira do Cruzeiro|Pomba Gira Rainha da Encruzilhada|Pombo Gira-Angola|Pomba Gira Rainha das Sete Encruzilhadas|Subida".split('|')
ALL={nm(x):x for x in EXU+PG}
pages={}; allp=[]
for f in sorted(glob.glob('ocr3333/p-*_L.png.out.txt')):
    k=f.split('/')[-1][:4]; allp.append((k,open(f).read()+'\n'+open(f.replace('_L','_R')).read()))
sig=lambda t: nm(t)[:700]
keep=[]
for i,(k,t) in enumerate(allp):
    dup=any(difflib.SequenceMatcher(None,sig(t),sig(t2)).quick_ratio()>0.9 and difflib.SequenceMatcher(None,sig(t),sig(t2)).ratio()>0.8 for k2,t2 in allp[i+1:i+30])
    if dup: print('duplicada descartada',k)
    else: keep.append((k,t))
for i,(k,t) in enumerate(keep): pages[i]=t
print(sorted(pages)[:50])
cat='Exu'; sec=''; cur=None; pts=[]
def flush():
    global cur
    if cur and cur['l']: pts.append(cur)
    cur=None
def clean(l):
    l=re.sub(r'^[“”"‘’\'—\-_»«\s]+','',l); l=re.sub(r'\s+[|—_h¥]{1,2}$','',l.rstrip()); return l.strip()
SEP=re.compile(r'^[\W_xX*¥%0]{1,4}$|^[xX*¥]\s?%?$')
stop=False
for pn in sorted(pages):
    if stop: break
    for ln in pages[pn].split('\n'):
        s=ln.strip()
        if not s: continue
        if re.search(r'PUNTOS RISCADOS',s,re.I) and len(s)<60: stop=True; break
        if re.search(r'Exu y Pomba|Cantados y|Riscados|Fomba-|Funtos|^\d{1,2}$',s,re.I): continue
        if re.search(r'PUNTOS CANTADOS DE POMBA',s,re.I): flush(); cat='Pombagira'; sec=''; continue
        if re.search(r'PUNTOS CANTADOS DE EXU',s,re.I): flush(); cat='Exu'; continue
        if SEP.match(s): flush_stanza=True; 
        if SEP.match(s):
            if cur and cur['l']: pts.append(cur); cur={'cat':cat,'ent':cur['ent'],'pg':pn,'l':[]}
            continue
        c=clean(s); n=nm(c)
        best=None
        if 2<=len(c.split())<=8 or n in ALL:
            cand=difflib.get_close_matches(n,list(ALL),1,0.86)
            if cand and len(c)<=45 and not c.endswith(','): best=ALL[cand[0]]
        if best and (cur is None or len(cur['l'])>=1 or True) and not (cur and cur['l'] and len(cur['l'])<1):
            # evita confundir verso curto com título: título só no início de bloco ou após separador
            if cur is None or not cur['l'] or True:
                flush(); cur={'cat':cat,'ent':best,'pg':pn,'l':[]}; continue
        if cur is None: cur={'cat':cat,'ent':'','pg':pn,'l':[]}
        cur['l'].append(c)
flush()
out=[{'cat':p['cat'],'sub':'Pontos cantados','ent':p['ent'],'tipo':('chamada' if p['ent']=='Chamada' else 'subida' if p['ent'] in('Subida','Despedida') else 'louvação' if p['ent']=='Louvação' else 'firmeza' if p['ent']=='Firmeza' else 'ponto'),'pag':p['pg'],'linhas':p['l']} for p in pts if len(p['l'])>=1]
json.dump(out,open('raw_3333.json','w'),ensure_ascii=False)
print(len(out)); print(collections.Counter(o['ent'] for o in out).most_common(15))
for o in out[30:34]: print(o['ent'],o['linhas'])
