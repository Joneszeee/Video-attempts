import json,math,numpy as np
from parse import norm
G=json.load(open('espn_games.json')); L=json.load(open('leagues.json'))
cur=L['2026']['4']
rows=[]
for date,h,a,hs,as_ in G['eng.4']:
    w=1.0 if date>='2026-07-01' else 0.5
    rows.append((h,a,hs,as_,w,date))
teams=sorted({r[0] for r in rows}|{r[1] for r in rows}); ix={t:i for i,t in enumerate(teams)}; n=len(teams)
# Poisson: log mu_home = c + home + att[h] - def[a]; ridge on att/def
def nll(p,lam=2.0):
    c,hm=p[0],p[1]; att=p[2:2+n]; de=p[2+n:]
    tot=0; g=np.zeros_like(p)
    for h,a,hs,as_,w,_ in rows:
        i,j=ix[h],ix[a]
        m1=math.exp(c+hm+att[i]-de[j]); m2=math.exp(c+att[j]-de[i])
        tot+=w*(m1-hs*math.log(m1)+m2-as_*math.log(m2))
        r1=w*(m1-hs); r2=w*(m2-as_)
        g[0]+=r1+r2; g[1]+=r1; g[2+i]+=r1; g[2+n+j]-=r1; g[2+j]+=r2; g[2+n+i]-=r2
    tot+=lam*(np.sum(att**2)+np.sum(de**2)); g[2:]+=2*lam*p[2:]
    return tot,g

H=np.array([ix[r[0]] for r in rows]); A=np.array([ix[r[1]] for r in rows]); HS=np.array([r[2] for r in rows],float); AS=np.array([r[3] for r in rows],float); Wt=np.array([r[4] for r in rows])
c,hm=0.2,0.1; att=np.zeros(n); de=np.zeros(n); lam=2.0; lr=0.002
for it in range(20000):
    m1=np.exp(c+hm+att[H]-de[A]); m2=np.exp(c+att[A]-de[H]); r1=Wt*(m1-HS); r2=Wt*(m2-AS)
    gc=r1.sum()+r2.sum(); gh=r1.sum()
    ga=np.bincount(H,r1,n)+np.bincount(A,r2,n)+2*lam*att
    gd=-np.bincount(A,r1,n)-np.bincount(H,r2,n)+2*lam*de
    c-=lr*gc/10; hm-=lr*gh/10; att-=lr*ga; de-=lr*gd
print('grad',abs(gc),abs(gh),np.abs(ga).max(),np.abs(gd).max())
att=dict(zip(teams,att)); de=dict(zip(teams,de))
print('base goals/team/game',round(math.exp(c+hm/2),3),'home adv x',round(math.exp(hm),3))
R={t:{'att':att[t],'def':de[t]} for t in cur}
json.dump({'c':c,'home':hm,'teams':R},open('l2ratings.json','w'))
# strength order (expected GD v average neutral)
s=sorted(cur,key=lambda t:-(math.exp(c+hm/2+att[t])-math.exp(c+hm/2-de[t])))
for t in s: print(f"{t:22s} GF {math.exp(c+hm/2+att[t]):.2f} GA {math.exp(c+hm/2-de[t]):.2f}  games26 {sum(1 for r_ in rows if r_[4]==1 and t in r_[:2])}")
