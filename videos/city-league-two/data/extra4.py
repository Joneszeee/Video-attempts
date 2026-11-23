# Part 4: numbers the video needs on top of ep4.json: City's expected points per matchday (the model's own expectation for each fixture, including the
# chance Haaland and Foden miss it), and the pre-season odds for last year's City in this season's league (to separate "the league got easier" from McCracken).
import json, math
import sim_l4 as S
E = json.load(open('ep4.json')); N = json.load(open('citymodel_l4.json'))
rounds = S.fixtures(S.SEED)
def pmf(l, k=16):
    p = [math.exp(-l)]
    for i in range(1, k): p.append(p[-1] * l / i)
    return p
def xpts(h, a, m):
    tot = 0
    for hp, wh in ((True, S.P_H), (False, 1 - S.P_H)):
        for fp, wf in ((True, S.P_F), (False, 1 - S.P_F)):
            cr = S.city_rates(hp, fp, m)
            ah, dh = cr if h == 'Manchester City' else S.T[h]; aa, da = cr if a == 'Manchester City' else S.T[a]
            ph, pa = pmf(math.exp(S.c + S.hm + ah - da)), pmf(math.exp(S.c + aa - dh))
            win = sum(ph[i] * pa[j] for i in range(16) for j in range(16) if i > j); dr = sum(ph[i] * pa[i] for i in range(16))
            lose = sum(ph[i] * pa[j] for i in range(16) for j in range(16) if i < j)
            city_home = h == 'Manchester City'
            pw, pl_ = (win, lose) if city_home else (lose, win)
            tot += wh * wf * (3 * pw + dr)
    return tot
per = []
for k, rd in enumerate(rounds[:23], 1):
    for h, a in rd:
        if 'Manchester City' in (h, a): per.append(xpts(h, a, S.MC))
cum = [round(sum(per[:i + 1]), 2) for i in range(23)]
actual = [g['pts'] for g in E['log']]
ep3_pre = S.odds(rounds, {t: [0, 0, 0] for t in S.teams}, 10000, 7, N['models']['ep3'])
json.dump({'xpts_by_md': cum, 'xpts_23': cum[-1], 'actual_by_md': actual, 'pre_ep3_city': {k: ep3_pre[k] for k in ('title', 'auto', 'promoted', 'avg_pts')}}, open('ep4_extra.json', 'w'), indent=1)
print('expected points after 23:', cum[-1], 'actual', actual[-1])
print('expected after each MD:', cum)
print('last year\'s City in this league: promoted %.3f title %.3f avg pts %.1f' % (ep3_pre['promoted'], ep3_pre['title'], ep3_pre['avg_pts']))
print('exact pre-season promoted with McCracken', E['pre']['promoted'], 'title', E['pre']['title'], '| without', E['pre_without_mccracken']['promoted'], E['pre_without_mccracken']['title'])
print('halfway promoted', E['half_odds']['promoted'], 'title', E['half_odds']['title'], 'auto', E['half_odds']['auto'], 'playoffs', E['half_odds']['playoffs'])
