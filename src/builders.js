// Mesh factories for every object kind and prop. Each builder returns a group whose
// origin is the top-centre contact point (see KINDS in timeline.js for the colliders
// these meshes are sized to).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const phys = (o) => new THREE.MeshPhysicalMaterial(o);
const shadow = (m, cast = true, recv = true) => { m.castShadow = cast; m.receiveShadow = recv; return m; };
const mesh = (geo, mat, x = 0, y = 0, z = 0) => { const m = shadow(new THREE.Mesh(geo, mat)); m.position.set(x, y, z); return m; };

// ------------------------------------------------------------------ textures
export function canvasTexture(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

export function ballTexture(base = '#f4e7cb', stripe = '#c21f2c') {
  return canvasTexture(1024, 512, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    // faint warm mottling so the clearcoat has something to sit on
    for (let i = 0; i < 900; i++) {
      g.fillStyle = `rgba(${200 + (i % 40)}, ${170 + (i % 30)}, 120, 0.035)`;
      const x = (i * 97.13) % w, y = (i * 53.71) % h;
      g.beginPath(); g.arc(x, y, 6 + (i % 13), 0, Math.PI * 2); g.fill();
    }
    const band = h * 0.11;
    g.fillStyle = stripe; g.fillRect(0, h / 2 - band / 2, w, band);
    g.fillStyle = '#' + new THREE.Color(stripe).multiplyScalar(0.6).getHexString();
    g.fillRect(0, h / 2 - band / 2 - 3, w, 3); g.fillRect(0, h / 2 + band / 2, w, 3);
  });
}

function stripeTexture(colA, colB, n = 8, diagonal = true) {
  const t = canvasTexture(512, 512, (g, w, h) => {
    g.fillStyle = colA; g.fillRect(0, 0, w, h);
    g.fillStyle = colB;
    const s = w / n;
    for (let i = -n; i < n * 2; i += 2) {
      g.beginPath();
      if (diagonal) { g.moveTo(i * s, 0); g.lineTo(i * s + s, 0); g.lineTo(i * s + s + h, h); g.lineTo(i * s + h, h); }
      else { g.rect(0, i * s, w, s); }
      g.fill();
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

export function softDotTexture() {
  return canvasTexture(64, 64, (g, w) => {
    const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.55)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, w, w);
  });
}

// ------------------------------------------------------------------ materials
export const M = {
  ivory: () => phys({ color: 0xf7efdd, roughness: 0.32, clearcoat: 0.7, clearcoatRoughness: 0.12, sheen: 0.3, sheenColor: 0xffffff }),
  ebony: () => phys({ color: 0x141118, roughness: 0.22, clearcoat: 1, clearcoatRoughness: 0.05 }),
  gold: phys({ color: 0xe0ac4c, metalness: 1, roughness: 0.22, clearcoat: 0.4 }),
  goldDark: phys({ color: 0xb07a2a, metalness: 1, roughness: 0.32 }),
  paper: phys({ color: 0xf1e3c4, roughness: 0.85 }),
  white: phys({ color: 0xffffff, roughness: 0.25, clearcoat: 0.6 }),
  black: phys({ color: 0x050505, roughness: 0.2, clearcoat: 1 }),
};

// ------------------------------------------------------------------ googly eyes
// An eye is a glossy white dome with a black pupil that slides inside it. main.js
// moves the pupil toward the ball every frame.
const eyeWhiteGeo = new THREE.SphereGeometry(1, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2);
const pupilGeo = new THREE.CircleGeometry(1, 24);
const eyeRimGeo = new THREE.TorusGeometry(1, 0.08, 6, 28);
const eyeWhiteMat = phys({ color: 0xffffff, roughness: 0.08, clearcoat: 1, transmission: 0, ior: 1.5 });
const pupilMat = new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.4 });
export const eyes = [];
const OPT = { eyes: true };
export function setOptions(o) { Object.assign(OPT, o); }
// shiny metal (trims, rims, rings) in any colour, cached
const metals = {};
export function metal(hex) {
  return metals[hex] || (metals[hex] = phys({ color: new THREE.Color(hex), metalness: 1, roughness: 0.22, clearcoat: 0.4 }));
}
export function googlyEye(size, owner) {
  const g = new THREE.Group();
  const white = new THREE.Mesh(eyeWhiteGeo, eyeWhiteMat);
  white.rotation.x = Math.PI / 2; white.scale.set(size, size * 0.45, size); // dome faces +Z
  white.castShadow = true;
  const rim = new THREE.Mesh(eyeRimGeo, eyeWhiteMat); rim.scale.setScalar(size);
  const pupil = new THREE.Mesh(pupilGeo, pupilMat);
  pupil.scale.setScalar(size * 0.52);
  pupil.position.z = size * 0.47;
  g.add(white, rim, pupil);
  const eye = { group: g, pupil, size, owner, lid: null };
  eyes.push(eye);
  return { group: g, eye };
}
function eyePair(parent, owner, size, y, z, sep, opts = {}) {
  const out = [];
  if (!OPT.eyes && !opts.always) return out;
  for (const s of [-1, 1]) {
    const { group, eye } = googlyEye(size * (s === 1 && opts.odd ? 1.25 : 1), owner);
    group.position.set(s * sep, y, z);
    if (opts.tilt) group.rotation.y = s * opts.tilt;
    parent.add(group);
    out.push(eye);
  }
  return out;
}

