import json,sys
E=json.load(open('espn.json')); O=json.load(open('all.json'))
nm={'Manchester United':'Man United','Manchester City':'Man City','Brighton & Hove Albion':'Brighton','Wolverhampton Wanderers':'Wolves','Tottenham Hotspur':'Tottenham','Newcastle United':'Newcastle','Nottingham Forest':'Forest','West Ham United':'West Ham','Leicester City':'Leicester','Ipswich Town':'Ipswich','Leeds United':'Leeds','AFC Bournemouth':'Bournemouth'}
n=lambda x:nm.get(x,x)
def table(ms):
    T={}
    for m in ms:
        for t in (m['home'],m['away']): T.setdefault(t,dict(P=0,W=0,D=0,L=0,GF=0,GA=0,Pts=0))
        h,a=T[m['home']],T[m['away']]
        for x,y,gf,ga in ((h,a,m['hs'],m['as_']),(a,h,m['as_'],m['hs'])):
            x['P']+=1; x['GF']+=gf; x['GA']+=ga
            if gf>ga: x['W']+=1; x['Pts']+=3
            elif gf==ga: x['D']+=1; x['Pts']+=1
            else: x['L']+=1
    return sorted(T.items(), key=lambda kv:(-kv[1]['Pts'],-(kv[1]['GF']-kv[1]['GA']),-kv[1]['GF'],kv[0]))
def pens_order():
    L=[]
    for s in ['2024','2025']:
        for e in E[s]:
            for g in e['goals']:
                if g['team']=='Manchester United' and g['scorer']=='Bruno Fernandes' and g['pen']: L.append((e['id'],g['min']))
    return L
def simulate(pen_rule='quarter'):
    P=pens_order(); missed=set(P[3::4]) if pen_rule=='quarter' else (set() if pen_rule=='all_scored' else set(P))
    res={}; changes={}
    for s,os in [('2024','2024-25'),('2025','2025-26')]:
        ms=[dict(m) for m in O[os]]; ch=[]
        for e in E[s]:
            h,a=n(e['home']),n(e['away'])
            rm=[]; kept_pen=[]
            for g in e['goals']:
                if g['team']!='Manchester United': continue
                isG = g['scorer']=='Bruno Fernandes' and not g['og']; isA = bool(g['assist'] and 'Bruno' in g['assist'])
                if isG and g['pen']:
                    if (e['id'],g['min']) in missed: rm.append(g['min']+' pen MISSED by stand-in')
                    else: kept_pen.append(g['min'])
                elif isG or isA: rm.append(g['min']+(' G' if isG else ' A('+g['scorer']+')'))
            k=len(rm)
            for m in ms:
                if m['home']==h and m['away']==a:
                    old=(m['hs'],m['as_'])
                    if h=='Man United': m['hs']-=k
                    else: m['as_']-=k
                    if k or kept_pen:
                        uo=old[0] if h=='Man United' else old[1]; oo=old[1] if h=='Man United' else old[0]
                        un=uo-k
                        r=lambda u,o:'W' if u>o else 'D' if u==o else 'L'
                        ch.append(dict(date=e['date'],opp=a if h=='Man United' else h,venue='H' if h=='Man United' else 'A',real=f'{uo}-{oo}',sim=f'{un}-{oo}',rr=r(uo,oo),rs=r(un,oo),removed=rm,pen_kept=kept_pen))
        res[s]=table(ms); changes[s]=ch
    return res,changes,P,missed
if __name__=='__main__':
    for s,os in [('2024','2024-25'),('2025','2025-26')]:
        t=table(O[os]); i=[k for k,_ in t].index('Man United')
        print('REAL',os,'United pos',i+1,t[i][1]); print('  top:',[(k,v['Pts']) for k,v in t[:4]],' bottom:',[(k,v['Pts']) for k,v in t[-4:]])
