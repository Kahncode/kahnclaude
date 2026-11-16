# Figure patterns

Copy a pattern, then change shapes and labels to the subject. All colours come from `base.html` tokens: `--a --b --c` (entities), `--good --bad` (right/wrong), `--fg --muted --rule --panel` (neutral). Text inherits `svg text` styles; use `class="small"` for secondary labels and `class="strong"` for emphasis.

Contents:
1. Two frames side by side
2. Right place vs wrong place (the gap)
3. Swim lanes (timing, server/client, races)
4. Components and data flow
5. Geometry drawn to scale
6. Spatial grid / map (cells, radii, who-sees-what)
7. State diagram
8. Pictogram row (tiers, kinds, categories)
9. Interactive: slider that redraws
10. Interactive: step-through sequence (play / next)
11. Interactive: canvas animation and 3D (three.js)
12. Checklist before you ship a figure

---

## 1. Two frames side by side

Use when one thing exists in two places or two coordinate systems: local vs world, server vs client copy, asset vs instance. Same element gets the same colour in both panels; the caption says what maps to what.

```html
<svg viewBox="0 0 760 220" role="img" aria-label="A child component in its parent's local space and in world space">
  <text x="20" y="24" class="strong">Local (relative to the parent)</text>
  <g stroke="var(--fg)" stroke-width="1.5">
    <rect x="20"  y="70" width="100" height="44" fill="var(--panel)"/>
    <rect x="120" y="70" width="100" height="44" fill="color-mix(in srgb, var(--a) 22%, var(--panel))"/>
  </g>
  <text x="400" y="24" class="strong">World (after the parent's transform)</text>
  <path d="M400 80 Q 560 80 720 190" fill="none" stroke="var(--muted)" stroke-dasharray="4 4"/>
  <rect x="512" y="64" width="100" height="44" fill="color-mix(in srgb, var(--a) 22%, var(--panel))"
        stroke="var(--fg)" stroke-width="1.5" transform="rotate(10 562 86)"/>
  <text x="400" y="210" class="small">angles exaggerated</text>
</svg>
```

## 2. Right place vs wrong place

The central figure for most "lands in the wrong place / wrong value" bugs. Draw the correct result in green, the wrong one in red, an arrow for the gap, and the formula for the gap as a label. Compute the two points; don't guess them.

```html
<svg viewBox="0 0 640 330" role="img" aria-label="Correct and wrong result with the gap between them">
  <defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10z" fill="var(--fg)"/></marker></defs>
  <!-- reference object -->
  <rect x="60" y="200" width="200" height="60" fill="color-mix(in srgb, var(--a) 22%, var(--panel))" stroke="var(--a)" stroke-width="2"/>
  <!-- what the code assumes (dashed, red) -->
  <rect x="260" y="200" width="200" height="60" fill="none" stroke="var(--bad)" stroke-width="1.5" stroke-dasharray="6 5"/>
  <!-- what is really there (rotated about the shared point 260,230) -->
  <g transform="rotate(12 260 230)">
    <rect x="260" y="200" width="200" height="60" fill="color-mix(in srgb, var(--b) 22%, var(--panel))" stroke="var(--b)" stroke-width="2"/>
  </g>
  <!-- points: computed as pivot + r*(cos θ, sin θ) -->
  <circle cx="426.3" cy="265.3" r="7" fill="var(--good)"/><text x="440" y="283" style="fill:var(--good)">should be here</text>
  <circle cx="430"   cy="230"   r="7" fill="var(--bad)"/><text x="444" y="226" style="fill:var(--bad)">ends up here</text>
  <line x1="428" y1="237" x2="426.6" y2="258" stroke="var(--fg)" stroke-width="1.5" marker-end="url(#ar)"/>
  <text x="330" y="150" class="small">gap ≈ Δangle × distance from pivot</text>
</svg>
```

Marker ids must be unique per page (`ar`, `ar2`, …) or later figures reuse the first one's colour.

## 3. Swim lanes

For races, network timing, frame ordering. One horizontal lane per actor (server, owning client, other client), time flowing left→right with tick marks, messages as diagonal arrows (they take time). Mark the moment it goes wrong with a red band.

