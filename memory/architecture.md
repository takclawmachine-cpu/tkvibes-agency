# Architecture

## High-level

```
Browser
   │
   ▼
Hostinger Apache (public_html/)
   ├── *.html          (7 pages, relative asset paths)
   ├── assets/
   │   ├── css/styles.css
   │   └── js/main.js
   ├── websites/       (portfolio demos + screenshots)
   ├── .htaccess       (rewrites, cache, security headers)
   └── brand/favicons
```

No application server. No SSR. No API routes on this repo.

## Repository layout

```
TkVibes/
├── index.html              Home (hero butterfly carousel, proof pills, metrics)
├── about.html              Mission, values, team, stats
├── services.html           Service list + why-grid
├── packages.html           Pricing tiers, add-ons, FAQ
├── portfolio.html          Filterable project grid
├── contact.html            FormSubmit form + map + multi-select
├── 404.html                Not found page
├── assets/
│   ├── css/styles.css      ~2200 lines, all styles + html.light block
│   └── js/main.js          Navbar, theme, carousels, filters, form UI
├── websites/
│   ├── *.html              Standalone client demo pages
│   └── screenshots/        PNG previews for hero/portfolio
├── tk-vibes-mark.svg       Primary logo (nav/footer)
├── tk-vibes-logo.svg       Full wordmark (legacy footer, unused)
├── favicon.ico, icon.png, apple-icon.png
├── .htaccess
├── .github/workflows/deploy.yml
├── memory/                 Agent memory bank (not deployed)
├── README.md
└── AGENTS.md
```

## HTML page pattern

Every page shares the same shell:

1. Inline theme init script in `<head>` (prevents flash)
2. `<html class="light">` / `<body class="light">` (home adds `home-route`)
3. Decorative layers: `.site-aurora`, `.site-grid`, `.site-noise`
4. `.navbar` → `.nav-panel` → logo, links, theme toggle, CTA, mobile toggle
5. `<main class="site-main">` — page sections
6. `.footer` — mark logo, links, social
7. `<script src="assets/js/main.js" defer>`

All asset URLs are **relative** (`assets/...`, `index.html`) so the site works via `file://` and static hosting.

## Apache / `.htaccess`

- **Clean URLs:** `/about` → `about.html` when file exists
- **404:** `ErrorDocument 404 /404.html`
- **Caching:** 1 year for CSS, JS, images, SVG
- **Compression:** `mod_deflate` for text assets
- **Security headers:** `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`

## External dependencies (CDN)

| Resource | URL |
|----------|-----|
| Manrope + IBM Plex Mono | fonts.googleapis.com |
| Font Awesome 6.5.1 | cdnjs.cloudflare.com |
| Google Maps embed | contact page iframe |
| FormSubmit | form action on contact form |

## History

Originally a **Next.js** app. Migrated to static HTML in commit `967c431` because Hostinger shared hosting has no Node runtime. All React components were flattened into HTML; styles consolidated into one CSS file; behavior into one JS file.
