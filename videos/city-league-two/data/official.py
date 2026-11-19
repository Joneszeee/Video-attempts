import json,math,random
import sim as S
SEED=2026                       # committed before running: the "official" season is whatever this seed produces
r=random.Random(SEED); teams=S.teams[:]; n=len(teams)
fx=random.Random(SEED+1).sample(teams,n)   # fixture order (circle method), double round robin, sides swap in the second half
rounds=[]; last={}; homes={}
arr=fx[:]
for k in range(n-1):
    rd=[]
    for i in range(n//2):
        a,b=arr[i],arr[n-1-i]
        # balance venues: whoever was away last time is at home now; otherwise the one with fewer home games
        la,lb=last.get(a),last.get(b)
        if la=='A' and lb!='A': h_,a_=a,b
        elif lb=='A' and la!='A': h_,a_=b,a
        else: h_,a_=(a,b) if homes.get(a,0)<=homes.get(b,0) else (b,a)
        rd.append((h_,a_)); last[h_]='H'; last[a_]='A'; homes[h_]=homes.get(h_,0)+1
    rounds.append(rd); arr=[arr[0]]+[arr[-1]]+arr[1:-1]
rounds+= [[(b,a) for a,b in rd] for rd in rounds]
tab={t:[0,0,0,0,0,0] for t in teams}; log=[]; pos_by_round=[]; hg=0; race=[]
for k,rd in enumerate(rounds,1):
    for h,a in rd:
        cr=None; hp=fp=True
        if 'Manchester City' in (h,a): hp=r.random()<S.P_H; fp=r.random()<S.P_F; cr=S.city_rates(hp,fp)
        ah,dh=cr if h=='Manchester City' else S.T[h]; aa,da=cr if a=='Manchester City' else S.T[a]
        x=S.pois(math.exp(S.c+S.hm+ah-da),r); y=S.pois(math.exp(S.c+aa-dh),r)
        for t,gf,ga in ((h,x,y),(a,y,x)):
            s=tab[t]; s[1]+=gf; s[2]+=ga
            if gf>ga: s[0]+=3; s[3]+=1
            elif gf==ga: s[0]+=1; s[4]+=1
            else: s[5]+=1
        if 'Manchester City' in (h,a):
            home=h=='Manchester City'; cg,og=(x,y) if home else (y,x)
            hgo=sum(1 for _ in range(cg) if hp and r.random()<S.H_SHARE); hg+=hgo
            log.append({'md':k,'opp':a if home else h,'venue':'H' if home else 'A','score':f'{cg}-{og}','res':'W' if cg>og else 'D' if cg==og else 'L','haaland':hp,'foden':fp,'hgoals':hgo,'hg_total':hg})
    order=sorted(teams,key=lambda t:(-tab[t][0],-(tab[t][1]-tab[t][2]),-tab[t][1],t))
    pos_by_round.append(order.index('Manchester City')+1); race.append({t:tab[t][0] for t in ('Manchester City','Grimsby Town','Barnet','Salford City')}); race[-1]['leader']=order[0]; race[-1]['gd']={t:tab[t][1]-tab[t][2] for t in ('Manchester City','Grimsby Town')}
    log[-1]['pos']=pos_by_round[-1]; log[-1]['pts']=tab['Manchester City'][0]
final=[(i+1,t,*tab[t]) for i,t in enumerate(order)]
json.dump({'seed':SEED,'log':log,'final':final,'pos_by_round':pos_by_round,'haaland':hg,'race':race},open('official.json','w'),indent=1)
for g in log: print(g['md'],g['venue'],g['opp'],g['score'],g['res'],'H' if g['haaland'] else '-','F' if g['foden'] else '-',g['hgoals'],'| pos',g['pos'],g['pts'])
print(); [print(*row) for row in final[:8]]; print('...'); print('Haaland',hg)
