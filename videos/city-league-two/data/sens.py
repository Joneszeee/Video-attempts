import json,math,random,collections,importlib,copy
import citymodel as CM
import sim as S
base=json.load(open('citymodel.json'))
def run(label,tiers=None,xi_override=None,N=3000):
    T0=dict(CM.TIERS)
    if tiers: CM.TIERS.update(tiers)
    M={'full':CM.team(xi_override or CM.XI_FULL),'no_haaland':CM.team(CM.XI_NOH),'no_haaland_foden':CM.team(CM.XI_NOHF),'no_foden':CM.team(CM.XI_NOF),'avg':base['avg']}
    CM.TIERS.clear(); CM.TIERS.update(T0)
    S.M.update(M)
    r=random.Random(11); P=collections.Counter(); pts=0
    for i in range(N):
        pos,tab,_,u,_,_,_,_=S.season(r); P[pos]+=1; pts+=tab['Manchester City'][0]
    print(f"{label:58s} full {M['full'][0]:.2f}-{M['full'][1]:.2f}  title {P[1]/N:.0%}  top3 {sum(P[k] for k in (1,2,3))/N:.0%}  avg pts {pts/N:.0f}")
    S.M.update({k:base[k] for k in ('full','no_haaland','no_haaland_foden','no_foden')})
run('base')
run("kids at City U21's own EFL record (1.6-2.8)",{'u21':(1.58*1.0,2.83)})
run('first-teamers at Premier League cup average (2.7-0.67)',{'city':(2.70,0.67)})
run('first-teamers at City raw 6-game level (4.1-0.63)',{'city':(4.14,0.63)})
run('no League Two signings (kids in GK/CB/DM)',xi_override=['u21','city','u21','u21','city','u21','u21','u21','city','u21','city'])
run('signings only League Two average (1.22-1.22)',{'l2':(1.22,1.22)})