// ------------------------------------------------------------------ object kinds
const GEO = {
  whiteKey: new RoundedBoxGeometry(0.36, 0.2, 1.24, 3, 0.035),
  whiteTrim: new THREE.BoxGeometry(0.37, 0.035, 1.25),
  frontPlate: new THREE.BoxGeometry(0.3, 0.06, 0.012),
  blackKey: new RoundedBoxGeometry(0.26, 0.26, 0.84, 3, 0.04),
  hex: new THREE.CylinderGeometry(0.21, 0.21, 0.6, 6, 1),
  hexBig: new THREE.CylinderGeometry(0.32, 0.32, 1.0, 6, 1),
  shard: new THREE.ConeGeometry(0.09, 0.42, 6),
  drumBody: new THREE.CylinderGeometry(0.33, 0.33, 0.34, 40, 1, true),
  drumSkin: new THREE.CircleGeometry(0.325, 40),
  rim: new THREE.TorusGeometry(0.33, 0.025, 10, 48),
  lug: new THREE.BoxGeometry(0.035, 0.12, 0.035),
  jelly: new RoundedBoxGeometry(0.38, 0.38, 0.38, 4, 0.07),
  spot: new THREE.SphereGeometry(1, 12, 8),
};
GEO.hex.rotateY(Math.PI / 6);
GEO.hexBig.rotateY(Math.PI / 6);


function hsl(h, s, l) { return new THREE.Color().setHSL(h, s, l, THREE.SRGBColorSpace); }

