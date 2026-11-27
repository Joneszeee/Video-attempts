"""Part 6 (season 4, Championship 2029/30): who is in the league and how strong City are. Same method as l4model.py (the stand-ins are today's real tables, Part 4's convention).
Championship 2029/30 = the real Championship today minus its top three (stand-ins for the clubs that went up to the Premier League: Middlesbrough, Stoke, Wolves) and its bottom three
(Preston, Burnley, Derby: already in League One in Part 4's season-3 sim), plus the real Premier League bottom three today (stand-ins for the clubs that came down: Sunderland, Manchester United,
Crystal Palace), plus City, MK Dons and Stockport County, who went up from League One in Part 5 (ep5_promotion.json). The 18 clubs that stay are rated by fitting the Championship's real results
(l4model.py, this season 1.0, last season 0.5); the three that come down by fitting the Premier League's real results the same way (espn_pl.json) and moving them onto the Championship scale with the
real Premier League v Championship cup ties (gap_pl.json); MK Dons and Stockport from their League One ratings (citymodel_l4.json) moved up with the Championship v League One cup ties (gap_ch.json).
City: the same XI as Part 5's second half with the fans' two picks, Jarrod Bowen (West Ham United, 54% of 616 votes) on the right wing and Jack Moylan (kept on a permanent deal, Cardiff City) on the left,
each rated at his real club's Championship level (the rule used for Ward-Prowse, Watts and McCracken); the academy players improve a third year at the same rate (GROW 0.20 compounds to 0.488).
Writes citymodel_c6.json."""
import json, math
import l4model as L
avg1, chv1, cc, hc, CHR = L.avg1, L.chv1, L.cc, L.hc, L.CHR
avgC = math.exp(cc + hc / 2); HAC = math.exp(hc / 2)
PLR = json.load(open('espn_pl.json')); GPL = json.load(open('gap_pl.json')); N4 = json.load(open('citymodel_l4.json')); P5 = json.load(open('ep5_promotion.json')); E5 = json.load(open('ep5.json'))
REAL_CH = json.load(open('real_eng2_table.json')); REAL_PL = json.load(open('real_eng1_table.json'))
pl_rows = [(h, a, hs, as_, 1.0 if d >= '2026-07-01' else 0.5) for d, h, a, hs, as_ in PLR]
cp, hp, attp, dep = L.fit(pl_rows); avgP = math.exp(cp + hp / 2)
def neutral_c(rows):   # rows: (goals for, goals against, was_home) from the Premier League side; per-game goals at a neutral venue (the Championship's home advantage)
    gf = ga = 0
    for a, b, home in rows:
        k = 1 / HAC if home else HAC; gf += a * k; ga += b / k
    return gf / len(rows), ga / len(rows)
plv = neutral_c([(r[0], r[1], r[2]) for r in GPL])            # an average Premier League side v an average Championship side
city_rows = [(r[0], r[1], r[2]) for r in GPL if r[4] == 'Manchester City']; cn = neutral_c(city_rows); ncity = len(city_rows)
def on_ch_from_pl(t): return {'att': attp[t] + math.log(plv[0] / avgC), 'def': dep[t] - math.log(plv[1] / avgC)}
def on_ch_from_l1(t): v = N4['teams'][t]; return {'att': v['att'] + math.log(chv1[1] / avgC), 'def': v['def'] - math.log(chv1[0] / avgC)}
# --- the league
CH_STAY = [r[1] for r in REAL_CH if 4 <= r[0] <= 21]; PL_DOWN = [r[1] for r in REAL_PL if r[0] >= 18]; L1_UP = [t for t in P5['promoted'] if t != 'Manchester City']
assert len(CH_STAY) == 18 and PL_DOWN == ['Sunderland', 'Manchester United', 'Crystal Palace'] and L1_UP == ['MK Dons', 'Stockport County'], (CH_STAY, PL_DOWN, L1_UP)
CH_UP = [r[1] for r in REAL_CH if r[0] <= 3]; CH_DOWN = [r[1] for r in REAL_CH if r[0] >= 22]
T = {t: {'att': CHR[t]['att'], 'def': CHR[t]['def']} for t in CH_STAY}
for t in PL_DOWN: T[t] = on_ch_from_pl(t)
for t in L1_UP: T[t] = on_ch_from_l1(t)
T['Manchester City'] = None
assert len(T) == 24
# --- City's tiers (goals for, against v an average Championship side, neutral venue)
fa, fd = chv1[1] / avg1, chv1[0] / avg1                      # an average Championship defence / attack v an average League One one
GROW1 = 0.20; GROW3 = 1 - (1 - GROW1) ** 3                    # the kids' third year: 0.488
u21 = N4['tiers']['u21']; u21raw = json.load(open('citymodel_l1.json'))['u21_raw']
gu = lambda x: math.exp(math.log(x) * (1 - GROW3) + math.log(avg1) * GROW3)
u21_l1 = (max(u21raw[0], gu(u21raw[0])), gu(u21raw[1]))      # on the League One scale, as l4model.py does it, with the third year of growth
tier_l1 = lambda t: (t[0] * fa, t[1] * fd)                    # a League One-scale tier moved onto the Championship scale
TIERS = {'city': ((ncity * cn[0] + 10 * plv[0]) / (ncity + 10), (ncity * cn[1] + 10 * plv[1]) / (ncity + 10)), 'pl': plv, 'u21': tier_l1(u21_l1), 'l2': tier_l1(tuple(N4['tiers']['l2'])),
         'watts': tier_l1(tuple(N4['tiers']['watts'])), 'mccracken': tier_l1(tuple(N4['tiers']['mccracken']))}
