"""Part 4 (season 3, League One 2028/29): who is in the league and how strong City are.
League One 2028/29 = the 2027/28 league (sim_l1.py) minus the 3 promoted (Oxford, Sheffield Wednesday, Bradford) and the 4 relegated (the bottom four:
Blackpool, Notts County, Wigan, Doncaster), plus 3 clubs from the Championship (stand-ins: the real bottom three today, Burnley, Derby, Preston; rated
by fitting the Championship's real results and moving them onto the League One scale with the cup-tie bridge in gap_ch.json) and 4 from League Two
(stand-ins: the four best-rated League Two clubs after Barnet and Grimsby, who came up in episode 1; moved onto the League One scale exactly as
Grimsby and Barnet were in l1model.py). City: Jon McCracken (the fans' pick, rated at Bradford's real League One level) replaces the League Two keeper,
and the academy players improve for a second year at the same rate as the first (GROW 0.20 compounds to 0.36)."""
import json, math, numpy as np
R1 = json.load(open('l1ratings.json')); R2 = json.load(open('l2ratings.json')); M = json.load(open('citymodel_l1.json'))
X = json.load(open('gap_l1.json')); CHL1 = json.load(open('gap_ch.json')); CH = json.load(open('espn_ch.json'))
c1, h1 = R1['c'], R1['home']; HA1 = math.exp(h1 / 2); avg1 = M['avg']
def fit(rows, lam=2.0):   # the same ridge-regularised Poisson fit l1model.py used for League One
    teams = sorted({r[0] for r in rows} | {r[1] for r in rows}); ix = {t: i for i, t in enumerate(teams)}; n = len(teams)
    H = np.array([ix[r[0]] for r in rows]); A = np.array([ix[r[1]] for r in rows]); HS = np.array([r[2] for r in rows], float); AS = np.array([r[3] for r in rows], float); Wt = np.array([r[4] for r in rows])
    c, hm = 0.2, 0.1; att = np.zeros(n); de = np.zeros(n); lr = 0.002
    for it in range(20000):
        m1 = np.exp(c + hm + att[H] - de[A]); m2 = np.exp(c + att[A] - de[H]); r1 = Wt * (m1 - HS); r2 = Wt * (m2 - AS)
        c -= lr * (r1.sum() + r2.sum()) / 10; hm -= lr * r1.sum() / 10
        att -= lr * (np.bincount(H, r1, n) + np.bincount(A, r2, n) + 2 * lam * att); de -= lr * (-np.bincount(A, r1, n) - np.bincount(H, r2, n) + 2 * lam * de)
    return c, hm, dict(zip(teams, att)), dict(zip(teams, de))
def neutral(rows):   # rows: (goals for, goals against, was_home) from the stronger league's side; returns per-game goals at a neutral venue
    gf = ga = 0
    for a, b, home in rows:
        k = 1 / HA1 if home else HA1; gf += a * k; ga += b / k
    return gf / len(rows), ga / len(rows)
# Championship ratings from real results (the same weights as League One: this season 1.0, last season 0.5; play-offs dropped)
ch_rows = [(h, a, hs, as_, 1.0 if d >= '2026-07-01' else 0.5) for d, h, a, hs, as_ in CH if not ('2026-05-04' <= d < '2026-07-01')]
cc, hc, attc, dec = fit(ch_rows)
CHR = {t: {'att': attc[t], 'def': dec[t]} for t in attc}
chv1 = neutral([(r[0], r[1], r[2]) for r in CHL1])          # an average Championship side v an average League One side
l1v2 = tuple(M['l1v2']); l2avg_vs_l1 = (l1v2[1], l1v2[0])  # an average League Two side v an average League One side (from l1model.py)
def on_l1_scale(t, league):
    if league == 'ch':
        a, d = CHR[t]['att'], CHR[t]['def']; g = chv1
    else:
        a, d = R2['teams'][t]['att'], R2['teams'][t]['def']; g = l2avg_vs_l1
    return {'att': math.log(g[0] / avg1) + a, 'def': -math.log(g[1] / avg1) + d}