export function buildObject(o, pal) {
  const g = new THREE.Group();
  const GLOW = new THREE.Color(pal.hit);
  const KEY_GLOW = GLOW, CAVE_GLOW = GLOW, PARTY_GLOW = GLOW;
  const trim = metal(pal.accent);
  const objCol = (i) => new THREE.Color(pal.objects[((i % pal.objects.length) + pal.objects.length) % pal.objects.length]);
  const glow = [];   // materials whose emissive lights up on a hit
  const anim = {};   // sub-groups main.js animates
  const add = (m) => { g.add(m); return m; };
  const k = o.kind;
  if (k === 'whiteKey') {
    const mat = M.ivory(); mat.emissive = KEY_GLOW.clone(); glow.push(mat);
    add(mesh(GEO.whiteKey, mat, 0, -0.1, 0));
    add(mesh(GEO.whiteTrim, trim, 0, -0.185, 0));
    add(mesh(GEO.frontPlate, trim, 0, -0.1, 0.626));
  } else if (k === 'blackKey') {
    const mat = M.ebony(); mat.emissive = KEY_GLOW.clone(); glow.push(mat);
    add(mesh(GEO.blackKey, mat, 0, -0.13, -0.18));
    const tr = add(mesh(new THREE.BoxGeometry(0.27, 0.03, 0.85), trim, 0, -0.245, -0.18));
    tr.castShadow = false;
  } else if (k === 'books') {
    const hs = [0.16, 0.17, 0.15];
    let y = 0;
    hs.forEach((h, j) => {
      const c = objCol(o.id + j);
      const cover = phys({ color: c, roughness: 0.55, clearcoat: 0.3, emissive: KEY_GLOW.clone() });
      glow.push(cover);
      const w = 0.68 - j * 0.02, d = 0.86 - (j % 2) * 0.04;
      const book = new THREE.Group();
      book.add(mesh(new RoundedBoxGeometry(w, h, d, 2, 0.02), cover, 0, 0, 0));
      book.add(mesh(new THREE.BoxGeometry(w - 0.02, h * 0.8, d - 0.05), M.paper, -0.012, 0, -0.012));
      // gold bands on the spine (+Z)
      for (const by of [-h * 0.3, h * 0.3]) book.add(mesh(new THREE.BoxGeometry(w * 0.9, 0.012, 0.01), trim, 0, by, d / 2 + 0.002));
      book.position.set(0, y - h / 2, 0);
      book.rotation.y = j === 0 ? 0 : (j % 2 ? 0.05 : -0.04);
      g.add(book);
      if (j === 1) eyePair(book, o, 0.055, 0.0, d / 2 + 0.006, 0.09, { odd: o.id % 2 === 0 });
      y -= h;
    });
  } else if (k === 'crystal' || k === 'bigCrystal') {
    const big = k === 'bigCrystal';
    const gh = GLOW.getHSL({}, THREE.SRGBColorSpace).h;
    const hue = big ? gh : gh - 0.05 + ((o.midi % 12) / 12) * 0.2;
    const mat = phys({ color: hsl(hue, 0.7, 0.55), roughness: 0.08, metalness: 0.0, clearcoat: 1,
      transparent: true, opacity: 0.88, emissive: CAVE_GLOW.clone(), iridescence: 0.6, iridescenceIOR: 1.6,
      flatShading: true });
    glow.push(mat);
    add(mesh(big ? GEO.hexBig : GEO.hex, mat, 0, big ? -0.5 : -0.3, 0));
    const n = big ? 5 : 2;
    for (let j = 0; j < n; j++) {
      const a = j / n * Math.PI * 2 + o.id;
      const s = mesh(GEO.shard, mat, Math.cos(a) * (big ? 0.34 : 0.2), big ? -0.72 : -0.5, Math.sin(a) * (big ? 0.34 : 0.2));
      s.rotation.set(Math.sin(a) * 0.7, 0, -Math.cos(a) * 0.7);
      s.scale.setScalar(big ? 1.2 : 0.7);
      add(s);
    }
  } else if (k === 'mushroom') {
    const cc = objCol(o.id);
    const capMat = phys({ color: cc, roughness: 0.35, clearcoat: 0.8, emissive: cc.clone().lerp(new THREE.Color(1, 1, 1), 0.25) });
    glow.push(capMat);
    const cap = mesh(new THREE.SphereGeometry(0.38, 40, 16, 0, Math.PI * 2, 0, Math.PI / 2), capMat, 0, -0.18, 0);
    cap.scale.y = 0.47;
    add(cap);
    const under = mesh(new THREE.CircleGeometry(0.37, 40), phys({ color: 0xe8d6c0, roughness: 0.9, side: THREE.DoubleSide }), 0, -0.18, 0);
    under.rotation.x = Math.PI / 2; add(under);
    for (let j = 0; j < 7; j++) {
      const a = j * 2.4 + o.id, el = 0.35 + (j % 3) * 0.33;
      const sp = mesh(GEO.spot, M.white,
        Math.cos(a) * 0.38 * Math.sin(el + 0.5) * 0.95, -0.18 + 0.18 * Math.cos(el + 0.5) * 0.98, Math.sin(a) * 0.38 * Math.sin(el + 0.5) * 0.95);
      sp.scale.set(0.05, 0.02, 0.05); sp.lookAt(0, -0.6, 0); add(sp);
    }
    const stem = mesh(new THREE.CylinderGeometry(0.1, 0.13, 0.58, 24), phys({ color: 0xf0e2c8, roughness: 0.6 }), 0, -0.46, 0);
    add(stem);
    eyePair(g, o, 0.045, -0.38, 0.115, 0.05, { odd: true });
  } else if (k === 'drum' || k === 'stage') {
    const s = k === 'stage' ? 0.9 / 0.33 : 1;
    const hh = k === 'stage' ? 0.25 : 0.17;
    const c = k === 'stage' ? new THREE.Color(pal.stage || pal.objects[0]) : objCol(o.id + 1);
    const bodyMat = phys({ color: c, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.05, metalness: 0.1 });
    const body = mesh(GEO.drumBody, bodyMat, 0, -hh, 0);
    body.scale.set(s, hh / 0.17, s); add(body);
    const skinMat = phys({ color: 0xf6efe2, roughness: 0.55, emissive: PARTY_GLOW.clone(),
      map: k === 'stage' ? starTexture(pal.hit, pal.accent) : null });
    glow.push(skinMat);
    const skin = mesh(GEO.drumSkin, skinMat, 0, -0.001, 0); skin.rotation.x = -Math.PI / 2; skin.scale.setScalar(s); add(skin);
    const bottom = mesh(GEO.drumSkin, bodyMat, 0, -2 * hh, 0); bottom.rotation.x = Math.PI / 2; bottom.scale.setScalar(s); add(bottom);
    for (const ry of [-0.025, -2 * hh + 0.02]) {
      const rim = mesh(GEO.rim, trim, 0, ry, 0); rim.rotation.x = Math.PI / 2; rim.scale.set(s, s, 1); add(rim);
    }
    const nl = k === 'stage' ? 16 : 8;
    for (let j = 0; j < nl; j++) {
      const a = j / nl * Math.PI * 2;
      const l = mesh(GEO.lug, trim, Math.cos(a) * 0.335 * s, -hh, Math.sin(a) * 0.335 * s);
      l.scale.y = hh / 0.17; add(l);
    }
    if (k === 'drum') bodyMat.emissive = PARTY_GLOW.clone(), glow.push(bodyMat);
  } else if (k === 'jelly') {
    const c = objCol(o.id);
    const mat = phys({ color: c, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.02, transparent: true,
      opacity: 0.8, emissive: c.clone(), sheen: 0.5, sheenColor: 0xffffff });
    glow.push(mat);
    const wob = new THREE.Group(); wob.position.y = -0.38; g.add(wob);
    const cube = mesh(GEO.jelly, mat, 0, 0.19, 0); wob.add(cube);
    const core = mesh(new RoundedBoxGeometry(0.26, 0.26, 0.26, 2, 0.06), phys({ color: c.clone().multiplyScalar(0.55), roughness: 0.4, transparent: true, opacity: 0.5 }), 0, 0.19, 0);
    core.castShadow = false; wob.add(core);
    eyePair(wob, o, 0.05, 0.24, 0.195, 0.075, { odd: o.id % 3 === 0 });
    anim.wobble = wob;
  } else if (k === 'duck') {
    const yellow = phys({ color: 0xffcf1a, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.08, emissive: new THREE.Color(0x6a3a00) });
    glow.push(yellow);
    const sq = new THREE.Group(); sq.position.y = -0.32; g.add(sq);
    const body = mesh(new THREE.SphereGeometry(1, 40, 24), yellow, 0, 0.16, -0.02); body.scale.set(0.27, 0.16, 0.21); sq.add(body);
    const tail = mesh(new THREE.ConeGeometry(0.07, 0.16, 16), yellow, 0, 0.24, -0.2); tail.rotation.x = -1.0; sq.add(tail);
    const head = mesh(new THREE.SphereGeometry(0.13, 32, 20), yellow, 0, 0.37, 0.3); sq.add(head);
    const beak = mesh(new THREE.SphereGeometry(1, 20, 12), phys({ color: 0xff6a00, roughness: 0.3, clearcoat: 1 }), 0, 0.34, 0.42);
    beak.scale.set(0.07, 0.03, 0.06); sq.add(beak);
    const e = eyePair(sq, o, 0.04, 0.43, 0.395, 0.055, { tilt: 0.35 });
    e.forEach((x) => { x.group.rotation.x = -0.3; });
    anim.squash = sq;
  }
  g.traverse((m) => { if (m.isMesh) m.userData.owner = o.id; });
  return { group: g, glow, anim };
}

