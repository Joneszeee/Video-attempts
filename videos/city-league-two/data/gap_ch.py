"""Part 4: the Championship -> League One bridge. Cup ties (FA Cup + League Cup) between a Championship club and a League One club
from the same season, seen from the Championship side: [goals for, goals against, was_home, season, championship club, league one club].
League membership per season: leagues.json (2015-2025); 2026 = this season's clubs (Championship from espn_ch.json, League One from leagues.json)."""
import json, collections
L = json.load(open('leagues.json')); G = json.load(open('espn_games.json')); C = json.load(open('espn_ch.json'))
def season(d): y, m = int(d[:4]), int(d[5:7]); return y if m >= 7 else y - 1
ch = {int(y): set(v['2']) for y, v in L.items() if '2' in v}
ch[2026] = {t for r in C if r[0] >= '2026-07-01' for t in r[1:3]}
l1 = {int(y): set(v['3']) for y, v in L.items() if '3' in v}
rows = []
for lg in ('eng.fa', 'eng.league_cup'):
    for d, h, a, hs, as_ in G[lg]:
        y = season(d)
        if h in ch.get(y, ()) and a in l1.get(y, ()): rows.append([hs, as_, True, y, h, a])
        elif a in ch.get(y, ()) and h in l1.get(y, ()): rows.append([as_, hs, False, y, a, h])
json.dump(rows, open('gap_ch.json', 'w'))
by = collections.defaultdict(list)
for r in rows: by[r[3]].append(r)
for y in sorted(by):
    v = by[y]; n = len(v)
    print(y, n, 'GF %.2f GA %.2f' % (sum(r[0] for r in v) / n, sum(r[1] for r in v) / n), 'W%d D%d L%d' % (sum(r[0] > r[1] for r in v), sum(r[0] == r[1] for r in v), sum(r[0] < r[1] for r in v)))
print(len(rows), 'ties; 2026 clubs', len(ch[2026]), sorted(ch[2026])[:3])
