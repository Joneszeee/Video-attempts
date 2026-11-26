"""Shared building blocks for videos/<slug>/gen.py (so each video's script stays short and the same fixes apply everywhere).

    import sys; sys.path.insert(0, 'engine'); from lib import *
    V, lines = start('videos/<slug>/')
    B = []
    ... B.append({...}) using P(), goal(), bug(), hud(), stamp(), big(), clean_tackle() ...
    save(V, B, lines, 'Title', accent=TEAL)

Everything here encodes rules the user asked for (see CLAUDE.md): shooters stay on screen through the run-up, one defender blocks and one
covers, the keeper is beaten or makes a real save, tackles are clean (no fall, the ball goes to a team-mate), score bugs clear the headline.
"""
import json
import math

RED, GOLD, GREEN, TEAL, SKY = "#ff4d5e", "#e9b949", "#2ecc71", "#3FE0C5", "#6cabdd"
GK_YELLOW = {"shirt": "#f7d117", "shorts": "#111111", "socks": "#f7d117", "text": "#111111"}
GK_GREEN = {"shirt": "#2ecc71", "shorts": "#111111", "socks": "#2ecc71", "text": "#111111"}


def kit(shirt, shorts=None, socks=None, text="#ffffff", **extra):
    """kit('#a50044', '#004d98', stripes=['#a50044', '#004d98'])"""
    d = {"shirt": shirt, "shorts": shorts or shirt, "socks": socks or shirt, "text": text}
    d.update(extra)
    return d


def stadium(crowd, seed=7, **k):
    d = {"type": "stadium", "crowd": crowd, "seed": seed}
    d.update(k)
    return d


def small(crowd, seed=7, **k):
    """League Two / lower-league ground."""
    return stadium(crowd, seed, ground="small", **k)


def start(folder):
    """Returns (folder, VO lines) from videos/<slug>/vo.txt."""
    lines = [l.strip() for l in open(folder + 'vo.txt').read().split('<break time="0.8s" />')]
    return folder, lines


def save(folder, beats, lines, title, accent=TEAL, **spec):
    for b, v in zip(beats, lines):
        b["vo"] = v
    assert len(beats) == len(lines), f'{len(beats)} beats but {len(lines)} VO lines'
    out = {"title": title, "brand": "theo6k", "accent": accent, "voSpeed": 1.08, "beats": beats}
    out.update(spec)
    json.dump(out, open(folder + 'spec.json', 'w'), indent=1, ensure_ascii=False)
    print("ok", len(beats), "beats")


def P(**k):
    d = {"name": "", "num": None}
    d.update(k)
    return d


def mid(a, c, h):
    return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]


def cam(pos, tgt, frm=None, frm_tgt=None, move=5, **k):
    d = {"camera": {"pos": pos, "tgt": tgt}, "camFrom": {"pos": frm or pos, "tgt": frm_tgt or tgt}, "move": move, "moveEase": "linear"}
    d.update(k)
    return d


def hud(sub, **k):
    """Simulation frame (what-if videos). counter=False for one simulated match (no 10,000-run counter; just the SIM tag, low in the corner)."""
    d = {"type": "simhud", "delay": 0, "sub": sub, "dur": 0, "clear": False}
    d.update(k)
    return d


def bug(home, away, score, mn, frm=None, goalAt=None, lag=0.3, **k):
    """TV score bug; home/away = {"name": "MCI", "color": "#6cabdd"}. It clears a two-line headline by itself."""
    d = {"type": "scorebug", "y": 560, "delay": 0, "home": home, "away": away, "score": score, "min": mn}
    if frm:
        d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    d.update(k)
    return d


def stamp(text, at, sub=None, color=RED, y=1600, size=96, lag=-0.1, rot=-0.07, **k):
    d = {"type": "stamp", "text": text, "at": at, "lag": lag, "color": color, "rot": rot, "size": size, "y": y}
    if sub:
        d["sub"] = sub
    d.update(k)
    return d


def big(value, at, label, frm=0, y=1500, size=170, dur=0.8, lag=-0.2, **k):
    d = {"type": "big", "at": at, "lag": lag, "from": frm, "value": value, "countDur": dur, "label": label, "y": y, "size": size}
    d.update(k)
    return d


def goal(word, x, z, side, shooter_kit, end, keeper_dir, keeper_kit, def_kit, lag=-0.5, label=None, save_it=False, **shooter):
    """A shot on goal timed so contact lands on `word`.
    x, z: shooter's spot (z about 40-42); side: +1/-1 = which side the camera sits; end: [x, y, 52.3] where the ball ends (inside the posts);
    keeper_dir: the way he dives (send him the wrong way for a goal). save_it=True puts the ball in his gloves instead.
    Returns (players, cards, camera keys) — the shooter is on screen for the whole run-up (camera behind and to one side)."""
    b0 = [x + (-0.22 if shooter.get('foot') == 'left' else 0.22), 0.11, z + 0.45]   # ball on his stronger foot
    sh = P(kit=shooter_kit, x=x, z=z, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate", runup=1.6, **shooter)
    if label:
        sh.update(label=label, labelDelay=0.1)
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=keeper_dir)
    if not save_it:
        keeper.update(actionAt=word, actionLag=lag + 0.45)
    pl = [sh, keeper,
          P(kit=def_kit, skin="#e7b593", hair="#141010", x=x + side * -1.9, z=z + 3.4, front=True, action="dive", dir=side, actionAt=word, actionLag=lag + 0.15, actionDur=0.7),
          P(kit=def_kit, skin="#8a5a3c", hair="#141010", x=-end[0] * 0.8, z=47.8, front=True)]
    shot = {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": 0.5, "slowmo": False, "points": [b0, mid(b0, end, 0.9), end]}
    if save_it:
        shot.update(flash=False, saveBy=1)
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34}, shot]
    camk = {"camFrom": {"pos": [round(x + side * 3.0, 2), 2.2, z - 9], "tgt": [round(x * 0.4, 2), 1.0, 52]},
            "camera": {"pos": [round(x + side * 2.4, 2), 1.9, z - 6.3], "tgt": [round(x * 0.4, 2), 1.0, 52]}, "move": 4, "moveEase": "linear", "follow": 0.5}
    return pl, cards, camk