function starTexture(star = '#ff4f9a', ring = '#ffcf3a') {
  return canvasTexture(512, 512, (g, w, h) => {
    g.fillStyle = '#f6efe2'; g.fillRect(0, 0, w, h);
    g.fillStyle = star;
    g.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? 70 : 170;
      g.lineTo(w / 2 + Math.cos(a) * r, h / 2 + Math.sin(a) * r);
    }
    g.fill();
    g.strokeStyle = ring; g.lineWidth = 14;
    g.beginPath(); g.arc(w / 2, h / 2, 220, 0, Math.PI * 2); g.stroke();
  });
}

// ------------------------------------------------------------------ props
export function buildTroll(p) {
  const g = new THREE.Group();
  const skin = phys({ color: 0x6f8a5a, roughness: 0.75, sheen: 0.6, sheenColor: 0xb6d79a });
  const ledge = mesh(new RoundedBoxGeometry(1.2, 0.16, 0.9, 3, 0.05), phys({ color: 0x2c3a3c, roughness: 0.95, flatShading: true }), 0, -0.08, 0);
  g.add(ledge);
  const bodyG = new THREE.Group(); g.add(bodyG);
  const body = mesh(new THREE.SphereGeometry(0.36, 40, 28), skin, 0, 0.3, 0); body.scale.set(1.05, 0.95, 0.9); bodyG.add(body);
  const belly = mesh(new THREE.SphereGeometry(0.25, 30, 20), phys({ color: 0x9fb07a, roughness: 0.8 }), 0, 0.22, 0.16); belly.scale.set(1, 0.9, 0.6); bodyG.add(belly);
  const nose = mesh(new THREE.SphereGeometry(0.11, 24, 16), phys({ color: 0x8a6a5a, roughness: 0.6 }), 0, 0.36, 0.33); nose.scale.set(1, 0.8, 1.1); bodyG.add(nose);
  for (const s of [-1, 1]) {
    const ear = mesh(new THREE.ConeGeometry(0.08, 0.26, 16), skin, s * 0.36, 0.45, 0); ear.rotation.z = -s * 1.2; bodyG.add(ear);
    const foot = mesh(new THREE.SphereGeometry(0.1, 16, 10), skin, s * 0.17, 0.03, 0.25); foot.scale.set(1, 0.6, 1.4); bodyG.add(foot);
    const tuft = mesh(new THREE.ConeGeometry(0.03, 0.12, 8), phys({ color: 0x3a2a1a, roughness: 1 }), s * 0.05, 0.66, 0.02); tuft.rotation.z = s * 0.4; bodyG.add(tuft);
  }
  const eyesG = new THREE.Group(); eyesG.position.set(0, 0.5, 0.27); eyesG.rotation.x = -0.25; bodyG.add(eyesG);
  const e = eyePair(eyesG, { id: -1 }, 0.075, 0, 0, 0.1, { tilt: 0.3, odd: true, always: true });
  // sleepy eyelids that snap open on the crash
  const lidMat = phys({ color: 0x5f7a4c, roughness: 0.7 });
  const lids = e.map((x) => {
    const lid = mesh(new THREE.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), lidMat);
    lid.scale.setScalar(x.size * 1.12); lid.rotation.x = Math.PI / 2;
    x.group.add(lid); return lid;
  });
  const mouth = mesh(new THREE.SphereGeometry(0.06, 16, 10), phys({ color: 0x2a0e10, roughness: 0.8 }), 0, 0.2, 0.31);
  mouth.scale.set(1.2, 0.25, 0.4); bodyG.add(mouth);
  // nightcap
  const capTex = stripeTexture('#d8213a', '#f6f0e8', 10, false);
  const cap = new THREE.Group();
  const cone = mesh(new THREE.ConeGeometry(0.2, 0.55, 32, 1, true), phys({ map: capTex, roughness: 0.8, sheen: 1, sheenColor: 0xffffff, side: THREE.DoubleSide }), 0, 0.26, 0);
  cone.rotation.z = -0.25; cone.position.x = 0.06;
  const brim = mesh(new THREE.TorusGeometry(0.2, 0.045, 10, 32), phys({ color: 0xf6f0e8, roughness: 0.9, sheen: 1 }), 0, 0, 0); brim.rotation.x = Math.PI / 2;
  const pom = mesh(new THREE.SphereGeometry(0.07, 16, 12), phys({ color: 0xf6f0e8, roughness: 0.95, sheen: 1 }), 0.17, 0.52, 0);
  cap.add(cone, brim, pom);
  cap.position.set(-0.04, 0.6, -0.02); cap.rotation.z = 0.35;
  bodyG.add(cap);
  return { group: g, body: bodyG, cap, lids, mouth, eyes: e };
}

