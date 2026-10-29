// The video, as a pure function of time: window.renderFrame(t) poses everything from the
// timeline and renders one frame. Used by tools/render.mjs (headless) and for previews
// (open index.html?t=12.3 for a still, or index.html?play for real-time playback).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { buildTimeline, backdropAt, hexToRgb, BALL_R, POLE_R } from './timeline.js';
import { buildObject, buildTroll, buildPin, buildBalloon, buildCandle, ballTexture, softDotTexture, canvasTexture, stripeTex, eyes, metal, setOptions } from './builders.js';

const params = new URLSearchParams(location.search);
const score = await (await fetch(params.get('score') || '/build/classic/score.json')).json();
const tl = buildTimeline(score);
const W = score.width, H = score.height;
const mood = score.mood;
const NS = score.scenes.length;
const SC = (s) => score.scenes[s - 1];
setOptions({ eyes: score.jokes.googlyEyes !== false });
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const lerp = (a, b, s) => a + (b - a) * s;
const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);
const Q = (q) => new THREE.Quaternion(q[0], q[1], q[2], q[3]);

// ------------------------------------------------------------------ renderer
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.prepend(renderer.domElement);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;
scene.fog = new THREE.Fog(0x000000, ...mood.fog);
const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 140);

// ------------------------------------------------------------------ lighting
const hemi = new THREE.HemisphereLight(0xffffff, 0x000000, 0.5);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xffffff, 2);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -4.5, right: 4.5, top: 4.5, bottom: -4.5, near: 0.5, far: 30 });
key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.02;
key.shadow.radius = 5;
key.shadow.blurSamples = 12;
scene.add(key, key.target);
const poleGlow = new THREE.PointLight(0xffaa44, 6, 7, 1.6);
const rimLight = new THREE.PointLight(0xffffff, 8, 10, 1.4);
const hitLight = new THREE.PointLight(0xffaa44, 0, 3.2, 1.8);
scene.add(poleGlow, rimLight, hitLight);

// per-world look (from the score); blended only while the camera falls through the
// gap between worlds
const LOOK = {};
score.scenes.forEach((sc, i) => { LOOK[i + 1] = sc.look; });
function lookAt(y) {
  const bs = tl.boundaries;
  const f = bs.map((b) => smooth((b + 3 - y) / 6));    // 0 above each band, 1 below it
  const w = {};
  for (let s = 1; s <= NS; s++) w[s] = (s === 1 ? 1 : f[s - 2]) * (s === NS ? 1 : 1 - f[s - 1]);
  const dark = 1 - 0.55 * Math.max(0, ...bs.map((b) => Math.exp(-(((y - b) / 2.2) ** 2))));
  const out = {};
  for (const k of Object.keys(LOOK[1])) {
    if (typeof LOOK[1][k] === 'string') {
      const c = new THREE.Color(0, 0, 0);
      for (let s = 1; s <= NS; s++) c.add(new THREE.Color(LOOK[s][k]).multiplyScalar(w[s]));
      out[k] = c;
    } else {
      let a = 0; for (let s = 1; s <= NS; s++) a += LOOK[s][k] * w[s];
      out[k] = a;
    }
  }
  out.dark = dark;
  out.w = w;
  return out;
}