def freekick(word, x, z, shooter_kit, wall_kit, keeper_kit, end, keeper_dir, side=1, lag=-0.5, label=None, wall_n=4, jump=True, **shooter):
    """A direct free kick with contact on `word`: the shooter stands over the ball at (x, z) (z about 28-33), a wall of `wall_n` faces him 9.15 m
    away on the line to goal and jumps as he strikes, the ball goes over it and dips into `end` ([x, y, 52.3], inside the posts). keeper_dir: the
    way the keeper dives (the same way as the ball = he is beaten by pace; he starts late so the ball passes his fingertips).
    Returns (players, cards, camera keys) like goal(); the camera sits behind and to one side of the shooter (side +1/-1)."""
    b0 = [x + (-0.22 if shooter.get('foot') == 'left' else 0.22), 0.11, z + 0.45]
    sh = P(kit=shooter_kit, x=x, z=z, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate", runup=2.0, **shooter)
    if label:
        sh.update(label=label, labelDelay=0.1)
    dx, dz = -x, 52.5 - z
    n = (dx * dx + dz * dz) ** 0.5
    ux, uz = dx / n, dz / n                           # unit vector from the ball to the middle of the goal
    cx, cz = x + 9.15 * ux, z + 9.15 * uz             # the wall stands 9.15 m away on that line
    looks = [("#e7b593", "#141010"), ("#8a5a3c", "#141010"), ("#f0c8a8", "#6a4a2a"), ("#c99b7a", "#2a1a10"), ("#e7b593", "#3a2a1a")]
    wall = []
    for i in range(wall_n):
        off = (i - (wall_n - 1) / 2) * 0.62
        sk, hr = looks[i % len(looks)]
        w = P(kit=wall_kit, skin=sk, hair=hr, x=round(cx - uz * off, 2), z=round(cz + ux * off, 2), front=True)
        if jump:
            w.update(hops=[{"at": word, "lag": lag + 0.28, "dur": 0.55, "height": 0.45}])
        wall.append(w)
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=keeper_dir,
               actionAt=word, actionLag=lag + 0.62)
    ctrl = [round(b0[0] + 0.55 * (end[0] - b0[0]), 2), 4.6, round(b0[2] + 0.55 * (end[2] - b0[2]), 2)]   # high over the wall, dipping late
    shot = {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": 1.0, "slowmo": True, "points": [b0, ctrl, end]}
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34}, shot]
    # the camera sits well to one side and behind the shooter, so his body never hides the ball's path to the corner;
    # it looks midway (in bearing) between the shooter and the middle of the goal, so both stay in frame
    def aim(cam):
        bearing = lambda px, pz: math.atan2(cam[0] - px, pz - cam[2])
        th = (bearing(x, z) + bearing(0.0, 52.5)) / 2
        return [round(cam[0] - math.tan(th) * (47 - cam[2]), 2), 1.2, 47]
    c0 = [round(x + side * 7.0, 2), 2.3, round(z - 6.5, 2)]
    c1 = [round(x + side * 6.0, 2), 2.0, round(z - 4.0, 2)]
    camk = {"camFrom": {"pos": c0, "tgt": aim(c0)}, "camera": {"pos": c1, "tgt": aim(c1)}, "move": 4, "moveEase": "linear", "follow": 0.12}
    return [sh] + wall + [keeper], cards, camk


def foul_from_behind(word, victim_kit, fouler_kit, victim=None, fouler=None, lag=0.0, lead=3.6, victim_label=None, fouler_label=None):
    """A clean-through player is brought down by a defender who chases him and slides in from behind, with contact on `word` (the engine's slide + fall).
    Both start running `lead` seconds before the word (a negative start = already mid-run on frame 0), so the contact always lands on the word.
    victim / fouler = extra P() kwargs (skin, hair, name, num, foot...). Returns (players, cards, camera keys): a side-on camera 6 m away that tracks
    the run (about 3.4 s). The loose ball keeps rolling after contact (a ballpath that is not a goal)."""
    v = dict(victim or {})
    f = dict(fouler or {})
    pv = P(kit=victim_kit, dribble=True, dribbleUntil=round(lead - 0.05, 2), x=0.2, z=17.5, path=[[0.2, 17.5], [0.5, 26.0], [0.9, 33.5], [1.2, 38.8]], pathDur=round(lead + 0.25, 2),
           at=word, lag=-lead + lag, action="fall", actionAt=word, actionLag=0.1 + lag, **v)
    pf = P(kit=fouler_kit, x=-2.4, z=11.0, path=[[-2.4, 11.0], [-1.7, 21.5], [-0.8, 30.0], [0.5, 36.0]], pathDur=round(lead - 0.1, 2),
           at=word, lag=-lead + lag, action="slide", dir=1, actionAt=word, actionLag=-0.5 + lag, actionDur=1.1, **f)
    if victim_label:
        pv.update(label=victim_label, labelDelay=round(lead - 1.2, 2))
    if fouler_label:
        pf.update(label=fouler_label, labelDelay=round(lead - 0.4, 2))
    cards = [{"type": "ballpath", "world": True, "at": word, "lag": 0.15 + lag, "dur": 0.9, "slowmo": True, "flash": False, "points": [[1.3, 0.11, 39.0], [2.4, 0.2, 41.5], [3.6, 0.11, 43.8]]}]
    camk = {"camFrom": {"pos": [7.0, 1.6, 19.5], "tgt": [0.6, 1.0, 23.0]}, "camera": {"pos": [6.2, 1.6, 34.5], "tgt": [1.2, 1.0, 38.0]}, "move": 3.4, "moveEase": "linear", "hype": False}
    return [pv, pf], cards, camk


