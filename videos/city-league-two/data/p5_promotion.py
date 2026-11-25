# Part 5 addendum: who else went up from League One 2028/29? City won the title and MK Dons were 2nd (automatic). The official run (seed 2031) never decided the third place because it only
# played the play-offs when City were in them. They are played here, among the clubs that finished 3rd-6th, with seed 2033 (fixed in plan.md before running), with the same rules as sim_l5.py:
# two-leg semi-finals (3rd v 6th, 4th v 5th), level on aggregate = a coin flip (shown as "on penalties"), then a one-match final.
import json, random
from sim_l4 import play, MC
SEED = 2033
E = json.load(open('ep5.json')); table = E['table_final']; o = [r[1] for r in table]
assert o[0] == 'Manchester City' and E['playoffs'] is None and o[1] == 'MK Dons' and o[2:6] == ['Stockport County', 'Luton Town', 'Reading', 'Stevenage']
r = random.Random(SEED)
def tie(a, b):
    legs = []; ga = gb = 0
    for hh, aa in ((a, b), (b, a)):
        x, y, _, _ = play(hh, aa, r, MC); legs.append([hh, aa, x, y])
        if hh == a: ga += x; gb += y
        else: gb += x; ga += y
    pens = ga == gb; win = a if ga > gb else b if gb > ga else (a if r.random() < .5 else b)
    return win, {'legs': legs, 'agg': [a, ga, b, gb], 'pens': pens, 'winner': win}
w1, s1 = tie(o[2], o[5]); w2, s2 = tie(o[3], o[4]); x, y, _, _ = play(w1, w2, r, MC); pens = x == y
fin = w1 if x > y else w2 if y > x else (w1 if r.random() < .5 else w2)
po = {'semi1': s1, 'semi2': s2, 'final': {'teams': [w1, w2], 'score': [x, y], 'pens': pens, 'winner': fin}}
out = {'seed': SEED, 'champions': o[0], 'automatic': [o[0], o[1]], 'playoffs': po, 'promoted': [o[0], o[1], fin], 'relegated': o[20:], 'table_top6': table[:6]}
json.dump(out, open('ep5_promotion.json', 'w'), indent=1)
for k in ('semi1', 'semi2'):
    s = po[k]; print(k, ' | '.join(f'{h} {a_} {x_}-{y_}' for h, a_, x_, y_ in s['legs']), '| agg', s['agg'], '| winner', s['winner'], '(level: coin flip)' if s['pens'] else '')
print('final', w1, 'v', w2, f'{x}-{y}', '(level: coin flip)' if pens else '', '| winner', fin)
print('PROMOTED:', out['promoted']); print('RELEGATED:', out['relegated'])