OUT_PROMOTED = ['Oxford United', 'Sheffield Wednesday', 'Bradford City']
OUT_RELEGATED = ['Blackpool', 'Notts County', 'Wigan Athletic', 'Doncaster Rovers']
IN_CH = ['Burnley', 'Derby County', 'Preston North End']
IN_L2 = [t for t, _ in sorted(R2['teams'].items(), key=lambda kv: -(kv[1]['att'] + kv[1]['def'])) if t not in ('Grimsby Town', 'Barnet')][:4]
# the 2027/28 league (sim_l1.py's 24 clubs) -> 2028/29
OUT27 = ['Bromley', 'Barnsley', 'Peterborough United']
T27 = {t: v for t, v in R1['teams'].items() if t not in OUT27}; T27['Manchester City'] = None
T28 = {t: v for t, v in T27.items() if t not in OUT_PROMOTED + OUT_RELEGATED}
for t in IN_CH: T28[t] = on_l1_scale(t, 'ch')
for t in IN_L2: T28[t] = on_l1_scale(t, 'l2')
assert len(T28) == 24 and 'Manchester City' in T28, len(T28)
# City: tiers (goals for, against v an average League One side), McCracken and the kids' second year
TIERS = {k: tuple(v) for k, v in M['tiers'].items()}
GROW1 = 0.20; GROW2 = 1 - (1 - GROW1) ** 2    # the same yearly gain, compounded over two years = 0.36
u21 = M['u21_raw']
# Growth only ever improves a rating: each one closes GROW2 of its gap to an average League One player, and a rating already better than average
# holds. (Part 2/3's rule also pulled the kids' goals-for DOWN towards the average, 1.42 -> 1.40, although they out-score the average; that was
# a small flaw in the first year's growth, fixed here without touching the published seasons.)
gu = lambda x: math.exp(math.log(x) * (1 - GROW2) + math.log(avg1) * GROW2)
TIERS['u21'] = (max(u21[0], gu(u21[0])), gu(u21[1]))
br = R1['teams']['Bradford City']
TIERS['mccracken'] = (avg1 * math.exp(br['att']), avg1 * math.exp(-br['def']))   # rated at his real club's League One level
POS = [('GK', 0, .20), ('RB', .06, .11), ('CB', .03, .15), ('CB', .03, .15), ('LB', .06, .11), ('DM', .07, .10), ('DM', .07, .10), ('RW', .15, .03), ('AM', .15, .02), ('LW', .15, .03), ('ST', .23, 0)]
def team(xi, T=None):
    T = T or TIERS
    return (math.exp(sum(w * math.log(T[t][0]) for (p, w, _), t in zip(POS, xi))), math.exp(sum(w * math.log(T[t][1]) for (p, _, w), t in zip(POS, xi))))
def swap(xi, i, t): x = list(xi); x[i] = t; return x
#        GK          RB      CB       CB    LB      DM    DM    RW     AM      LW     ST
XI3 = ['l2', 'city', 'watts', 'l2', 'city', 'pl', 'l2', 'u21', 'city', 'u21', 'city']   # episode 3's XI (Watts in, the League Two keeper in goal)
XI4 = swap(XI3, 0, 'mccracken')
def variants(xi):
    return {'full': team(xi), 'no_haaland': team(swap(xi, 10, 'u21')), 'no_foden': team(swap(xi, 8, 'u21')), 'no_haaland_foden': team(swap(swap(xi, 10, 'u21'), 8, 'u21'))}
MODELS = {'ep3': variants(XI3), 'kids_only': variants(XI3), 'mccracken': variants(XI4)}
# 'ep3' = last season's City exactly (kids at GROW 0.20), 'kids_only' = second-year kids but the League Two keeper, 'mccracken' = the real Part 4 City
T_ep3 = dict(TIERS); T_ep3['u21'] = tuple(M['tiers']['u21'])
MODELS['ep3'] = {k: team(xi, T_ep3) for k, xi in (('full', XI3), ('no_haaland', swap(XI3, 10, 'u21')), ('no_foden', swap(XI3, 8, 'u21')), ('no_haaland_foden', swap(swap(XI3, 10, 'u21'), 8, 'u21')))}
out = {'avg': avg1, 'HA': HA1, 'champ_c_h': [cc, hc], 'chv1': chv1, 'l2avg_vs_l1': l2avg_vs_l1, 'ch_cup_ties': len(CHL1), 'tiers': TIERS, 'grow': [GROW1, GROW2],
       'out_promoted': OUT_PROMOTED, 'out_relegated': OUT_RELEGATED, 'in_ch': IN_CH, 'in_l2': IN_L2,
       'teams': {t: (None if v is None else {'att': v['att'], 'def': v['def']}) for t, v in T28.items()}, 'models': MODELS, 'xi': {'ep3': XI3, 'ep4': XI4}}
json.dump(out, open('citymodel_l4.json', 'w'), indent=1)
if __name__ == '__main__':
    print('Championship fit: base %.3f home %.3f ; ch v l1 (neutral) goals for %.2f against %.2f from %d cup ties' % (cc, hc, chv1[0], chv1[1], len(CHL1)))
    print('avg1 %.3f; l2 avg v l1 %s' % (avg1, tuple(round(x, 2) for x in l2avg_vs_l1)))
    print('Championship ratings, worst 8 by att+def:'); [print('  %-24s %+.2f %+.2f' % (t, v['att'], v['def'])) for t, v in sorted(CHR.items(), key=lambda kv: kv[1]['att'] + kv[1]['def'])[:8]]
    print('League One 2028/29 clubs on the League One scale (att+def desc):')
    for t, v in sorted(T28.items(), key=lambda kv: -(9 if kv[1] is None else kv[1]['att'] + kv[1]['def'])):
        print('  %-22s' % t, 'CITY' if v is None else '%+.2f %+.2f = %+.2f' % (v['att'], v['def'], v['att'] + v['def']), '<- from Championship' if t in IN_CH else '<- from League Two' if t in IN_L2 else '')
    print('promoted out', OUT_PROMOTED, '| relegated out', OUT_RELEGATED, '| in from Championship', IN_CH, '| in from League Two', IN_L2)
    print('tiers (GF, GA v average L1):', {k: tuple(round(x, 2) for x in v) for k, v in TIERS.items()})
    for k, m in MODELS.items(): print(k, {kk: tuple(round(x, 3) for x in vv) for kk, vv in m.items()})
