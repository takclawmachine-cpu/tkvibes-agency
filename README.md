# TKVibes Agency

Public agency website for [tkvibes.com](https://tkvibes.com). **Plain HTML/CSS/JS** — deployed to **Hostinger shared hosting** via GitHub Actions (FTPS).

## Structure

```
├── index.html              # Home
├── about.html              # About
├── services.html           # Services
├── packages.html           # Packages
├── portfolio.html          # Portfolio
├── contact.html            # Contact
├── assets/
│   ├── css/styles.css      # All styles
│   └── js/main.js          # Navbar, hero stack, filters, form UI
├── websites/               # Portfolio demos + screenshots
├── .htaccess               # Apache cache, security, clean URLs
└── .github/workflows/      # FTPS deploy on push to main
```

## Local preview

Double-click `index.html`, or serve the folder with any static server:

```bash
npx serve .
# or: python -m http.server 8080
```

Asset paths are relative, so opening HTML files directly in the browser works without a server.

## Deployment

Push to `main` uploads the repo root (excluding `.github/`, `scripts/`, docs) to Hostinger `public_html/`.

**No Node.js or build step required on the server.**

Required GitHub secrets: `FTP_USER`, `FTP_PASS`, `FTP_HOST`

## Pages

| URL | File |
|-----|------|
| `/` | `index.html` |
| `/about` | `about.html` |
| `/services` | `services.html` |
| `/packages` | `packages.html` |
| `/portfolio` | `portfolio.html` |
| `/contact` | `contact.html` |

Clean URLs (`/about` → `about.html`) are handled by `.htaccess`.