// ------------------------------------------------------------------ backdrop
const sceneCol = (s) => new THREE.Color().setRGB(...hexToRgb(SC(s).colors.background), THREE.SRGBColorSpace);
const backdrop = new THREE.Mesh(
  new THREE.CylinderGeometry(60, 60, 400, 64, 1, true),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      bnds: { value: [0, 1, 2, 3].map((k) => (k < tl.boundaries.length ? tl.boundaries[k] : -1e9)) },
      cols: { value: [1, 2, 3, 4, 5].map((s) => sceneCol(Math.min(s, NS))) },
      camY: { value: 0 },
    },
    vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `
      uniform float bnds[4]; uniform vec3 cols[5]; uniform float camY; varying vec3 vW;
      void main(){
        // the backdrop is read at a height that follows the view ray, compressed so
        // the world colour band you are in fills the frame
        float y = camY + (vW.y - camY) * 0.12;
        vec3 dark = vec3(0.004, 0.003, 0.008);
        vec3 c = cols[0];
        for (int k = 0; k < 4; k++) if (y < bnds[k]) c = cols[k + 1];
        for (int k = 0; k < 4; k++) {
          float d = y - bnds[k];
          if (abs(d) < 3.) c = d > 0. ? mix(dark, cols[k], smoothstep(0., 1., d / 3.)) : mix(dark, cols[k + 1], smoothstep(0., 1., -d / 3.));
        }
        float a = atan(vW.z, vW.x);
        float stripes = pow(0.5 + 0.5 * sin(a * 5. + vW.y * 0.05), 6.);
        float vert = smoothstep(-60., 60., vW.y - camY);
        c *= 1.15 + 0.4 * stripes - 0.3 * vert;
        gl_FragColor = vec4(c, 1.);
        #include <colorspace_fragment>
      }`,
  }),
);
backdrop.frustumCulled = false;
backdrop.renderOrder = -1;
scene.add(backdrop);

// ------------------------------------------------------------------ pole
// one segment per world, styled by its kit
const yTop = tl.sceneRange[1].top + 12;
const poleSeg = (y0, y1, mat, geo) => {
  const g = geo || new THREE.CylinderGeometry(POLE_R, POLE_R, y0 - y1, 48, Math.ceil((y0 - y1) * 2));
  const m = new THREE.Mesh(g, mat); m.position.y = (y0 + y1) / 2; m.castShadow = m.receiveShadow = true; scene.add(m); return m;
};
const segTop = (s) => (s === 1 ? yTop : tl.boundaries[s - 2]);
const segBot = (s) => (s === NS ? -60 : tl.boundaries[s - 1]);
for (let s = 1; s <= NS; s++) {
  const { kit, colors } = SC(s);
  const y0 = segTop(s), y1 = segBot(s);
  if (kit === 'salon') {
    poleSeg(y0, y1, new THREE.MeshPhysicalMaterial({ color: colors.pole, roughness: 0.45, clearcoat: 0.8, clearcoatRoughness: 0.15 }));
    for (let y = y1 + 1.5; y < y0; y += 1.6) {
      const r = new THREE.Mesh(new THREE.TorusGeometry(POLE_R + 0.01, 0.035, 10, 40), metal(colors.accent));
      r.rotation.x = Math.PI / 2; r.position.y = y; r.castShadow = true; scene.add(r);
    }
  } else if (kit === 'cave') {
    const rockGeo = new THREE.CylinderGeometry(POLE_R, POLE_R, y0 - y1, 40, Math.ceil((y0 - y1) * 2.5));
    const p = rockGeo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      const a = Math.atan2(z, x);
      const n = 1 + 0.12 * Math.sin(a * 3 + y * 1.7) * Math.sin(y * 0.9 + a) + 0.05 * Math.sin(a * 11 + y * 5.3);
      p.setX(i, x * n); p.setZ(i, z * n);
    }
    rockGeo.computeVertexNormals();
    poleSeg(y0, y1, new THREE.MeshPhysicalMaterial({ color: colors.pole, roughness: 0.85, flatShading: true }), rockGeo);
    // little glowing crystals and mushrooms on the rock column (inside r < 0.6, clear of the ball)
    const span = Math.max(2, Math.min(y0, tl.sceneRange[s].top + 6) - Math.max(y1, tl.sceneRange[s].bottom - 6));
    const yb = Math.max(y1, tl.sceneRange[s].bottom - 6);
    const geo = new THREE.ConeGeometry(0.045, 0.22, 6);
    const glow = new THREE.Color(colors.glow);
    const mat = new THREE.MeshPhysicalMaterial({ color: glow.clone().lerp(new THREE.Color(1, 1, 1), 0.3), emissive: glow, emissiveIntensity: 1.6, roughness: 0.1 });
    const n = Math.round(span * 4.5); const inst = new THREE.InstancedMesh(geo, mat, n);
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
    for (let i = 0; i < n; i++) {
      const a = i * 2.399, y = yb + ((i * 0.618) % 1) * span;
      e.set(Math.sin(i) * 0.5, -a, Math.PI / 2 - 0.5);
      q.setFromEuler(e);
      m4.compose(new THREE.Vector3(Math.cos(a) * 0.33, y, Math.sin(a) * 0.33), q, new THREE.Vector3(1, 1 + (i % 3) * 0.4, 1));
      inst.setMatrixAt(i, m4);
    }
    scene.add(inst);
    const capGeo = new THREE.SphereGeometry(0.16, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2);
    const stemGeo = new THREE.CylinderGeometry(0.035, 0.05, 0.22, 10);
    const capCols = colors.objects.slice(0, 2);
    for (let i = 0; i < Math.round(span * 1.1); i++) {
      const a = i * 2.1 + 0.4, y = yb + 1 + ((i * 0.618) % 1) * (span - 2);
      const c = new THREE.Color(capCols[i % capCols.length]);
      const capMat = new THREE.MeshPhysicalMaterial({ color: c, roughness: 0.35, clearcoat: 0.8, emissive: c, emissiveIntensity: 0.35 });
      const g = new THREE.Group();
      const cap = new THREE.Mesh(capGeo, capMat); cap.scale.y = 0.6; cap.position.y = 0.11;
      const stem = new THREE.Mesh(stemGeo, new THREE.MeshPhysicalMaterial({ color: 0xeadbc4, roughness: 0.6 }));
      g.add(cap, stem);
      g.position.set(Math.cos(a) * 0.42, y, Math.sin(a) * 0.42);
      g.rotation.set(Math.sin(a) * 0.5, 0, -Math.cos(a) * 0.5);
      g.scale.setScalar(0.8 + (i % 3) * 0.25);
      g.traverse((m) => { if (m.isMesh) m.castShadow = true; });
      scene.add(g);
    }
  } else {
    const candy = stripeTex('#f8f2ea', colors.pole, 6, true);
    candy.repeat.set(1, (y0 - y1) / 1.2);
    poleSeg(y0, y1, new THREE.MeshPhysicalMaterial({ map: candy, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.05 }));
  }
}