```html
<svg viewBox="0 0 700 250" role="img" aria-label="Server and client timelines with a late correction">
  <defs><marker id="ar3" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10z" fill="var(--fg)"/></marker></defs>
  <text x="10" y="64" class="strong">Server</text>
  <line x1="90" y1="60" x2="680" y2="60" stroke="var(--a)" stroke-width="3"/>
  <text x="10" y="164" class="strong">Client</text>
  <line x1="90" y1="160" x2="680" y2="160" stroke="var(--b)" stroke-width="3"/>
  <!-- time ticks -->
  <g stroke="var(--rule)"><line x1="150" y1="40" x2="150" y2="180"/><line x1="300" y1="40" x2="300" y2="180"/><line x1="450" y1="40" x2="450" y2="180"/></g>
  <text x="140" y="200" class="small">t0</text><text x="290" y="200" class="small">t1</text><text x="440" y="200" class="small">t2</text>
  <!-- message: sent at t0 on server, arrives t1 on client -->
  <line x1="150" y1="60" x2="300" y2="160" stroke="var(--fg)" stroke-width="1.5" marker-end="url(#ar3)"/>
  <text x="200" y="100" class="small">correction (old state)</text>
  <!-- the bad moment -->
  <rect x="290" y="40" width="20" height="140" fill="color-mix(in srgb, var(--bad) 18%, transparent)"/>
  <text x="320" y="225" style="fill:var(--bad)">arrives after the shift → copies disagree</text>
</svg>
```

## 4. Components and data flow

Boxes for the 5–8 pieces that matter, using the project's class names; arrows labelled with *what* flows (an event, a struct, an RPC). Lay out left→right in the order data moves. Group anything else into one "…" box rather than drawing everything.

```html
<svg viewBox="0 0 760 200" role="img" aria-label="Data flow between components">
  <defs><marker id="ar4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10z" fill="var(--muted)"/></marker></defs>
  <g stroke="var(--fg)" stroke-width="1.5" fill="var(--panel)">
    <rect x="20"  y="70" width="150" height="56" rx="6"/>
    <rect x="300" y="70" width="150" height="56" rx="6"/>
    <rect x="580" y="70" width="150" height="56" rx="6"/>
  </g>
  <text x="38" y="103">UItemSpawner</text><text x="318" y="103">AItemActor</text><text x="598" y="103">UItemData</text>
  <g stroke="var(--muted)" stroke-width="1.5" fill="none">
    <line x1="170" y1="98" x2="296" y2="98" marker-end="url(#ar4)"/>
    <line x1="450" y1="98" x2="576" y2="98" marker-end="url(#ar4)"/>
  </g>
  <text x="190" y="88" class="small">SpawnItem()</text><text x="470" y="88" class="small">LoadData()</text>
  <text x="20" y="160" class="small">file refs go in the caption or a table, not in the boxes</text>
</svg>
```

(Example names are placeholders. Read the code for the real ones.)

## 5. Geometry drawn to scale

For maths and spatial bugs. Pick a scale (e.g. 1 unit = 40 px), compute every vertex, and draw right-angle markers, labelled sides and angles. Put the worked numbers next to the figure. Example: a 3-4-5 triangle at 40 px per unit, with squares on each side for a Pythagoras figure:

```python
# compute once, paste the numbers into the SVG
s = 40; A = (100, 300); B = (100 + 4*s, 300); C = (100, 300 - 3*s)
# square on the hypotenuse: rotate BC by -90° around each end
import math
bx, by = B; cx, cy = C; dx, dy = cx - bx, cy - by
D = (cx + dy, cy - dx); E = (bx + dy, by - dx)
print(A, B, C, D, E)
```

Then `<polygon points="...">` with `fill="color-mix(in srgb, var(--a) 20%, var(--panel))"` for each square, and a small square at the right angle: `<path d="M100 288 h12 v12" fill="none" stroke="var(--fg)"/>`.

## 6. Spatial grid / map

For anything about space: dormancy cells, relevancy radius, spawn zones, grid cells, streaming ranges. Draw top-down, to scale, with the grid lines, the actor/player as a marker, and the active cells or radius filled. Label the cell size and real units.

