import json,random,collections,sys
E=json.load(open('espn_mins.json')); O=json.load(open('all.json'))
nm={'Manchester United':'Man United','Manchester City':'Man City','Brighton & Hove Albion':'Brighton','Wolverhampton Wanderers':'Wolves','Tottenham Hotspur':'Tottenham','Newcastle United':'Newcastle','Nottingham Forest':'Forest','West Ham United':'West Ham','Leicester City':'Leicester','Ipswich Town':'Ipswich','Leeds United':'Leeds','AFC Bournemouth':'Bournemouth'}
n=lambda x:nm.get(x,x)
RATE={'2024':(1+0+2)/(619+1054)*90, '2025':(3+0)/1017*90}   # stand-in non-penalty G+A per 90
PEN=0.75
def base(s):
    """per United match: goals after deleting Bruno's (non-pen) goals+assists and his scored pens; plus his pen attempts and minutes"""
    rows=[]
    for m in E[s]:
        h,a=n(m['home']),n(m['away']); uh=h=='Man United'
        ug=m['hs'] if uh else m['as_']; og=m['as_'] if uh else m['hs']
        dele=0
        for g in m['goals']:
            if g['team']!='Manchester United' or g['og']: continue
            if g['scorer']=='Bruno Fernandes' or (g['assist'] and 'Bruno' in g['assist']): dele+=1
        pens=sum(1 for g in m['goals'] if g['team']=='Manchester United' and g['scorer']=='Bruno Fernandes' and g['pen'])
        pens+=sum(1 for p in m['pens_missed'] if 'Bruno' in p['text'])
        rows.append(dict(h=h,a=a,uh=uh,ug=ug-dele,og=og,pens=pens,mins=m['mins'].get('Bruno Fernandes',0),date=m['date']))
    return rows
def table(ms):
    T=collections.defaultdict(lambda:[0,0,0])
    for h,a,hs,as_ in ms:
        for t,gf,ga in ((h,hs,as_),(a,as_,hs)):
            T[t][1]+=gf-ga; T[t][2]+=gf; T[t][0]+=3 if gf>ga else 1 if gf==ga else 0
    return sorted(T.items(), key=lambda kv:(-kv[1][0],-kv[1][1],-kv[1][2],kv[0]))
def poisson(lam,r):
    L=2.718281828**(-lam); k=0; p=1.0
    while True:
        p*=r.random()
        if p<=L: return k
        k+=1
def run(s,N=10000,seed=1):
    os={'2024':'2024-25','2025':'2025-26'}[s]; r=random.Random(seed)
    others=[(m['home'],m['away'],m['hs'],m['as_']) for m in O[os] if 'Man United' not in (m['home'],m['away'])]
    B=base(s); pos=collections.Counter(); pts=[]; ga=[]
    for _ in range(N):
        ms=list(others); extra=0
        for b in B:
            add=poisson(RATE[s]*b['mins']/90.0,r)+sum(1 for _ in range(b['pens']) if r.random()<PEN); extra+=add
            u=b['ug']+add
            ms.append((b['h'],b['a'],u,b['og']) if b['uh'] else (b['h'],b['a'],b['og'],u))
        t=table(ms); i=[k for k,_ in t].index('Man United'); pos[i+1]+=1; pts.append(t[i][1][0]); ga.append(extra)
    return pos,pts,ga,B
if __name__=='__main__':
    for s in ['2024','2025']:
        pos,pts,ga,B=run(s)
        N=sum(pos.values()); pts.sort()
        mode=pos.most_common(1)[0]
        print(f"=== {s}: stand-in rate {RATE[s]:.2f}/90 over Bruno's {sum(b['mins'] for b in B):.0f} mins -> avg {sum(ga)/N:.1f} goals added (incl. pens; {sum(b['pens'] for b in B)} pens)")
        print(f"  avg points {sum(pts)/N:.1f}  median {pts[N//2]}  10th-90th pct {pts[N//10]}-{pts[9*N//10]}")
        print(f"  most likely finish {mode[0]} ({mode[1]/N:.0%});  average finish {sum(k*v for k,v in pos.items())/N:.1f}")
        print('  finish distribution:',{k:f'{v/N:.1%}' for k,v in sorted(pos.items())})
        print(f"  relegated (18-20): {sum(v for k,v in pos.items() if k>=18)/N:.1%}   top 4: {sum(v for k,v in pos.items() if k<=4)/N:.1%}   top 5: {sum(v for k,v in pos.items() if k<=5)/N:.1%}  10th or worse: {sum(v for k,v in pos.items() if k>=10)/N:.1%}")
