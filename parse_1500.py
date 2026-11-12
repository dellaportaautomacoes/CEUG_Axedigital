import pdfplumber, re, json, collections
pdf=pdfplumber.open('/mnt/user-data/uploads/1500pontosumbanda-letrasdepontosdeumbanda-110622133953-phpapp02.pdf')
OUT=[]
def rows_from(ws):
    rows=[]
    for w in sorted(ws,key=lambda w:(round(w['top']),w['x0'])):
        if rows and abs(rows[-1][0]-w['top'])<=3: rows[-1][1].append(w)
        else: rows.append([w['top'],[w]])
    res=[]
    for top,l in rows:
        l.sort(key=lambda w:w['x0']); toks=[w['text'] for w in l]
        while toks and re.fullmatch(r'[|>]+|\d?\s*>',toks[-1]): toks.pop()
        t=' '.join(toks).strip()
        if t: res.append({'top':top,'t':t,'size':round(l[0]['size'])})
    return res
tabs_seen={}
for i,pg in enumerate(pdf.pages):
    if i<4: continue
    W=pg.width
    ws=[w for w in pg.extract_words(extra_attrs=['fontname','size']) if 0<=w['x0']<W]
    frames=[(0,W)] if W<600 else [(0,W/2),(W/2,W)]
    for fi,(a,b) in enumerate(frames):
        fw=[w for w in ws if a<=w['x0']<b]
        # abas verticais: letras soltas empilhadas
        singles=[w for w in fw if len(w['text'])==1 and w['size']<=11]
        byx=collections.defaultdict(list)
        for w in singles: byx[round(w['x0']/3)].append(w)
        tab=''
        for k,l in byx.items():
            l.sort(key=lambda w:-w['top'])
            if len(l)>=3 and all(abs(l[j]['top']-l[j+1]['top'])<14 for j in range(len(l)-1)):
                tab=''.join(w['text'] for w in l); tabw={id(w) for w in l}
                fw=[w for w in fw if id(w) not in tabw]; break
        mid=(a+b)/2
        body=[w for w in fw if 34<w['top']<552]
        for col,sel in ((0,[w for w in body if w['x0']<mid-4]),(1,[w for w in body if w['x0']>=mid-4])):
            for r in rows_from(sel):
                if 'Tenda Caboclo' in r['t'] or '1.540 Pontos' in r['t'] or re.fullmatch(r'\d+',r['t']): continue
                r.update(pg=i+1,fr=fi,col=col,tab=tab); OUT.append(r)
json.dump(OUT,open('rows_1500.json','w'),ensure_ascii=False)
print(len(OUT)); print(collections.Counter(r['tab'] for r in OUT).most_common(40))