def clean_tackle(word, tackler, runner_kit, mate_kit, label=None):
    """A clean slide tackle with contact on `word` (user: no foul, the ball never vanishes): the runner dribbles across, the tackler jogs
    in and slides, the ball is poked into a team-mate's stride, the runner hurdles the leg and keeps going. tackler = P(...) kwargs (kit, skin...).
    Returns (players, cards, camera keys); filmed side-on from 8-10 m."""
    t = dict(tackler)
    t.update(x=-4.5, z=2.2, path=[[-4.5, 2.2], [-1.6, 4.4], [0.5, 6.1]], pathDur=2.4, at=word, lag=-2.1, action="slide", dir=-1, actionAt=word, actionLag=-0.4)
    if label:
        t.update(label=label, labelAt=word)
    pl = [P(kit=runner_kit, skin="#e7b593", hair="#141010", x=4.5, z=8.5, path=[[4.5, 8.5], [0.8, 6.6], [-2.2, 6.4]], pathDur=1.5, at=word, lag=-0.87,
            dribble=True, dribbleUntil=0.87, hops=[{"at": word, "lag": -0.08, "dur": 0.5, "height": 0.3}]),
          P(**t),
          P(kit=mate_kit, skin="#f0c8a8", hair="#6a4a2a", num=4, x=4.0, z=2.8, path=[[4.0, 2.8], [2.4, 4.3], [0.6, 8.0]], pathDur=1.5, at=word, lag=0.05, dribble=True, dribbleFrom=0.55)]
    cards = [{"type": "ballpath", "world": True, "at": word, "lag": 0.0, "dur": 0.6, "slowmo": False, "flash": False, "points": [[0.27, 0.11, 6.32], [1.3, 0.16, 5.6], [2.09, 0.11, 4.93]]}]
    camk = {"camFrom": {"pos": [-6.0, 1.7, -1.6], "tgt": [0.6, 0.8, 6.2]}, "camera": {"pos": [-4.9, 1.6, -0.3], "tgt": [0.8, 0.8, 6.4]}, "move": 5, "moveEase": "linear",
            "punch": [{"at": word, "lag": -0.05, "amount": 0.14, "dur": 1.3, "x": 480, "y": 1060}], "hype": False}
    return pl, cards, camk


def tags_count(tags):
    """YouTube's tag-box count: each tag's length, +2 for a tag with a space, +1 per comma (aim for 490-500)."""
    return sum(len(t) + (2 if ' ' in t else 0) for t in tags) + len(tags) - 1


# ---------------------------------------------------------------------------------------------------------------------------------
# Choreographed goals (user: "the defenders stand still, the shooter stands still, moves his leg, shoots, the keeper dives: lifeless").
# Every player runs a route (path + pathT: runs, stops to strike, runs again), defenders close down, slide, lunge and chase, a decoy runs
# into the box, the keeper shuffles, steps out and dives (then gets up), and the scorer wheels away with team-mates running to him.
# Times are in seconds relative to the moment `word` is said: the ball hits the net at tau = 0 (plus `lag`), the strike is `flight` earlier.
# ---------------------------------------------------------------------------------------------------------------------------------
class When:
    """Choreography times relative to a phrase in the line (a string) or, for a test without a voice, to a number of seconds from the shot's start."""

    def __init__(self, word, lag=0.0):
        self.w, self.lag = word, lag

    def _s(self):
        return isinstance(self.w, str)

    def start(self, tau):          # a route or a card starts at tau
        return {"at": self.w, "lag": round(tau + self.lag, 3)} if self._s() else {"delay": round(self.w + tau + self.lag, 3)}

    def act(self, tau):            # a player's single action starts at tau
        return {"actionAt": self.w, "actionLag": round(tau + self.lag, 3)} if self._s() else {"actionDelay": round(self.w + tau + self.lag, 3)}

    def action(self, tau, **k):    # one entry of a player's "actions" list
        d = {"at": self.w, "lag": round(tau + self.lag, 3)} if self._s() else {"delay": round(self.w + tau + self.lag, 3)}
        d.update(k)
        return d

    def item(self, tau, **k):      # one entry of "hops", "punch", "shake" or "speedlines"
        d = {"at": self.w, "lag": round(tau + self.lag, 3)} if self._s() else {"t": round(self.w + tau + self.lag, 3)}
        d.update(k)
        return d

    def rest(self, tau0, tau1, point):   # a ball lying at `point` from tau0 until tau1
        d = {"type": "ball", "point": [round(v, 3) for v in point]}
        d.update(self.start(tau0))
        if self._s():
            d.update(untilAt=self.w, untilLag=round(tau1 + self.lag, 3))
        else:
            d["until"] = round(tau1 - tau0, 3)
        return d

    def shot(self, tau, dur, points, **k):
        d = {"type": "ballpath", "world": True, "dur": dur, "points": [[round(v, 3) for v in p] for p in points]}
        d.update(self.start(tau))
        d.update(k)
        return d


def dribble_ball(x, z, hx, hz, foot="right"):
    """Where the engine draws the dribbled ball at the second his dribble ends (dribbleUntil): 0.45 m ahead on his strong foot. A resting ball card takes over from here."""
    side = -0.18 if foot == "left" else 0.18
    return [x + side * hz + hx * 0.45, 0.11, z + hz * 0.45 - side * hx]


def _heading(a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dz * dz) ** 0.5 or 1.0
    return dx / n, dz / n


def _cut(word, lag, cut_lag, **k):
    """The second shot of a choreographed goal: on a phrase it carries its own "at"/"lag" (add it to the beat's "shots"); with a number of seconds (tests) it does not."""
    d = {"at": word, "lag": round(lag + cut_lag, 3)} if isinstance(word, str) else {}
    d.update(k)
    return d


def _label_until(word, lag, cut_lag):
    return {"labelUntilAt": word, "labelUntilLag": round(lag + cut_lag, 3)} if isinstance(word, str) else {"labelUntil": round(word + lag + cut_lag, 3)}


def _swing(word, lag, cut_lag):
    """When the chase camera starts swinging to the scorer (a phrase, or seconds for a test)."""
    return {"at": word, "lag": round(lag + cut_lag, 3)} if isinstance(word, str) else {"t": round(word + lag + cut_lag, 3)}


