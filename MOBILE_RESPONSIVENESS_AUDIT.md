# Mobile Responsiveness Audit — TKVibes Agency

**Audited:** 2026-08-01
**CSS:** `assets/css/styles.css` (3058 lines)
**Pages:** index.html, about.html, services.html, portfolio.html, packages.html, contact.html, 404.html
**Breakpoints:** 1080px, 991px, 820px, 800px, 700px, 640px, 600px, 560px

---

## Summary

The site has a solid responsive foundation with breakpoints at 1080px, 820px, and 560px. Most grids collapse correctly. Below are the remaining issues, ranked by severity.

---

## CRITICAL ISSUES

### 🔴 Issue 1: Mobile nav hides the primary CTA button

**Files:** `styles.css`, all HTML pages

**Problem:** At 820px, `.nav-button` is set to `display: none` (line 2498). This removes the "Start a Project" CTA entirely from the mobile navigation. Mobile users lose the primary conversion action.

**.nav-button disappears at 820px:**
```css
/* line 2497-2499 */
.nav-button {
  display: none;
}
```

**Fix — add the CTA as the last item in the mobile nav menu:**
```css
@media (max-width: 820px) {
  /* line 2497-2499 — replace with: */
  .nav-button {
    display: inline-flex;
    width: 100%;
    justify-content: center;
    margin-top: 0.5rem;
  }

  .nav-links.open .nav-button {
    display: inline-flex;
  }
}
```

Or better, move the CTA link into the mobile nav-links list so it appears as a proper menu item. The HTML currently has it outside `.nav-links` inside `.nav-cta`. To add it to the mobile menu dropdown:

```css
@media (max-width: 820px) {
  .nav-links.open .mobile-cta-item {
    display: block;
    padding: 0.5rem 1rem;
    margin-top: 0.5rem;
    border-top: 1px solid var(--color-border);
  }
}
```

And in each HTML file, add a li to `.nav-links`:
```html
<li class="mobile-cta-item" style="display:none">
  <a class="btn-custom btn-primary-custom" href="contact.html">
    <i class="fas fa-paper-plane"></i> Start a Project
  </a>
</li>
```

---

### 🔴 Issue 2: Enterprise inquiry modal submit button overflows on small phones

**Files:** `styles.css` lines 1551-1556

**Problem:** `.enterprise-form-submit .btn-consult-custom` has `min-width: 280px`. On a 320–375px phone, the container width is ~288px (320 - 32px padding), and the form has `padding: 1.2rem 1.6rem`, leaving only ~243px of usable width. The button overflows horizontally.

```css
/* lines 1551-1556 */
.enterprise-form-submit .btn-consult-custom {
  width: auto;
  min-width: 280px;
  padding: 0.85rem 2rem;
  font-size: 0.95rem;
}
```

**Fix:**
```css
@media (max-width: 600px) {
  .enterprise-form-submit .btn-consult-custom {
    width: 100%;
    min-width: 0;
    padding: 0.85rem 1.5rem;
    font-size: 0.9rem;
  }
}
```

---

### 🔴 Issue 3: Hero windows (absolute-positioned) may overflow at medium breakpoints

**Files:** `styles.css` lines 528-544

**Problem:** The `.hero-window.large` uses `inset: 2rem 3.5rem 0 0` — these are absolute-positioned windows inside `.hero-visual`. At 1080px when `hero-grid` collapses to `1fr`, the hero-visual moves below the hero-copy. The fixed inset values (3.5rem right, 2rem top) were designed for the desktop layout proportion and may look misaligned or overlap at mid-size screens (820-1080px).

```css
/* lines 528-536 */
.hero-window.large {
  inset: 2rem 3.5rem 0 0;
}
.hero-window.small {
  right: 0;
  width: 38%;
  height: 36%;
}
```

**Fix — reduce/remove window decorations at mid breakpoints since the carousel + globe do the visual work:**
```css
@media (max-width: 1080px) {
  .hero-window {
    display: none; /* The globe + orbital carousel handle the visual */
  }
}
```

