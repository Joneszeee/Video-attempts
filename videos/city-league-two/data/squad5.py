# Part 5 squad cards: ratings and simulated stats "since joining" (matchdays 24-46) for City's new XI, and the weak spot for next season.
# - RATING: 60 + 80 x (goals per game a player adds to City's goal difference v an average League One player in his slot), from the Part 5 model (new XI, Moylan at Cardiff's level).
# - STATS: same method as squad.py. Haaland's goals are the sim's own (hgoals); every other City goal goes to a scorer in proportion to the model's attack weight for his slot,
#   P_ASSIST of goals carry an assist (shared by the same weights, never the scorer); players play every league game of the half (Haaland and Foden by the sim's own availability).
#   SEED 2032 was fixed before running (written into plan.md first). No published score changes.
import json, math, random
import l4model as L
import sim_l5 as S
E5 = json.load(open('ep5.json')); Q = json.load(open('squad.json'))
SEED = 2032
P_ASSIST = Q['p_assist']
SLOTS = ['GK', 'RB', 'CB1', 'CB2', 'LB', 'DM1', 'DM2', 'RW', 'AM', 'LW', 'ST']
W = dict(zip(SLOTS, [0, .06, .03, .03, .06, .07, .07, .15, .15, .15, .23]))
NAMES = ['McCracken', 'Lewis', 'Watts', 'Scarr', "O'Reilly", 'Iroegbunam', 'Ward-Prowse', 'McAidoo', 'Foden', 'Moylan', 'Haaland']
assert [g['md'] for g in E5['log']] == list(range(24, 47))
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
st = {}
def Sx(n): return st.setdefault(n, {'apps': 0, 'goals': 0, 'assists': 0, 'cs': 0, 'conceded': 0})
for g in E5['log']:
    cg, og = (int(x) for x in g['score'].split('-')); hp, fp = g['haaland'], g['foden']; who = xi(hp, fp)
    for slot, nm in who.items():
        r = Sx(nm); r['apps'] += 1
        if slot in ('GK', 'RB', 'CB1', 'CB2', 'LB'): r['cs'] += og == 0
        if slot == 'GK': r['conceded'] += og
    hg = g['hgoals'] if hp else 0
    assert hg <= cg
    for k in range(cg):
        scorer = 'ST' if k < hg else pick([s for s in SLOTS if not (s == 'ST' and hp)])
        Sx(who[scorer])['goals'] += 1
        if rng.random() < P_ASSIST: Sx(who[pick(SLOTS, exclude=scorer)])['assists'] += 1
# ---- ratings
T = dict(S.TIERS); T['LOAN'] = tuple(E5['loan']['tier']); avg = L.avg1; T['avg'] = (avg, avg); T['champ'] = tuple(L.chv1)
POS = [('GK', 0, .20), ('RB', .06, .11), ('CB', .03, .15), ('CB', .03, .15), ('LB', .06, .11), ('DM', .07, .10), ('DM', .07, .10), ('RW', .15, .03), ('AM', .15, .02), ('LW', .15, .03), ('ST', .23, 0)]
def team(x): return (math.exp(sum(w * math.log(T[t][0]) for (p, w, _), t in zip(POS, x))), math.exp(sum(w * math.log(T[t][1]) for (p, _, w), t in zip(POS, x))))
XI5 = E5['xi']; gf, ga = team(XI5)
rating, upgrade = {}, {}
for i, nm in enumerate(NAMES):
    x = list(XI5); x[i] = 'avg'; g2, a2 = team(x); imp = (gf - g2) + (a2 - ga)
    y = list(XI5); y[i] = 'champ'; g3, a3 = team(y)
    rating[nm] = {'impact': round(imp, 4), 'ovr': round(60 + 80 * imp), 'pos': POS[i][0]}; upgrade[nm] = round((g3 - gf) + (ga - a3), 4)
out = {'seed': SEED, 'p_assist': P_ASSIST, 'ratings': rating, 'upgrade_to_championship': upgrade, 'stats_second_half': {n: st[n] for n in NAMES}, 'stand_in': st.get('stand-in'), 'team': {'gf': gf, 'ga': ga}}
json.dump(out, open('squad5.json', 'w'), indent=1)
print('P_ASSIST', P_ASSIST, '| City v an average L1 side: %.3f for, %.3f against' % (gf, ga))
print('%-12s %-3s %-4s | %-26s | upgrade to an average Championship player' % ('', 'pos', 'ovr', 'MD24-46 apps G A CS GC'))
for nm in sorted(NAMES, key=lambda n: -rating[n]['ovr']):
    s = st[nm]; print('%-12s %-3s %-4d | %3d %3d %3d %3d %3d            | %+.3f' % (nm, rating[nm]['pos'], rating[nm]['ovr'], s['apps'], s['goals'], s['assists'], s['cs'], s['conceded'], upgrade[nm]))
cg = sum(int(g['score'].split('-')[0]) for g in E5['log']); print('City second-half goals', cg, 'allocated', sum(v['goals'] for v in st.values()), '| stand-in', st.get('stand-in'), '| Haaland', st['Haaland']['goals'], 'apps', st['Haaland']['apps'])
