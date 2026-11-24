# Part 5: League One 2028/29, matchdays 24-46 (+ play-offs), after the January signings. Starts from Part 4's exact matchday-23 table (replayed here and asserted against ep4.json),
# then plays on with the new City model. The seed for the second half (2031) was fixed before running (Part 4's first half used 2029, the squad stats 2030).
# Set SIGN (the poll winner, replaces the second holding midfielder, slot 6) and LOAN (the comment-vote loan player: name, tier key or (gf, ga), slot index) before running.
import json, math, random, sys
from sim_l4 import T, teams, fixtures, play, upd, order, odds, P_H, P_F, H_SHARE, SEED as SEED1, MC, MK
import l4model as L
SEED2 = 2031
N5 = json.load(open('citymodel_l5.json')); E4 = json.load(open('ep4.json'))
SIGN = None    # e.g. 'Phillips' | 'Ward-Prowse' | 'Norwood'
LOAN = None    # e.g. {'name': 'X', 'tier': [gf, ga], 'slot': 7}  (slot: 0 GK, 1 RB, 2 CB, 3 CB, 4 LB, 5 DM, 6 DM, 7 RW, 8 AM, 9 LW, 10 ST)
TIERS = {k: tuple(v) for k, v in N5['tiers'].items()}
for nm, c in N5['candidates'].items(): TIERS[nm] = tuple(c['tier'])
def variants(xi):
    sw = L.swap
    mk = lambda x: L.team(x, TIERS)
    return {'full': mk(xi), 'no_haaland': mk(sw(xi, 10, 'u21')), 'no_foden': mk(sw(xi, 8, 'u21')), 'no_haaland_foden': mk(sw(sw(xi, 10, 'u21'), 8, 'u21'))}
def build(sign, loan):
    xi = list(N5.get('xi4') or L.XI4)
    if sign: xi[6] = sign
    if loan: TIERS['LOAN'] = tuple(loan['tier']); xi[loan['slot']] = 'LOAN'
    return variants(xi), xi
def replay_first_half():
    rounds = fixtures(SEED1); r = random.Random(SEED1); tab = {t: [0, 0, 0] for t in teams}
    for k, rd in enumerate(rounds[:23], 1):
        for h, a in rd:
            x, y, hp, fp = play(h, a, r, MC); upd(tab, h, a, x, y)
            if 'Manchester City' in (h, a):
                cg = x if h == 'Manchester City' else y
                sum(1 for _ in range(cg) if hp and r.random() < H_SHARE)
    md23 = [[i + 1, t, *tab[t]] for i, t in enumerate(order(tab))]
    assert md23 == [list(row) for row in E4['table_md23']], 'matchday-23 table differs from Part 4'
    return rounds, tab
def run():
    assert SIGN and LOAN, 'set SIGN and LOAN first'
    rounds, tab23 = replay_first_half(); rest = rounds[23:]
    M5, xi5 = build(SIGN, LOAN); M_sign, _ = build(SIGN, None); M_none = MC
    without = odds(rest, tab23, 10000, 9, MC); assert abs(without['promoted'] - E4['half_odds']['promoted']) < 1e-9, 'no-signing odds should reproduce Part 4'
    with_sign = odds(rest, tab23, 10000, 9, M_sign); with_both = odds(rest, tab23, 10000, 9, M5)
    r = random.Random(SEED2); tab = {t: list(v) for t, v in tab23.items()}; log = []; hg = E4['haaland']; cs = E4['clean_sheets']; snaps = {}
    for k, rd in enumerate(rest, 24):
        for h, a in rd:
            x, y, hp, fp = play(h, a, r, M5); upd(tab, h, a, x, y)
            if 'Manchester City' in (h, a):
                home = h == 'Manchester City'; cg, og = (x, y) if home else (y, x)
                hgo = sum(1 for _ in range(cg) if hp and r.random() < H_SHARE); hg += hgo; cs += og == 0
                log.append({'md': k, 'opp': a if home else h, 'venue': 'H' if home else 'A', 'score': f'{cg}-{og}', 'res': 'W' if cg > og else 'D' if cg == og else 'L',
                            'haaland': hp, 'foden': fp, 'hgoals': hgo, 'hg_total': hg, 'clean_sheets': cs})
        o = order(tab); log[-1]['pos'] = o.index('Manchester City') + 1; log[-1]['pts'] = tab['Manchester City'][0]
        snaps[k] = [[i + 1, t, tab[t][0], tab[t][1] - tab[t][2]] for i, t in enumerate(o)]
    final = [[i + 1, t, *tab[t]] for i, t in enumerate(order(tab))]; pos = order(tab).index('Manchester City') + 1
    def tie(a, b):
        legs = []; ga = gb = 0
        for hh, aa in ((a, b), (b, a)):
            x, y, _, _ = play(hh, aa, r, M5); legs.append([hh, aa, x, y])
            if hh == a: ga += x; gb += y
            else: gb += x; ga += y
        pens = ga == gb; win = a if ga > gb else b if gb > ga else (a if r.random() < .5 else b)
        return win, {'legs': legs, 'agg': [a, ga, b, gb], 'pens': pens, 'winner': win}
    po = None
    if 2 < pos <= 6:
        o = order(tab); w1, s1 = tie(o[2], o[5]); w2, s2 = tie(o[3], o[4]); x, y, _, _ = play(w1, w2, r, M5); pens = x == y
        fin = w1 if x > y else w2 if y > x else (w1 if r.random() < .5 else w2)
        po = {'semi1': s1, 'semi2': s2, 'final': {'teams': [w1, w2], 'score': [x, y], 'pens': pens, 'winner': fin}}
    promoted = pos <= 2 or (po is not None and po['final']['winner'] == 'Manchester City')
    res = {'seeds': [SEED1, SEED2], 'sign': SIGN, 'loan': LOAN, 'xi': xi5, 'odds_without': without, 'odds_with_sign': with_sign, 'odds_with_both': with_both, 'log': log, 'haaland': hg,
           'clean_sheets': cs, 'table_final': final, 'snaps': snaps, 'pos': pos, 'playoffs': po, 'promoted': promoted, 'champions': pos == 1, 'model': {'with_both': M5['full'], 'without': MC['full']}}
    json.dump(res, open('ep5.json', 'w'), indent=1)
    f = lambda d: {k: round(d[k], 3) if isinstance(d[k], float) else d[k] for k in ('title', 'auto', 'playoffs', 'promoted', 'avg_pts')}
    print('WITHOUT', f(without)); print('SIGNING', f(with_sign)); print('BOTH   ', f(with_both))
    for g in log: print(g['md'], g['venue'], g['opp'], g['score'], g['res'], '| pos', g['pos'], g['pts'])
    print('FINAL:'); [print(*row) for row in final[:8]]; print('City', pos, 'promoted', promoted, '| Haaland', hg, '| CS', cs)
    if po: print('PLAY-OFFS', json.dumps(po))
if __name__ == '__main__':
    run()