def goal_dribble(word, scorer_kit, keeper_kit, def_kit, mate_kit=None, foot="right", flight=0.55, lag=0.0, label=None, scorer=None, keeper_wrong_way=True, cut_lag=0.25, cut=True):
    """DRIBBLE AND FINISH. The scorer runs at goal with the ball, a defender slides in and the scorer hops it, another chases from behind, a covering defender
    shuffles across, a team-mate runs alongside as a decoy, the keeper comes off his line and is sent the wrong way by a low finish into the far corner. The net
    bulges on `word`; then the scorer turns and runs at the camera with his arms up, the decoy and a late team-mate sprint after him, and the keeper gets up.
    foot="left" mirrors everything (he comes in from the right and finishes with his left). scorer = extra P() kwargs (name, num, skin, hair...).
    Returns (players, cards, camera keys, cut2): a chase camera tracks the scorer from behind (beat key camTrack); `cut2` is a second shot (add it to the beat's
    "shots" as it is) that cuts, `cut_lag` s after the net hit, to a camera in front of the scorer tracking his celebration run. players[0] is the scorer, players[1] the keeper."""
    W, sd, L = When(word, lag), (1 if foot != "left" else -1), 4.4
    X = lambda x: round(sd * x, 3)
    route = lambda pts: [[X(x), z] for x, z in pts]
    sc = dict(scorer or {})
    tc = -flight                                   # tau of the strike (ball leaves his foot)
    net = L + lag                                  # route time of the net hit
    go = net + cut_lag                             # he starts his celebration run as the camera cuts to the front
    S_pts = [(-7.5, 20.0), (-5.4, 26.0), (-3.4, 31.5), (-1.8, 34.2), (0.1, 36.7), (0.1, 36.7), (-2.8, 35.4), (-5.9, 33.6), (-8.2, 32.0)]   # after the goal he runs back toward where he came from, away from the chaser
    S_T = [0, 1.0, 2.0, 2.6, 3.3, go, go + 1.0, go + 2.0, go + 2.7]       # arrives at 3.3, plants and strikes, watches it in, then runs at the camera
    hx, hz = _heading(route(S_pts)[3], route(S_pts)[4])
    b0 = dribble_ball(X(S_pts[4][0]), S_pts[4][1], hx, hz, foot)
    end = [X(2.9), 0.5, 52.3]
    ctrl = [b0[0] + (end[0] - b0[0]) * 0.55, 0.9, b0[2] + (end[2] - b0[2]) * 0.55]
    kick_len = 0.8
    look = {"skin": "#f1d3bd", "hair": "#d9b46a"}
    look.update(sc)
    scorer_p = P(kit=scorer_kit, foot=foot, dribble=True, dribbleUntil=3.3, path=route(S_pts), pathT=S_T, **W.start(-L), frontT=round(go, 3),
                 actions=[W.action(tc - 0.42 * kick_len, action="kick", dur=kick_len, foot=foot), W.action(0.0, loop="celebrate")], **look)
    scorer_p["hops"] = [W.item(2.35 - L, dur=0.5, height=0.22)]
    if label:
        scorer_p.update(label=label, labelDelay=0.2, **_label_until(word, lag, cut_lag))
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=route([(0.0, 52.0), (0.0, 52.0), (0.15, 50.4), (0.15, 50.4)]), pathT=[0, 2.9, 3.75, 9.0], **W.start(-L),
               actions=[W.action(tc + 0.12, action="dive", dir=-sd if keeper_wrong_way else sd), W.action(1.55, action="getup", dir=-sd if keeper_wrong_way else sd)])
    d1 = P(kit=def_kit, skin="#e7b593", hair="#141010", front=True, path=route([(3.8, 37.8), (1.6, 34.8), (-0.6, 33.4)]), pathT=[0, 1.75, 2.55], **W.start(-L), action="slide", dir=sd, **W.act(2.05 - L), actionDur=1.1)
    d2 = P(kit=def_kit, skin="#8a5a3c", hair="#141010", path=route([(-4.7, 17.0), (-2.6, 23.0), (-0.6, 28.6), (0.9, 33.6), (1.5, 36.2)]), pathT=[0, 1.0, 2.0, 3.0, 3.6], **W.start(-L), action="dive", dir=sd, **W.act(tc + 0.15))
    d3 = P(kit=def_kit, skin="#f0c8a8", hair="#6a4a2a", front=True, path=route([(-2.6, 44.2), (-1.5, 43.4), (-0.9, 44.0)]), pathT=[0, 3.0, 3.9], **W.start(-L), action="dive", dir=sd, **W.act(tc + 0.1), actionDur=0.7)
    mk = mate_kit or scorer_kit
    a1 = P(kit=mk, skin="#e7b593", hair="#3a2a1a", path=route([(5.6, 19.0), (5.0, 29.0), (4.4, 37.5), (4.0, 42.5), (4.0, 42.5), (1.0, 40.0), (-3.2, 37.4), (-6.4, 34.8)]), pathT=[0, 2.0, 3.4, 4.0, go - 0.05, go + 1.0, go + 2.0, go + 2.7],
           **W.start(-L), action="celebrate", **W.act(2.7 + cut_lag + lag), frontT=round(go, 3))
    a2 = P(kit=mk, skin="#f0c8a8", hair="#6a4a2a", path=route([(-12.0, 27.5), (-12.0, 27.5), (-10.6, 29.0), (-9.6, 30.2), (-9.0, 30.8)]), pathT=[0, go - 0.05, go + 0.9, go + 1.9, go + 2.7],
           **W.start(-L), action="celebrate", **W.act(2.7 + cut_lag + lag), frontT=round(go, 3))
    cards = [W.rest(3.3 - L, tc, b0), W.shot(tc, flight, [b0, ctrl, end], slowmo=False)]
    # shot 1: a chase camera 5.4 m behind and 2.2 m to the side of the scorer, looking past him at the goal; the aim drifts toward the goal as he closes in
    camk = {"camTrack": {"player": 0, "off": [X(-2.2), 1.55, -5.4], "tgt": [X(0.7), 1.0, 9.0], "look": [0.0, 1.0, 50.0], "lookW": 0.3, "smooth": 0.35}, "hype": False,
            "punch": [W.item(tc - 0.04, amount=0.12, dur=1.1, anchor=0)], "shake": [W.item(0.0, amount=14)], "speedlines": [W.item(tc - 0.05, dur=0.6, amount=0.4)], "flashes": 12}
    # shot 2: a low camera ahead of the scorer looking back at him as he runs at it, the team-mates chasing and the beaten defenders on the grass behind
    cut2 = _cut(word, lag, cut_lag, cut=True, transition="whip", camTrack={"player": 0, "off": [X(-4.7), 1.3, -2.1], "tgt": [0.0, 1.25, 0.0], "smooth": 0.25}, hype=False, flashes=16, confetti=True,
                shake=[{"t": 0.05, "amount": 10}])
    if not cut:   # one long shot: the camera swings to the scorer instead of cutting (for a beat too short to hold two shots of 2 s)
        camk["camTrack"]["to"] = {**_swing(word, lag, cut_lag), "dur": 0.8, "off": [X(-4.7), 1.3, -2.1], "tgt": [0.0, 1.25, 0.0], "lookW": 0.0}
        camk["confetti"] = False
        cut2 = None
    return [scorer_p, keeper, d1, d2, d3, a1, a2], cards, camk, cut2