// ------------------------------------------------------------------ objects
const palette = (s) => ({ ...SC(s).colors, kit: SC(s).kit, hit: SC(s).look.hit });
const objs = tl.objects.map((o) => {
  const b = buildObject(o, palette(o.scene));
  b.group.rotation.y = o.yaw;
  scene.add(b.group);
  return { o, ...b };
});
// support arms from the pole
const armMats = {};
const armMat = (s) => armMats[s] || (armMats[s] = SC(s).kit === 'salon' ? metal(SC(s).colors.accent)
  : SC(s).kit === 'cave' ? new THREE.MeshPhysicalMaterial({ color: new THREE.Color(SC(s).colors.pole).multiplyScalar(1.2), roughness: 0.9 })
    : new THREE.MeshPhysicalMaterial({ color: 0xfff6ee, roughness: 0.3, clearcoat: 1 }));
for (const a of tl.props.filter((p) => p.type === 'arm')) {
  const A = V(a.a), B = V(a.b);
  const len = A.distanceTo(B);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(a.r, a.r, len, 12), armMat(a.scene));
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  m.castShadow = m.receiveShadow = true;
  scene.add(m);
}

// ------------------------------------------------------------------ props
const propState = [];
const zTex = canvasTexture(128, 128, (g) => {
  g.fillStyle = '#e9fbff'; g.font = 'italic 900 110px Playfair, serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('z', 64, 70);
});
for (const p of tl.props) {
  if (p.type === 'troll') {
    const t = buildTroll(p);
    t.group.position.copy(V(p.pos)); t.group.rotation.y = p.yaw;
    t.group.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
    scene.add(t.group);
    const zs = [0, 1, 2].map(() => {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: zTex, transparent: true, depthWrite: false, fog: false }));
      t.group.add(s); return s;
    });
    propState.push({ p, t, zs });
  } else if (p.type === 'pin') {
    const pin = buildPin();
    pin.group.position.copy(V(p.pos)); pin.group.rotation.y = p.yaw;
    pin.group.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
    scene.add(pin.group);
    propState.push({ p, pin });
  } else if (p.type === 'balloon') {
    const cols = SC(p.scene).colors.objects;
    const b = buildBalloon(cols[p.idx % cols.length]);
    b.position.copy(V(p.pos)); b.rotation.y = p.yaw;
    b.traverse((m) => { if (m.isMesh) m.castShadow = true; });
    scene.add(b);
    propState.push({ p, b });
  } else if (p.type === 'candle') {
    const c = buildCandle();
    c.group.position.copy(V(p.pos)); c.group.rotation.y = p.yaw;
    scene.add(c.group);
    propState.push({ p, c });
  }
}

