# TKVibes Agency

Public agency website for [tkvibes.com](https://tkvibes.com). Built as a **static export** and deployed to **Hostinger shared hosting** via GitHub Actions (FTPS).

## Repository layout

```
tkvibes-agency/
├── src/                          # Agency website source
│   ├── app/                      # Next.js App Router pages
│   ├── components/
│   │   ├── layout/               # Navbar, Footer
│   │   └── ui/                   # Page-specific UI components
│   └── lib/                      # Shared data and config
├── public/
│   ├── .htaccess                 # Apache cache & security (copied to out/ on build)
│   └── websites/                 # Portfolio demo sites + screenshots
└── .github/workflows/
    ├── ci.yml                    # Lint + build on PR/push
    └── deploy.yml                # Build + FTPS deploy to Hostinger
```

## Tech stack

- Next.js 16 (App Router, `output: 'export'`)
- React 19 + TypeScript 5
- Tailwind CSS v4
- Font Awesome via CDN

## Local development

```bash
npm install
npm run dev        # http://localhost:3000
npm run build      # outputs static files to out/
npm run lint
```

## Deployment

Push to `main` triggers `.github/workflows/deploy.yml`:

1. `npm ci && npm run build` → static files in `out/`
2. PNG compression via optipng
3. FTPS mirror to Hostinger `public_html/`

Required GitHub secrets: `FTP_USER`, `FTP_PASS`, `FTP_HOST`

No VPS or Node.js runtime is needed on the server — shared hosting serves plain HTML/CSS/JS.

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home |
| `/about` | About |
| `/services` | Services |
| `/packages` | Pricing packages |
| `/portfolio` | Client work showcase |
| `/contact` | Contact form (FormSubmit.co) |
