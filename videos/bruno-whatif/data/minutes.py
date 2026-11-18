import json,re,collections
E=json.load(open('espn.json'))
def mins(eid):
    d=json.load(open(f'espn/sum-{eid}.json'))
    t=[x for x in d['rosters'] if x['team']['displayName']=='Manchester United'][0]
    M={}; pos={}
    for p in t['roster']:
        n=p['athlete']['displayName']
        if p.get('starter'): M[n]=[0,90]; pos[n]=p['position']['abbreviation']
    for k in d['keyEvents']:
        if k.get('team',{}).get('displayName')!='Manchester United': continue
        mn=k['clock']['value']/60.0; mn=min(mn,90)
        if k['type']['type']=='substitution':
            ps=[p['athlete']['displayName'] for p in k['participants']]
            if len(ps)==2:
                M[ps[0]]=[mn,90]; pos.setdefault(ps[0],'SUB')
                if ps[1] in M: M[ps[1]][1]=mn
        if 'red' in k['type']['type'] and k.get('participants'):
            n=k['participants'][0]['athlete']['displayName']
            if n in M: M[n][1]=min(M[n][1],mn)
    return {n:max(0,b-a) for n,(a,b) in M.items()}, pos
GA=collections.defaultdict(lambda:[0,0,0.0,0])  # g,a,mins,apps
out={}
for s in E:
    S=collections.defaultdict(lambda:[0,0,0.0,0,0])  # g (non-pen), pens, a, mins, apps
    for m in E[s]:
        mm,pos=mins(m['id']); m['mins']=mm; m['pos']=pos
        for n,v in mm.items(): S[n][3]+=v; S[n][4]+=1
        for g in m['goals']:
            if g['team']!='Manchester United' or g['og']: continue
            if g['pen']: S[g['scorer']][1]+=1
            else: S[g['scorer']][0]+=1
            if g['assist']:
                for a in g['assist'].split(' and '): S[a.strip()][2]+=1
    out[s]=S
    print('=== season',s)
    for n,(g,p,a,mi,ap) in sorted(S.items(), key=lambda kv:-kv[1][3]):
        if mi<300: continue
        print(f"{n:24} apps {ap:2} mins {mi:5.0f}  np-goals {g:2} pens {p} assists {a:2}  npG+A/90 {(g+a)/mi*90:4.2f}")
json.dump(E,open('espn_mins.json','w'))