// ------------------------------------------------------------------ particles
const dot = softDotTexture();
function particles(scene_, n, color, size, additive, confetti, paletteHex) {
  const r = tl.sceneRange[scene_];
  const y0 = r.top + 8, y1 = r.bottom - 8;
  const pos = new Float32Array(n * 3), seed = new Float32Array(n), col = new Float32Array(n * 3);
  const palette = [...(paletteHex || []), '#ffffff'].map((c) => new THREE.Color(c));
  for (let i = 0; i < n; i++) {
    const a = i * 2.39996, rad = 3.4 + ((i * 0.7548) % 1) * 9;
    pos.set([Math.cos(a) * rad, y1 + ((i * 0.5698) % 1) * (y0 - y1), Math.sin(a) * rad], i * 3);
    seed[i] = (i * 0.618034) % 1;
    const c = confetti ? palette[i % palette.length] : new THREE.Color(color);
    col.set([c.r, c.g, c.b], i * 3);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('seed', new THREE.BufferAttribute(seed, 1));
  geo.setAttribute('col', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
    uniforms: { time: { value: 0 }, map: { value: dot }, size: { value: size }, span: { value: y0 - y1 }, yBot: { value: y1 }, confetti: { value: confetti ? 1 : 0 } },
    vertexShader: `
      attribute float seed; attribute vec3 col; uniform float time, size, span, yBot, confetti; varying vec3 vC; varying float vA; varying float vS;
      void main(){
        vec3 p = position;
        float fall = confetti > 0.5 ? -0.55 : 0.12;
        p.y = yBot + mod(p.y - yBot + time * fall * (0.6 + seed), span);
        float a = time * (0.05 + 0.04 * seed) * (confetti > 0.5 ? 2.0 : 1.0);
        p.xz = mat2(cos(a), -sin(a), sin(a), cos(a)) * p.xz;
        p.x += sin(time * 0.7 + seed * 40.) * 0.25;
        vec4 mv = modelViewMatrix * vec4(p, 1.);
        gl_Position = projectionMatrix * mv;
        float flick = confetti > 0.5 ? abs(sin(time * (4. + 6. * seed) + seed * 30.)) : (0.6 + 0.4 * sin(time * 2. + seed * 50.));
        vS = flick;
        gl_PointSize = size * (0.5 + seed) * (confetti > 0.5 ? max(flick, 0.25) : 1.0) * 300. / -mv.z;
        vA = smoothstep(26., 8., -mv.z) * smoothstep(0.8, 2.5, -mv.z);
        vC = col;
      }`,
    fragmentShader: `
      uniform sampler2D map; uniform float confetti; varying vec3 vC; varying float vA; varying float vS;
      void main(){
        float a = texture2D(map, gl_PointCoord).a;
        if (confetti > 0.5) { vec2 q = abs(gl_PointCoord - 0.5); a = step(max(q.x, q.y * (0.4 + vS)), 0.42); }
        gl_FragColor = vec4(vC * (confetti > 0.5 ? 1.0 : 2.2), a * vA * (confetti > 0.5 ? 0.9 : 0.55));
        #include <colorspace_fragment>
      }`,
  });
  const pts = new THREE.Points(geo, mat);
  pts.frustumCulled = false;
  scene.add(pts);
  return mat;
}
// big out-of-focus lights far behind the tower, for depth
function bokeh(scene_, n, colors) {
  const r = tl.sceneRange[scene_];
  const y0 = r.top + 10, y1 = r.bottom - 10;
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), sz = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const a = i * 2.39996 + 1.3, rad = 16 + ((i * 0.37) % 1) * 18;
    pos.set([Math.cos(a) * rad, y1 + ((i * 0.6180339) % 1) * (y0 - y1), Math.sin(a) * rad], i * 3);
    const c = new THREE.Color(colors[i % colors.length]);
    col.set([c.r, c.g, c.b], i * 3);
    sz[i] = 0.6 + ((i * 0.7548) % 1) * 1.4;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('col', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('sz', new THREE.BufferAttribute(sz, 1));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { map: { value: dot } },
    vertexShader: `attribute vec3 col; attribute float sz; varying vec3 vC;
      void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.); gl_Position = projectionMatrix * mv;
        gl_PointSize = sz * 1100. / -mv.z; vC = col; }`,
    fragmentShader: `uniform sampler2D map; varying vec3 vC;
      void main(){ vec2 q = gl_PointCoord - 0.5; float d = length(q) * 2.;
        float a = smoothstep(1.0, 0.82, d) * (0.55 + 0.45 * smoothstep(0.5, 0.95, d));
        gl_FragColor = vec4(vC * 0.16 * a, 1.0);
        #include <colorspace_fragment>
      }`,
  });
  const pts = new THREE.Points(geo, mat);
  pts.frustumCulled = false;
  scene.add(pts);
}
const partMats = [];
for (let s = 1; s <= NS; s++) {
  const sc = SC(s);
  bokeh(s, 70, sc.bokeh);
  const n = Math.round(800 * (mood.particles || 1));
  if (sc.particles === 'confetti') partMats.push(particles(s, n, '#ffffff', 0.06, false, true, sc.colors.objects));
  else partMats.push(particles(s, n, sc.mote, sc.particles === 'spores' ? 0.045 : 0.05, true, false));
}

