import json,sys,collections
sys.argv=['x']; 
from parse import norm
L=json.load(open('leagues.json')); L={int(k):v for k,v in L.items()}
d=json.load(open('l1pl.json')); L[2026]['1']=sorted({norm(t['team']['displayName']) for t in d['sports'][0]['leagues'][0]['teams']})
G=json.load(open('espn_games.json')); T=json.load(open('trophy.json'))
def season(date): y,m=int(date[:4]),int(date[5:7]); return y if m>=7 else y-1
def summ(rows,label):
    n=len(rows); gf=sum(r[0] for r in rows); ga=sum(r[1] for r in rows)
    w=sum(r[0]>r[1] for r in rows); dr=sum(r[0]==r[1] for r in rows)
    print(f"{label}: n={n} GF {gf/n:.2f} GA {ga/n:.2f} GD {(gf-ga)/n:+.2f}  W{w} D{dr} L{n-w-dr} ({w/n:.0%} wins)")
# A) Trophy: PL U21 sides v League Two / League One first teams (from the U21's side)
u21={'4':[],'3':[]}; city=[]
for date,h,a,hs,as_ in T:
    y=season(date); hu=' U21' in h; au=' U21' in a
    if hu==au: continue
    acad,opp=(h,a) if hu else (a,h); o=norm(opp); gf,ga=(hs,as_) if hu else (as_,hs)
    for lg in ('4','3'):
        if o in L.get(y,{}).get(lg,[]): u21[lg].append((gf,ga,hu,date,acad,o))
    if 'Manchester City' in acad: city.append((gf,ga,date,o))
summ(u21['4'],'PL U21 v League Two (EFL Trophy, 2023-26)'); summ(u21['3'],'PL U21 v League One')
summ(city,'Man City U21 v EFL clubs'); print(city)
# B) Cups: PL first team v League Two club
cup=[]
for lg in ('eng.fa','eng.league_cup'):
    for date,h,a,hs,as_ in G[lg]:
        y=season(date); P=L.get(y,{}).get('1',[]); F=L.get(y,{}).get('4',[])
        if h in P and a in F: cup.append((hs,as_,'A',date,h,a))
        elif a in P and h in F: cup.append((as_,hs,'H',date,a,h))
summ(cup,'PL first team v League Two (FA Cup + League Cup)')
summ([c for c in cup if c[4]=='Manchester City'],'Man City first team v League Two'); print([c for c in cup if c[4]=='Manchester City'])
json.dump({'u21_l2':u21['4'],'u21_l1':u21['3'],'cup':cup},open('gapdata.json','w'))
