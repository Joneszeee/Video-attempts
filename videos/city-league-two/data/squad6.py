# Part 6 squad numbers: ratings (Championship scale) and the simulated stats for the first five matchdays (ep6.json), shared out with seed 2036 (written into plan.md before running).
# - RATING: 60 + 80 x (goals per game a player adds to City's goal difference v an average Championship player in his slot), from the Part 6 model (Bowen at West Ham's level, Moylan at Cardiff's).
# - STATS: same method as squad5.py. Haaland's goals are the sim's own (hgoals); every other City goal goes to a scorer in proportion to the model's attack weight for his slot,
#   P_ASSIST of goals carry an assist (shared by the same weights, never the scorer); players play every league game (Haaland and Foden by the sim's own availability). No published score changes.
# - UPGRADE: how much City's goal difference per game would rise if a slot were filled by an average Premier League player (the weak spot for the next vote).
import json, math, random
import l4model as L
import c6model as C
E6 = json.load(open('ep6.json')); Q = json.load(open('squad.json'))
SEED = 2036
P_ASSIST = Q['p_assist']
SLOTS = ['GK', 'RB', 'CB1', 'CB2', 'LB', 'DM1', 'DM2', 'RW', 'AM', 'LW', 'ST']
W = dict(zip(SLOTS, [0, .06, .03, .03, .06, .07, .07, .15, .15, .15, .23]))
NAMES = ['McCracken', 'Lewis', 'Watts', 'Scarr', "O'Reilly", 'Iroegbunam', 'Ward-Prowse', 'Bowen', 'Foden', 'Moylan', 'Haaland']
assert [g['md'] for g in E6['log']] == list(range(1, 6)) and E6['seed'] == 2034
def xi(hp, fp):
    d = dict(zip(SLOTS, NAMES)); d['AM'] = 'Foden' if fp else 'stand-in'; d['ST'] = 'Haaland' if hp else 'stand-in'; return d
rng = random.Random(SEED)
def pick(slots, exclude=None):
    ws = [(s, W[s]) for s in slots if s != exclude and W[s] > 0]
    r = rng.random() * sum(w for _, w in ws)
    for s, w in ws:
        r -= w
        if r <= 0: return s
    return ws[-1][0]
st = {}; goals = []
def Sx(n): return st.setdefault(n, {'apps': 0, 'goals': 0, 'assists': 0, 'cs': 0, 'conceded': 0})
for g in E6['log']:
    cg, og = (int(x) for x in g['score'].split('-')); hp, fp = g['haaland'], g['foden']; who = xi(hp, fp)
    for slot, nm in who.items():
        r = Sx(nm); r['apps'] += 1
        if slot in ('GK', 'RB', 'CB1', 'CB2', 'LB'): r['cs'] += og == 0
        if slot == 'GK': r['conceded'] += og
    hg = g['hgoals'] if hp else 0
    assert hg <= cg
    for k in range(cg):
        scorer = 'ST' if k < hg else pick([s for s in SLOTS if not (s == 'ST' and hp)])
        Sx(who[scorer])['goals'] += 1; ast = None
        if rng.random() < P_ASSIST: ast = who[pick(SLOTS, exclude=scorer)]; Sx(ast)['assists'] += 1
        goals.append({'md': g['md'], 'opp': g['opp'], 'scorer': who[scorer], 'assist': ast})
# ---- ratings and the upgrade analysis, on the Championship scale
T = dict(C.TIERS); avg = C.avgC; T['avg'] = (avg, avg); T['pl'] = tuple(C.plv)
XI = E6['xi']; gf, ga = L.team(XI, T)
rating, upgrade = {}, {}
for i, nm in enumerate(NAMES):
    x = list(XI); x[i] = 'avg'; g2, a2 = L.team(x, T); imp = (gf - g2) + (a2 - ga)
    y = list(XI); y[i] = 'pl'; g3, a3 = L.team(y, T)
    rating[nm] = {'impact': round(imp, 4), 'ovr': round(60 + 80 * imp), 'pos': SLOTS[i][:2] if SLOTS[i][:2] != 'DM' else 'DM'}; upgrade[nm] = round((g3 - gf) + (ga - a3), 4)
out = {'seed': SEED, 'p_assist': P_ASSIST, 'ratings': rating, 'upgrade_to_premier_league_average': upgrade, 'stats_five_games': {n: st[n] for n in NAMES}, 'stand_in': st.get('stand-in'), 'goals': goals, 'team': {'gf': gf, 'ga': ga}}
json.dump(out, open('squad6.json', 'w'), indent=1)
if __name__ == '__main__':
    print('P_ASSIST', P_ASSIST, '| City v an average Championship side: %.3f for, %.3f against' % (gf, ga))
    print('%-12s %-3s %-4s | %-22s | upgrade to an average Premier League player' % ('', 'pos', 'ovr', 'MD1-5 apps G A CS GC'))
    for nm in sorted(NAMES, key=lambda n: -rating[n]['ovr']):
        s = st[nm]; print('%-12s %-3s %-4d | %3d %3d %3d %3d %3d      | %+.3f' % (nm, rating[nm]['pos'], rating[nm]['ovr'], s['apps'], s['goals'], s['assists'], s['cs'], s['conceded'], upgrade[nm]))
    cg = sum(int(g['score'].split('-')[0]) for g in E6['log']); print('City goals', cg, 'allocated', sum(v['goals'] for v in st.values()), '| stand-in', st.get('stand-in'), '| Haaland', st['Haaland']['goals'], 'apps', st['Haaland']['apps'])
    for g in goals: print(g)
