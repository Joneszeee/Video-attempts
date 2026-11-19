import json,math,random,collections,sys
R=json.load(open('l2ratings.json')); M=json.load(open('citymodel.json'))
c,hm=R['c'],R['home']; avgN=M['avg']
OUT=sys.argv[1] if len(sys.argv)>1 else 'Crawley Town'
T={t:(v['att'],v['def']) for t,v in R['teams'].items() if t!=OUT}
P_H,P_F=0.90,0.85          # chance Haaland / Foden are available for a game (injuries, rest)
H_SHARE=0.38               # Haaland's share of City's goals when he plays (assumption, his City share has been ~28-38%)
def city_rates(h,f):
    k='full' if h and f else 'no_foden' if h else 'no_haaland' if f else 'no_haaland_foden'
    gf,ga=M[k]; return math.log(gf/avgN), -math.log(ga/avgN)
T['Manchester City']=None
teams=sorted(T)
def pois(l,r):
    L=math.exp(-l);k=0;p=1.0
    while True:
        p*=r.random()
        if p<=L: return k
        k+=1
def rate(team,r,cache):
    if team!='Manchester City': return T[team]
    return cache
def season(r,log=False):
    tab={t:[0,0,0,0,0,0] for t in teams}   # pts, gf, ga, w, d, l
    hg=0; games=[]; hmiss=0
    for h in teams:
        for a in teams:
            if h==a: continue
            cr=None; hp=fp=True
            if 'Manchester City' in (h,a):
                hp=r.random()<P_H; fp=r.random()<P_F; cr=city_rates(hp,fp); hmiss+=not hp
            ah,dh=cr if h=='Manchester City' else T[h]; aa,da=cr if a=='Manchester City' else T[a]
            x=pois(math.exp(c+hm+ah-da),r); y=pois(math.exp(c+aa-dh),r)
            for t,gf,ga in ((h,x,y),(a,y,x)):
                s=tab[t]; s[1]+=gf; s[2]+=ga
                if gf>ga: s[0]+=3; s[3]+=1
                elif gf==ga: s[0]+=1; s[4]+=1
                else: s[5]+=1
            if 'Manchester City' in (h,a):
                cg=x if h=='Manchester City' else y
                hgoals=sum(1 for _ in range(cg) if hp and r.random()<H_SHARE); hg+=hgoals
                if log: games.append({'opp':a if h=='Manchester City' else h,'home':h=='Manchester City','for':cg,'against':y if h=='Manchester City' else x,'haaland':hp,'foden':fp,'hgoals':hgoals})
    order=sorted(teams,key=lambda t:(-tab[t][0],-(tab[t][1]-tab[t][2]),-tab[t][1],t))
    pos=order.index('Manchester City')+1
    # play-offs: 4v7, 5v6 (two legs), final neutral; ties 50/50
    def tie(a,b,legs):
        ga=gb=0
        for i in range(legs):
            hh,aa_=(a,b) if i==0 else (b,a)
            def rr(t,home): return city_rates(r.random()<P_H,r.random()<P_F) if t=='Manchester City' else T[t]
            A1,D1=rr(hh,True); A2,D2=rr(aa_,False)
            hadv=hm if legs==2 else 0
            x=pois(math.exp(c+hadv+A1-D2),r); y=pois(math.exp(c+A2-D1),r)
            if hh==a: ga+=x; gb+=y
            else: gb+=x; ga+=y
        return a if ga>gb else b if gb>ga else (a if r.random()<.5 else b)
    w1=tie(order[3],order[6],2); w2=tie(order[4],order[5],2); po=tie(w1,w2,1)
    up=pos<=3 or po=='Manchester City'
    return pos,tab,order,up,po,hg,games,hmiss
if __name__=='__main__':
    N=10000; r=random.Random(7); P=collections.Counter(); pts=[]; gf=[]; ga=[]; up=0; hgs=[]; pof=collections.Counter()
    for i in range(N):
        pos,tab,order,u,po,hg,_,_=season(r)
        P[pos]+=1; s=tab['Manchester City']; pts.append(s[0]); gf.append(s[1]); ga.append(s[2]); up+=u; hgs.append(hg)
        if 4<=pos<=7: pof['in']+=1; pof['won']+=po=='Manchester City'
    pts.sort(); hgs.sort()
    res={'replaced':OUT,'N':N,'pos':{k:v/N for k,v in sorted(P.items())},'title':P[1]/N,'auto':sum(P[k] for k in (1,2,3))/N,'playoffs':pof['in']/N,
         'playoff_win_given_in':pof['won']/max(1,pof['in']),'promoted':up/N,'avg_pts':sum(pts)/N,'pts_10_90':(pts[N//10],pts[9*N//10]),
         'avg_gf':sum(gf)/N,'avg_ga':sum(ga)/N,'haaland_avg':sum(hgs)/N,'haaland_10_90':(hgs[N//10],hgs[9*N//10])}
    json.dump(res,open('simresult.json','w'),indent=1); print(json.dumps(res,indent=1))
