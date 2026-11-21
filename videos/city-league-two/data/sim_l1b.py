# Episode 3: League One 2027/28, matchdays 24-46 (+ play-offs), after the fans' January signing Kelland Watts.
# Starts from episode 2's exact matchday-23 table (replayed here and checked against ep2.json), then plays on with the Watts model.
import json, random, collections
from sim_l1 import M, teams, fixtures, play, upd, order, odds, sw, H_SHARE

SEED2, SEED3 = 2027, 2028          # episode 2's seed (to replay the first half), episode 3's seed (fixed before running)
EP2 = json.load(open('ep2.json'))
MW = dict(M)                       # City with Watts in place of one League Two centre-back (l1model.py: full_watts etc.)
for k in ('full', 'no_haaland', 'no_foden', 'no_haaland_foden'):
    MW[k] = M[k + '_watts']

rounds = fixtures(SEED2)
rounds_sw = [[(sw(h, k), sw(a, k)) for h, a in rd] for k, rd in enumerate(rounds, 1)]

# 1. replay the first half exactly as sim_l1.py did (same RNG draws), and check it matches episode 2
r = random.Random(SEED2); tab = {t: [0, 0, 0] for t in teams}
for k, rd in enumerate(rounds[:23], 1):
    for h0, a0 in rd:
        x, y, hp, fp = play(h0, a0, r); h, a = sw(h0, k), sw(a0, k); upd(tab, h, a, x, y)
        if 'Manchester City' in (h, a):
            cg = x if h == 'Manchester City' else y
            sum(1 for _ in range(cg) if hp and r.random() < H_SHARE)
md23 = [[i + 1, t, *tab[t]] for i, t in enumerate(order(tab))]
assert md23 == [list(row) for row in EP2['table_md23']], 'matchday-23 table differs from episode 2'
tab23 = {t: list(v) for t, v in tab.items()}

# 2. the odds for the second half, with and without Watts (same seed as episode 2's half_odds, so the runs are paired)
rest = rounds_sw[23:]
without = odds(rest, tab23, 10000, 9)
assert abs(without['promoted'] - EP2['half_odds']['promoted']) < 1e-9, 'no-Watts odds should reproduce episode 2'
withw = odds(rest, tab23, 10000, 9, MW)

# 3. the official run-in, played once
r = random.Random(SEED3); tab = {t: list(v) for t, v in tab23.items()}; log = []; hg = EP2['haaland']; cs = 0; snaps = {}
for k, rd in enumerate(rest, 24):
    for h, a in rd:
        x, y, hp, fp = play(h, a, r, MW); upd(tab, h, a, x, y)
        if 'Manchester City' in (h, a):
            home = h == 'Manchester City'; cg, og = (x, y) if home else (y, x)
            hgo = sum(1 for _ in range(cg) if hp and r.random() < H_SHARE); hg += hgo; cs += og == 0
            log.append({'md': k, 'opp': a if home else h, 'venue': 'H' if home else 'A', 'score': f'{cg}-{og}',
                        'res': 'W' if cg > og else 'D' if cg == og else 'L', 'haaland': hp, 'foden': fp, 'hgoals': hgo, 'hg_total': hg, 'clean_sheets': cs})
    o = order(tab); log[-1]['pos'] = o.index('Manchester City') + 1; log[-1]['pts'] = tab['Manchester City'][0]
    snaps[k] = [[i + 1, t, tab[t][0], tab[t][1] - tab[t][2]] for i, t in enumerate(o)]
final = [[i + 1, t, *tab[t]] for i, t in enumerate(order(tab))]
pos = order(tab).index('Manchester City') + 1

# 4. play-offs (3rd v 6th, 4th v 5th over two legs, then the final), the same rules the odds use; City's ties are logged
def tie(a, b):
    legs = []; ga = gb = 0
    for hh, aa in ((a, b), (b, a)):
        x, y, _, _ = play(hh, aa, r, MW); legs.append([hh, aa, x, y])
        if hh == a: ga += x; gb += y
        else: gb += x; ga += y
    pens = ga == gb
    win = a if ga > gb else b if gb > ga else (a if r.random() < .5 else b)
    return win, {'legs': legs, 'agg': [a, ga, b, gb], 'pens': pens, 'winner': win}
po = None
if 2 < pos <= 6:
    o = order(tab); w1, s1 = tie(o[2], o[5]); w2, s2 = tie(o[3], o[4])
    x, y, _, _ = play(w1, w2, r, MW); pens = x == y; fin = w1 if x > y else w2 if y > x else (w1 if r.random() < .5 else w2)
    po = {'semi1': s1, 'semi2': s2, 'final': {'teams': [w1, w2], 'score': [x, y], 'pens': pens, 'winner': fin}}
promoted = pos <= 2 or (po is not None and po['final']['winner'] == 'Manchester City')
champions = pos == 1

gfr = sorted(teams, key=lambda t: -tab[t][1]).index('Manchester City') + 1
gar = sorted(teams, key=lambda t: tab[t][2]).index('Manchester City') + 1
c23 = tab23['Manchester City']; cf = tab['Manchester City']
second_half = {'pts': cf[0] - c23[0], 'gf': cf[1] - c23[1], 'ga': cf[2] - c23[2]}
res = {'seeds': [SEED2, SEED3], 'odds_without_watts': without, 'odds_with_watts': withw, 'log': log, 'haaland': hg, 'clean_sheets': cs,
       'table_final': final, 'snaps': snaps, 'pos': pos, 'playoffs': po, 'promoted': promoted, 'champions': champions,
       'city_gf_rank': gfr, 'city_ga_rank': gar, 'second_half': second_half,
       'model': {k: MW[k] for k in ('full', 'no_haaland')} | {'tier_watts': M['tiers']['watts'], 'tier_l2': M['tiers']['l2']}}
json.dump(res, open('ep3.json', 'w'), indent=1)

f = lambda d: {k: round(d[k], 3) if isinstance(d[k], float) else d[k] for k in ('title', 'auto', 'playoffs', 'promoted', 'avg_pts')}
print('WITHOUT', f(without)); print('WITH   ', f(withw))
for g in log:
    print(g['md'], g['venue'], g['opp'], g['score'], g['res'], 'H' if g['haaland'] else '-', 'F' if g['foden'] else '-', g['hgoals'], '| pos', g['pos'], g['pts'])
print('FINAL:'); [print(*row) for row in final[:8]]; print('...'); print(*final[pos - 1])
print('City', pos, 'promoted', promoted, 'champions', champions, '| GF rank', gfr, 'GA rank', gar, '| Haaland', hg, '| clean sheets', cs, '| 2nd half', second_half)
if po: print('PLAY-OFFS', json.dumps(po))