def goal_curler(word, scorer_kit, keeper_kit, def_kit, mate_kit=None, foot="right", flight=1.05, lag=0.0, label=None, scorer=None, cut_lag=0.25, cut=True):
    """LONG-RANGE CURLER. The scorer cuts in from the wing with the ball, a defender closes him down and lunges, another jumps in the way, a third chases; he curls it
    over them (the ball arcs high, then bends into the far top corner) and the keeper dives at full stretch and misses it by a hand. Then he turns and runs at the
    camera to celebrate with the team-mates chasing him. foot="left" mirrors everything. Returns (players, cards, camera keys, cut2) like goal_dribble;
    players[0] is the scorer, players[1] the keeper."""
    W, sd, L = When(word, lag), (1 if foot != "left" else -1), 4.6
    X = lambda x: round(sd * x, 3)
    route = lambda pts: [[X(x), z] for x, z in pts]
    sc = dict(scorer or {})
    tc = -flight
    net = L + lag
    go = net + cut_lag
    S_pts = [(-16.0, 27.0), (-12.0, 29.5), (-8.5, 31.0), (-6.0, 32.0), (-4.2, 31.4), (-4.2, 31.4), (-6.2, 29.2), (-8.6, 26.4), (-9.6, 24.4)]
    S_T = [0, 1.0, 1.9, 2.6, 3.2, go, go + 0.9, go + 1.9, go + 2.6]
    hx, hz = _heading(route(S_pts)[3], route(S_pts)[4])
    b0 = dribble_ball(X(S_pts[4][0]), S_pts[4][1], hx, hz, foot)
    end = [X(3.4), 2.15, 52.3]
    ctrl = [X(-2.6), 4.4, 41.0]
    kick_len = 0.8
    look = {"skin": "#e7b593", "hair": "#141010"}
    look.update(sc)
    scorer_p = P(kit=scorer_kit, foot=foot, dribble=True, dribbleUntil=3.2, path=route(S_pts), pathT=S_T, **W.start(-L), frontT=round(go, 3),
                 actions=[W.action(tc - 0.42 * kick_len, action="kick", dur=kick_len, foot=foot), W.action(0.0, loop="celebrate")], **look)
    if label:
        scorer_p.update(label=label, labelDelay=0.2, **_label_until(word, lag, cut_lag))
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=route([(0.3, 52.0), (0.3, 52.0), (-0.3, 51.6), (-0.3, 51.6)]), pathT=[0, 1.5, 2.6, 9.0], **W.start(-L),
               actions=[W.action(-0.68, action="dive", dir=sd), W.action(1.7, action="getup", dir=sd)])
    d1 = P(kit=def_kit, skin="#e7b593", hair="#141010", front=True, path=route([(-9.5, 38.5), (-7.5, 35.5), (-5.8, 33.2)]), pathT=[0, 2.0, 3.3], **W.start(-L), action="dive", dir=sd, **W.act(tc - 0.15), actionDur=0.7)
    d2 = P(kit=def_kit, skin="#8a5a3c", hair="#141010", front=True, path=route([(1.8, 38.5), (0.6, 37.6), (-0.6, 37.0)]), pathT=[0, 2.5, 3.5], **W.start(-L), hops=[W.item(tc + 0.0, dur=0.55, height=0.32)])
    d3 = P(kit=def_kit, skin="#f0c8a8", hair="#6a4a2a", path=route([(-1.5, 22.5), (-1.5, 26.5), (-1.6, 29.0)]), pathT=[0, 2.0, 3.4], **W.start(-L), action="dive", dir=sd, **W.act(tc + 0.2), actionDur=0.7)
    mk = mate_kit or scorer_kit
    a1 = P(kit=mk, skin="#e7b593", hair="#3a2a1a", path=route([(8.5, 30.0), (4.0, 40.0), (2.2, 45.0), (2.2, 45.0), (-2.5, 37.0), (-6.5, 29.6), (-8.2, 26.8)]), pathT=[0, 3.0, 3.8, go - 0.05, go + 1.1, go + 2.0, go + 2.6],
           **W.start(-L), action="celebrate", **W.act(2.6 + cut_lag + lag), frontT=round(go, 3))
    a2 = P(kit=mk, skin="#f0c8a8", hair="#6a4a2a", path=route([(5.5, 23.0), (5.5, 23.0), (-1.0, 26.0), (-6.0, 25.0)]), pathT=[0, go - 0.05, go + 1.4, go + 2.6],
           **W.start(-L), action="celebrate", **W.act(2.6 + cut_lag + lag), frontT=round(go, 3))
    cards = [W.rest(3.2 - L, tc, b0), W.shot(tc, flight, [b0, ctrl, end], slowmo=True)]
    camk = {"camTrack": {"player": 0, "off": [X(-2.4), 1.7, -6.0], "tgt": [X(1.0), 1.1, 9.0], "look": [0.0, 1.2, 50.0], "lookW": 0.4, "smooth": 0.35}, "hype": False,
            "punch": [W.item(tc - 0.04, amount=0.1, dur=1.2, anchor=0)], "shake": [W.item(0.0, amount=14)], "speedlines": [W.item(tc - 0.05, dur=0.6, amount=0.4)], "flashes": 12}
    cut2 = _cut(word, lag, cut_lag, cut=True, transition="whip", camTrack={"player": 0, "off": [X(-1.0), 1.3, -4.6], "tgt": [0.0, 1.25, 0.0], "smooth": 0.25}, hype=False, flashes=16, confetti=True,
                shake=[{"t": 0.05, "amount": 10}])
    if not cut:   # one long shot: the camera swings to the scorer instead of cutting
        camk["camTrack"]["to"] = {**_swing(word, lag, cut_lag), "dur": 0.8, "off": [X(-1.0), 1.3, -4.6], "tgt": [0.0, 1.25, 0.0], "lookW": 0.0}
        cut2 = None
    return [scorer_p, keeper, d1, d2, d3, a1, a2], cards, camk, cut2


