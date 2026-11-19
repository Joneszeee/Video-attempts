# League One ratings (real results) + Man City's League One strength by tier, for episode 2.
import json,math,numpy as np
from parse import norm
G=json.load(open('espn_games.json')); L=json.load(open('leagues.json'))
def fit(rows,lam=2.0):
    teams=sorted({r[0] for r in rows}|{r[1] for r in rows}); ix={t:i for i,t in enumerate(teams)}; n=len(teams)
    H=np.array([ix[r[0]] for r in rows]); A=np.array([ix[r[1]] for r in rows]); HS=np.array([r[2] for r in rows],float); AS=np.array([r[3] for r in rows],float); Wt=np.array([r[4] for r in rows])
    c,hm=0.2,0.1; att=np.zeros(n); de=np.zeros(n); lr=0.002
    for it in range(20000):
        m1=np.exp(c+hm+att[H]-de[A]); m2=np.exp(c+att[A]-de[H]); r1=Wt*(m1-HS); r2=Wt*(m2-AS)
        c-=lr*(r1.sum()+r2.sum())/10; hm-=lr*r1.sum()/10
        att-=lr*(np.bincount(H,r1,n)+np.bincount(A,r2,n)+2*lam*att); de-=lr*(-np.bincount(A,r1,n)-np.bincount(H,r2,n)+2*lam*de)
    return c,hm,dict(zip(teams,att)),dict(zip(teams,de))
rows=[(h,a,hs,as_,1.0 if d>='2026-07-01' else 0.5) for d,h,a,hs,as_ in G['eng.3']]
c1,h1,att1,de1=fit(rows)
cur=L['2026']['3']
R1={'c':c1,'home':h1,'teams':{t:{'att':att1[t],'def':de1[t]} for t in cur}}
# League Two clubs that come up with City in the story (Grimsby, Barnet): their League Two rating, moved onto the League One scale
R2=json.load(open('l2ratings.json')); X=json.load(open('gap_l1.json'))
HA1=math.exp(h1/2)
def neutral(rows):   # rows: (gf, ga, home) from the higher side
    gf=ga=0
    for a,b,home in rows:
        k=1/HA1 if home else HA1; gf+=a*k; ga+=b/k
    return gf/len(rows),ga/len(rows)
l1v2=neutral(X['l1l2'])              # League One club v League Two club
avg1=math.exp(c1+h1/2)               # League One average goals per team per game (neutral)
l2avg_vs_l1=(l1v2[1],l1v2[0])        # a League Two average side v a League One average side: scores l1v2[1], concedes l1v2[0]
for t in ('Grimsby Town','Barnet'):
    a,d=R2['teams'][t]['att'],R2['teams'][t]['def']
    R1['teams'][t]={'att':math.log(l2avg_vs_l1[0]/avg1)+a,'def':-math.log(l2avg_vs_l1[1]/avg1)+d}
json.dump(R1,open('l1ratings.json','w'))
# tiers v an average League One side (goals for, against per game, neutral venue)
pl=neutral([(r[0],r[1],r[2]) for r in X['pll1']])
cityg=[(r[0],r[1],r[2]) for r in X['pll1'] if r[3]=='Manchester City']; cn=neutral(cityg); n=len(cityg)
city=((n*cn[0]+10*pl[0])/(n+10),(n*cn[1]+10*pl[1])/(n+10))
u21_raw=json.load(open('gapdata.json'))['u21_l1']
u21=neutral([(r[0],r[1],r[2]) for r in u21_raw])
GROW=0.20   # the kids improve a little: their rating moves 20% of the way (log scale) toward a League One average player
u21g=(math.exp(math.log(u21[0])*(1-GROW)+math.log(avg1)*GROW), math.exp(math.log(u21[1])*(1-GROW)+math.log(avg1)*GROW))
top=sorted(R2['teams'].values(),key=lambda t:-(t['att']+t['def']))[:12]
l2good=(l2avg_vs_l1[0]*math.exp(sum(t['att'] for t in top)/12), l2avg_vs_l1[1]*math.exp(-sum(t['def'] for t in top)/12))
TIERS={'city':city,'pl':pl,'u21':u21g,'l2':l2good}
POS=[('GK',0,.20),('RB',.06,.11),('CB',.03,.15),('CB',.03,.15),('LB',.06,.11),('DM',.07,.10),('DM',.07,.10),('RW',.15,.03),('AM',.15,.02),('LW',.15,.03),('ST',.23,0)]
def team(xi,T=TIERS):
    return (math.exp(sum(w*math.log(T[t][0]) for (p,w,_),t in zip(POS,xi))), math.exp(sum(w*math.log(T[t][1]) for (p,_,w),t in zip(POS,xi))))
#       GK   RB     CB   CB   LB     DM(Iroeg) DM(Braybrooke) RW   AM(Foden) LW   ST(Haaland)
FULL=['l2','city','l2','l2','city','pl','l2','u21','city','u21','city']
def swap(xi,i,t): x=list(xi); x[i]=t; return x
out={'avg':avg1,'HA':HA1,'tiers':TIERS,'u21_raw':u21,'l1v2':l1v2,'city_games':n,
     'full':team(FULL),'no_haaland':team(swap(FULL,10,'u21')),'no_foden':team(swap(FULL,8,'u21')),'no_haaland_foden':team(swap(swap(FULL,10,'u21'),8,'u21')),
     'ep1_xi_no_iroeg':team(swap(FULL,5,'u21'))}
json.dump(out,open('citymodel_l1.json','w'),indent=1)
for k,v in out.items(): print(k, v if not isinstance(v,tuple) else tuple(round(x,2) for x in v))
s=sorted(R1['teams'],key=lambda t:-(R1['teams'][t]['att']+R1['teams'][t]['def']))
print('strongest:',s[:6]); print('weakest:',s[-5:])