def ch_tier(club): r = CHR[club]; return (avgC * math.exp(r['att']), avgC * math.exp(-r['def']))
TIERS['ward'] = ch_tier('Southampton'); TIERS['bowen'] = ch_tier('West Ham United'); TIERS['moylan'] = ch_tier('Cardiff City')
POS = L.POS
XI6 = ['mccracken', 'city', 'watts', 'l2', 'city', 'pl', 'ward', 'bowen', 'city', 'moylan', 'city']      # GK RB CB CB LB DM DM RW AM LW ST (RW Bowen, LW Moylan: the two fan picks)
assert [E5['xi'][i] for i in range(11) if i not in (6, 7, 9)] == [XI6[i] for i in range(11) if i not in (6, 7, 9)]      # the rest of the XI is Part 5's
swap = L.swap
def variants(xi):
    mk = lambda x: L.team(x, TIERS)
    return {'full': mk(xi), 'no_haaland': mk(swap(xi, 10, 'u21')), 'no_foden': mk(swap(xi, 8, 'u21')), 'no_haaland_foden': mk(swap(swap(xi, 10, 'u21'), 8, 'u21'))}
SCEN = {'both': XI6, 'moylan_only': swap(XI6, 7, 'u21'), 'bowen_only': swap(XI6, 9, 'u21'), 'neither': swap(swap(XI6, 7, 'u21'), 9, 'u21')}
MODELS = {k: variants(xi) for k, xi in SCEN.items()}
out = {'avg': avgC, 'c': cc, 'home': hc, 'tiers': TIERS, 'plv': plv, 'chv1': chv1, 'avgP': avgP, 'pl_c_h': [cp, hp], 'city_ties': ncity, 'grow': [GROW1, GROW3],
       'stay': CH_STAY, 'came_down': PL_DOWN, 'came_up': L1_UP + ['Manchester City'], 'went_up': CH_UP, 'went_down': CH_DOWN,
       'teams': {t: (None if v is None else {'att': v['att'], 'def': v['def']}) for t, v in T.items()}, 'xi': XI6, 'models': MODELS}
json.dump(out, open('citymodel_c6.json', 'w'), indent=1)
if __name__ == '__main__':
    print('Championship base %.3f home %.3f (avg %.3f) | Premier League base %.3f home %.3f (avg %.3f)' % (cc, hc, avgC, cp, hp, avgP))
    print('PL v Championship (neutral) goals for %.2f against %.2f from %d cup ties; Man City alone %.2f / %.2f from %d ties' % (*plv, len(GPL), *cn, ncity))
    print('Championship v League One %.2f / %.2f; League One avg %.3f' % (*chv1, avg1))
    print('Championship 2029/30 on the Championship scale (att+def desc):')
    for t, v in sorted(T.items(), key=lambda kv: -(9 if kv[1] is None else kv[1]['att'] + kv[1]['def'])):
        print('  %-26s' % t, 'CITY' if v is None else '%+.2f %+.2f = %+.2f' % (v['att'], v['def'], v['att'] + v['def']), '<- from the Premier League' if t in PL_DOWN else '<- from League One' if t in L1_UP else '')
    print('went up (stand-ins)', CH_UP, '| went down', CH_DOWN)
    print('tiers (GF, GA v an average Championship side):', {k: tuple(round(x, 2) for x in v) for k, v in TIERS.items()})
    for k, m in MODELS.items(): print(k, {kk: tuple(round(x, 3) for x in vv) for kk, vv in m.items()})
