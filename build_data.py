"""Gera data/pontos.json a partir de raw_ceug.json (saída do parse_ceug.py)."""
import json, re, sys
src = sys.argv[1] if len(sys.argv) > 1 else 'raw_ceug.json'
d = json.load(open(src, encoding='utf-8'))
GRUPOS = [(1,5,'Abertura'),(6,18,'Orixás'),(19,25,'Linhas de trabalho'),(26,27,'Diversos')]
def grupo(n):
    n = int(n.split('.')[0])
    for a,b,g in GRUPOS:
        if a<=n<=b: return g
    return 'Outros'
def tc(s):
    if not s.isupper(): return s
    s = s.title()
    for a in ('De','Da','Do','E','Dos','Das','Para'): s = s.replace(' '+a+' ',' '+a.lower()+' ')
    return s
out=[]; ov=None
for p in d['points']:
    if p['num'].split('.')[0]=='28': continue   # texto explicativo/créditos
    path=p['path']; ent=''
    for t in path[1:]:
        if not re.match(r'(PONTOS?|SAUDA)',t.upper()): ent=t
    m=re.match(r'^\d+(?:\.\s?\d+)+\s+(\S.*)$',p['linhas'][0])
    if m and len(p['linhas'])==1:      # título de seção que escapou do sumário
        ov=(p['num'],m.group(1)); continue
    if ov and p['num']==ov[0]: ent=ov[1]
    else: ov=None
    texto='\n'.join(p['linhas'])
    out.append({'id':len(out)+1,'grupo':grupo(p['num']),'cat':tc(path[0]),
      'sub':' › '.join(tc(t) for t in path[1:]),'ent':ent,'tipo':p['tipo'],'toque':p['toque'],
      'pag':p['pagina'],'sec':p['num'],'titulo':re.sub(r'\s*\(\w+\)$','',p['linhas'][0])[:70],
      'texto':texto,'revisar':len(p['linhas'])<=1 and p['tipo']!='saudação'})
json.dump({'fonte':'Apostila de Pontos Cantados CEUG v2.0 (Nov/2022)','pontos':out},
          open('data/pontos.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'pontos;',sum(o['revisar'] for o in out),'para revisar')
