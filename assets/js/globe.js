/**
 * hero-globe.js — SVG wireframe globe + orbital carousel for TKVibes hero.
 * Theme-aware (dark/light), requestAnimationFrame driven.
 */
(function () {
  "use strict";

  const svg = document.getElementById("hero-globe-svg");
  if (!svg) return;
  const NS = "http://www.w3.org/2000/svg";

  const DEG = Math.PI / 180;
  const TAU = Math.PI * 2;
  let W, H, cx, cy, R;
  let angle = 0;
  let running = true;

  /* ── theme detection ─────────────────────────────────── */
  function isLight() {
    return document.documentElement.classList.contains("light");
  }

  function pal() {
    if (isLight()) {
      return {
        bg:       "transparent",
        wire:     "rgba(91,108,255,0.20)",
        cont:     "rgba(91,108,255,0.50)",
        contFill: "rgba(91,108,255,0.05)",
        dot:      "#5b6cff",
        dotGlow:  "rgba(91,108,255,0.20)",
        beam:     "rgba(91,108,255,0.08)",
        glow1:    "rgba(91,108,255,0.12)",
        glow2:    "rgba(91,108,255,0.02)",
        star:     null,
      };
    }
    return {
      bg:       "transparent",
      wire:     "rgba(26,111,196,0.30)",
      cont:     "rgba(74,158,255,0.70)",
      contFill: "rgba(20,100,200,0.06)",
      dot:      "#5cbcff",
      dotGlow:  "rgba(92,188,255,0.25)",
      beam:     "rgba(58,160,255,0.10)",
      glow1:    "rgba(6,26,58,0)",
      glow2:    "rgba(10,61,145,0.20)",
      star:     "rgba(180,210,255,",
    };
  }

  /* ── sizing ──────────────────────────────────────────── */
  function measure() {
    const rect = svg.parentElement.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    cx = W / 2;
    cy = H / 2;
    R = Math.min(W, H) * 0.30;
    glowCircle.setAttribute("cx", cx);
    glowCircle.setAttribute("cy", cy);
    glowCircle.setAttribute("r", R * 1.4);
  }

  /* ── build SVG structure ─────────────────────────────── */
  // Defs
  const defs = document.createElementNS(NS, "defs");

  const glowGrad = document.createElementNS(NS, "radialGradient");
  glowGrad.id = "gGlow";
  const gs1 = document.createElementNS(NS, "stop");
  gs1.setAttribute("offset", "0%");
  const gs2 = document.createElementNS(NS, "stop");
  gs2.setAttribute("offset", "100%");
  glowGrad.append(gs1, gs2);
  defs.append(glowGrad);

  const dotFilter = document.createElementNS(NS, "filter");
  dotFilter.id = "gDotGlow";
  dotFilter.setAttribute("x", "-100%");
  dotFilter.setAttribute("y", "-100%");
  dotFilter.setAttribute("width", "300%");
  dotFilter.setAttribute("height", "300%");
  const feBlur = document.createElementNS(NS, "feGaussianBlur");
  feBlur.setAttribute("in", "SourceGraphic");
  feBlur.setAttribute("stdDeviation", "4");
  feBlur.setAttribute("result", "b");
  const feMerge = document.createElementNS(NS, "feMerge");
  const fm1 = document.createElementNS(NS, "feMergeNode");
  fm1.setAttribute("in", "b");
  const fm2 = document.createElementNS(NS, "feMergeNode");
  fm2.setAttribute("in", "SourceGraphic");
  feMerge.append(fm1, fm2);
  dotFilter.append(feBlur, feMerge);
  defs.append(dotFilter);

  const beamFilter = document.createElementNS(NS, "filter");
  beamFilter.id = "gBeamGlow";
  beamFilter.setAttribute("x", "-50%");
  beamFilter.setAttribute("y", "-50%");
  beamFilter.setAttribute("width", "200%");
  beamFilter.setAttribute("height", "200%");
  const feB = document.createElementNS(NS, "feGaussianBlur");
  feB.setAttribute("in", "SourceGraphic");
  feB.setAttribute("stdDeviation", "2");
  beamFilter.append(feB);
  defs.append(beamFilter);

  svg.append(defs);

  // Glow circle
  const glowCircle = document.createElementNS(NS, "circle");
  glowCircle.setAttribute("fill", "url(#gGlow)");
  svg.append(glowCircle);

  // Stars group
  const starsG = document.createElementNS(NS, "g");
  starsG.setAttribute("id", "gStars");
  svg.append(starsG);

  // Beams group
  const beamsG = document.createElementNS(NS, "g");
  beamsG.setAttribute("filter", "url(#gBeamGlow)");
  svg.append(beamsG);

  // Wireframe group
  const wireG = document.createElementNS(NS, "g");
  wireG.setAttribute("id", "gWire");
  svg.append(wireG);

  // Continents group
  const contG = document.createElementNS(NS, "g");
  svg.append(contG);

  // Dots group
  const dotsG = document.createElementNS(NS, "g");
  dotsG.setAttribute("filter", "url(#gDotGlow)");
  svg.append(dotsG);

  // ── stars ──
  const starEls = [];
  for (let i = 0; i < 180; i++) {
    const c = document.createElementNS(NS, "circle");
    c.setAttribute("cx", Math.random());
    c.setAttribute("cy", Math.random());
    c.setAttribute("r", (Math.random() * 1.1 + 0.3).toFixed(1));
    c.dataset.b = (Math.random() * 0.5 + 0.3).toFixed(2);
    starsG.append(c);
    starEls.push(c);
  }

  /* ── 3-D helpers ─────────────────────────────────────── */
  function rotY(p, a) {
    const c = Math.cos(a), s = Math.sin(a);
    return [p[0]*c - p[2]*s, p[1], p[0]*s + p[2]*c];
  }
  function project(p) {
    return [cx + p[0]*R, cy - p[1]*R, p[2]];
  }
  function spherePt(lat, lon) {
    const phi = lat * DEG, lam = lon * DEG;
    return [Math.cos(phi)*Math.cos(lam), Math.sin(phi), Math.cos(phi)*Math.sin(lam)];
  }

  /* ── continent outlines ──────────────────────────────── */
  const CONTINENTS = [
    [[72,-170],[68,-165],[64,-140],[60,-139],[58,-148],[60,-152],[63,-165],[65,-168],[70,-165],[72,-170]],
    [[60,-139],[57,-135],[55,-130],[50,-127],[48,-124],[42,-124],[37,-122],[33,-118],[30,-115],[28,-105],[26,-98],[25,-90],[29,-85],[30,-82],[27,-80],[25,-80],[27,-77],[30,-82],[35,-76],[40,-74],[42,-70],[44,-68],[46,-64],[48,-59],[50,-57],[53,-56],[55,-60],[58,-63],[60,-64]],
    [[60,-64],[62,-75],[58,-80],[55,-83],[50,-88],[48,-88],[48,-95],[52,-97],[55,-100],[58,-110],[60,-120],[60,-139]],
    [[12,-73],[10,-72],[8,-68],[7,-63],[5,-57],[4,-53],[2,-50],[0,-50],[-2,-44],[-5,-35],[-8,-35],[-10,-37],[-13,-38],[-17,-39],[-22,-41],[-25,-46],[-28,-49],[-32,-52],[-35,-57],[-38,-58],[-40,-62],[-43,-65],[-46,-67],[-50,-73],[-53,-70],[-55,-68],[-52,-70],[-47,-74],[-42,-73],[-38,-63],[-34,-58],[-30,-50],[-25,-48],[-22,-43],[-20,-40],[-17,-39],[-13,-38],[-8,-35],[-5,-35],[-2,-44],[0,-50],[2,-50],[4,-53],[5,-57],[7,-63],[8,-68],[10,-72],[12,-73]],
    [[37,-10],[36,-5],[35,0],[33,10],[32,32],[30,33],[27,34],[22,37],[18,41],[15,42],[12,44],[10,45],[8,43],[5,42],[2,42],[0,42],[-3,40],[-7,40],[-10,40],[-13,40],[-17,37],[-20,35],[-25,33],[-28,32],[-30,30],[-34,26],[-35,20],[-34,18],[-30,17],[-25,15],[-20,12],[-15,12],[-10,14],[-5,10],[0,10],[5,8],[5,2],[5,-2],[7,-8],[10,-15],[14,-17],[18,-17],[21,-17],[25,-15],[30,-10],[35,-5],[37,-10]],
    [[70,20],[68,25],[65,28],[63,30],[60,30],[58,28],[56,24],[55,21],[54,14],[53,10],[52,7],[51,4],[50,2],[48,0],[47,-2],[44,-5],[43,-9],[37,-8],[36,-6],[37,0],[38,5],[39,8],[40,10],[42,13],[43,16],[44,14],[45,14],[47,15],[48,17],[50,20],[52,18],[54,16],[55,13],[56,12],[57,10],[59,10],[60,10],[62,15],[64,15],[66,16],[68,18],[70,20]],
    [[70,30],[70,60],[68,70],[65,80],[63,90],[60,100],[58,110],[55,120],[53,130],[50,135],[48,140],[45,142],[43,145],[40,140],[38,135],[35,130],[33,128],[30,122],[28,120],[25,120],[22,115],[20,110],[18,108],[15,108],[12,108],[10,106],[8,105],[5,105],[2,104],[0,104],[-2,105],[-5,106],[-8,115],[-7,120],[-5,120],[0,118],[3,115],[5,110],[8,108],[10,106],[12,100],[15,100],[18,98],[20,95],[22,90],[25,88],[28,85],[30,80],[32,75],[30,70],[28,65],[25,62],[25,58],[28,55],[30,50],[33,48],[35,45],[38,43],[40,43],[42,40],[45,38],[48,40],[50,45],[52,50],[55,55],[58,60],[60,65],[63,70],[65,75],[68,80],[70,80],[72,75],[73,60],[72,45],[70,30]],
    [[-12,131],[-14,127],[-17,123],[-20,118],[-24,115],[-28,114],[-32,115],[-35,117],[-37,140],[-38,145],[-37,150],[-34,151],[-30,153],[-26,153],[-22,150],[-19,147],[-16,145],[-14,142],[-13,137],[-12,131]],
    [[78,-72],[76,-68],[73,-56],[72,-52],[70,-52],[68,-54],[65,-54],[62,-50],[60,-45],[60,-48],[63,-52],[65,-54],[68,-56],[70,-56],[72,-55],[74,-60],[76,-68],[78,-72]],
  ];

  /* ── city dots ───────────────────────────────────────── */
  const CITIES = [
    [40.7,-74],[34,-118],[51.5,0],[48.9,2.3],[52.5,13.4],[35.7,139.7],
    [22.3,114.2],[1.3,103.8],[28.6,77.2],[-33.9,151.2],[37.6,127],
    [31.2,121.5],[23.1,113.3],[41,29],[39.9,116.4],[55.8,37.6],
    [30,31.2],[19.1,72.9],[25,55.3],[-23,-43.2],[19.4,-99.1],
    [-12,-77],[33.6,-7.6],[14.6,121],[13.7,100.5],[3.1,101.7],
    [37.6,55.3],[24.7,46.7],[41.7,44.8],[6.5,3.4],[-26,28],
    [9,38.7],[38.9,-77],[43.6,-79.4],[47.6,-122],[29.8,-95.4],
    [25.8,-80.2],[40.4,-3.7],[41.4,2.2],[59.9,10.7],[60.2,25],
    [55.7,12.6],[50.4,30.5],[36.8,10.2],[-1.3,36.8],[-6.2,106.8],
    [21,105.8],[16.9,82.2],[26.9,75.8],[9.9,76.3],[23,72.6],
    [13.1,77.6],[19.1,72.9],[33.3,44.4],[27.7,85.3],
  ];

  // Pre-build dot SVG circles
  const dotPairs = [];
  for (let i = 0; i < CITIES.length; i++) {
    const outer = document.createElementNS(NS, "circle");
    outer.setAttribute("r", "6");
    outer.setAttribute("fill", "none");
    outer.setAttribute("stroke-width", "1.5");
    dotsG.append(outer);
    const core = document.createElementNS(NS, "circle");
    core.setAttribute("r", "2.5");
    dotsG.append(core);
    dotPairs.push({ outer, core });
  }

  // Pre-build beam lines
  const BEAM_N = 16;
  const beamEls = [];
  for (let i = 0; i < BEAM_N; i++) {
    const l = document.createElementNS(NS, "line");
    l.setAttribute("stroke-width", "0.8");
    beamsG.append(l);
    beamEls.push(l);
  }

  // Pre-build wireframe paths
  const latPaths = [];
  for (let lat = -80; lat <= 80; lat += 20) {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-width", "0.6");
    wireG.append(p);
    latPaths.push({ el: p, lat });
  }
  const lonPaths = [];
  for (let lon = 0; lon < 360; lon += 30) {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-width", "0.6");
    wireG.append(p);
    lonPaths.push({ el: p, lon });
  }

  // Pre-build continent paths
  const contPaths = [];
  for (let i = 0; i < CONTINENTS.length; i++) {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-width", "1");
    p.setAttribute("stroke-linejoin", "round");
    contG.append(p);
    contPaths.push(p);
  }

  /* ── ring path builder ───────────────────────────────── */
  function ringPathD(pts) {
    if (pts.length < 2) return "";
    let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
    for (let i = 1; i < pts.length; i++) d += `L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
    return d + "Z";
  }

  function splitPathD(pts) {
    let d = "", cur = [];
    for (const pt of pts) {
      if (!pt) { if (cur.length > 1) d += ringPathD(cur); cur = []; }
      else cur.push(pt);
    }
    if (cur.length > 1) d += ringPathD(cur);
    return d;
  }

  /* ── frame ───────────────────────────────────────────── */
  function frame(ts) {
    if (!running) return;
    requestAnimationFrame(frame);

    const rect = svg.parentElement.getBoundingClientRect();
    if (rect.width < 10 || rect.height < 10) return;
    if (rect.bottom < -100 || rect.top > window.innerHeight + 100) return;
    if (Math.abs(rect.width - W) > 2 || Math.abs(rect.height - H) > 2) measure();

    const t = ts * 0.001;
    angle += 0.004;
    const rad = angle;
    const p = pal();

    // Update gradient colors
    gs1.setAttribute("stop-color", p.glow1);
    gs2.setAttribute("stop-color", p.glow2);

    // Stars
    const showStars = !!p.star;
    starsG.setAttribute("display", showStars ? "" : "none");
    if (showStars) {
      for (const s of starEls) {
        s.setAttribute("fill", p.star + s.dataset.b + ")");
        s.setAttribute("cx", (parseFloat(s.getAttribute("cx")) < 1
          ? parseFloat(s.getAttribute("cx")) * W
          : parseFloat(s.getAttribute("cx"))
        ).toFixed(0));
      }
      // Only convert once
      if (!starsG.dataset.init) {
        for (const s of starEls) {
          s.setAttribute("cx", (parseFloat(s.getAttribute("cx")) * W).toFixed(0));
          s.setAttribute("cy", (parseFloat(s.getAttribute("cy")) * H).toFixed(0));
        }
        starsG.dataset.init = "1";
      }
    }

    // Wireframe
    for (const { el, lat } of latPaths) {
      const pts = [];
      for (let lon = 0; lon <= 360; lon += 5) {
        const v = rotY(spherePt(lat, lon), rad);
        if (v[2] < 0) { pts.push(null); continue; }
        pts.push(project(v));
      }
      el.setAttribute("d", splitPathD(pts));
      el.setAttribute("stroke", p.wire);
    }

    for (const { el, lon } of lonPaths) {
      const pts = [];
      for (let lat = -90; lat <= 90; lat += 5) {
        const v = rotY(spherePt(lat, lon), rad);
        if (v[2] < 0) { pts.push(null); continue; }
        pts.push(project(v));
      }
      el.setAttribute("d", splitPathD(pts));
      el.setAttribute("stroke", p.wire);
    }

    // Continents
    for (let ci = 0; ci < CONTINENTS.length; ci++) {
      const pts = CONTINENTS[ci].map(([la, lo]) => {
        const v = rotY(spherePt(la, lo), rad);
        return v[2] < 0 ? null : project(v);
      });
      const d = splitPathD(pts);
      contPaths[ci].setAttribute("d", d);
      contPaths[ci].setAttribute("stroke", p.cont);
      contPaths[ci].setAttribute("fill", p.contFill);
    }

    // City dots
    const visDots = [];
    for (let i = 0; i < CITIES.length; i++) {
      const [lat, lon] = CITIES[i];
      const v = rotY(spherePt(lat, lon), rad);
      const { outer, core } = dotPairs[i];
      if (v[2] < -0.05) {
        outer.setAttribute("display", "none");
        core.setAttribute("display", "none");
        continue;
      }
      const [sx, sy] = project(v);
      const depth = (v[2] + 1) / 2;
      const sz = 1.5 + depth * 2;
      const pulse = 1 + 0.25 * Math.sin(t * 2.5 + i * 0.8);

      outer.removeAttribute("display");
      outer.setAttribute("cx", sx.toFixed(1));
      outer.setAttribute("cy", sy.toFixed(1));
      outer.setAttribute("r", ((sz + 3) * pulse).toFixed(1));
      outer.setAttribute("stroke", p.dotGlow);
      outer.setAttribute("stroke-opacity", (0.2 + depth * 0.3).toFixed(2));

      core.removeAttribute("display");
      core.setAttribute("cx", sx.toFixed(1));
      core.setAttribute("cy", sy.toFixed(1));
      core.setAttribute("r", (sz * pulse).toFixed(1));
      core.setAttribute("fill", p.dot);
      core.setAttribute("fill-opacity", (0.5 + depth * 0.5).toFixed(2));

      if (v[2] > 0.15) visDots.push([sx, sy, depth]);
    }

    // Beams
    for (let i = 0; i < BEAM_N; i++) {
      const b = beamEls[i];
      if (!visDots.length) { b.setAttribute("display", "none"); continue; }
      b.removeAttribute("display");
      const d = visDots[i % visDots.length];
      const ba = (i / BEAM_N) * TAU + angle * 0.5;
      const len = R * (0.6 + 0.25 * Math.sin(t * 1.3 + i));
      b.setAttribute("x1", d[0].toFixed(1));
      b.setAttribute("y1", d[1].toFixed(1));
      b.setAttribute("x2", (d[0] + Math.cos(ba) * len).toFixed(1));
      b.setAttribute("y2", (d[1] + Math.sin(ba) * len).toFixed(1));
      b.setAttribute("stroke", p.beam);
      b.setAttribute("stroke-opacity", (0.06 + d[2] * 0.14).toFixed(2));
    }

    // Rim
    wireG.setAttribute("opacity", "1");
  }

  /* ── init ────────────────────────────────────────────── */
  measure();
  requestAnimationFrame(frame);

  /* ── visibility pause ────────────────────────────────── */
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { running = false; }
    else { running = true; requestAnimationFrame(frame); }
  });

  /* ── Orbital carousel (JS-driven for 3D depth) ─────── */
  const orbitContainer = document.querySelector(".orbit-container");
  if (!orbitContainer) return;

  const cards = Array.from(orbitContainer.querySelectorAll(".orbit-card"));
  const cardCount = cards.length;
  const ORBIT_DURATION = 28; // seconds for full rotation
  const ORBIT_RADIUS = 260; // px from center (adjusted by CSS var)

  function getOrbitRadius() {
    const vw = window.innerWidth;
    if (vw < 600) return 140;
    if (vw < 900) return 190;
    return 260;
  }

  function getCardSize() {
    const vw = window.innerWidth;
    if (vw < 600) return { w: 140, h: 90 };
    if (vw < 900) return { w: 170, h: 110 };
    return { w: 210, h: 136 };
  }

  function orbitFrame(ts) {
    if (!running) { requestAnimationFrame(orbitFrame); return; }
    const t = ts * 0.001;
    const baseAngle = (t / ORBIT_DURATION) * 360;
    const radius = getOrbitRadius();
    const { w, h } = getCardSize();

    // Sort cards by depth for z-ordering
    const cardData = cards.map((card, i) => {
      const angleDeg = baseAngle + (360 / cardCount) * i;
      const angleRad = angleDeg * DEG;
      const x = Math.sin(angleRad) * radius;
      const z = Math.cos(angleRad) * radius;
      const depth = (z + radius) / (2 * radius); // 0 (back) to 1 (front)
      return { card, angleDeg, x, z, depth, i };
    });

    // Sort by z (back to front)
    cardData.sort((a, b) => a.z - b.z);

    cardData.forEach((d, sortOrder) => {
      // cos(angleRad): +1 at front (0°), 0 at sides (90°/270°), -1 at back (180°)
      const cosAngle = Math.cos(d.angleDeg * DEG);
      const frontness = (cosAngle + 1) / 2; // 0 (back) → 1 (front)
      const scale = 0.30 + frontness * 1.20;
      const opacity = 0.10 + frontness * 0.90;
      const blur = frontness < 0.4 ? (1 - frontness / 0.4) * 3 : 0;
      const y = (1 - frontness) * -18;

      d.card.style.transform =
        `translateX(${d.x.toFixed(1)}px) translateY(${y.toFixed(1)}px) scale(${scale.toFixed(3)})`;
      d.card.style.opacity = opacity.toFixed(3);
      d.card.style.zIndex = sortOrder + 1;
      d.card.style.filter = blur > 0.1 ? `blur(${blur.toFixed(1)}px)` : "none";
      d.card.style.width = w + "px";
      d.card.style.height = h + "px";
      d.card.style.marginLeft = (-w / 2) + "px";
      d.card.style.marginTop = (-h / 2) + "px";
    });

    requestAnimationFrame(orbitFrame);
  }

  requestAnimationFrame(orbitFrame);

})();