# ---------------------------------------------------------------------------------------------------------------------------------
# Penalties, bundles, divots, crosses and a disallowed goal (built for videos/united-sporting). Same conventions as goal_dribble / goal_curler: everything is in seconds
# relative to `word` (lib.When), players start mid-action, the cameras were placed with a projection check (the portrait frame is only ~25 degrees either side of the
# aim, so anything standing beside the camera turns into a giant blob: keep other players out of the camera's cone). Screen-left is world -x for a camera looking toward +z.
# ---------------------------------------------------------------------------------------------------------------------------------
def penalty(word, kicker_kit, keeper_kit, outcome="scored", corner=-1, foot="right", flight=0.5, lag=0.0, label=None, kicker=None, save="lunge", save_dir=1, celebrate=True, side=-1):
    """PENALTY (a three-quarter view from behind the taker, so his body never hides the ball). The taker stands back, then runs in and strikes; the keeper sways on his line and moves.
    The ball reaches the net (scored) or the keeper's gloves (saved) on `word`; the run-up is about 2.8 s long, so the clip needs its word >= 1.5 s into the beat.
    outcome="scored": a low shot into the corner (corner: -1 = screen-left, +1 = screen-right) while the keeper dives the other way, then the taker turns and celebrates.
    outcome="saved": a weak shot that the keeper stops (save="lunge": a reaching step, for a shot down the middle; save="dive": a full dive; save_dir = the screen side he goes) and holds
    (the ball ends in his gloves via the engine's saveBy). side = which side of the taker the camera sits (-1 = screen-left).
    Returns (players, cards, camera keys); players[0] = taker, players[1] = keeper."""
    W, L = When(word, lag), 3.6
    sc = dict(kicker or {})
    tau_s = -flight
    kick_len = 0.8
    t_arr = L + tau_s - 0.42 * kick_len
    sd = side
    pts = [(sd * 1.5, 38.4), (sd * 1.5, 38.4), (sd * 0.34, 40.9), (sd * 0.34, 40.9)]   # he stands back (hands on hips), then runs in: a walk-back would look like running backwards (the body only ever faces one way)
    pT = [0, round(t_arr - 0.85, 3), round(t_arr, 3), 12.0]
    b0 = [0.0, 0.11, 41.5]
    dk = 0.95 if save == "dive" else 0.6
    if outcome == "saved":
        end = [round(save_dir * (1.25 if save == "dive" else 0.5), 3), 0.95, 52.0]
        shot = W.shot(tau_s, flight, [b0, [round(end[0] * 0.5, 3), 0.4, 46.5], end], slowmo=False, flash=False, saveBy=1)
        kacts = [W.action(-0.7 * dk, action=save, dir=save_dir)] + ([W.action(1.2, action="getup", dir=save_dir)] if save == "dive" else [])
    else:
        end = [round(corner * 2.9, 3), 0.42, 52.3]
        shot = W.shot(tau_s, flight, [b0, [round(end[0] * 0.5, 3), round(0.35 + end[1] * 0.4, 3), 46.5], end], slowmo=False)
        kacts = [W.action(tau_s + 0.1, action="dive", dir=-corner), W.action(1.7, action="getup", dir=-corner)]
    look = {"skin": "#e7b593", "hair": "#141010"}
    look.update(sc)
    acts = [W.action(tau_s - 0.42 * kick_len, action="kick", dur=kick_len, foot=foot)]
    if outcome == "scored" and celebrate:
        acts.append(W.action(0.25, loop="celebrate"))
    taker = P(kit=kicker_kit, foot=foot, path=[list(p) for p in pts], pathT=pT, **W.start(-L), actions=acts, **look)
    if outcome == "scored" and celebrate:
        taker["frontT"] = round(L + 0.2, 3)
    if label:
        taker.update(label=label, labelDelay=0.25, **_label_until(word, lag, 0.9))
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=[[0.0, 52.0], [-0.5, 52.0], [0.6, 52.0], [0.0, 52.0], [0.0, 52.0]], pathT=[0, 0.9, 1.9, 2.8, 12.0],
               **W.start(-L), actions=kacts)
    cards = [W.rest(0.4 - L, tau_s, b0), shot]
    camk = {"camFrom": {"pos": [sd * 3.9, 3.4, 33.0], "tgt": [0.0, 0.8, 48.5]}, "camera": {"pos": [sd * 3.3, 3.1, 34.6], "tgt": [0.0, 0.8, 48.5]}, "move": 7.0, "moveEase": "linear", "hype": False,
            "punch": [W.item(tau_s - 0.04, amount=0.1, dur=1.1)], "shake": [W.item(0.0, amount=14 if outcome == "scored" else 9)], "speedlines": [W.item(tau_s - 0.05, dur=0.6, amount=0.35)], "flashes": 12}
    return [taker, keeper], cards, camk


def bundle(word, victim_kit, keeper_kit, lag=0.0, label=None, victim=None, hit=0.0):
    """THE KEEPER BUNDLES HIM OVER. A striker chases a loose ball into the box, the keeper charges off his line and dives at his feet; contact on `word`: the striker falls and stays
    down, the ball runs loose. Side-on camera from the right (the keeper comes in from the right of frame). Returns (players, cards, camera keys); players[0] = striker, players[1] = keeper."""
    W, L = When(word, lag), 2.6
    look = {"skin": "#c99b7a", "hair": "#141010"}
    look.update(victim or {})
    hx, hz = 0.64, 0.77
    ball_rest = dribble_ball(-2.6, 47.0, hx, hz, "right")
    v = P(kit=victim_kit, dribble=True, dribbleUntil=round(L - 0.02, 3), path=[[-5.4, 43.7], [-2.6, 47.0], [-2.6, 47.0]], pathT=[0, round(L - 0.02, 3), 12.0], **W.start(-L), actions=[W.action(0.0, action="fall")], **look)
    if label:
        v.update(label=label, labelDelay=0.3)
    k = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=[[0.4, 52.0], [0.4, 52.0], [-0.9, 48.7], [-0.9, 48.7]], pathT=[0, 0.5, round(L - 0.55, 3), 12.0], **W.start(-L),
          actions=[W.action(-0.5, action="dive", dir=-1)])
    cards = [W.rest(-0.02, 0.0, ball_rest), W.shot(0.0, 1.4, [ball_rest, [-1.7, 0.11, 49.0], [-0.6, 0.11, 51.6]], slowmo=False, flash=False)]
    camk = {"camFrom": {"pos": [7.5, 1.7, 41.0], "tgt": [-1.0, 1.1, 48.0]}, "camera": {"pos": [6.8, 1.65, 41.6], "tgt": [-1.4, 1.1, 48.2]}, "move": 4.0, "moveEase": "linear", "hype": False,
            "punch": [W.item(-0.1, amount=0.12, dur=1.0)], "shake": [W.item(0.0, amount=10)], "flashes": 10}
    return [v, k], cards, camk