```html
<svg viewBox="0 0 420 420" role="img" aria-label="5x5 relevancy window of 100 m cells around a player">
  <!-- 7x7 grid of 50 px cells starting at 35,35 -->
  <path d="M35 35 H385 M35 85 H385 M35 135 H385 M35 185 H385 M35 235 H385 M35 285 H385 M35 335 H385 M35 385 H385
           M35 35 V385 M85 35 V385 M135 35 V385 M185 35 V385 M235 35 V385 M285 35 V385 M335 35 V385 M385 35 V385"
        fill="none" stroke="var(--rule)"/>
  <!-- relevant window: 5x5 cells around the player's cell -->
  <rect x="85" y="85" width="250" height="250" fill="color-mix(in srgb, var(--good) 14%, transparent)" stroke="var(--good)" stroke-width="2"/>
  <circle cx="210" cy="210" r="9" fill="var(--a)"/><text x="224" y="206" class="small">player</text>
  <circle cx="360" cy="60" r="7" fill="var(--muted)"/><text x="290" y="56" class="small">actor (dormant)</text>
  <circle cx="150" cy="270" r="7" fill="var(--b)"/><text x="160" y="290" class="small">actor (active)</text>
  <text x="35" y="408" class="small">1 cell = 100 m · window = radius 2 cells</text>
</svg>
```

Make it interactive when the reader would ask "what if I move?": a slider or drag that moves the player marker and recolours which cells/actors are relevant.

## 7. State diagram

States as rounded boxes, transitions as arrows labelled with the event or condition that fires them (`file:line` in the caption or a table). Put the normal loop in a row or circle; error/terminal states off to the side.

```html
<svg viewBox="0 0 640 220" role="img" aria-label="Match states and transitions">
  <defs><marker id="ar7" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10z" fill="var(--muted)"/></marker></defs>
  <g stroke="var(--fg)" stroke-width="1.5" fill="var(--panel)">
    <rect x="30" y="80" width="120" height="50" rx="25"/><rect x="260" y="80" width="120" height="50" rx="25"/><rect x="490" y="80" width="120" height="50" rx="25"/>
  </g>
  <text x="60" y="110">Waiting</text><text x="282" y="110">InProgress</text><text x="528" y="110">Ended</text>
  <g stroke="var(--muted)" stroke-width="1.5" fill="none">
    <path d="M150 95 H256" marker-end="url(#ar7)"/><path d="M380 95 H486" marker-end="url(#ar7)"/>
    <path d="M550 130 C 550 190, 90 190, 90 134" marker-end="url(#ar7)"/>
  </g>
  <text x="160" y="85" class="small">players ready</text><text x="395" y="85" class="small">time up</text><text x="280" y="200" class="small">next round</text>
</svg>
```
(State names are placeholders: use the real ones from the code.)

## 8. Pictogram row

For a set of kinds (test tiers, server types, damage types): one card per kind with a small drawn pictogram that encodes the difference (e.g. the size of the world each test tier boots: a dot, a room, a level, a whole world), a name, and one line on when to use it. Draw pictograms as tiny SVGs with the same tokens; an emoji is fine when it says the thing faster than a drawing. Lay the cards out with CSS grid (`.facts` works) so they wrap on phones.

## 9. Interactive: slider that redraws

The most useful interaction. Keep the static state complete and meaningful, and keep the script short: read the slider, recompute, set SVG attributes and a text readout.

```html
<div class="controls">
  <label for="lat">Latency <input id="lat" type="range" min="0" max="300" value="100"> <output id="latv">100 ms</output></label>
</div>
<svg viewBox="0 0 600 120" role="img" aria-label="Target moves further from where the shooter saw it as latency grows">
  <line x1="40" y1="60" x2="560" y2="60" stroke="var(--rule)"/>
  <circle id="seen" cx="200" cy="60" r="10" fill="var(--a)"/>
  <circle id="now" cx="260" cy="60" r="10" fill="none" stroke="var(--bad)" stroke-width="2"/>
  <text id="gap" x="200" y="100" class="small"></text>
</svg>
<script>
(() => {
  const lat = document.getElementById('lat'), out = document.getElementById('latv');
  const now = document.getElementById('now'), gap = document.getElementById('gap');
  const speed = 6, pxPerM = 100;                 // 6 m/s target, 1 m = 100 px
  const draw = () => {
    const m = speed * lat.value / 1000;          // metres moved during the delay
    now.setAttribute('cx', 200 + m * pxPerM);
    out.value = `${lat.value} ms`; gap.textContent = `target moved ${m.toFixed(2)} m`;
  };
  lat.addEventListener('input', draw); draw();
})();
</script>
```

Wrap each figure's script in its own `(() => { ... })()` so ids and variables don't collide between figures.

## 10. Interactive: step-through sequence

For a walk-through (a smoke test's phases, a shot's life, a spawn request): all steps drawn, the current one highlighted, Prev / Play / Next buttons, and a line of text that changes per step with its `file:line`. At rest, step 1 is highlighted and every step is visible.

