"""Une todas as fontes em data/pontos.json (CEUG = oficial). Rodar na pasta do projeto, com os raw_*.json em tools/."""
import json, re, unicodedata, os
T = os.path.dirname(os.path.abspath(__file__))
def nm(s): return re.sub(r'[^a-z0-9]','',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn'))
FONTES = [
 {'id':'ceug','nome':'Apostila CEUG v2.0 (2022)','oficial':True,'ocr':False},
 {'id':'terreiro','nome':'Apostila de Pontos (pontos.pdf)','oficial':False,'ocr':False},
 {'id':'t1540','nome':'1.540 Pontos Cantados (Tenda Caboclo Sete Cachoeiras)','oficial':False,'ocr':False},
 {'id':'jurema','nome':'Pontos de Jurema – Mestres','oficial':False,'ocr':False},
 {'id':'p3333','nome':'3333 Pontos – Exu e Pomba-Gira (Pallas) · OCR','oficial':False,'ocr':True},
]
MAP = {'Exu':'Exus','Exu e Pombagira':'Exus','Pombagira':'Pombas-Giras','Pombagiras':'Pombas-Giras','Pretos Velhos':'Pretos-Velhos',
 'Baiano':'Baianos / Cangaceiros / Zé-Pilintra','Baianos':'Baianos / Cangaceiros / Zé-Pilintra','Cangaço':'Baianos / Cangaceiros / Zé-Pilintra','Malandro':'Baianos / Cangaceiros / Zé-Pilintra',
 'Boiadeiro':'Boiadeiros','Oriente':'Povo do Oriente / Ciganos / Esquimós / Povo Chinês','Povo do Oriente':'Povo do Oriente / Ciganos / Esquimós / Povo Chinês','Ciganos':'Povo do Oriente / Ciganos / Esquimós / Povo Chinês',
 'Erês':'Cosme e Damião','Ibejis (Erês)':'Cosme e Damião','Nanã':'Nanã Buruquê','Omolu':'Omolu / Obaluaê','Yabas':'Yabás','Abertura':'Abertura da Gira',
 'Diversos':'Pontos Diversos','Abertura Quimbanda':'Abertura Quimbanda'}
ABERT = {'Abertura da Gira','Abertura dos Trabalhos','Preces de Abertura','Abertura das Cortinas','Hino da Umbanda','Anjo da Guarda','Engoma de Ogan Kaian','Hino aos 9 Orixás','A Grande Luz','Saudação às Sete Linhas','Abertura Quimbanda'}
ORIX = {'Oxóssi','Ogum','Cosme e Damião','Xangô','Iemanjá','Iansã','Omolu / Obaluaê','Oxalá','Oxum','Nanã Buruquê','Oxumaré','Tempo / Oyá-Tempo','Ossaim','Yabás'}
DIVERSOS = {'Pontos Diversos','Saudações','Descarrego','Obi','Ocasiões Especiais'}
def grupo(cat):
    if cat=='Jurema': return 'Jurema'
    if cat in ABERT: return 'Abertura'
    if cat in ORIX: return 'Orixás'
    if cat in DIVERSOS: return 'Diversos'
    return 'Linhas de trabalho'
def load(n): return json.load(open(os.path.join(T,n),encoding='utf-8'))
out=[]; seen={}
def add(fonte,cat,sub,ent,tipo,toque,pag,linhas,sec='',revisar=False):
    ls=[l for l in linhas]
    while ls and not ls[0].strip(): ls.pop(0)
    while ls and not ls[-1].strip(): ls.pop()
    if not ls: return
    texto='\n'.join(ls); k=nm(texto)
    if len(k)<12: return
    if k in seen and fonte!='ceug': seen[k]['tambem']=seen[k].get('tambem',[])+[fonte]; return
    meio=sum(1 for l in ls if re.search(r'[|¥\[\]{}<>=~^\\]|[a-zà-ú][0-9]|[0-9][a-zà-ú]',re.sub(r'\(\d+x\)|\b\d+ ?x\b|\b7 ?[A-Za-zà-ú]+',' ',l)))
    rec={'id':len(out)+1,'fonte':fonte,'grupo':grupo(cat),'cat':cat,'sub':sub,'ent':ent,'tipo':tipo,'toque':toque,'pag':pag,'sec':sec,
         'titulo':re.sub(r'\s*\(\d+x\)$','',next(l for l in ls if l.strip()))[:70],'texto':texto,
         'revisar':bool(revisar) or meio>0 or (len(ls)<=1 and tipo not in('saudação',))}
    out.append(rec); seen[k]=rec
for p in load('../data/pontos.json')['pontos'] if False else []: pass
ceug=json.load(open(os.path.join(T,'pontos_ceug.json'),encoding='utf-8'))['pontos']
for p in ceug: add('ceug',p['cat'],p['sub'],p['ent'],p['tipo'],p['toque'],p['pag'],p['texto'].split('\n'),p['sec'],p['revisar'])
for fid,fn in (('terreiro','raw_pontos.json'),('t1540','raw_1500.json'),('jurema','raw_mestres.json'),('p3333','raw_3333.json')):
    for p in load(fn):
        cat=p['cat']
        if fid=='p3333' and cat=='Exu': cat='Exus'
        cat=MAP.get(cat,cat)
        add(fid,cat,p.get('sub',''),p.get('ent',''),p.get('tipo','ponto'),p.get('toque',''),p.get('pag',0),p['linhas'],'',fid=='p3333' and False)
json.dump({'fontes':FONTES,'pontos':out},open(os.path.join(T,'..','data','pontos.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
import collections
print(len(out),collections.Counter(o['fonte'] for o in out)); print('revisar',sum(o['revisar'] for o in out))
