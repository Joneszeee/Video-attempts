# Part 6: Championship 2029/30 (season 4), the first five matchdays, with the fans' two picks (Jarrod Bowen on the right wing, Jack Moylan on the left on a permanent deal).
# The league and the ratings come from c6model.py (citymodel_c6.json). Same engine as sim_l4.py: Poisson goals from att/def ratings, Haaland and Foden available 90% / 85% of games,
# 10,000-run odds, then one official run played once. The seed (2034) and the number of matchdays (5) were fixed before running (plan.md, 27 Nov 2026).
import json, math, random, collections
N = json.load(open('citymodel_c6.json'))
c, hm = N['c'], N['home']; avg = N['avg']
T = {t: (v['att'], v['def']) for t, v in N['teams'].items() if v}; T['Manchester City'] = None
teams = sorted(T); assert len(teams) == 24
P_H, P_F, H_SHARE = 0.90, 0.85, 0.38
SEED = 2034; MDS = 5
M = N['models']; MB = M['both']
def city_rates(h, f, m):
    k = 'full' if h and f else 'no_foden' if h else 'no_haaland' if f else 'no_haaland_foden'
    gf, ga = m[k]; return math.log(gf / avg), -math.log(ga / avg)
def pois(l, r):
    L = math.exp(-l); k = 0; p = 1.0
    while True:
        p *= r.random()
        if p <= L: return k
        k += 1
def play(h, a, r, m):
    hp = fp = True; cr = None
    if 'Manchester City' in (h, a): hp = r.random() < P_H; fp = r.random() < P_F; cr = city_rates(hp, fp, m)
    ah, dh = cr if h == 'Manchester City' else T[h]; aa, da = cr if a == 'Manchester City' else T[a]
    return pois(math.exp(c + hm + ah - da), r), pois(math.exp(c + aa - dh), r), hp, fp
