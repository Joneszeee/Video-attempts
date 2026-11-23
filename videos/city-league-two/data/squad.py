# Squad update (between Parts 4 and 5): a rating and simulated stats for every member of City's XI.
# - RATING: 60 + 80 x (goals per game he adds to City's goal difference v an average League One player in his slot), from the Part 4 model (citymodel_l4.json).
# - STATS: the sim records City's scores, Haaland's and Foden's availability and Haaland's goals (H_SHARE 38% of City's goals when he plays). Everything else is shared out here,
#   after the fact, with a seed fixed before running (SEED 2030) and no change to any published score: Haaland's goals stay as they were; every other City goal goes to a scorer
#   in proportion to the model's attack weight for his slot (POS: AM .15, wingers .15, DMs .07, full-backs .06, centre-backs .03; the ST slot only counts when a stand-in plays);
#   P_ASSIST of goals have an assist, shared by the same weights (never the scorer). Players play every league game of their tenure (the model has no other absences),
#   except Haaland and Foden, whose availability is the sim's own. Clean sheets and goals conceded come straight from the scores. League games only (no play-off or cup data exists).
import json, math, random
D = ''
O = json.load(open('official.json')); E2 = json.load(open('ep2.json')); E3 = json.load(open('ep3.json')); E4 = json.load(open('ep4.json'))
N = json.load(open('citymodel_l4.json'))
SEED = 2030                                   # fixed before running
LP = json.load(open('l1_players.json'))
G = sum((p['stats'].get('totalGoals') or 0) for p in LP); A = sum((p['stats'].get('goalAssists') or 0) for p in LP)
P_ASSIST = round(A / G, 2)                    # the real League One 2026/27 share of goals that carry an assist (ESPN rosters)
SEASONS = {1: O['log'], 2: E2['log'] + E3['log'], 3: E4['log']}
for s, lg in SEASONS.items():
    assert [g['md'] for g in lg] == list(range(1, len(lg) + 1)) and len(lg) == (23 if s == 3 else 46), s
SLOTS = ['GK', 'RB', 'CB1', 'CB2', 'LB', 'DM1', 'DM2', 'RW', 'AM', 'LW', 'ST']
W = dict(zip(SLOTS, [0, .06, .03, .03, .06, .07, .07, .15, .15, .15, .23]))   # the model's attack weights (POS in l1model.py)
def xi(season, md, hp, fp):
    return {'GK': 'McCracken' if season == 3 else 'Hudson', 'RB': 'Lewis', 'CB1': 'Watts' if season == 3 or (season == 2 and md >= 24) else 'Fitzwater', 'CB2': 'Scarr',
            'LB': "O'Reilly", 'DM1': 'Iroegbunam' if season >= 2 else 'Fapetu', 'DM2': 'Braybrooke', 'RW': 'McAidoo', 'AM': 'Foden' if fp else 'stand-in',
            'LW': 'T. Samba', 'ST': 'Haaland' if hp else 'stand-in'}
rng = random.Random(SEED)
def pick(slots, exclude=None):
    ws = [(s, W[s]) for s in slots if s != exclude and W[s] > 0]
    r = rng.random() * sum(w for _, w in ws)
    for s, w in ws:
        r -= w
        if r <= 0: return s
    return ws[-1][0]
st = {}
def S(name, season): return st.setdefault(name, {}).setdefault(season, {'apps': 0, 'goals': 0, 'assists': 0, 'cs': 0, 'conceded': 0})
for season in (1, 2, 3):
    for g in SEASONS[season]:
        cg, og = (int(x) for x in g['score'].split('-')); hp, fp = g['haaland'], g['foden']
        who = xi(season, g['md'], hp, fp)
        for slot, nm in who.items():
            r = S(nm, season); r['apps'] += 1
            if slot in ('GK', 'RB', 'CB1', 'CB2', 'LB'): r['cs'] += og == 0
            if slot == 'GK': r['conceded'] += og
        hg = g['hgoals'] if hp else 0
        assert hg <= cg
        for k in range(cg):
            if k < hg: scorer = 'ST'                       # Haaland's goals are the sim's own
            else: scorer = pick([s for s in SLOTS if not (s == 'ST' and hp)])
            S(who[scorer], season)['goals'] += 1
            if rng.random() < P_ASSIST: S(who[pick([s for s in SLOTS], exclude=scorer)], season)['assists'] += 1
