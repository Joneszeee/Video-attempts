"""Runs Part 5's second half: the poll winner James Ward-Prowse (Southampton, 47% of 785 votes) in the second holding-midfield slot, and the comment-vote loan Jack Moylan (Cardiff City)
on the left wing in place of T. Samba (6-month loan = the whole second half). Both rated at their real club's level on the League One scale. Seed 2031 (fixed before running)."""
import math
import sim_l5 as S, l4model as L
cf = L.on_l1_scale('Cardiff City', 'ch')
S.SIGN = 'Ward-Prowse'
S.LOAN = {'name': 'Moylan', 'tier': [L.avg1 * math.exp(cf['att']), L.avg1 * math.exp(-cf['def'])], 'slot': 9}
print('Cardiff on the League One scale: att %+.2f def %+.2f -> tier %.2f / %.2f' % (cf['att'], cf['def'], *S.LOAN['tier']))
S.run()