```html
<div class="controls"><button id="prev">◀ Prev</button><button id="play">▶ Play</button><button id="next">Next ▶</button>
  <span id="stepText" class="mono"></span></div>
<svg viewBox="0 0 700 120" role="img" aria-label="Phases of a smoke test, one highlighted at a time">
  <g id="steps" stroke="var(--fg)" stroke-width="1.5">
    <rect x="10" y="40" width="120" height="44" rx="6" fill="var(--panel)"/>
    <rect x="150" y="40" width="120" height="44" rx="6" fill="var(--panel)"/>
    <rect x="290" y="40" width="120" height="44" rx="6" fill="var(--panel)"/>
  </g>
</svg>
<script>
(() => {
  const info = [['Boot PIE', 'File.cpp:10'], ['Find players', 'File.cpp:20'], ['Run steps', 'File.cpp:30']];  // real names + refs
  const rects = [...document.querySelectorAll('#steps rect')], txt = document.getElementById('stepText');
  let i = 0, timer = null;
  const show = () => {
    rects.forEach((r, k) => r.setAttribute('fill', k === i ? 'color-mix(in srgb, var(--a) 25%, var(--panel))' : 'var(--panel)'));
    txt.textContent = `${i + 1}. ${info[i][0]} · ${info[i][1]}`;
  };
  document.getElementById('prev').onclick = () => { i = (i + rects.length - 1) % rects.length; show(); };
  document.getElementById('next').onclick = () => { i = (i + 1) % rects.length; show(); };
  document.getElementById('play').onclick = () => {
    if (timer) { clearInterval(timer); timer = null; return; }
    timer = setInterval(() => { i = (i + 1) % rects.length; show(); }, 1200);
  };
  show();
})();
</script>
```

## 11. Interactive: canvas animation and 3D

Use `<canvas>` when many things move at once (actors going dormant and waking as a player walks, packets in flight). Use three.js only when depth really matters (a socket-attached actor seen from different angles, hitboxes rewinding in 3D). Respect `prefers-reduced-motion`: start paused and show a meaningful still frame.

Read theme colours from CSS so canvas/WebGL follow dark mode:
```js
const css = getComputedStyle(document.documentElement);
const col = name => css.getPropertyValue(name).trim();   // col('--a'), col('--bad'), col('--panel')
```

three.js from cdnjs, pinned:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<div id="view3d" style="width:100%;aspect-ratio:16/9;max-width:100%"></div>
<script>
(() => {
  const el = document.getElementById('view3d'), css = getComputedStyle(document.documentElement);
  const col = n => new THREE.Color(css.getPropertyValue(n).trim());
  const scene = new THREE.Scene(); scene.background = col('--panel');
  const cam = new THREE.PerspectiveCamera(45, 16 / 9, 0.1, 100);
  const r = new THREE.WebGLRenderer({ antialias: true }); el.appendChild(r.domElement);
  const fit = () => r.setSize(el.clientWidth, el.clientWidth * 9 / 16); fit(); addEventListener('resize', fit);
  scene.add(new THREE.AmbientLight(0xffffff, 0.8));
  scene.add(new THREE.Mesh(new THREE.BoxGeometry(4, 1, 1.2), new THREE.MeshLambertMaterial({ color: col('--a') })));
  let down = false, x0 = 0, ang = 0.6;                      // drag horizontally to orbit
  el.addEventListener('pointerdown', e => { down = true; x0 = e.clientX; });
  addEventListener('pointerup', () => down = false);
  addEventListener('pointermove', e => { if (down) { ang += (e.clientX - x0) * 0.01; x0 = e.clientX; } });
  const loop = () => { cam.position.set(10 * Math.sin(ang), 6, 10 * Math.cos(ang)); cam.lookAt(0, 0, 0); r.render(scene, cam); requestAnimationFrame(loop); };
  loop();
})();
</script>
```
Always pair a 3D view with a 2D figure or caption that states the point, so the page still works without WebGL.

## 12. Checklist before you ship a figure

- Does it show the one thing the caption says to notice?
- Is every colour a token? (search the SVG for `#` followed by hex: there should be none)
- Every shape has an explicit `fill` (`none` where intended)?
- Labels clear of shapes and inside the viewBox?
- Exaggerations labelled with the real value?
- `aria-label` on the `<svg>`, caption under it?
- Numbers in the figure match the text and the evidence table?
- Interactive figure: correct at rest, script wrapped in its own scope, ids unique, usable with keyboard (buttons/sliders, not hover only)?
