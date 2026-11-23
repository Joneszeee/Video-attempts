# Part 4: City's weak spot after McCracken. From the exact matchday-23 table, upgrade ONE slot of the XI to an average Championship player
# (the Championship->League One bridge: scores 1.68, concedes 1.20 against an average League One side) and see what the promotion odds do.
import json
import l4model as L
import sim_l4 as S
E = json.load(open('ep4.json')); tab = {r[1]: [r[2], r[3], r[4]] for r in E['table_md23']}
rounds = S.fixtures(S.SEED)[23:]
TIERS = dict(L.TIERS); TIERS['champ'] = tuple(L.chv1)
SLOTS = {2: 'centre-back (Watts)', 3: 'centre-back (League Two signing)', 6: 'defensive midfielder (League Two signing)', 7: 'right wing (academy)', 9: 'left wing (academy)'}
def model(xi): return L.variants(xi) if False else {k: L.team(x, TIERS) for k, x in (('full', xi), ('no_haaland', L.swap(xi, 10, 'u21')), ('no_foden', L.swap(xi, 8, 'u21')), ('no_haaland_foden', L.swap(L.swap(xi, 10, 'u21'), 8, 'u21')))}
base = model(L.XI4); b = S.odds(rounds, tab, 6000, 9, base)
print('current XI  : promoted %.3f title %.3f avg pts %.1f | goals for/against %.3f / %.3f' % (b['promoted'], b['title'], b['avg_pts'], *base['full']))
for i, name in SLOTS.items():
    xi = L.swap(L.XI4, i, 'champ'); m = model(xi); o = S.odds(rounds, tab, 6000, 9, m)
    print('%-42s promoted %+.3f title %+.3f pts %+.2f | goals for %.3f against %.3f' % (name, o['promoted'] - b['promoted'], o['title'] - b['title'], o['avg_pts'] - b['avg_pts'], *m['full']))