Or if keeping them:
```css
@media (max-width: 1080px) {
  .hero-window.large {
    inset: 1rem 1rem 0 0;
  }
  .hero-window.small {
    display: none; /* Too cramped at mid sizes */
  }
}
```

---

## HIGH SEVERITY ISSUES

### 🟠 Issue 4: Pricing tabs may overflow on very small screens (320-375px)

**Files:** `styles.css` lines 1323-1367

**Problem:** `.pricing-tabs` has `max-width: 400px` and contains two flex tabs. Each tab has `padding: 0.65rem 1.25rem` (~40px horizontal padding) plus an icon and text ("Individual" / "Enterprise"). On a 320px phone, the container is ~288px wide, minus 0.35rem padding on each side = ~277px for the tabs. Each tab needs ~130-140px. Two tabs at 140px = 280px, causing horizontal overflow or text wrapping.

```css
.pricing-tab {
  flex: 1;
  padding: 0.65rem 1.25rem;
  font-size: 0.9rem;
  gap: 0.45rem;
}
```

**Fix:**
```css
@media (max-width: 480px) {
  .pricing-tabs {
    max-width: 100%;
    border-radius: 1rem;
    padding: 0.25rem;
    gap: 0.25rem;
  }
  .pricing-tab {
    padding: 0.5rem 0.75rem;
    font-size: 0.78rem;
    gap: 0.3rem;
  }
  .pricing-tab i {
    font-size: 0.7rem;
  }
}
```

---

### 🟠 Issue 5: Hero globe glow circle has 340px minimum — overflows on small screens

**Files:** `styles.css` lines 2941-2951

**Problem:** `.hero-globe-glow` uses `clamp(340px, 40vw, 560px)` for both width and height. On a 320px phone, this resolves to 340px — wider than the viewport. While `.hero-visual` has `overflow: hidden`, the glow is clipped on the left and right, making it look off-center.

```css
.hero-globe-glow {
  width: clamp(340px, 40vw, 560px);
  height: clamp(340px, 40vw, 560px);
}
```

**Fix:**
```css
@media (max-width: 560px) {
  .hero-globe-glow {
    width: min(320px, 85vw);
    height: min(320px, 85vw);
  }
}
```

---

### 🟠 Issue 6: Orbital carousel cards may overflow globe stage at mid breakpoints (820-991px)

**Files:** `globe.js` lines 411-417, `styles.css` line 3050-3052

**Problem:** At 991px, `.hero-globe-stage` is set to `height: 420px`. The orbit carousel uses `getOrbitRadius()` which returns 190px for screens <900px. 190px radius + card width (170px)/2 = 275px from center, requiring 550px of width. At 820px the stage is 820px wide, which fits. But at 991px the stage is 991px wide. However, between 820-900px width, the stage width is 820-900px while the orbit requires 550px — fine. But at 820px, the globe stage is now full-width below the hero-copy (since hero-grid → 1fr). With `min-height: 420px` and `width: 100%`, this is fine.

However, the `.hero-visual` has `min-height: 420px` at 820px (line 2537-2539). With an orbit radius of 190px + card half-width (85px) = 275px from center, the topmost card would be 275px above center, so the total height needed is 420/2 + 275 = 485px. But `min-height: 420px` may not be enough — the cards could clip.

**Fix:**
```css
@media (max-width: 991px) {
  .hero-globe-stage {
    height: 480px; /* Was 420px — needs room for orbital cards */
  }
}

@media (max-width: 820px) {
  .hero-visual {
    min-height: 480px; /* Was 420px */
  }
}
```

Or in `globe.js`, reduce the orbit radius more aggressively at 820-900px:
```js
function getOrbitRadius() {
  const vw = window.innerWidth;
  if (vw < 600) return 140;
  if (vw < 900) return 160; // was 190
  return 260;
}
```

---

### 🟠 Issue 7: No 480px breakpoint — gap between 560px and 480px screens

**Files:** `styles.css`

