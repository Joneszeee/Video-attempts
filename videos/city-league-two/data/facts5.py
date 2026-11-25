# Part 5: the story facts from ep5.json (second half of season 3, seed 2031) and the model's view of City's next weak spot (for the step-up vote).
import json, math
import l4model as L
import sim_l5 as S
E4 = json.load(open('ep4.json')); E5 = json.load(open('ep5.json'))
log = E4['log'] + E5['log']; second = E5['log']
fin = {r[1]: r for r in E5['table_final']}; city = fin['Manchester City']
print('FINAL (pos, team, pts, gf, ga):'); [print(' ', *r) for r in E5['table_final'][:6]]
print('City: pts %d, GF %d, GA %d, GD %+d | second half: W%d D%d L%d, %d pts' % (city[2], city[3], city[4], city[3] - city[4], sum(g['res'] == 'W' for g in second), sum(g['res'] == 'D' for g in second), sum(g['res'] == 'L' for g in second), sum({'W': 3, 'D': 1, 'L': 0}[g['res']] for g in second)))
print('most goals scored?', city[3] == max(r[3] for r in E5['table_final']), '| fewest conceded?', city[4] == min(r[4] for r in E5['table_final']), '| best GD?', city[3] - city[4] == max(r[3] - r[4] for r in E5['table_final']))
print('Haaland:', E5['haaland'], 'league goals (13 at halfway); clean sheets', E5['clean_sheets'], '(6 at halfway)')
# the title race: City's points v the best of the others after each matchday
race = []
for k in range(24, 47):
    snap = E5['snaps'][str(k)]; c = next(r for r in snap if r[1] == 'Manchester City'); oth = max((r for r in snap if r[1] != 'Manchester City'), key=lambda r: (r[2], r[3]))
    race.append((k, c[0], c[2], oth[1], oth[2], c[2] - oth[2]))
print('matchday: City pos, pts | best of the rest, pts | lead'); [print(' ', *x) for x in race]
first = next(k for k, pos, *_ in race if pos == 1); print('City first reached top at matchday', first, '| last time not top:', max(k for k, pos, *_ in race if pos != 1))
clinch = next(k for k, pos, cp, on, op, lead in race if all(lead > (46 - kk) * 3 for kk, _, _, _, _, lead in [x for x in race if x[0] == k]))
print('title mathematically clinched at matchday', clinch, '(lead more than the points left)' if True else '')
print('biggest wins:', sorted(((int(g['score'][0]) - int(g['score'][2]), g['md'], g['opp'], g['score'], g['venue']) for g in second), reverse=True)[:4])
print('defeats:', [(g['md'], g['opp'], g['score'], g['venue']) for g in second if g['res'] == 'L'])
print('first-half v second-half record:', 'MD1-23 38 pts (W10 D8 L5)', '| MD24-46', sum({'W': 3, 'D': 1, 'L': 0}[g['res']] for g in second), 'pts')
print('odds:', {k: round(E5[k]['promoted'], 3) for k in ('odds_without', 'odds_with_sign', 'odds_with_both')}, {k: round(E5[k]['title'], 3) for k in ('odds_without', 'odds_with_sign', 'odds_with_both')})
# ratings of the two new players (60 + 80 x goals per game added v an average League One player in the slot) and the weak spot for next season
T = dict(S.TIERS); T['LOAN'] = tuple(E5['loan']['tier']); avg = L.avg1; T['avg'] = (avg, avg); T['champ'] = tuple(L.chv1)
POS = [('GK', 0, .20), ('RB', .06, .11), ('CB', .03, .15), ('CB', .03, .15), ('LB', .06, .11), ('DM', .07, .10), ('DM', .07, .10), ('RW', .15, .03), ('AM', .15, .02), ('LW', .15, .03), ('ST', .23, 0)]
def team(x): return (math.exp(sum(w * math.log(T[t][0]) for (p, w, _), t in zip(POS, x))), math.exp(sum(w * math.log(T[t][1]) for (p, _, w), t in zip(POS, x))))
XI5 = E5['xi']; print('XI5 tiers:', XI5)
gf, ga = team(XI5); print('City v an average League One side: %.3f for, %.3f against (Part 4: 2.164 / 1.104)' % (gf, ga))
NAMES = ['McCracken', 'Lewis', 'Watts', 'Scarr', "O'Reilly", 'Iroegbunam', 'Ward-Prowse', 'McAidoo', 'Foden', 'Moylan', 'Haaland']
print('slot: impact v an average League One player -> rating | gain if upgraded to an average Championship player (goals per game)')
for i, nm in enumerate(NAMES):
    x = list(XI5); x[i] = 'avg'; g2, a2 = team(x); imp = (gf - g2) + (a2 - ga)
    y = list(XI5); y[i] = 'champ'; g3, a3 = team(y); up = (g3 - gf) + (ga - a3)
    print('  %-12s %-3s %+.3f -> %d | upgrade gain %+.3f' % (nm, POS[i][0], imp, round(60 + 80 * imp), up))
