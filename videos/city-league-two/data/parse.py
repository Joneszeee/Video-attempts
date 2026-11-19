import json,glob,re
def norm(n):
    n=re.sub(r'\s+',' ',n).strip()
    for s in (' U21',' U23',' FC',' AFC',' A.F.C.',' F.C.'): n=n.replace(s,'')
    n=n.replace('AFC ','').strip()
    al={'Milton Keynes Dons':'MK Dons','Brighton & Hove Albion':'Brighton','Brighton and Hove Albion':'Brighton','Wolves':'Wolverhampton Wanderers','Man City':'Manchester City','Man United':'Manchester United',
        'Tottenham':'Tottenham Hotspur','Newcastle':'Newcastle United','West Ham':'West Ham United','Leicester':'Leicester City','Nottingham':'Nottingham Forest',"Nott'm Forest":'Nottingham Forest',
        'Bournemouth':'AFC Bournemouth','Sheffield Utd':'Sheffield United','Leeds':'Leeds United','Ipswich':'Ipswich Town','Norwich':'Norwich City','Luton':'Luton Town','Cardiff':'Cardiff City','Huddersfield':'Huddersfield Town','Swansea':'Swansea City','Stoke':'Stoke City','Hull':'Hull City','West Brom':'West Bromwich Albion','Sunderland AFC':'Sunderland'}
    return al.get(n,n)
P1=re.compile(r'^\s*(?:\d\d[:.]\d\d\s+)?(.+?)\s+v\s+(.+?)\s+(\d+)-(\d+)\b')
P2=re.compile(r'^\s*(?:\d\d[:.]\d\d\s+)?(.+?)\s{2,}(\d+)-(\d+)(?:\s*\(\d+-\d+\))?\s{2,}(.+?)\s*$')
def matches(path):
    M=[]
    for line in open(path):
        if line.lstrip().startswith(('#','=','▪')): continue
        m=P1.match(line)
        if m: M.append((norm(m.group(1)),norm(m.group(2)),int(m.group(3)),int(m.group(4)))); continue
        m=P2.match(line)
        if m: M.append((norm(m.group(1)),norm(m.group(4)),int(m.group(2)),int(m.group(3))))
    return M
L={};R={}
for f in glob.glob('of/*.txt'):
    s,lg=f[3:].split('_',1); y=int(s[:4]); M=matches(f)
    L.setdefault(y,{})[lg[:1]]=sorted({t for m in M for t in m[:2]}); R.setdefault(y,{})[lg[:1]]=M
for lg,fn in (('4','l2teams.json'),('3','l1teams.json')):
    d=json.load(open(fn)); L.setdefault(2026,{})[lg]=sorted({norm(t['team']['displayName']) for t in d['sports'][0]['leagues'][0]['teams']})
json.dump(L,open('leagues.json','w')); json.dump(R,open('results.json','w'))
print({y:{k:(len(v),len(R.get(y,{}).get(k,[]))) for k,v in sorted(m.items())} for y,m in sorted(L.items())})
print(L[2026]['4'])
