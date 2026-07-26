# Design system

## Typography

- **Sans:** Manrope (`--font-sans`) — body, headings, UI
- **Mono:** IBM Plex Mono (`--font-mono`) — eyebrows, pills, labels

## Color tokens (`:root`)

Dark mode uses default `:root` variables. Light mode overrides them under `html.light { ... }`.

| Token | Dark (default) | Light |
|-------|----------------|-------|
| `--color-background` | `#06080c` | `#f4f6fb` |
| `--color-text-primary` | `#f5f7fb` | `#0f172a` |
| `--color-primary` | `#7c8cff` | `#5b6cff` |
| `--color-primary-strong` | `#a8b4ff` | `#4a59e6` |
| `--color-accent` | `#dcb676` | (unchanged) |
| `--color-border` | white @ 8% | slate @ 8% |

## Layout

- **Container:** `.container-main` → `width: min(var(--container-max), calc(100% - 2rem))`
- **`--container-max`:** `1400px` (was 1180px)
- **Section spacing:** `.section-padding` — vertical rhythm between blocks
- **CTAs:** `.cta-buttons` — flex, centered, wrap

## Theme system

| Piece | Detail |
|-------|--------|
| Default | Light |
| Persistence | `localStorage['tkvibes-theme']` → `'light'` \| `'dark'` |
| DOM classes | `html` + `body` get `.light` or `.dark` |
| Toggle | `.theme-toggle` in navbar; moon = switch to dark when in light mode |
| Flash guard | Inline IIFE in every page `<head>` before CSS |
| Light overrides | `html.light ...` block at end of `styles.css` |

### Light mode must override hardcoded dark UI

These components use hardcoded dark rgba/hex in base CSS — light overrides exist:

- `.nav-links.open` (mobile menu panel)
- `.form-group input/textarea/select`
- `.multi-select-trigger` / `.multi-select-options`
- Cards, footer, nav panel, proof strip fades

When adding new dropdowns or overlays, add matching `html.light` rules.

## Key UI components

### Navbar (`.navbar` / `.nav-panel`)

- Glass blur: `backdrop-filter: blur(24–32px)`
- Scrolled state: `.navbar.scrolled` — slightly more opaque panel
- Mobile (≤820px): `.nav-links` hidden until `.open`; hamburger → X

### Home hero

- **Copy column:** `.hero-copy` — headline, actions
- **Visual column:** `.hero-visual` — butterfly carousel (`.hero-butterfly`)
- **Metrics row:** `.hero-metrics` — full-width grid row below hero columns (`grid-column: 1 / -1`)
- Carousel: one `.hero-stack-card.active` at a time, 3D rotateY transition, 4.5s autoplay, dot nav

### Proof strip (`.proof-strip`)

- Infinite horizontal pill carousel (`.proof-carousel`)
- Two `.proof-carousel-group` copies for seamless loop
- JS clones pills if track narrower than container
- Edge fade via `::before` / `::after` gradients

### Cards

Shared pattern: border, subtle gradient background, `backdrop-filter` on some. Light mode sets white gradient via `html.light .feature-card, ...` group selector.

### Footer

- Uses **mark logo only** (`.brand-logo-mark`), not full wordmark
- `.footer-grid` — 4 columns desktop, stacks on mobile

## Buttons

- `.btn-custom.btn-primary-custom` — filled primary CTA
- `.btn-custom.btn-outline-custom` — bordered secondary
- Icons via Font Awesome inside buttons

## Editing CSS on Windows

`styles.css` must remain **UTF-8**. A prior UTF-16 encoding caused browsers to ignore the entire stylesheet. If StrReplace fails on this file, use a Node script to patch it.
