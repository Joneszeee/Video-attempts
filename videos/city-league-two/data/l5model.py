"""Part 5 (second half of season 3, matchdays 24-46 + play-offs): the January signings, each rated at his real club's level on the League One scale
(the same rule as Watts at Cambridge and McCracken at Bradford): the poll candidates Kalvin Phillips (Sheffield United), James Ward-Prowse (Southampton),
Oliver Norwood (Stockport County). The loan player from the comment vote is added in sim_l5.py once the user names him. Writes citymodel_l5.json."""
import json, math
import l4model as L
R1, avg1 = L.R1, L.avg1
def tier(att, de): return (avg1 * math.exp(att), avg1 * math.exp(-de))
CANDS = {'Phillips': ('Sheffield United', 'ch'), 'Ward-Prowse': ('Southampton', 'ch'), 'Norwood': ('Stockport County', 'l1')}
out = {'avg': avg1, 'candidates': {}}
for nm, (club, lg) in CANDS.items():
    r = L.on_l1_scale(club, 'ch') if lg == 'ch' else R1['teams'][club]
    out['candidates'][nm] = {'club': club, 'league': lg, 'att': r['att'], 'def': r['def'], 'tier': tier(r['att'], r['def'])}
out['tiers'] = {k: list(v) for k, v in L.TIERS.items()}
json.dump(out, open('citymodel_l5.json', 'w'), indent=1)
if __name__ == '__main__':
    for nm, v in out['candidates'].items(): print('%-12s %-18s on the League One scale att %+.2f def %+.2f -> goals for/against v an average side %.2f / %.2f' % (nm, v['club'], v['att'], v['def'], *v['tier']))