**Problem:** The smallest breakpoint is 560px. On phones 480-559px wide (e.g. iPhone 6/7/8 at 375px, iPhone 12 mini at 360px, Galaxy S8 at 360px), the layout uses the 560px rules. While this mostly works, the gap means:
- Cards still have `1.2rem` padding (could be `1rem` at very small sizes)
- Hero h1 max-width `none` is correct but font could be tighter
- Pricing tab padding is still `1.25rem` horizontal per tab

**Fix — add a 480px breakpoint for very small phones:**
```css
@media (max-width: 480px) {
  .feature-card,
  .process-card,
  .value-card,
  .team-card,
  .addon-card,
  .testimonial-card,
  .mission-card,
  .contact-form-box,
  .custom-plan-card,
  .pricing-card-light {
    padding: 1rem;
  }

  .pricing-tab {
    padding: 0.45rem 0.6rem;
    font-size: 0.75rem;
  }

  .cta-panel {
    padding: 1.25rem;
  }

  .page-header .container-main {
    padding: 1.5rem;
  }
}
```

---

## MEDIUM SEVERITY ISSUES

### 🟡 Issue 8: Service menu cards have horizontal icon+text flex layout — text truncation on small screens

**Files:** `styles.css` lines 1609-1617

**Problem:** `.service-menu-card` uses `display: flex; gap: 1rem` with a fixed 40px icon and flex body. On a 320px screen (container ~288px), with 1.2rem padding on both sides + 1rem gap + 40px icon = ~78px overhead, leaving ~210px for text. Service names like "Google Business Optimization" could wrap or feel cramped.

This is mostly cosmetic, but the `sm-icon` width is fixed at 40px with `flex-shrink: 0` so it won't compress.

**Fix — make cards stack vertically at very small sizes:**
```css
@media (max-width: 400px) {
  .service-menu-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
```

---

### 🟡 Issue 9: FAQ padding doesn't shrink at mobile breakpoints

**Files:** `styles.css` lines 2007-2032

**Problem:** `.faq-item summary` has `padding: 1.3rem 1.5rem` and `.faq-answer` has `padding: 0 1.5rem 1.4rem`. These don't reduce at the 560px breakpoint or any smaller breakpoint. On a 320px phone, this leaves very little room for text.

**Fix:**
```css
@media (max-width: 560px) {
  .faq-item summary {
    padding: 1rem 1rem;
  }
  .faq-answer {
    padding: 0 1rem 1rem;
  }
}
```

---

### 🟡 Issue 10: Portfolio cards use fixed-width meta text max-width

**Files:** `styles.css` line 869

**Problem:** `.showcase-meta p, .pf-meta-row p` has `max-width: 16rem` (256px). On a 320px phone with card padding `1.35rem`, the available text area is ~260px, so this is tight but generally fine. However, at 560px with card padding `1.2rem`, available text area is ~256px — same as max-width. At 320px, the text could overflow.

```css
/* line 869 */
.showcase-meta p,
.pf-meta-row p {
  max-width: 16rem;
}
```

**Fix:**
```css
@media (max-width: 820px) {
  .showcase-meta p,
  .pf-meta-row p {
    max-width: none;
  }
}
```

---

### 🟡 Issue 11: Stats row stat font size doesn't shrink on mobile

**Files:** `styles.css` lines 1189-1193

**Problem:** `.stat h3` has `font-size: 2rem` at all breakpoints. At 820px the stats-row collapses to 1fr so each stat is full-width, making 2rem appropriate. But at the 560px breakpoint, the font remains 2rem which is large for small screens. This is minor since the stat is alone per row.

No fix strictly needed, but optionally:
```css
@media (max-width: 560px) {
  .stat h3 {
    font-size: 1.6rem;
  }
}
```

---

### 🟡 Issue 12: Section padding reduction only at 820px, not at 560px

**Files:** `styles.css` line 2566-2568

**Problem:** `.section-padding` drops from `5.5rem` to `3.5rem` at 820px but doesn't reduce further at 560px. On a 320px phone, 3.5rem (56px) vertical padding per section is reasonable but could be tighter.

