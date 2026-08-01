# Changelog (project-level)

Major milestones and migrations. Git commits on `main` are the source of truth.

## 2026 — Static site era

| Commit | Summary |
|--------|---------|
| `41b9001` | Initial cleanup for Hostinger shared hosting; brand logo |
| `6c00da3` | Favicon and app icons from logo |
| `967c431` | **Next.js → plain HTML/CSS/JS migration** |
| `5a436d9` | Fix local preview: UTF-8 CSS + relative asset paths |
| `7be7453` | Faster deploy: remove optipng, incremental FTP |
| `18d422d` | UI polish: light/dark theme, butterfly hero, proof carousel, navbar blur, layout fixes |

## Post-`18d422d` (local / pending push)

Work done in agent sessions, may exist uncommitted until next push:

- Remove hero stack header ("Project stack / Featured launches")
- Hero metrics: full-width row below hero grid
- Container width: 1180px → **1400px** (`--container-max`)
- Light mode fixes: mobile nav dropdown + contact form selects/multi-select
- Memory bank + README expansion

## Pre-migration (Next.js era)

Earlier commits included FTPS CI tuning (`aacaa30`, `e8b21cb`, `19ae1b3`) for Hostinger timeouts before static migration.

## Product decisions log

| Decision | Reason |
|----------|--------|
| No build step | Hostinger shared hosting has no Node |
| Relative URLs | Support opening HTML files without a server |
| FormSubmit | No backend on shared hosting |
| Default light theme | Client preference |
| Footer mark logo only | Cleaner footer, less visual weight |
| Single CSS + JS file | Simplicity, easy deploy, no bundler |

## When to update this file

After any commit that changes architecture, deploy, default theme, hosting, or migration status.

## 2026-07-30
- Replaced hero right-side butterfly card stack with CSS/SVG globe orbit animation (`.hero-globe-stage`, `hgOrbit` keyframes, 13.33s linear loop). Removed hero-stack/butterfly CSS + JS carousel.

## 2026-08-01
- Complete pricing restructure: tabbed Individual/Enterprise design on packages page
- Individual: Starter Rs 9,999 / Growth Rs 14,999 / Pro Rs 24,999 (all +5k)
- Enterprise: Business Rs 69,999 / Enterprise+ (Book Free Consultation, no price)
- New CSS: pricing tabs, enterprise grid, consult CTA, enterprise inquiry modal
- New JS: tab switching (pricing.js) + enterprise inquiry modal (enterprise-inquiry.js)
- Enterprise+ form captures name, org, email, phone, company size, budget, project details
