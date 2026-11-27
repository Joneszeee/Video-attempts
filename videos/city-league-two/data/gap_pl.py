"""Part 6: the Premier League -> Championship bridge. Cup ties (FA Cup + League Cup) between a Premier League club and a Championship club from the same season,
seen from the Premier League side: [goals for, goals against, was_home, season, premier league club, championship club].
League membership per season: leagues.json (2015-2025); 2026 = this season's clubs (Premier League from espn_pl.json, Championship from espn_ch.json). Same method as gap_ch.py."""
import json, collections
L = json.load(open('leagues.json')); G = json.load(open('espn_games.json')); C = json.load(open('espn_ch.json')); PL = json.load(open('espn_pl.json'))
def season(d): y, m = int(d[:4]), int(d[5:7]); return y if m >= 7 else y - 1
pl = {int(y): set(v['1']) for y, v in L.items() if '1' in v}; ch = {int(y): set(v['2']) for y, v in L.items() if '2' in v}
pl[2026] = {t for r in PL if r[0] >= '2026-07-01' for t in r[1:3]}; ch[2026] = {t for r in C if r[0] >= '2026-07-01' for t in r[1:3]}
rows = []
for lg in ('eng.fa', 'eng.league_cup'):
    for d, h, a, hs, as_ in G[lg]:
        y = season(d)
        if h in pl.get(y, ()) and a in ch.get(y, ()): rows.append([hs, as_, True, y, h, a])
        elif a in pl.get(y, ()) and h in ch.get(y, ()): rows.append([as_, hs, False, y, a, h])
json.dump(rows, open('gap_pl.json', 'w'))
by = collections.defaultdict(list)
for r in rows: by[r[3]].append(r)
for y in sorted(by):
    v = by[y]; n = len(v)
    print(y, n, 'GF %.2f GA %.2f' % (sum(r[0] for r in v) / n, sum(r[1] for r in v) / n), 'W%d D%d L%d' % (sum(r[0] > r[1] for r in v), sum(r[0] == r[1] for r in v), sum(r[0] < r[1] for r in v)))
print(len(rows), 'ties; 2026 clubs', len(pl[2026]), len(ch[2026]))
