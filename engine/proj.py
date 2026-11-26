#!/usr/bin/env python3
"""Where do points land on screen? A Python copy of the engine's camera maths (engine.js toCam / proj: a 1080x1920 frame, FOC 1150, horizon line at 56% of the height), for placing
cameras and players before rendering. The portrait frame is only about 25 degrees either side of the aim, so anything standing beside the camera turns into a giant blob and anything
more than ~25 degrees off the aim is not in shot at all; check each start position, not just the strike.

    from proj import cam, scr, show
    show([-3.0, 2.0, 32.0], [0.4, 1.0, 49.0], {'ball': [0, 0.11, 41.5], 'keeper': [0, 0, 52]})
    -> ball (664, 1227, depth 10.0 m, ~207 px tall for a 1.8 m player)

scr() returns (x, y, depth in metres, height in pixels of a 1.8 m player at that depth) or None when the point is behind the camera. y is the screen y of the point itself
(use y = 0 for a player's feet). A card or headline lives in y 330-700 (headline, score bug), the bottom 250 px is covered by the apps' own buttons.
"""
import math

W, H, FOC = 1080, 1920, 1150
CY = H * 0.56


def _sub(a, b): return [a[i] - b[i] for i in range(3)]
def _dot(a, b): return sum(a[i] * b[i] for i in range(3))
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _nrm(a):
    n = math.sqrt(_dot(a, a)) or 1.0
    return [x / n for x in a]


def cam(pos, tgt):
    f = _nrm(_sub(tgt, pos)); r = _nrm(_cross([0, 1, 0], f)); u = _cross(f, r)
    return dict(pos=pos, f=f, r=r, u=u)


def scr(c, p):
    d = _sub(p, c['pos']); q = [_dot(d, c['r']), _dot(d, c['u']), _dot(d, c['f'])]
    if q[2] < 0.6:
        return None
    return (round(W / 2 + FOC * q[0] / q[2]), round(CY - FOC * q[1] / q[2]), round(q[2], 1), round(FOC * 1.8 / q[2]))


def show(pos, tgt, pts):
    c = cam(pos, tgt)
    for name, p in pts.items():
        print(f'{name:14s}', scr(c, p))


if __name__ == '__main__':
    show([0, 1.4, -3.1], [0, 2.6, 10], {'hero feet': [0.3, 0, 0], 'hero head': [0.3, 1.8, 0], 'ghost feet': [-0.55, 0, 0.8]})