// ------------------------------------------------------------------ ball
const ballOuter = new THREE.Group();
const ballInner = new THREE.Mesh(
  new THREE.SphereGeometry(BALL_R, 96, 64),
  new THREE.MeshPhysicalMaterial({ map: ballTexture(score.ball.color, score.ball.stripe), roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.03, sheen: 0.2, sheenColor: 0xffffff }),
);
ballInner.castShadow = true; ballInner.receiveShadow = true;
ballOuter.add(ballInner);
scene.add(ballOuter);

// ------------------------------------------------------------------ post
const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(1);
composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), ...mood.bloom);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const finish = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, aspect: { value: W / H }, vig: { value: mood.vignette }, grain: { value: mood.grain } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }`,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float time, aspect, vig, grain; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + time * 7.13) * 43758.5453); }
    void main(){
      vec4 c = texture2D(tDiffuse, vUv);
      vec2 d = (vUv - 0.5) * vec2(aspect, 1.0) * 1.25;
      float v = smoothstep(0.95, 0.25, length(d));
      c.rgb *= mix(1.0 - vig, 1.0, v);
      c.rgb += (hash(vUv * 1000.) - 0.5) * grain;
      gl_FragColor = c;
    }`,
});
composer.addPass(finish);

// ------------------------------------------------------------------ per-frame update
const tmpV = new THREE.Vector3();
const up = new THREE.Vector3(0, 1, 0);
const finEl = document.getElementById('fin');
finEl.innerHTML = '';
const endText = score.endText || '';
for (const ch of endText) { const sp = document.createElement('span'); sp.textContent = ch === ' ' ? '\u00a0' : ch; finEl.appendChild(sp); }
finEl.style.fontSize = `${Math.round(Math.min(300, 1250 / Math.max(1, endText.length)))}px`;
const finSpans = [...finEl.querySelectorAll('span')];
const beats3 = score.beats.filter((b) => b.scene === NS).map((b) => b.t);
const landT = tl.ending.land !== undefined ? tl.ending.land : tl.ending.fin - 0.3;
const melTimes = tl.mel.map((n) => n.t);
const lastHitBefore = (t) => { let k = -1; for (let i = 0; i < melTimes.length && melTimes[i] <= t; i++) k = i; return k; };
const lastHitOn = (o, t) => { let h = -Infinity; for (const x of o.hitTimes) if (x <= t) h = x; return h; };

