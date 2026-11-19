import json,math
R=json.load(open('l2ratings.json')); c,hm=R['c'],R['home']; HA=math.exp(hm/2)   # home side x HA, away side / HA, relative to neutral
D=json.load(open('gapdata.json'))
def neutral(rows,home_idx):
    gf=ga=0
    for r in rows:
        home=r[home_idx]
        k=1/HA if home else HA          # undo venue: a home side's goals are inflated by HA, conceded deflated
        gf+=r[0]*k; ga+=r[1]/k
    return gf/len(rows),ga/len(rows)
u21=neutral(D['u21_l2'],2)                                  # hu flag = U21 side at home
cup=neutral([(r[0],r[1],r[2]=='A') for r in D['cup']],2)    # 'A' in gap.py = PL side at home
city=neutral([(r[0],r[1],r[2]=='A') for r in D['cup'] if r[4]=='Manchester City'],2)
n_city=sum(1 for r in D['cup'] if r[4]=='Manchester City')
# City first-team level: City's own 6 games shrunk toward the 104-game Premier League average (prior weight 10 games)
cityL=((n_city*city[0]+10*cup[0])/(n_city+10),(n_city*city[1]+10*cup[1])/(n_city+10))
avg=math.exp(c+hm/2)                                        # League Two average goals per team per game, neutral venue
top=sorted(R['teams'].values(),key=lambda t:-(t['att']+t['def']))[:12]
l2good=(avg*math.exp(sum(t['att'] for t in top)/12),avg*math.exp(-sum(t['def'] for t in top)/12))
TIERS={'city':cityL,'u21':u21,'l2':l2good}
# 4-2-3-1 positional weights (share of a team's attacking / defensive contribution)
POS=[('GK',0,.20),('RB',.06,.11),('CB',.03,.15),('CB',.03,.15),('LB',.06,.11),('DM',.07,.10),('DM',.07,.10),('RW',.15,.03),('AM',.15,.02),('LW',.15,.03),('ST',.23,0)]
def team(xi):
    la=sum(w*math.log(TIERS[t][0]) for (p,w,_),t in zip(POS,xi)); ld=sum(w*math.log(TIERS[t][1]) for (p,_,w),t in zip(POS,xi))
    return math.exp(la),math.exp(ld)
#            GK    RB      CB    CB    LB      DM     DM     RW     AM      LW     ST
XI_FULL=  ['l2','city','l2','l2','city','u21','l2','u21','city','u21','city']   # Lewis RB, O'Reilly LB, Foden AM, Haaland ST
XI_NOH=   ['l2','city','l2','l2','city','u21','l2','u21','city','u21','u21']    # Haaland out
XI_NOHF=  ['l2','city','l2','l2','city','u21','l2','u21','u21','u21','u21']     # Haaland and Foden out
XI_NOF=   ['l2','city','l2','l2','city','u21','l2','u21','u21','u21','city']     # Foden out
XI_KIDS=  ['u21']*11
out={'avg':avg,'HA':HA,'tiers':TIERS,'n_city':n_city,'city_raw':city,'pl_cup':cup,'u21_raw':u21,
     'full':team(XI_FULL),'no_haaland':team(XI_NOH),'no_haaland_foden':team(XI_NOHF),'no_foden':team(XI_NOF),'kids_only':team(XI_KIDS)}
json.dump(out,open('citymodel.json','w'),indent=1)
for k,v in out.items(): print(k,v if not isinstance(v,tuple) else tuple(round(x,2) for x in v))