**Optional fix:**
```css
@media (max-width: 560px) {
  .section-padding {
    padding: 2.5rem 0;
  }
}
```

---

## LOW SEVERITY / COSMETIC

### 🟢 Issue 13: Contact form headline text too large on small screens (already partially fixed)

**Files:** `styles.css` lines 2695-2703

The 640px breakpoint already reduces `contact-form-headline-text` from 1.75rem to 1.35rem. This is adequate.

### 🟢 Issue 14: Plan builder modal form inputs at small screens

**Files:** `styles.css` lines 1888-1916

The modal collapses to 1-column at 700px. Form inputs are `width: 100%` with `box-sizing: border-box`. This is fine.

### 🟢 Issue 15: Enterprise form row collapses at 600px

Already handled at lines 1503-1507. This is correct.

---

## SUMMARY TABLE

| # | Severity | Issue | Fix Location |
|---|----------|-------|-------------|
| 1 | 🔴 Critical | Mobile nav hides CTA button | `@media (max-width: 820px)` — show `.nav-button` in mobile menu |
| 2 | 🔴 Critical | Enterprise submit button min-width 280px overflows | `@media (max-width: 600px)` — set `min-width: 0; width: 100%` |
| 3 | 🔴 Critical | Hero absolute windows misaligned at mid breakpoints | `@media (max-width: 1080px)` — hide or reposition hero-windows |
| 4 | 🟠 High | Pricing tabs overflow on <375px screens | Add `@media (max-width: 480px)` with reduced tab padding/font |
| 5 | 🟠 High | Hero globe glow 340px min overflows small viewports | `@media (max-width: 560px)` — use `min(320px, 85vw)` |
| 6 | 🟠 High | Orbital carousel cards clip in 420px globe stage | Increase stage height or reduce orbit radius at 820-991px |
| 7 | 🟠 High | No 480px breakpoint for very small phones | Add `@media (max-width: 480px)` with tighter card padding/tab sizing |
| 8 | 🟡 Medium | Service menu cards may wrap text at <375px | `@media (max-width: 400px)` — flex-direction: column |
| 9 | 🟡 Medium | FAQ padding doesn't shrink at mobile | `@media (max-width: 560px)` — reduce padding to 1rem |
| 10 | 🟡 Medium | Portfolio card meta text max-width: 16rem may overflow | `@media (max-width: 820px)` — set max-width: none |
| 11 | 🟡 Medium | Stats h3 at 2rem doesn't reduce on small screens | Optional: `@media (max-width: 560px)` — font-size: 1.6rem |
| 12 | 🟡 Medium | Section padding could be tighter at 560px | Optional: `@media (max-width: 560px)` — padding: 2.5rem 0 |
| 13 | 🟢 Low | Contact form headline already handled at 640px | — |
| 14 | 🟢 Low | Plan modal already collapses at 700px | — |
| 15 | 🟢 Low | Enterprise form rows already collapse at 600px | — |

---

## RECOMMENDED FIX ORDER

1. **Critical Issues 1-3** — missing CTA on mobile is a conversion blocker; button overflow and window overflow are layout-breaking
2. **High Issues 4-7** — pricing tabs, globe glow, orbital clipping, and missing 480px breakpoint cause poor UX on smaller phones
3. **Medium Issues 8-12** — visual polish items that improve the experience but don't break functionality

## VERIFICATION CHECKLIST

After applying fixes:
- [ ] Nav mobile menu shows "Start a Project" CTA
- [ ] Enterprise modal button fits within 320px viewport width
- [ ] Pricing tabs don't overflow or wrap on 320-375px screens
- [ ] Hero globe glow circle doesn't clip asymmetrically
- [ ] Orbital carousel cards are fully visible within globe stage
- [ ] FAQ spacing is reasonable on 320px screens
- [ ] Service menu cards remain readable at all widths
- [ ] All grids display single-column below 820px
- [ ] No horizontal scrollbars appear at any width