function update(t) {
  // camera
  const cam = tl.camera(t);
  camera.position.copy(V(cam.pos));
  camera.fov = cam.fov; camera.updateProjectionMatrix();
  camera.lookAt(V(cam.target));
  const camY = cam.pos[1];

  // ball: squash/stretch along an axis, spin inside it
  const b = tl.ball(t);
  ballOuter.position.copy(V(b.p));
  const R = new THREE.Quaternion().setFromUnitVectors(up, V(b.axis).normalize());
  ballOuter.quaternion.copy(R);
  const side = 1 / Math.sqrt(b.scale);
  ballOuter.scale.set(side, b.scale, side);
  ballInner.quaternion.copy(R.clone().invert().multiply(Q(b.rot)));

  // objects
  for (const ob of objs) {
    const { o, group, glow, anim } = ob;
    const pose = tl.objectPose(o, t);
    const vis = Math.abs(pose.pos[1] - camY) < 16 && pose.pos[1] > camY - 30;
    group.visible = vis;
    if (!vis) continue;
    group.position.copy(V(pose.pos));
    group.quaternion.copy(Q(pose.q));
    const gl = tl.glowOf(o, t);
    for (const m of glow) m.emissiveIntensity = mood.glowPeak * gl * gl;
    const th = lastHitOn(o, t), tau = t - th;
    if (anim.wobble) {
      const a = tau >= 0 && tau < 1.2 ? 0.16 * Math.exp(-tau / 0.2) * Math.sin(tau * 34) : 0;
      anim.wobble.scale.set(1 + a * 0.6, 1 - a, 1 + a * 0.6);
    }
    if (anim.squash) {
      const a = tau >= 0 && tau < 0.6 ? 0.22 * Math.exp(-tau / 0.09) * Math.sin(Math.min(tau * 28, Math.PI)) : 0;
      anim.squash.scale.set(1 + a * 0.5, 1 - a, 1 + a * 0.5);
    }
  }

  // props
  const ballPos = V(tl.ballRaw(t - 0.05).p);
  for (const ps of propState) {
    const p = ps.p;
    if (ps.t) { // troll
      const { body, cap, lids, mouth, eyes: te } = ps.t;
      const tw = t - p.tWake;
      if (tw < 0) {
        const br = Math.sin(t * Math.PI * 2 / 2.4);
        body.scale.set(1 + 0.02 * br, 1 + 0.035 * br, 1 + 0.02 * br);
        body.position.y = 0;
        lids.forEach((l) => { l.visible = true; });
        mouth.scale.set(1.2, 0.25, 0.4);
        cap.position.set(-0.04, 0.6, -0.02); cap.rotation.set(0, 0, 0.35);
        ps.zs.forEach((s, i) => {
          const ph = ((t / 2.1 + i / 3) % 1 + 1) % 1;
          s.visible = true;
          s.position.set(0.25 + 0.3 * ph + 0.06 * Math.sin(ph * 9), 0.8 + 0.7 * ph, 0.1);
          s.scale.setScalar(0.1 + 0.16 * ph);
          s.material.opacity = Math.sin(Math.PI * ph) * 0.9;
        });
      } else {
        const hop = Math.max(0, 4.2 * tw - 25 * tw * tw);
        body.position.y = hop;
        const s = 1 + 0.12 * Math.exp(-tw / 0.15) * Math.sin(tw * 30);
        body.scale.set(2 - s, s, 2 - s);
        lids.forEach((l) => { l.visible = tw < 0.03; });
        mouth.scale.set(0.9, 1.1, 0.5);
        ps.zs.forEach((z) => { z.visible = false; });
        // the nightcap flies off: ballistic in the troll's frame, tumbling
        cap.position.set(-0.04 + 0.3 * tw, 0.6 + 3.8 * tw - 25 * tw * tw, -0.02 + 1.4 * tw);
        cap.rotation.set(-3 * tw, 0, 0.35 + 9 * tw);
      }
      te.forEach((e) => { e.pupilScale = tw >= 0 ? 0.36 : 0.52; });
    } else if (ps.pin) {
      const g = ps.pin.group;
      const k = p.idx;
      let tilt = 0, hop = 0, bow = 0, kick = 0;
      const cc0 = beats3[0];
      const tEnd = tl.ending;
      // freeze mid-pose during the silence, bow on "Fin."
      const tt = t > tEnd.rollOff && t < tEnd.boing ? tEnd.rollOff : t;
      if (beats3.length && tt >= cc0 - 0.3 && tt < landT) {
        let bi = 0; for (let i = 0; i < beats3.length; i++) if (beats3[i] <= tt) bi = i;
        const bt = beats3[bi], bl = (beats3[bi + 1] || bt + 0.38) - bt;
        const ph = clamp((tt - bt) / bl, 0, 1);
        const sgn = (bi % 2 === 0 ? 1 : -1);
        tilt = sgn * 0.28 * Math.sin(Math.PI * Math.min(1, ph * 1.4));
        hop = 0.05 * Math.sin(Math.PI * ph);
        kick = (bi % 4 === k % 4 ? 1 : 0) * 0.45 * Math.sin(Math.PI * ph);
        if (tt >= tl.tF) { tilt *= 0.6; }
      }
      if (t > landT) bow = 0.55 * smooth((t - landT - 0.25) / 0.35) * (1 - 0.3 * smooth((t - tEnd.fin - 1.2) / 0.5));
      const base = V(p.pos);
      const dip = tl.dipOf(tl.stage, t);
      g.position.set(base.x, base.y + hop + dip, base.z);
      g.rotation.set(0, 0, 0);
      g.rotation.y = p.yaw;
      g.rotateZ(tilt);
      g.rotateX(bow + kick * 0.5);
    } else if (ps.b) {
      const b0 = V(p.pos);
      ps.b.position.set(b0.x + 0.05 * Math.sin(t * 1.1 + p.idx), b0.y + 0.07 * Math.sin(t * 1.7 + p.idx * 2), b0.z);
      ps.b.rotation.z = 0.08 * Math.sin(t * 1.3 + p.idx);
    } else if (ps.c) {
      const f = 1 + 0.12 * Math.sin(t * 23 + p.idx) * Math.sin(t * 7.3 + p.idx * 3);
      ps.c.flame.scale.set(1 / f, 2.1 * f, 1 / f);
      ps.c.group.position.y = p.pos[1] + 0.04 * Math.sin(t * 1.4 + p.idx);
    }
  }

  // googly eyes: pupils roll toward the ball (with a little lag and a jiggle on hits)
  const recent = lastHitBefore(t);
  const jig = recent >= 0 ? Math.exp(-(t - melTimes[recent]) / 0.12) * Math.sin((t - melTimes[recent]) * 55) : 0;
  for (const e of eyes) {
    if (!e.group.parent || !isVisible(e.group)) continue;
    e.group.updateWorldMatrix(true, false);
    tmpV.copy(ballPos);
    e.group.worldToLocal(tmpV);
    const d = Math.hypot(tmpV.x, tmpV.y);
    const reach = e.size * 0.42;
    const k = Math.min(1, d / Math.max(0.2, Math.abs(tmpV.z) * 0.6 + 0.1));
    let x = d > 1e-6 ? tmpV.x / d * reach * k : 0, y = d > 1e-6 ? tmpV.y / d * reach * k : 0;
    x += jig * e.size * 0.12; y -= Math.abs(jig) * e.size * 0.1;
    e.pupil.position.x = x; e.pupil.position.y = y;
    e.pupil.scale.setScalar(e.size * (e.pupilScale || 0.52));
  }

  // lighting follows the camera's world
  const L = lookAt(camY);
  hemi.color.copy(L.sky); hemi.groundColor.copy(L.ground); hemi.intensity = L.hemi * L.dark;
  key.color.copy(L.key); key.intensity = L.keyI * L.dark;
  scene.environmentIntensity = L.env * L.dark;
  const tgt = V(cam.target);
  const fwd = tgt.clone().sub(camera.position).setY(0).normalize();
  const right = new THREE.Vector3().crossVectors(fwd, up).normalize();
  key.target.position.copy(V(b.p));
  key.position.copy(V(b.p)).addScaledVector(up, 8).addScaledVector(right, -3.5).addScaledVector(fwd, -4);
  poleGlow.color.copy(L.glow); poleGlow.intensity = L.glowI * L.dark;
  poleGlow.position.copy(V(b.p)).addScaledVector(fwd, -1.6).addScaledVector(right, -1.2).addScaledVector(up, 0.9);
  rimLight.color.copy(L.rim); rimLight.intensity = L.rimI * L.dark;
  rimLight.position.copy(V(b.p)).addScaledVector(fwd, 1.4).addScaledVector(up, 1.2).addScaledVector(right, 1.6);
  if (recent >= 0) {
    const o = tl.objects[tl.hitObj[recent]];
    const pose = tl.objectPose(o, t);
    hitLight.position.copy(V(pose.pos)).addScaledVector(up, 0.35).addScaledVector(fwd, -0.5);
    hitLight.color.copy(new THREE.Color(LOOK[o.scene].hit));
    hitLight.intensity = 4 * tl.glowOf(o, t);
  }
  renderer.toneMappingExposure = L.exposure;

  // world colour: backdrop + fog
  backdrop.position.set(camera.position.x, camY, camera.position.z);
  backdrop.material.uniforms.camY.value = camY;
  const bg = backdropAt(tl, camY) || [0.02, 0.015, 0.03];
  scene.fog.color.setRGB(...bg, THREE.SRGBColorSpace).multiplyScalar(1.1);
  partMats.forEach((m) => { m.uniforms.time.value = t; });
  finish.uniforms.time.value = (Math.floor(t * score.fps) % 97) * 0.37;

  // "Fin."
  const tf = t - tl.ending.fin;
  finEl.style.opacity = tf > 0 ? '1' : '0';
  finSpans.forEach((s, i) => {
    const u = tf - i * 0.09;
    const a = clamp(u / 0.12, 0, 1);
    const sc = u <= 0 ? 0.4 : 1 + 0.35 * Math.exp(-u / 0.12) * Math.sin(u * 30);
    s.style.opacity = a.toFixed(3);
    s.style.transform = `translateY(${(u <= 0 ? 40 : 40 * Math.exp(-u / 0.08)).toFixed(1)}px) scale(${sc.toFixed(3)})`;
  });
}
function isVisible(o) { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; }

window.renderFrame = async (t) => {
  update(t);
  composer.render();
  return true;
};

await document.fonts.load('italic 900 100px Playfair');
// compile everything once so the first rendered frame is not special
update(0);
renderer.compile(scene, camera);
composer.render();

if (params.has('t')) window.renderFrame(parseFloat(params.get('t')));
if (params.has('play')) {
  const t0 = performance.now() - (parseFloat(params.get('play')) || 0) * 1000;
  const loop = () => { window.renderFrame((performance.now() - t0) / 1000); requestAnimationFrame(loop); };
  loop();
}
window.ready = true;
