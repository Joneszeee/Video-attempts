"""Mood presets and colour handling for the generator.

A mood is a bundle of numbers that changes the feel without changing the style:
tempo, how floaty the bounces are, camera, bloom, fog, reverb, default accompaniment
and instruments. Any value can be overridden per video with "moodOverrides".
"""
import colorsys

MOODS = {
    # the original video
    "playful": {
        "tempo": 1.0, "gravity": 50, "drop": 1.0, "diveGap": 1.35,
        "camDist": 6.2, "camHeight": 1.35, "fov": 50,
        "bloom": [0.32, 0.38, 1.9], "glowPeak": 2.6, "fog": [9, 34], "exposure": 1.0,
        "grain": 0.018, "vignette": 0.38, "particles": 1.0,
        "light": 1.0, "reverb": 1.0, "finalHit": "big", "styles": {}, "instruments": {},
        # layout: drop per note is capped at maxDrop units; notes longer than dwell seconds
        # land and sit instead of flying (the original video uses neither)
        "maxDrop": 99, "dwell": 0.8,
    },
    "dreamy": {
        "maxDrop": 1.5, "dwell": 0.78,
        "tempo": 0.85, "gravity": 36, "drop": 0.8, "diveGap": 1.7,
        "camDist": 6.4, "camHeight": 1.45, "fov": 50,
        "bloom": [0.45, 0.5, 1.7], "glowPeak": 2.4, "fog": [7, 28], "exposure": 1.0,
        "grain": 0.012, "vignette": 0.45, "particles": 1.7,
        "light": 0.9, "reverb": 1.7, "finalHit": "soft",
        "styles": {"salon": "arpeggio", "cave": "pad", "party": "pad"},
        "instruments": {"party": "musicbox", "cave": "bell"},
    },
    "energetic": {
        "maxDrop": 1.5, "dwell": 0.6,
        "tempo": 1.12, "gravity": 62, "drop": 1.05, "diveGap": 1.15,
        "camDist": 5.9, "camHeight": 1.25, "fov": 52,
        "bloom": [0.42, 0.4, 1.6], "glowPeak": 3.0, "fog": [10, 36], "exposure": 1.05,
        "grain": 0.02, "vignette": 0.35, "particles": 1.3,
        "light": 1.05, "reverb": 0.6, "finalHit": "big",
        "styles": {"salon": "pulse", "cave": "pulse", "party": "pulse"},
        "instruments": {"salon": "lead", "cave": "pluck", "party": "brass"},
    },
    "spooky": {
        "maxDrop": 1.5, "dwell": 0.7,
        "tempo": 0.95, "gravity": 45, "drop": 1.1, "diveGap": 1.5,
        "camDist": 6.0, "camHeight": 1.2, "fov": 50,
        "bloom": [0.45, 0.5, 1.5], "glowPeak": 2.8, "fog": [6, 22], "exposure": 0.82,
        "grain": 0.03, "vignette": 0.62, "particles": 1.4,
        "light": 0.7, "reverb": 1.6, "finalHit": "big",
        "styles": {"salon": "march", "cave": "march", "party": "march"},
        "instruments": {"salon": "musicbox", "party": "pluck"},
    },
    "epic": {
        "maxDrop": 1.5, "dwell": 0.7,
        "tempo": 1.0, "gravity": 55, "drop": 1.15, "diveGap": 1.6,
        "camDist": 6.8, "camHeight": 1.5, "fov": 52,
        "bloom": [0.5, 0.5, 1.6], "glowPeak": 3.2, "fog": [10, 38], "exposure": 1.0,
        "grain": 0.02, "vignette": 0.5, "particles": 1.2,
        "light": 1.0, "reverb": 1.45, "finalHit": "big",
        "styles": {"salon": "march", "cave": "march", "party": "march"},
        "instruments": {"salon": "brass", "party": "brass"},
    },
    "chill": {
        "maxDrop": 1.5, "dwell": 0.78,
        "tempo": 0.8, "gravity": 38, "drop": 0.85, "diveGap": 1.6,
        "camDist": 6.3, "camHeight": 1.4, "fov": 50,
        "bloom": [0.25, 0.4, 2.0], "glowPeak": 2.2, "fog": [8, 30], "exposure": 0.95,
        "grain": 0.015, "vignette": 0.4, "particles": 1.2,
        "light": 0.9, "reverb": 1.2, "finalHit": "soft",
        "styles": {"salon": "waltz", "cave": "pad", "party": "pad"},
        "instruments": {"salon": "piano", "cave": "marimba", "party": "marimba"},
    },
}

