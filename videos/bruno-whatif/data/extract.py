import json,re,sys
D=sys.argv[1]
ids=[l.split() for l in open(D+'/ids.txt')]
out={'2024':[], '2025':[]}
for s,i in ids:
    d=json.load(open(f'{D}/sum-{i}.json'))
    comp=d['header']['competitions'][0]; teams={c['team']['displayName']:(c['homeAway'],int(c.get('score',0) or 0)) for c in comp['competitors']}
    date=comp['date'][:10]
    home=[t for t,v in teams.items() if v[0]=='home'][0]; away=[t for t,v in teams.items() if v[0]=='away'][0]
    goals=[]; pens_missed=[]
    for k in d.get('keyEvents',[]):
        ty=k['type']['type']; txt=k.get('text','')
        if k.get('scoringPlay') or ty.startswith('goal') or ty=='penalty---scored' or ty=='own-goal':
            ps=[p['athlete']['displayName'] for p in k.get('participants',[])]
            team=k.get('team',{}).get('displayName')
            og = 'own goal' in txt.lower() or ty=='own-goal'
            m=re.search(r'Assisted by ([^.]+?)(?: with| following|\.|$)',txt)
            goals.append(dict(min=k['clock']['displayValue'],team=team,scorer=ps[0] if ps else None,assist=m.group(1).strip() if m else None,pen=('penalty' in ty),og=og,text=txt))
        if 'penalty' in ty and 'scored' not in ty and 'Penalty' in k['type']['text']:
            pens_missed.append(dict(min=k['clock']['displayValue'],type=k['type']['text'],text=txt))
    out[s].append(dict(id=i,date=date,home=home,away=away,hs=teams[home][1],as_=teams[away][1],goals=goals,pens_missed=pens_missed))
for s in out: out[s].sort(key=lambda m:m['date'])
json.dump(out,open(D+'/../espn.json','w'),indent=1)
for s in out:
    g=a=p=0
    for m in out[s]:
        for x in m['goals']:
            if x['team']!='Manchester United': continue
            if x['scorer']=='Bruno Fernandes' and not x['og']: g+=1; p+=x['pen']
            if x['assist'] and 'Bruno Fernandes' in x['assist']: a+=1
    print(s,'Bruno goals',g,'(pens',p,') assists',a, 'matches',len(out[s]))
