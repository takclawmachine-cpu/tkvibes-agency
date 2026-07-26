# TKVibes Agency

Public marketing website for **[TKVibes Digital Agency](https://tkvibes.com)** — premium websites, brand identity, SEO, paid ads, and automation for modern service brands.

Built as **plain HTML, CSS, and JavaScript** with no build step. Deployed to **Hostinger shared hosting** via GitHub Actions (FTPS).

## Quick start

```bash
# Clone
git clone https://github.com/takclawmachine-cpu/tkvibes-agency.git
cd tkvibes-agency

# Local preview (recommended)
npx serve .

# Or open index.html directly in a browser (relative paths supported)
```

## Tech stack

| Layer | Choice |
|-------|--------|
| Markup | Static HTML (7 pages) |
| Styles | Single file — `assets/css/styles.css` |
| Scripts | Single file — `assets/js/main.js` |
| Fonts | Manrope + IBM Plex Mono (Google Fonts) |
| Icons | Font Awesome 6.5.1 (CDN) |
| Forms | [FormSubmit](https://formsubmit.co) → `services@tkvibes.in` |
| Hosting | Hostinger Apache (`public_html/`) |
| CI/CD | GitHub Actions + `lftp` FTPS mirror |

## Project structure

```
├── index.html                 Home
├── about.html                 About, team, values
├── services.html              Services
├── packages.html              Pricing & FAQ
├── portfolio.html             Project gallery + filters
├── contact.html               Contact form & map
├── 404.html                   Not found
├── assets/
│   ├── css/styles.css         All styles (incl. light/dark theme)
│   └── js/main.js             Navbar, theme, carousels, filters, form UI
├── websites/                  Portfolio demo pages + screenshots
├── tk-vibes-mark.svg          Primary logo (nav & footer)
├── tk-vibes-logo.svg          Full wordmark
├── favicon.ico, icon.png, apple-icon.png
├── .htaccess                  Clean URLs, cache, security headers
├── memory/                    Project memory bank (for agents & maintainers)
├── .github/workflows/deploy.yml
├── AGENTS.md                  Short guide for AI coding agents
└── README.md                  This file
```

## Pages & URLs

Apache rewrites extensionless paths to `.html` files (see `.htaccess`).

| URL | File |
|-----|------|
| `/` | `index.html` |
| `/about` | `about.html` |
| `/services` | `services.html` |
| `/packages` | `packages.html` |
| `/portfolio` | `portfolio.html` |
| `/contact` | `contact.html` |

## Features

- **Light / dark theme** — toggle in navbar; default light; persisted in `localStorage` (`tkvibes-theme`)
- **Hero butterfly carousel** — featured project screenshots with 3D transition (home)
- **Proof pill carousel** — continuous scrolling services strip (home)
- **Portfolio filters** — category buttons on portfolio page
- **Contact multi-select** — custom services dropdown with FormSubmit hidden fields
- **Responsive nav** — mobile hamburger menu with glass panel
- **Aurora background** — scroll-driven parallax on home page

## Design tokens

- Max content width: **1400px** (`--container-max` in CSS)
- Theme classes: `html.light` / `html.dark` + matching `body` classes
- See [`memory/design-system.md`](memory/design-system.md) for full token list

## Deployment

Push to **`main`** triggers automatic deploy to Hostinger `public_html/`.

**Required GitHub repository secrets:**

| Secret | Description |
|--------|-------------|
| `FTP_USER` | Hostinger FTP username |
| `FTP_PASS` | Hostinger FTP password |
| `FTP_HOST` | FTP host |

No Node.js or build step runs on the server. The workflow verifies core static files, then mirrors the repo (excluding `.github/`, docs, and `memory/`).

Details: [`memory/deployment.md`](memory/deployment.md)

## Contact & brand

| | |
|-|-|
| **Email** | services@tkvibes.in |
| **Phone / WhatsApp** | +91 98182 46938 |
| **Site** | [tkvibes.com](https://tkvibes.com) |

## Memory bank

Long-lived project knowledge for maintainers and AI agents lives in **[`memory/`](memory/)**:

- [`memory/summary.md`](memory/summary.md) — quick context
- [`memory/architecture.md`](memory/architecture.md) — structure & hosting
- [`memory/design-system.md`](memory/design-system.md) — theme & UI
- [`memory/features.md`](memory/features.md) — JS behavior & pages
- [`memory/troubleshooting.md`](memory/troubleshooting.md) — common fixes

Start with [`memory/README.md`](memory/README.md).

## Contributing / editing

1. Edit HTML for content, `assets/css/styles.css` for styling, `assets/js/main.js` for behavior.
2. Keep asset paths **relative** (never `/assets/...`).
3. Keep `styles.css` saved as **UTF-8**.
4. Add `html.light` overrides when introducing new dark-hardcoded overlays or dropdowns.
5. Push to `main` to deploy — no separate release step.

## License

Proprietary — TKVibes Agency. All rights reserved.