# --- ratings
T = {k: tuple(v) for k, v in N['tiers'].items()}; avg = N['avg']; T['avg'] = (avg, avg)
POSW = [('GK', 0, .20), ('RB', .06, .11), ('CB', .03, .15), ('CB', .03, .15), ('LB', .06, .11), ('DM', .07, .10), ('DM', .07, .10), ('RW', .15, .03), ('AM', .15, .02), ('LW', .15, .03), ('ST', .23, 0)]
def team(x): return (math.exp(sum(w * math.log(T[t][0]) for (p, w, _), t in zip(POSW, x))), math.exp(sum(w * math.log(T[t][1]) for (p, _, w), t in zip(POSW, x))))
XI4 = N['xi']['ep4']; gf, ga = team(XI4)
NAMES = ['McCracken', 'Lewis', 'Watts', 'Scarr', "O'Reilly", 'Iroegbunam', 'Braybrooke', 'McAidoo', 'Foden', 'T. Samba', 'Haaland']
POSN = ['GK', 'RB', 'CB', 'CB', 'LB', 'DM', 'DM', 'RW', 'AM', 'LW', 'ST']
rating = {}
for i, nm in enumerate(NAMES):
    x = list(XI4); x[i] = 'avg'; gf2, ga2 = team(x); imp = (gf - gf2) + (ga2 - ga); rating[nm] = {'impact': round(imp, 4), 'ovr': round(60 + 80 * imp), 'pos': POSN[i], 'tier': XI4[i]}
out = {'seed': SEED, 'p_assist': P_ASSIST, 'ratings': rating, 'stats': {}, 'team': {'gf': gf, 'ga': ga}}
for nm in NAMES:
    per = st.get(nm, {}); tot = {k: sum(per.get(s, {}).get(k, 0) for s in (1, 2, 3)) for k in ('apps', 'goals', 'assists', 'cs', 'conceded')}
    out['stats'][nm] = {'seasons': {str(s): per.get(s) for s in (1, 2, 3)}, 'all': tot, 'now': per.get(3)}
json.dump(out, open('squad.json', 'w'), indent=1)
print('P_ASSIST', P_ASSIST, '(real League One assists', A, 'goals', G, ')')
print('%-11s %-3s %-4s | %-30s | %-30s' % ('', 'pos', 'ovr', 'THIS SEASON (apps G A CS GC)', 'ALL-TIME (apps G A CS GC)'))
for nm in sorted(NAMES, key=lambda n: -rating[n]['ovr']):
    a, n_ = out['stats'][nm]['all'], out['stats'][nm]['now']
    print('%-11s %-3s %-4d | %3d %3d %3d %3d %3d             | %3d %3d %3d %3d %3d' % (nm, rating[nm]['pos'], rating[nm]['ovr'], n_['apps'], n_['goals'], n_['assists'], n_['cs'], n_['conceded'], a['apps'], a['goals'], a['assists'], a['cs'], a['conceded']))
for s in (1, 2, 3):
    lg = SEASONS[s]; cgt = sum(int(g['score'].split('-')[0]) for g in lg)
    tot = sum(v[s]['goals'] for v in st.values() if s in v)
    print('season', s, 'City goals', cgt, 'allocated', tot, '| Haaland', st['Haaland'][s]['goals'], 'apps', st['Haaland'][s]['apps'], '| stand-in goals', st.get('stand-in', {}).get(s, {}).get('goals', 0))
