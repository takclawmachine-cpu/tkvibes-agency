# Features & behavior (`assets/js/main.js`)

All JS is one IIFE, `'use strict'`, loaded with `defer` on every page.

## Navbar

- **Scroll:** Adds `.scrolled` to `.navbar` when `scrollY > 20`
- **Active link:** Matches current page from `pathname` vs link `href` (supports `index.html` and clean URLs)
- **Mobile menu:** Toggles `.nav-links.open`; swaps bars ↔ times icon; `aria-expanded`

## Theme toggle

- Reads/writes `localStorage['tkvibes-theme']`
- Default: `'light'`
- Updates `html`/`body` classes and toggle button icon/labels

## Proof carousel fill (home)

- Targets `.proof-carousel` / `.proof-carousel-track`
- Clones pills inside each `.proof-carousel-group` until group width ≥ container + 80px
- Re-runs on `resize`

## Footer year

- Elements with `[data-year]` get `new Date().getFullYear()`

## Aurora scroll (home only)

When `body.home-route`:

- Updates CSS vars on scroll: `--aurora-scroll`, `--aurora-tilt`, `--aurora-depth`, `--aurora-opacity`, `--aurora-grid-shift`
- Drives `.site-aurora` parallax via CSS

## Hero butterfly carousel (home)

- Container: `.hero-stack-frame` inside `.hero-butterfly`
- Cards: `.hero-stack-card` with `.active` on one
- Dots: `.hero-stack-dot` click → `setIndex`
- Autoplay: every 4500ms, wraps forward
- Animation classes: `butterfly-out-left`, `butterfly-in-right`, etc. (~850ms)

## Portfolio filter (`portfolio.html`)

- `.filter-bar` buttons with `data-filter`
- Cards: `.portfolio-card` with `data-categories` (space-separated)
- `"all"` shows everything; else match category token

## Website preview fallback

- `.website-preview-image` `error` → replaces with `.website-preview-fallback` message

## Contact multi-select (`contact.html`)

Custom services dropdown (not native `<select>`):

- Built from JS options array: Website design, Brand identity, SEO, Google ads, Meta ads, Automation workflows, Custom package
- Toggle `.multi-select.open`; list `.multi-select-options`
- Selected values → hidden `<input name="services">` fields for FormSubmit
- Clear button when selections exist

## Contact budget select

Native `<select id="budget">` — styled in CSS; light mode uses `color-scheme: light` override.

## Form submission

```html
<form action="https://formsubmit.co/services@tkvibes.in" method="POST">
```

Hidden fields: `_subject`, `_captcha=false`, `_template=table`

Fields: name, phone, email, services (multi), budget, message

## Pages overview

| Page | Notable sections |
|------|------------------|
| `index.html` | Hero carousel, proof strip, features, showcase, process, CTA |
| `about.html` | Mission, values, team, stats |
| `services.html` | Service detail cards, why-grid (3 col, centered) |
| `packages.html` | Pricing grid, add-ons, FAQ |
| `portfolio.html` | Category filter, project cards, demo links |
| `contact.html` | Form, map iframe, WhatsApp CTA |
| `404.html` | Minimal error layout |

## Portfolio demos (`websites/`)

Standalone HTML files for client projects:

- `lets-smile-dental.html`
- `tasty-bites-3d-cafe.html`
- `deep-water-tank-cleaning-modern.html`
- `mita-dental-website.html`
- `dental-clinic-3d.html`

Screenshots in `websites/screenshots/` feed hero and portfolio cards.
