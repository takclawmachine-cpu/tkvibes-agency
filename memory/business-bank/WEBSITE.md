# Main Website — Deep Reference

## Pages & Files
| URL | File | Sections |
|-----|------|----------|
| `/` | `index.html` | Hero butterfly carousel, proof strip, features, showcase, process, CTA |
| `/about` | `about.html` | Mission, values, team, stats |
| `/services` | `services.html` | Service detail cards, why-grid |
| `/packages` | `packages.html` | Pricing grid, add-ons, FAQ |
| `/portfolio` | `portfolio.html` | Category filter, project cards, demo links |
| `/contact` | `contact.html` | Form, map, WhatsApp CTA |
| `/404` | `404.html` | Error page |

## Design System
- Max width: `1400px` (`--container-max`)
- Font: Manrope (sans) + IBM Plex Mono (mono)
- Icons: Font Awesome 6.5.1 CDN
- Form: FormSubmit → `services@tkvibes.in`
- Contact: `+91 98182 46938` · WhatsApp: `wa.me/919818246938`
- Theme: Light default, `localStorage` key `tkvibes-theme`, inline head script prevents flash

## CSS/JS
- `assets/css/styles.css` (~2200 lines, all styles + html.light block)
- `assets/js/main.js` (defer, IIFE): navbar, theme toggle, carousels, portfolio filters, contact multi-select, aurora parallax

## Apache
- `.htaccess`: clean URLs (`/about` → `about.html`), cache headers, deflate, security headers
- ErrorDocument 404 → `/404.html`

## Deploy
Push to `main` → GitHub Actions: `lftp` FTPS → Hostinger `public_html/`
Secrets: `FTP_USER`, `FTP_PASS`, `FTP_HOST` (GitHub, NOT in repo)

## Client Demo Sites
`websites/` — standalone HTML files:
- `lets-smile-dental.html` · `tasty-bites-3d-cafe.html` · `deep-water-tank-cleaning-modern.html`
- `mita-dental-website.html` · `dental-clinic-3d.html`