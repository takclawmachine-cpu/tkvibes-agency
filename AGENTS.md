# TKVibes Agency — Main Website

## Identity
This is our **agency's own website** — the public-facing site at tkvibes.com. NOT the operations dashboard. NOT a client project.

## Tech Stack
- Next.js 16.2.10 + React 19 + TypeScript 5 + TailwindCSS v4
- App Router (file-system based routing)
- Dark theme by default

## Project Structure
- `src/app/about/` — About page
- `src/app/contact/` — Contact page
- `src/app/packages/` — Services/Packages page
- `src/app/portfolio/` — Portfolio page
- `src/app/services/` — Services page
- `src/components/` — Shared components (Navbar, Footer, ScrollToTop, WebsitePreview, WhatsAppFloat)
- `public/` — Static assets

## Commands
- `npm run dev` — Start dev server
- `npm run build` — Production build
- `npm run start` — Start production server

## Notes
- Uses **TailwindCSS v4** with `@tailwindcss/postcss` (NOT the old v3 PostCSS plugin)
- Layout is in `src/app/layout.tsx` — needs `dark` class on `<html>` for dark mode
- Do NOT confuse with `operations-dashboard/` subfolder — that's a separate project
- Next.js 16 has breaking changes from older versions. Read `node_modules/next/dist/docs/` before writing code.