def goal_divot(word, shooter_kit, keeper_kit, def_kit, foot="right", lag=0.0, label=None, shooter=None, divot_label="DIVOT", t1=0.95, t2=0.95, cut_lag=0.3, cut=True):
    """THE DIVOT GOAL. A hopeful shot from outside the box skids low, hits a scuffed patch of turf just outside the six-yard box (a PUFF card: dust, a ring, a patch that stays on the
    grass, a pill saying DIVOT), kicks up and flies over the keeper into the net on `word`. Shot 1 is the 3/4 view from behind the shooter; `cut2` (add it to the beat's "shots") is a low
    camera beside the divot, `cut_lag` s after the strike: the ball whips in, the turf explodes and it rises over the keeper. t1 = flight to the divot, t2 = flight from it into the net.
    foot="left" mirrors it. Returns (players, cards, camera keys, cut2); players[0] = shooter, players[1] = keeper."""
    W, sd, L = When(word, lag), (1 if foot != "left" else -1), 3.6
    X = lambda x: round(sd * x, 3)
    tau_s, tau_b = -(t1 + t2), -t2
    look = {"skin": "#f0c8a8", "hair": "#4a3324"}
    look.update(shooter or {})
    kick_len = 0.8
    b0 = [X(-1.6), 0.11, 33.4]
    dv = [X(0.7), 0.04, 46.2]
    net = [X(0.15), 2.05, 52.3]
    t_arr = round(L + tau_s - 0.42 * kick_len, 3)
    sh = P(kit=shooter_kit, foot=foot, path=[[X(-1.2), 28.5], [X(-1.2), 28.5], [X(-1.9), 33.0], [X(-1.9), 33.0]], pathT=[0, round(t_arr - 1.05, 3), t_arr, 12.0], **W.start(-L),
           actions=[W.action(tau_s - 0.42 * kick_len, action="kick", dur=kick_len, foot=foot)], **look)
    if label:
        sh.update(label=label, labelDelay=0.2, **_label_until(word, lag, tau_s + cut_lag))
    k = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=[[X(0.3), 52.0], [X(-0.5), 52.0], [X(0.5), 52.0], [X(-0.1), 52.0], [X(-0.1), 52.0]], pathT=[0, 1.0, 2.0, 3.0, 12.0],
          **W.start(-L), actions=[W.action(tau_b - 0.1, action="lunge", dir=-sd)])
    d1 = P(kit=def_kit, skin="#e7b593", hair="#141010", front=True, x=X(2.6), z=49.2, action="idle")
    d2 = P(kit=def_kit, skin="#8a5a3c", hair="#141010", front=True, x=X(-2.7), z=48.7, action="idle")
    cards = [W.rest(0.3 - L, tau_s, b0),
             W.shot(tau_s, t1, [b0, [X(-0.4), 0.55, 40.0], dv], slowmo=False, flash=False),
             W.shot(tau_b, t2, [dv, [X(0.55), 3.4, 49.4], net], slowmo=True),
             {"type": "puff", "point": dv, "label": divot_label, "labelDx": X(-210), "labelDy": 200, **W.start(tau_b)}]
    camk = {"camFrom": {"pos": [X(0.6), 2.4, 21.2], "tgt": [X(-0.3), 1.2, 46.0]}, "camera": {"pos": [X(0.2), 2.3, 22.0], "tgt": [X(-0.3), 1.2, 46.0]}, "move": 5.0, "moveEase": "linear", "hype": False,
            "punch": [W.item(tau_s - 0.04, amount=0.12, dur=1.0)], "speedlines": [W.item(tau_s - 0.05, dur=0.6, amount=0.35)], "flashes": 10}
    cut2 = _cut(word, lag, tau_s + cut_lag, cut=True, camFrom={"pos": [X(-5.5), 1.0, 39.0], "tgt": [X(0.9), 1.0, 48.0]}, camera={"pos": [X(-5.0), 1.0, 40.2], "tgt": [X(0.5), 1.15, 49.0]}, move=3.2, moveEase="linear", hype=False,
                punch=[W.item(tau_b - 0.05, amount=0.12, dur=1.2)], shake=[W.item(0.0, amount=12)], flashes=12)
    if not cut:
        cut2 = None
    return [sh, k, d1, d2], cards, camk, cut2


