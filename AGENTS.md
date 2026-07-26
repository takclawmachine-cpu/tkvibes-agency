# TKVibes Agency — Main Website

## Identity

This is our **agency's own website** — the public-facing site at tkvibes.com. NOT a client project.

## Tech stack

- Next.js 16.2.10 + React 19 + TypeScript 5 + TailwindCSS v4
- App Router (file-system based routing)
- Static export (`output: 'export'`) for shared hosting
- Dark theme by default

## Project structure

```
src/
├── app/                    # Pages (about, contact, packages, portfolio, services)
├── components/
│   ├── layout/             # Navbar, Footer
│   └── ui/                 # HeroProjectStack, WebsitePreview, MultiSelectServices
└── lib/
    ├── nav-links.ts        # Shared navigation config
    └── portfolio.ts        # Portfolio project data
public/
├── .htaccess               # Apache cache/security for Hostinger
└── websites/               # Client demo HTML + screenshots
```

## Commands

- `npm run dev` — Start dev server (port 3000)
- `npm run build` — Static export to `out/` (this is what gets deployed)
- `npm run lint` — ESLint

## Deployment (shared hosting)

Production does **not** use `npm run start`. The site is a static export deployed to Hostinger via GitHub Actions:

1. `npm run build` → `out/`
2. CI uploads `out/` to `public_html/` over FTPS

See `.github/workflows/deploy.yml` and root `README.md`.

## Notes

- Uses **TailwindCSS v4** with `@tailwindcss/postcss` (NOT the old v3 PostCSS plugin)
- Layout is in `src/app/layout.tsx` — needs `dark` class on `<html>` for dark mode
- Font Awesome loaded from CDN in layout (not an npm package)
- Next.js 16 has breaking changes from older versions. Read `node_modules/next/dist/docs/` before writing code.