# kit defaults: the three worlds of the original video
KITS = {
    "salon": {
        "instrument": "piano", "style": "arpeggio", "particles": "motes",
        "colors": {"background": "#241a3d", "glow": "#ffa640", "accent": "#e0ac4c",
                   "objects": ["#6d1a2a", "#1f4a3a", "#1d2c5c", "#5a2f6e", "#7a4a1a"], "pole": "#3b2116"},
        "look": {"sky": "#a58ad8", "ground": "#2a1426", "hemi": 0.55, "key": "#ffe6c4", "keyI": 2.3, "env": 0.55,
                 "glow": "#ffa640", "glowI": 3.5, "rim": "#b28cff", "rimI": 3, "hit": "#ffb347"},
        "bokeh": ["#ffb24a", "#ffd28a", "#ff8a3a", "#c89bff"], "mote": "#ffc46b",
    },
    "cave": {
        "instrument": "pluck", "style": "march", "particles": "spores",
        "colors": {"background": "#061a1d", "glow": "#24e6ff", "accent": "#e0ac4c",
                   "objects": ["#c4243a", "#7d2fc0"], "pole": "#1d3134"},
        "look": {"sky": "#3ad9d0", "ground": "#02090a", "hemi": 0.45, "key": "#c4f4ff", "keyI": 1.7, "env": 0.4,
                 "glow": "#24e6ff", "glowI": 4, "rim": "#c85cff", "rimI": 3.5, "hit": "#5ff6ff"},
        "bokeh": ["#2ff0ff", "#1a9cff", "#b05cff", "#3fffc0"], "mote": "#6ff7ff",
    },
    "party": {
        "instrument": "brass", "style": "oompah", "particles": "confetti",
        "colors": {"background": "#b8306e", "glow": "#ffd24a", "accent": "#e0ac4c",
                   "objects": ["#7cff4f", "#ff8a1f", "#3fd8ff", "#ff4fa8", "#ffe14f"], "pole": "#e3203f",
                   "stage": "#d81f4a"},
        "look": {"sky": "#ffc2e2", "ground": "#5a1036", "hemi": 0.75, "key": "#fff4ec", "keyI": 2.5, "env": 0.6,
                 "glow": "#ffd24a", "glowI": 3, "rim": "#7fd8ff", "rimI": 3, "hit": "#ff7ac8"},
        "bokeh": ["#fff3a0", "#ffffff", "#8fe6ff", "#ffb0e0"], "mote": "#ffffff",
    },
}
KIT_ORDER = ["salon", "cave", "party"]


def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_hex(c):
    return "#" + "".join(f"{max(0, min(255, round(x * 255))):02x}" for x in c)


def hls(h):
    return colorsys.rgb_to_hls(*hex_rgb(h))


def from_hls(h, l, s):
    return rgb_hex(colorsys.hls_to_rgb(h % 1.0, max(0, min(1, l)), max(0, min(1, s))))


def scene_look(kit, colors, mood):
    """Lighting for one world. With the kit's own colours this returns the original
    look exactly; with custom colours the lights are derived from background and glow."""
    k = KITS[kit]
    base = dict(k["look"])
    custom_bg = colors.get("background", k["colors"]["background"]).lower() != k["colors"]["background"]
    custom_glow = colors.get("glow", k["colors"]["glow"]).lower() != k["colors"]["glow"]
    if custom_bg:
        h, l, s = hls(colors["background"])
        base["sky"] = from_hls(h, 0.55 + 0.25 * l, min(0.75, s + 0.2))
        base["ground"] = from_hls(h, l * 0.5, s)
        # bright backgrounds need more fill so objects do not read as silhouettes
        base["hemi"] = 0.45 + 0.4 * l
    if custom_glow:
        g = colors["glow"]
        h, l, s = hls(g)
        base["glow"] = g
        base["hit"] = from_hls(h, max(l, 0.65), s)
        base["key"] = from_hls(h, 0.9, 0.6)
        base["rim"] = from_hls(h + 0.45, 0.72, 0.8)
    if colors.get("rim"):
        base["rim"] = colors["rim"]
    li = mood["light"]
    for key in ("hemi", "keyI", "env", "glowI", "rimI"):
        base[key] = round(base[key] * li, 3)
    base["exposure"] = mood["exposure"]
    return base


def scene_colors(kit, colors):
    out = dict(KITS[kit]["colors"])
    out.update({k: v for k, v in colors.items() if v})
    if colors.get("glow") and not colors.get("objects") and kit != "salon":
        # derive a matching object palette around the glow colour
        h, l, s = hls(colors["glow"])
        out["objects"] = [from_hls(h + d, 0.6, 0.8) for d in (0, 0.12, -0.12, 0.3, 0.5)]
    return out


def bokeh_for(kit, colors):
    if colors.get("glow"):
        h, l, s = hls(colors["glow"])
        return [colors["glow"], from_hls(h, 0.78, s), from_hls(h + 0.08, 0.6, s), from_hls(h + 0.45, 0.7, 0.7)]
    return KITS[kit]["bokeh"]


def mote_for(kit, colors):
    if colors.get("glow") and kit != "party":
        h, l, s = hls(colors["glow"])
        return from_hls(h, 0.72, s)
    return KITS[kit]["mote"]