def goal_cross(word, scorer_kit, keeper_kit, def_kit, lag=0.0, label=None, scorer=None, own_goal=False, mirror=False):
    """CROSS AND FINISH (the keeper flaps). A high ball drops into the six-yard box from the top of the frame (a cross from the wing); the keeper comes off his line and jumps for it
    with a defender beside him, the striker arrives at the same moment and nudges him off balance (the keeper lands flat), the ball drops and the striker finishes from a yard with a
    leap and a volley into the net on `word`. One camera at the front-left of the box (mirror=True: front-right).
    own_goal=True: the same corner or cross, but nobody finishes it: the striker (a defender, no kick, no celebration) leans on the keeper, who flaps at it with both hands and the ball drops
    in off his gloves (the caller's varcheck rules it out). Returns (players, cards, camera keys); players[0] = striker (or the defender), players[1] = keeper."""
    W, L, sd = When(word, lag), 3.4, (-1 if mirror else 1)
    X = lambda x: round(sd * x, 3)
    look = {"skin": "#c99b7a", "hair": "#141010"}
    look.update(scorer or {})
    kick_len = 0.7
    T_s = -0.25                                              # the volley leaves his boot (or the ball drops in off the keeper's hands)
    T_j = T_s - 0.2                                          # the keeper's jump and the nudge
    x_end, z_end = 0.9, 48.8
    acts = [] if own_goal else [W.action(T_s - 0.42 * kick_len, action="kick", dur=kick_len, foot="right"), W.action(0.45, loop="celebrate")]
    st = P(kit=scorer_kit, path=[[X(0.8), 45.9], [X(0.8), 45.9], [X(x_end), z_end], [X(x_end), z_end]], pathT=[0, round(L + T_s - 1.0, 3), round(L + T_s - 0.35, 3), 12.0], **W.start(-L), hops=[W.item(T_s - 0.2, dur=0.5, height=0.35)],
           actions=acts, **look)
    if not own_goal:
        st["frontT"] = round(L + 0.45, 3)
    if label:
        st.update(label=label, labelDelay=0.3, **_label_until(word, lag, 0.9))
    kact = [W.action(T_j - 0.25, action="lunge", dir=-sd)] if own_goal else [W.action(T_j + 0.05, action="fall", dir=sd)]
    kk = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=[[0.0, 52.0], [0.0, 52.0], [X(-0.5), 49.6], [X(-0.5), 49.6]], pathT=[0, 1.0, round(L + T_j, 3), 12.0],
           **W.start(-L), hops=[W.item(T_j - 0.1, dur=0.5, height=0.28)], actions=kact)
    d1 = P(kit=def_kit, skin="#e7b593", hair="#141010", front=True, x=X(-2.7), z=50.5, action="idle")      # keep other players out of the camera's cone: one standing beside it turns into a giant blob
    d2 = P(kit=def_kit, skin="#8a5a3c", hair="#141010", front=True, x=X(3.2), z=47.0, action="idle")
    vol, net = [X(0.4), 1.0, 49.5], [X(0.1), 0.8, 52.3]
    cards = [W.shot(T_s - 1.5, 1.5, [[X(-8.5), 3.0, 44.0], [X(-3.6), 6.0, 47.2], vol], slowmo=False, flash=False),
             W.shot(T_s, -T_s, [vol, [X(0.3), 0.9, 51.0], net], slowmo=False)]
    camk = {"camFrom": {"pos": [X(-9.5), 1.6, 43.5], "tgt": [X(0.4), 1.4, 49.5]}, "camera": {"pos": [X(-8.6), 1.6, 44.2], "tgt": [X(0.4), 1.4, 49.7]}, "move": 5.0, "moveEase": "linear", "hype": False,
            "punch": [W.item(T_s - 0.1, amount=0.12, dur=1.2)], "shake": [W.item(0.0, amount=14)], "speedlines": [W.item(T_s - 0.05, dur=0.5, amount=0.35)], "flashes": 14}
    return [st, kk, d1, d2], cards, camk


def disallowed(word, scorer_kit, keeper_kit, def_kit, lag=0.0, label=None, scorer=None, whistle=True):
    """THE WHISTLE WENT FIRST. A through ball rolls in from the left, the winger shoots, the keeper turns it onto the crossbar, the REFEREE'S WHISTLE sounds (a `sound` card, plus the
    caller's varcheck/stamp cards), and the winger heads the rebound into the net on `word` (the goal bulges and the crowd jumps, then it will be ruled out). Camera at the front-left of
    the box. Returns (players, cards, camera keys); players[0] = the winger, players[1] = the keeper."""
    W, L = When(word, lag), 3.2
    look = {"skin": "#8a5a3c", "hair": "#141010"}
    look.update(scorer or {})
    t_shot, t_bar, t_head = -1.45, -1.12, -0.5            # contact of the shot, the bar, the header
    a = P(kit=scorer_kit, path=[[-5.4, 41.0], [-1.4, 45.4], [-1.4, 45.4], [-0.6, 49.1], [-0.6, 49.1]], pathT=[0, round(L + t_shot - 0.35, 3), round(L + t_shot + 0.45, 3), round(L + t_head - 0.12, 3), 12.0], **W.start(-L),
          hops=[W.item(t_head - 0.28, dur=0.55, height=0.45)], actions=[W.action(t_shot - 0.42 * 0.8, action="kick", dur=0.8, foot="right"), W.action(0.3, loop="celebrate")], frontT=round(L + 0.35, 3), **look)
    if label:
        a.update(label=label, labelDelay=0.3, **_label_until(word, lag, 0.9))
    k = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", front=True, pose="keeper", path=[[0.0, 52.0], [0.0, 52.0], [0.3, 51.4], [0.3, 51.4]], pathT=[0, 1.0, 1.8, 12.0], **W.start(-L),
          actions=[W.action(t_shot + 0.12, action="dive", dir=-1), W.action(0.9, action="getup", dir=-1)])
    d1 = P(kit=def_kit, skin="#e7b593", hair="#141010", front=True, x=3.1, z=49.0, action="idle")
    d2 = P(kit=def_kit, skin="#f0c8a8", hair="#6a4a2a", front=True, x=5.2, z=46.0, action="idle")
    bar, head, net = [-0.3, 2.44, 52.4], [-0.55, 2.05, 49.7], [0.1, 0.8, 52.3]
    cards = [W.shot(t_shot - 1.0, 1.0, [[-9.0, 0.11, 41.2], [-5.0, 0.11, 43.6], [-1.4, 0.11, 45.4]], slowmo=False, flash=False),
             W.shot(t_shot, t_bar - t_shot, [[-1.4, 0.11, 45.5], [-0.9, 1.6, 49.0], bar], slowmo=False, flash=False),
             W.shot(t_bar, t_head - t_bar, [bar, [-0.5, 3.2, 51.4], head], slowmo=False, flash=False),
             W.shot(t_head, -t_head, [head, [-0.2, 1.4, 51.0], net], slowmo=False)]
    if whistle:
        cards.append({"type": "sound", "name": "whistle", **W.start(t_bar + 0.12)})
    camk = {"camFrom": {"pos": [-9.5, 1.6, 43.5], "tgt": [0.2, 1.5, 49.4]}, "camera": {"pos": [-8.7, 1.6, 44.1], "tgt": [0.2, 1.5, 49.7]}, "move": 5.0, "moveEase": "linear", "hype": False,
            "punch": [W.item(t_shot - 0.05, amount=0.1, dur=1.0), W.item(t_head - 0.1, amount=0.1, dur=1.0)], "shake": [W.item(t_bar, amount=9), W.item(0.0, amount=14)], "flashes": 12}
    return [a, k, d1, d2], cards, camk
