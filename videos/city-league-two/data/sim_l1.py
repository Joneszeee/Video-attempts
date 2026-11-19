# Episode 2: League One 2027/28 with City (+ Grimsby and Barnet, promoted with them in episode 1) in place of the real bottom three.
import json,math,random,collections,sys
R=json.load(open('l1ratings.json')); M=json.load(open('citymodel_l1.json'))
c,hm=R['c'],R['home']; avg=M['avg']
OUT=['Bromley','Barnsley','Peterborough United']   # bottom three of the real League One table, 19 Nov 2026
T={t:(v['att'],v['def']) for t,v in R['teams'].items() if t not in OUT}
T['Manchester City']=None
teams=sorted(T); assert len(teams)==24, len(teams)
P_H,P_F,H_SHARE=0.90,0.85,0.38
KEYS={'full':'full'}
def city_rates(h,f,m=None):
    m=m or M
    k='full' if h and f else 'no_foden' if h else 'no_haaland' if f else 'no_haaland_foden'
    gf,ga=m[k]; return math.log(gf/avg), -math.log(ga/avg)
def pois(l,r):
    L=math.exp(-l);k=0;p=1.0
    while True:
        p*=r.random()
        if p<=L: return k
        k+=1
def play(h,a,r,m=None):
    hp=fp=True; cr=None
    if 'Manchester City' in (h,a): hp=r.random()<P_H; fp=r.random()<P_F; cr=city_rates(hp,fp,m)
    ah,dh=cr if h=='Manchester City' else T[h]; aa,da=cr if a=='Manchester City' else T[a]
    return pois(math.exp(c+hm+ah-da),r),pois(math.exp(c+aa-dh),r),hp,fp
def fixtures(seed):
    fx=random.Random(seed+1).sample(teams,len(teams)); n=len(fx); rounds=[]; last={}; homes={}; arr=fx[:]
    for k in range(n-1):
        rd=[]
        for i in range(n//2):
            a,b=arr[i],arr[n-1-i]; la,lb=last.get(a),last.get(b)
            if la=='A' and lb!='A': h_,a_=a,b
            elif lb=='A' and la!='A': h_,a_=b,a
            else: h_,a_=(a,b) if homes.get(a,0)<=homes.get(b,0) else (b,a)
            rd.append((h_,a_)); last[h_]='H'; last[a_]='A'; homes[h_]=homes.get(h_,0)+1
        rounds.append(rd); arr=[arr[0]]+[arr[-1]]+arr[1:-1]
    return rounds+[[(b,a) for a,b in rd] for rd in rounds]
def upd(tab,h,a,x,y):
    for t,gf,ga in ((h,x,y),(a,y,x)):
        s=tab[t]; s[1]+=gf; s[2]+=ga; s[0]+=3 if gf>ga else 1 if gf==ga else 0
def order(tab): return sorted(teams,key=lambda t:(-tab[t][0],-(tab[t][1]-tab[t][2]),-tab[t][1],t))
def finish(tab,rounds_left,r,m=None):
    tab={t:list(v) for t,v in tab.items()}
    for rd in rounds_left:
        for h,a in rd: x,y,_,_=play(h,a,r,m); upd(tab,h,a,x,y)
    o=order(tab); pos=o.index('Manchester City')+1
    def tie(a,b):   # two legs, then 50/50
        ga=gb=0
        for hh,aa in ((a,b),(b,a)):
            x,y,_,_=play(hh,aa,r,m)
            if hh==a: ga+=x; gb+=y
            else: gb+=x; ga+=y
        return a if ga>gb else b if gb>ga else (a if r.random()<.5 else b)
    w1=tie(o[2],o[5]); w2=tie(o[3],o[4])
    x,y,_,_=play(w1,w2,r,m); fin=w1 if x>y else w2 if y>x else (w1 if r.random()<.5 else w2)
    return pos, pos<=2 or fin=='Manchester City', tab['Manchester City'][0], o
def odds(rounds,tab0,N,seed,m=None):
    r=random.Random(seed); P=collections.Counter(); up=0; pts=[]
    for _ in range(N):
        pos,u,p,_=finish(tab0,rounds,r,m); P[pos]+=1; up+=u; pts.append(p)
    pts.sort()
    return {'title':P[1]/N,'auto':(P[1]+P[2])/N,'playoffs':sum(P[k] for k in range(3,7))/N,'promoted':up/N,'avg_pts':sum(pts)/N,'pts_10_90':(pts[N//10],pts[9*N//10]),'pos':{k:v/N for k,v in sorted(P.items())}}
if __name__=='__main__':
    SEED=2027; rounds=fixtures(SEED); empty={t:[0,0,0] for t in teams}
    pre=odds(rounds,empty,10000,7)
    no_iroeg=dict(M); no_iroeg['full']=M['ep1_xi_no_iroeg']
    pre_wo=odds(rounds,empty,4000,8,no_iroeg)
    # the official season, matchdays 1-23 only (seed fixed before running)
    r=random.Random(SEED); tab={t:[0,0,0] for t in teams}; log=[]; hg=0; snaps={}
    for k,rd in enumerate(rounds[:23],1):
        for h,a in rd:
            x,y,hp,fp=play(h,a,r); upd(tab,h,a,x,y)
            if 'Manchester City' in (h,a):
                home=h=='Manchester City'; cg,og=(x,y) if home else (y,x)
                hgo=sum(1 for _ in range(cg) if hp and r.random()<H_SHARE); hg+=hgo
                log.append({'md':k,'opp':a if home else h,'venue':'H' if home else 'A','score':f'{cg}-{og}','res':'W' if cg>og else 'D' if cg==og else 'L','haaland':hp,'foden':fp,'hgoals':hgo,'hg_total':hg})
        o=order(tab); log[-1]['pos']=o.index('Manchester City')+1; log[-1]['pts']=tab['Manchester City'][0]
        snaps[k]=[(i+1,t,tab[t][0],tab[t][1]-tab[t][2]) for i,t in enumerate(o[:6])]
    o=order(tab); gfr=sorted(teams,key=lambda t:-tab[t][1]).index('Manchester City')+1; gar=sorted(teams,key=lambda t:tab[t][2]).index('Manchester City')+1
    half=odds(rounds[23:],tab,10000,9)
    res={'seed':SEED,'out':OUT,'pre':pre,'pre_without_iroegbunam':pre_wo,'log':log,'haaland':hg,'table_md23':[(i+1,t,*tab[t]) for i,t in enumerate(o)],
         'city_gf_rank':gfr,'city_ga_rank':gar,'half_odds':half,'model':{k:M[k] for k in ('full','no_haaland','tiers')}}
    json.dump(res,open('ep2.json','w'),indent=1)
    print('PRE',json.dumps({k:pre[k] for k in ('title','auto','playoffs','promoted','avg_pts','pts_10_90')}))
    print('PRE w/o Iroeg',json.dumps({k:pre_wo[k] for k in ('title','auto','promoted','avg_pts')}))
    for g in log: print(g['md'],g['venue'],g['opp'],g['score'],g['res'],'H' if g['haaland'] else '-','F' if g['foden'] else '-',g['hgoals'],'| pos',g['pos'],g['pts'])
    print('MD23 table:'); [print(*row) for row in res['table_md23'][:8]]
    print('City GF rank',gfr,'GA rank',gar,'Haaland',hg)
    print('HALF',json.dumps({k:half[k] for k in ('title','auto','playoffs','promoted','avg_pts')}))