def fixtures(seed):
    fx = random.Random(seed + 1).sample(teams, len(teams)); n = len(fx); rounds = []; last = {}; homes = {}; arr = fx[:]
    for k in range(n - 1):
        rd = []
        for i in range(n // 2):
            a, b = arr[i], arr[n - 1 - i]; la, lb = last.get(a), last.get(b)
            if la == 'A' and lb != 'A': h_, a_ = a, b
            elif lb == 'A' and la != 'A': h_, a_ = b, a
            else: h_, a_ = (a, b) if homes.get(a, 0) <= homes.get(b, 0) else (b, a)
            rd.append((h_, a_)); last[h_] = 'H'; last[a_] = 'A'; homes[h_] = homes.get(h_, 0) + 1
        rounds.append(rd); arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    return rounds + [[(b, a) for a, b in rd] for rd in rounds]
def upd(tab, h, a, x, y):
    for t, gf, ga in ((h, x, y), (a, y, x)):
        s = tab[t]; s[1] += gf; s[2] += ga; s[0] += 3 if gf > ga else 1 if gf == ga else 0
def order(tab): return sorted(teams, key=lambda t: (-tab[t][0], -(tab[t][1] - tab[t][2]), -tab[t][1], t))
def finish(tab, rounds_left, r, m):
    tab = {t: list(v) for t, v in tab.items()}
    for rd in rounds_left:
        for h, a in rd: x, y, _, _ = play(h, a, r, m); upd(tab, h, a, x, y)
    o = order(tab); pos = o.index('Manchester City') + 1
    def tie(a, b):
        ga = gb = 0
        for hh, aa in ((a, b), (b, a)):
            x, y, _, _ = play(hh, aa, r, m)
            if hh == a: ga += x; gb += y
            else: gb += x; ga += y
        return a if ga > gb else b if gb > ga else (a if r.random() < .5 else b)
    w1 = tie(o[2], o[5]); w2 = tie(o[3], o[4]); x, y, _, _ = play(w1, w2, r, m)
    fin = w1 if x > y else w2 if y > x else (w1 if r.random() < .5 else w2)
    return pos, pos <= 2 or fin == 'Manchester City', tab['Manchester City'][0], o, fin
def odds(rounds, tab0, n, seed, m, clubs=False):
    r = random.Random(seed); P = collections.Counter(); up = 0; pts = []; title = collections.Counter(); prom = collections.Counter()
    for _ in range(n):
        pos, u, p, o, fin = finish(tab0, rounds, r, m); P[pos] += 1; up += u; pts.append(p)
        title[o[0]] += 1
        for t in (o[0], o[1], fin): prom[t] += 1
    pts.sort()
    res = {'title': P[1] / n, 'auto': (P[1] + P[2]) / n, 'playoffs': sum(P[k] for k in range(3, 7)) / n, 'promoted': up / n, 'avg_pts': sum(pts) / n,
           'pts_10_90': (pts[n // 10], pts[9 * n // 10]), 'pos': {k: v / n for k, v in sorted(P.items())}}
    if clubs: res['clubs'] = {t: {'title': title[t] / n, 'promoted': prom[t] / n} for t in teams}
    return res
if __name__ == '__main__':
    rounds = fixtures(SEED); empty = {t: [0, 0, 0] for t in teams}
    derby = next(k for k, rd in enumerate(rounds, 1) if ('Manchester City', 'Manchester United') in rd or ('Manchester United', 'Manchester City') in rd)
    print('Manchester derby fixtures: matchday', derby, [(k, h, a) for k, rd in enumerate(rounds, 1) for h, a in rd if {h, a} == {'Manchester City', 'Manchester United'}])
    pre = {k: odds(rounds, empty, 10000, 7, M[k], clubs=(k == 'both')) for k in ('neither', 'moylan_only', 'bowen_only', 'both')}
    r = random.Random(SEED); tab = {t: [0, 0, 0] for t in teams}; log = []; hg = 0; cs = 0; snaps = {}; results = {}
    for k, rd in enumerate(rounds[:MDS], 1):
        results[k] = []
        for h, a in rd:
            x, y, hp, fp = play(h, a, r, MB); upd(tab, h, a, x, y); results[k].append([h, a, x, y])
            if 'Manchester City' in (h, a):
                home = h == 'Manchester City'; cg, og = (x, y) if home else (y, x)
                hgo = sum(1 for _ in range(cg) if hp and r.random() < H_SHARE); hg += hgo; cs += og == 0
                log.append({'md': k, 'opp': a if home else h, 'venue': 'H' if home else 'A', 'score': f'{cg}-{og}', 'res': 'W' if cg > og else 'D' if cg == og else 'L',
                            'haaland': hp, 'foden': fp, 'hgoals': hgo, 'hg_total': hg, 'clean_sheets': cs})
        o = order(tab); log[-1]['pos'] = o.index('Manchester City') + 1; log[-1]['pts'] = tab['Manchester City'][0]
        snaps[k] = [[i + 1, t, tab[t][0], tab[t][1] - tab[t][2], tab[t][1]] for i, t in enumerate(o)]
    o = order(tab); after = odds(rounds[MDS:], tab, 10000, 9, MB, clubs=True)
    res = {'seed': SEED, 'mds': MDS, 'fixtures': rounds, 'derby_md': derby, 'pre': pre, 'log': log, 'haaland': hg, 'clean_sheets': cs, 'results': results, 'snaps': snaps,
           'table_md5': [[i + 1, t, *tab[t]] for i, t in enumerate(o)], 'odds_after': after, 'model': {'both': MB['full'], 'neither': M['neither']['full']}, 'xi': N['xi']}
    json.dump(res, open('ep6.json', 'w'), indent=1)
    f = lambda d: {k: round(d[k], 3) if isinstance(d[k], float) else d[k] for k in ('title', 'auto', 'playoffs', 'promoted', 'avg_pts', 'pts_10_90')}
    for k, v in pre.items(): print('PRE %-12s' % k, f(v))
    print('Title odds (both) top 8:', sorted(((round(v['title'], 3), t) for t, v in pre['both']['clubs'].items()), reverse=True)[:8])
    print('Promotion odds (both) top 8:', sorted(((round(v['promoted'], 3), t) for t, v in pre['both']['clubs'].items()), reverse=True)[:8])
    for g in log: print(g['md'], g['venue'], g['opp'], g['score'], g['res'], 'H' if g['haaland'] else '-', 'F' if g['foden'] else '-', g['hgoals'], '| pos', g['pos'], g['pts'])
    print('MD%d table:' % MDS); [print(*row) for row in res['table_md5']]
    print('AFTER odds', f(after)); print('Haaland', hg, 'clean sheets', cs)
