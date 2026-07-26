# TKVibes Agency — Static HTML Site

## Identity

Public agency website at tkvibes.com. Plain HTML/CSS/JS — no framework.

## Structure

- `index.html`, `about.html`, `services.html`, `packages.html`, `portfolio.html`, `contact.html`
- `assets/css/styles.css` — all styles
- `assets/js/main.js` — navbar, aurora scroll, hero stack, portfolio filters, contact multi-select
- `websites/` — portfolio demos and screenshots

## Deployment

Push to `main` → GitHub Actions → FTPS → Hostinger `public_html/`

No build step. Edit HTML/CSS/JS directly.

## Local preview

```bash
npx serve .
```
