/**
 * DecryptText — vanilla JS decrypt animation for hero heading.
 * Preserves site font (Manrope), CSS variable colors, light/dark theme.
 * Zero dependencies. Drop-in replacement for the React component.
 */
(function(){
  'use strict';

  if (typeof window === 'undefined') return;

  /* ── config ── */
  var SPEED       = 45;       // ms per glyph cycle
  var STAGGER     = 55;       // ms between each char lock-in
  var START_DELAY = 400;      // ms before first char can lock
  var JITTER      = 120;      // ±ms random spread per char
  var LOOP_MS     = 8000;     // ms before auto re-run
  var HOVER_CD    = 1500;     // ms cooldown before hover re-trigger

  var POOL = '#%&@$?!*+=/{}[]<>~^';

  /* mulberry32 PRNG */
  function makeRng(seed) {
    var a = seed >>> 0;
    return function(){
      a = (a + 0x6d2b79f5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ── text decrypt instance ── */
  function createDecrypt(el) {
    var rng = makeRng(1);
    var rafId = null;
    var timerId = null;
    var lastStart = -Infinity;
    var runCount = 0;
    var lockAt, nextAt, locked, cells;

    /* Read original structure and preserve color intent:
       base text node => base color, text inside span => accent color */
    function collectChars(node, accent, out) {
      if (!node) return;
      if (node.nodeType === 3) {
        var txt = node.textContent || '';
        for (var i = 0; i < txt.length; i++) out.push({ ch: txt[i], accent: !!accent });
        return;
      }
      if (node.nodeType !== 1) return;
      var isAccent = accent || node.tagName.toLowerCase() === 'span';
      var children = node.childNodes;
      for (var j = 0; j < children.length; j++) collectChars(children[j], isAccent, out);
    }

    var charMap = [];
    var initialChildren = Array.prototype.slice.call(el.childNodes);
    for (var n = 0; n < initialChildren.length; n++) collectChars(initialChildren[n], false, charMap);
    if (!charMap.length) return;

    /* Build character wrappers */
    el.innerHTML = '';
    for (var k = 0; k < charMap.length; k++) {
      var item = charMap[k];
      var span = document.createElement('span');
      span.className = 'dt-char';
      span.setAttribute('data-mk-char', item.ch);
      span.setAttribute('data-state', 'plain');
      span.setAttribute('data-tone', item.accent ? 'accent' : 'base');
      span.textContent = item.ch;
      el.appendChild(span);
    }

    var cellsRaw = el.querySelectorAll('.dt-char');
    cells = Array.prototype.slice.call(cellsRaw);

    /* Hide the original chars, show scrambled */
    function stop() {
      if (rafId !== null) cancelAnimationFrame(rafId);
      rafId = null;
      if (timerId !== null) clearTimeout(timerId);
      timerId = null;
    }

    function resolveAll() {
      for (var i = 0; i < cells.length; i++) {
        var c = cells[i];
        if (!c) continue;
        c.textContent = c.getAttribute('data-mk-char') || c.textContent;
        c.setAttribute('data-state', 'plain');
      }
    }

    function play() {
      rng = makeRng(1 + runCount * 7919);
      runCount++;
      stop();

      var n = cells.length;
      if (n === 0) return;

      lastStart = performance.now();

      lockAt = new Float64Array(n);
      nextAt = new Float64Array(n);
      locked = new Uint8Array(n);

      for (var i = 0; i < n; i++) {
        lockAt[i] = START_DELAY + i * STAGGER + (rng() * 2 - 1) * JITTER;
        nextAt[i] = 0;
        cells[i].setAttribute('data-state', 'scramble');
        cells[i].textContent = POOL.charAt((rng() * POOL.length) | 0);
      }

      var remaining = n;
      var t0 = performance.now();

      function frame() {
        var now = performance.now() - t0;
        for (var i = 0; i < n; i++) {
          if (locked[i]) continue;
          var c = cells[i];
          if (now >= lockAt[i]) {
            c.textContent = c.getAttribute('data-mk-char') || '';
            c.setAttribute('data-state', 'lock');
            locked[i] = 1;
            remaining--;
          } else if (now >= nextAt[i]) {
            c.textContent = POOL.charAt((rng() * POOL.length) | 0);
            nextAt[i] = now + SPEED + rng() * 35;
          }
        }
        if (remaining <= 0) {
          rafId = null;
          if (LOOP_MS > 0) {
            timerId = setTimeout(function(){
              timerId = null;
              play();
            }, LOOP_MS);
          }
          return;
        }
        rafId = requestAnimationFrame(frame);
      }
      rafId = requestAnimationFrame(frame);
    }

    /* ── intersection observer (inview trigger) ── */
    var io = null;
    var inviewPlayed = false;

    function startOnInview() {
      if (typeof IntersectionObserver === 'undefined') {
        play();
        return;
      }
      io = new IntersectionObserver(function(entries) {
        if (entries.some(function(e){ return e.isIntersecting; })) {
          if (!inviewPlayed) {
            inviewPlayed = true;
            play();
          }
          if (io) { io.disconnect(); io = null; }
        }
      }, { threshold: 0.12 });
      io.observe(el);
    }

    startOnInview();

    /* ── hover re-trigger ── */
    el.addEventListener('pointerenter', function(){
      if (rafId !== null) return;
      if (performance.now() - lastStart < HOVER_CD) return;
      play();
    });

    /* ── reduced motion ── */
    var mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mq.matches) {
      stop();
      resolveAll();
    }
    mq.addListener(function(e){
      if (e.matches) {
        stop();
        resolveAll();
      }
    });

    return { stop: stop, resolveAll: resolveAll, play: play };
  }

  /* ── init ── */
  function init() {
    var h1 = document.querySelector('.hero-copy h1');
    if (!h1) return;

    /* Mark target and initialize */
    h1.setAttribute('data-decrypt', '');
    createDecrypt(h1);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* ── inject decrypt char styles ── */
  /* Uses the same CSS variables as the site for seamless theme switching */
  var style = document.createElement('style');
  style.textContent = [
    '[data-decrypt] .dt-char {',
    '  transition: none;',
    '}',
    '[data-decrypt] .dt-char[data-tone="base"][data-state="plain"],',
    '[data-decrypt] .dt-char[data-tone="base"][data-state="lock"] {',
    '  color: var(--color-text-primary, #f5f7fb);',
    '}',
    '[data-decrypt] .dt-char[data-tone="accent"][data-state="plain"],',
    '[data-decrypt] .dt-char[data-tone="accent"][data-state="lock"] {',
    '  color: var(--color-primary-strong, #a8b4ff);',
    '}',
    '[data-decrypt] .dt-char[data-state="scramble"] {',
    '  color: var(--color-primary, #7c8cff);',
    '  opacity: 0.72;',
    '}',
    '[data-decrypt] .dt-char[data-state="lock"] {',
    '  animation: dt-flash 420ms cubic-bezier(.2,0,0,1);',
    '}',
    '@keyframes dt-flash {',
    '  0% {',
    '    text-shadow: 0 0 24px color-mix(in oklab, var(--color-primary, #7c8cff) 70%, transparent);',
    '  }',
    '  100% { text-shadow: 0 0 0 transparent; }',
    '}',
    '@media (prefers-reduced-motion: reduce) {',
    '  [data-decrypt] .dt-char[data-state="lock"] { animation: none; }',
    '}'
  ].join('\n');
  document.head.appendChild(style);
})();