const pinProfile = (() => {
  const pts = [[0, 0], [0.05, 0], [0.07, 0.04], [0.085, 0.11], [0.08, 0.17], [0.055, 0.25], [0.04, 0.29], [0.042, 0.32], [0.05, 0.36], [0.046, 0.41], [0.03, 0.435], [0, 0.44]];
  return pts.map(([x, y]) => new THREE.Vector2(x, y));
})();
const pinTex = (() => {
  const t = canvasTexture(64, 256, (g, w, h) => {
    g.fillStyle = '#fbf8f2'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#d4182c';
    g.fillRect(0, h * 0.24, w, h * 0.035); g.fillRect(0, h * 0.3, w, h * 0.035);
  });
  t.flipY = false;
  return t;
})();
export function buildPin() {
  const g = new THREE.Group();
  const geo = new THREE.LatheGeometry(pinProfile, 32);
  const m = mesh(geo, phys({ map: pinTex, roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.05 }));
  g.add(m);
  const e = eyePair(g, { id: -2 }, 0.022, 0.37, 0.042, 0.025, {});
  return { group: g, eyes: e };
}

export function buildBalloon(color) {
  const g = new THREE.Group();
  const mat = phys({ color, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.1, sheen: 0.6, sheenColor: 0xffffff });
  const b = mesh(new THREE.SphereGeometry(0.3, 40, 28), mat); b.scale.set(1, 1.18, 1); g.add(b);
  const knot = mesh(new THREE.ConeGeometry(0.04, 0.07, 12), mat, 0, -0.37, 0); g.add(knot);
  const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, -0.38, 0), new THREE.Vector3(0.05, -0.6, 0.02), new THREE.Vector3(-0.04, -0.85, -0.02), new THREE.Vector3(0.02, -1.15, 0)]);
  const str = new THREE.Mesh(new THREE.TubeGeometry(curve, 20, 0.006, 5), phys({ color: 0xf0f0f0, roughness: 0.6 }));
  g.add(str);
  return g;
}

export function buildCandle() {
  const g = new THREE.Group();
  const wax = mesh(new THREE.CylinderGeometry(0.07, 0.075, 0.36, 24), phys({ color: 0xf5ead2, roughness: 0.5, sheen: 0.5, sheenColor: 0xffe0b0 }), 0, -0.22, 0);
  const holder = mesh(new THREE.CylinderGeometry(0.11, 0.09, 0.05, 24), M.gold, 0, -0.41, 0);
  const flame = new THREE.Mesh(new THREE.SphereGeometry(0.035, 16, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.0, 0.62, 0.25).multiplyScalar(7) }));
  flame.scale.set(1, 2.1, 1); flame.position.y = 0.0;
  g.add(wax, holder, flame);
  return { group: g, flame };
}

export function stripeTex(a, b, n, diag) { return stripeTexture(a, b, n, diag); }
