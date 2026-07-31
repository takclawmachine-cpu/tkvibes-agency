/**
 * hero-globe.js  –  3-D wireframe globe for the TKVibes hero section.
 * Canvas-based, dark/light-mode aware, requestAnimationFrame loop.
 * Drop-in replacement for the old static SVG globe.
 */
(function () {
  "use strict";

  const canvas = document.getElementById("hero-globe-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const DEG = Math.PI / 180;
  const TAU = Math.PI * 2;
  let W, H, cx, cy, R, dpr;
  let angle = 0;
  let running = true;

  /* ── resize ──────────────────────────────────────────── */
  function measure() {
    const rect = canvas.parentElement.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width;
    H = rect.height;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = W + "px";
    canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cx = W / 2;
    cy = H / 2;
    R = Math.min(W, H) * 0.38;
  }

  /* ── 3-D helpers ─────────────────────────────────────── */
  function rotY(p, a) {
    const c = Math.cos(a), s = Math.sin(a);
    return [p[0] * c - p[2] * s, p[1], p[0] * s + p[2] * c];
  }
  function project(p) {
    const s = R;
    return [cx + p[0] * s, cy - p[1] * s, p[2]];
  }
  function spherePt(lat, lon) {
    const phi = lat * DEG, lam = lon * DEG;
    return [Math.cos(phi) * Math.cos(lam), Math.sin(phi), Math.cos(phi) * Math.sin(lam)];
  }

  /* ── theme-aware palette ─────────────────────────────── */
  function isLight() {
    return document.documentElement.classList.contains("light");
  }
  function pal() {
    if (isLight()) {
      return {
        bg:      "#eef2f9",
        wire:    "rgba(91,108,255,0.22)",
        cont:    "rgba(91,108,255,0.45)",
        contFill:"rgba(91,108,255,0.06)",
        dot:     "#5b6cff",
        dotGlow: "rgba(91,108,255,0.25)",
        beam:    "rgba(91,108,255,0.10)",
        glow1:   "rgba(91,108,255,0.10)",
        glow2:   "rgba(91,108,255,0.02)",
        star:    null,   // no stars in light mode
      };
    }
    return {
      bg:      "#020b18",
      wire:    "rgba(26,111,196,0.35)",
      cont:    "rgba(74,158,255,0.7)",
      contFill:"rgba(20,100,200,0.08)",
      dot:     "#5cbcff",
      dotGlow: "rgba(92,188,255,0.3)",
      beam:    "rgba(58,160,255,0.12)",
      glow1:   "rgba(6,26,58,0)",
      glow2:   "rgba(10,61,145,0.25)",
      star:    "rgba(180,210,255,",
    };
  }

  /* ── stars (pre-generated, dark mode only) ───────────── */
  const stars = [];
  for (let i = 0; i < 220; i++) {
    stars.push({
      x: Math.random(),   // normalised 0-1
      y: Math.random(),
      r: Math.random() * 1.1 + 0.3,
      b: Math.random() * 0.5 + 0.3,
    });
  }
  function drawStars(p) {
    if (!p.star) return;
    for (const s of stars) {
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, s.r, 0, TAU);
      ctx.fillStyle = p.star + s.b + ")";
      ctx.fill();
    }
  }

  /* ── continent outlines (lat, lon) ───────────────────── */
  const CONTINENTS = [
    // North America
    [[72,-170],[68,-165],[64,-140],[60,-139],[58,-148],[60,-152],[63,-165],[65,-168],[70,-165],[72,-170]],
    [[60,-139],[57,-135],[55,-130],[50,-127],[48,-124],[42,-124],[37,-122],[33,-118],[30,-115],[28,-105],[26,-98],[25,-90],[29,-85],[30,-82],[27,-80],[25,-80],[27,-77],[30,-82],[35,-76],[40,-74],[42,-70],[44,-68],[46,-64],[48,-59],[50,-57],[53,-56],[55,-60],[58,-63],[60,-64]],
    [[60,-64],[62,-75],[58,-80],[55,-83],[50,-88],[48,-88],[48,-95],[52,-97],[55,-100],[58,-110],[60,-120],[60,-139]],
    // South America
    [[12,-73],[10,-72],[8,-68],[7,-63],[5,-57],[4,-53],[2,-50],[0,-50],[-2,-44],[-5,-35],[-8,-35],[-10,-37],[-13,-38],[-17,-39],[-22,-41],[-25,-46],[-28,-49],[-32,-52],[-35,-57],[-38,-58],[-40,-62],[-43,-65],[-46,-67],[-50,-73],[-53,-70],[-55,-68],[-52,-70],[-47,-74],[-42,-73],[-38,-63],[-34,-58],[-30,-50],[-25,-48],[-22,-43],[-20,-40],[-17,-39],[-13,-38],[-8,-35],[-5,-35],[-2,-44],[0,-50],[2,-50],[4,-53],[5,-57],[7,-63],[8,-68],[10,-72],[12,-73]],
    // Africa
    [[37,-10],[36,-5],[35,0],[33,10],[32,32],[30,33],[27,34],[22,37],[18,41],[15,42],[12,44],[10,45],[8,43],[5,42],[2,42],[0,42],[-3,40],[-7,40],[-10,40],[-13,40],[-17,37],[-20,35],[-25,33],[-28,32],[-30,30],[-34,26],[-35,20],[-34,18],[-30,17],[-25,15],[-20,12],[-15,12],[-10,14],[-5,10],[0,10],[5,8],[5,2],[5,-2],[7,-8],[10,-15],[14,-17],[18,-17],[21,-17],[25,-15],[30,-10],[35,-5],[37,-10]],
    // Europe
    [[70,20],[68,25],[65,28],[63,30],[60,30],[58,28],[56,24],[55,21],[54,14],[53,10],[52,7],[51,4],[50,2],[48,0],[47,-2],[44,-5],[43,-9],[37,-8],[36,-6],[37,0],[38,5],[39,8],[40,10],[42,13],[43,16],[44,14],[45,14],[47,15],[48,17],[50,20],[52,18],[54,16],[55,13],[56,12],[57,10],[59,10],[60,10],[62,15],[64,15],[66,16],[68,18],[70,20]],
    // Asia (simplified)
    [[70,30],[70,60],[68,70],[65,80],[63,90],[60,100],[58,110],[55,120],[53,130],[50,135],[48,140],[45,142],[43,145],[40,140],[38,135],[35,130],[33,128],[30,122],[28,120],[25,120],[22,115],[20,110],[18,108],[15,108],[12,108],[10,106],[8,105],[5,105],[2,104],[0,104],[-2,105],[-5,106],[-8,115],[-7,120],[-5,120],[0,118],[3,115],[5,110],[8,108],[10,106],[12,100],[15,100],[18,98],[20,95],[22,90],[25,88],[28,85],[30,80],[32,75],[30,70],[28,65],[25,62],[25,58],[28,55],[30,50],[33,48],[35,45],[38,43],[40,43],[42,40],[45,38],[48,40],[50,45],[52,50],[55,55],[58,60],[60,65],[63,70],[65,75],[68,80],[70,80],[72,75],[73,60],[72,45],[70,30]],
    // Australia
    [[-12,131],[-14,127],[-17,123],[-20,118],[-24,115],[-28,114],[-32,115],[-35,117],[-37,140],[-38,145],[-37,150],[-34,151],[-30,153],[-26,153],[-22,150],[-19,147],[-16,145],[-14,142],[-13,137],[-12,131]],
    // Greenland
    [[78,-72],[76,-68],[73,-56],[72,-52],[70,-52],[68,-54],[65,-54],[62,-50],[60,-45],[60,-48],[63,-52],[65,-54],[68,-56],[70,-56],[72,-55],[74,-60],[76,-68],[78,-72]],
  ];

  /* ── city dots (lat, lon) ────────────────────────────── */
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

  /* ── beams ───────────────────────────────────────────── */
  const BEAM_N = 16;

  /* ── draw helpers ────────────────────────────────────── */
  function drawRing(pts, color, width) {
    if (pts.length < 2) return;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
  }

  function drawContour(points, rad, color, fillColor) {
    // Split at hidden-back discontinuities
    let segments = [], cur = [];
    for (const [la, lo] of points) {
      const p = rotY(spherePt(la, lo), rad);
      if (p[2] < 0) { if (cur.length > 1) segments.push(cur); cur = []; continue; }
      cur.push(project(p));
    }
    if (cur.length > 1) segments.push(cur);
    for (const seg of segments) {
      if (seg.length < 2) continue;
      ctx.beginPath();
      ctx.moveTo(seg[0][0], seg[0][1]);
      for (let i = 1; i < seg.length; i++) ctx.lineTo(seg[i][0], seg[i][1]);
      if (fillColor) {
        ctx.closePath();
        ctx.fillStyle = fillColor;
        ctx.fill();
      }
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.lineJoin = "round";
      ctx.stroke();
    }
  }

  /* ── main loop ───────────────────────────────────────── */
  function frame(ts) {
    if (!running) return;
    requestAnimationFrame(frame);

    // Check if canvas is visible
    const rect = canvas.getBoundingClientRect();
    if (rect.width < 10 || rect.height < 10) return;

    // Check if stage is still visible (perf guard)
    const stageRect = canvas.parentElement.getBoundingClientRect();
    if (stageRect.bottom < -100 || stageRect.top > window.innerHeight + 100) return;

    // Resize if needed
    const cw = rect.width, ch = rect.height;
    if (Math.abs(cw - W) > 2 || Math.abs(ch - H) > 2) measure();

    const t = ts * 0.001;
    angle += 0.004;                    // Y-axis rotation speed
    const rad = angle;
    const p = pal();

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Canvas is transparent — page background shows through

    // Stars (dark mode only)
    drawStars(p);

    // Ambient glow behind globe
    const g1 = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 1.35);
    g1.addColorStop(0, p.glow1);
    g1.addColorStop(1, p.glow2);
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.35, 0, TAU);
    ctx.fillStyle = g1;
    ctx.fill();

    // ── latitude rings ──
    for (let lat = -80; lat <= 80; lat += 20) {
      const pts = [];
      for (let lon = 0; lon <= 360; lon += 5) {
        const v = rotY(spherePt(lat, lon), rad);
        if (v[2] < 0) { if (pts.length > 1) drawRing(pts, p.wire, 0.6); pts.length = 0; continue; }
        pts.push(project(v));
      }
      if (pts.length > 1) drawRing(pts, p.wire, 0.6);
    }

    // ── longitude rings ──
    for (let lon = 0; lon < 360; lon += 30) {
      const pts = [];
      for (let lat = -90; lat <= 90; lat += 5) {
        const v = rotY(spherePt(lat, lon), rad);
        if (v[2] < 0) { if (pts.length > 1) drawRing(pts, p.wire, 0.6); pts.length = 0; continue; }
        pts.push(project(v));
      }
      if (pts.length > 1) drawRing(pts, p.wire, 0.6);
    }

    // ── continents ──
    for (const poly of CONTINENTS) drawContour(poly, rad, p.cont, p.contFill);

    // ── visible dots for beams ──
    const visDots = [];

    // ── city dots ──
    for (let i = 0; i < CITIES.length; i++) {
      const [lat, lon] = CITIES[i];
      const v = rotY(spherePt(lat, lon), rad);
      if (v[2] < -0.05) continue;
      const [sx, sy] = project(v);
      const depth = (v[2] + 1) / 2;
      const sz = 1.5 + depth * 2;
      const pulse = 1 + 0.25 * Math.sin(t * 2.5 + i * 0.8);
      // Glow
      ctx.beginPath();
      ctx.arc(sx, sy, (sz + 3) * pulse, 0, TAU);
      ctx.fillStyle = p.dotGlow;
      ctx.globalAlpha = 0.2 + depth * 0.3;
      ctx.fill();
      ctx.globalAlpha = 1;
      // Core
      ctx.beginPath();
      ctx.arc(sx, sy, sz * pulse, 0, TAU);
      ctx.fillStyle = p.dot;
      ctx.globalAlpha = 0.5 + depth * 0.5;
      ctx.fill();
      ctx.globalAlpha = 1;

      if (v[2] > 0.15) visDots.push([sx, sy, depth]);
    }

    // ── beams ──
    for (let i = 0; i < BEAM_N; i++) {
      if (!visDots.length) break;
      const d = visDots[i % visDots.length];
      const ba = (i / BEAM_N) * TAU + angle * 0.5;
      const len = R * (0.6 + 0.25 * Math.sin(t * 1.3 + i));
      const ex = d[0] + Math.cos(ba) * len;
      const ey = d[1] + Math.sin(ba) * len;
      ctx.beginPath();
      ctx.moveTo(d[0], d[1]);
      ctx.lineTo(ex, ey);
      ctx.strokeStyle = p.beam;
      ctx.lineWidth = 0.8;
      ctx.globalAlpha = 0.06 + d[2] * 0.14;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // ── rim highlight ──
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, TAU);
    ctx.strokeStyle = p.cont;
    ctx.lineWidth = 1.4;
    ctx.globalAlpha = 0.6;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  /* ── init ────────────────────────────────────────────── */
  measure();
  requestAnimationFrame(frame);

  /* ── react to theme toggle ───────────────────────────── */
  // Observe class changes on <html> for instant palette swap
  const observer = new MutationObserver(function () {
    // Palette is read every frame via pal(), nothing else needed
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });

  /* ── pause when tab hidden ───────────────────────────── */
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { running = false; }
    else { running = true; requestAnimationFrame(frame); }
  });

})();
