import re,json,sys
def norm(n):
    n=n.strip(); n=re.sub(r'\s+FC$','',n); n=n.replace('AFC ','')
    return {'Manchester United':'Man United','Manchester City':'Man City','Brighton & Hove Albion':'Brighton','Wolverhampton Wanderers':'Wolves','Tottenham Hotspur':'Tottenham','Newcastle United':'Newcastle','Nottingham Forest':'Forest','West Ham United':'West Ham','Leicester City':'Leicester','Ipswich Town':'Ipswich','Leeds United':'Leeds','Chelsea FC':'Chelsea'}.get(n,n)
def parse(path):
    L=open(path).read().split('\n'); ms=[]; date=None
    i=0
    while i<len(L):
        l=L[i]
        m=re.match(r'\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\w+ \d+)(?: (\d{4}))?\s*$',l)
        if m: date=m.group(1)
        m=re.match(r'\s*(?:\d\d:\d\d)?\s+(.+?)\s+v\s+(.+?)\s+(\d+)-(\d+)',l) or re.match(r'\s*(?:\d\d:\d\d)?\s+(.+?)\s+(\d+)-(\d+)(?:\s+\(\d+-\d+\))?\s+(.+?)\s*$',l)
        if m:
            g=m.groups()
            if ' v ' in l: h,a,hs,as_=g[0],g[1],int(g[2]),int(g[3])
            else: h,hs,as_,a=g[0],int(g[1]),int(g[2]),g[3]
            sc=''
            j=i+1
            while j<len(L) and L[j].strip().startswith(('(', )) or (j<len(L) and L[j].startswith('                   ') and sc):
                sc+=L[j].strip()+' '; j+=1
                if sc.rstrip().endswith(')'): break
            ms.append(dict(date=date,home=norm(h),away=norm(a),hs=hs,as_=as_,scorers=sc.strip()))
        i+=1
    return ms
out={}
for s in ['2024-25','2025-26']:
    ms=parse(f'pl-{s}.txt'); out[s]=ms
    utd=[m for m in ms if 'Man United' in (m['home'],m['away'])]
    print(s,len(ms),'matches; United',len(utd))
json.dump(out,open('all.json','w'),indent=0)
