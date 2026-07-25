# TKVibes Agency

## Workspace Structure
```
Desktop/
├── clients/                          ← ALL client projects
│   ├── mita-dental/                  → Dental clinic (4.9★, no website)
│   ├── deep-water-tank-cleaning/     → Water tank cleaning (SEO C grade)
│   ├── tasty-bites-cafe/             → Local cafe (3D website done)
│   ├── dental-clinic/                → Dental clinic (2 versions done)
│   └── lets-smile-dental/            → Dental practice (proposal ready)
├── tkvibes-agency/                   ← OUR agency (2 sub-projects)
│   ├── (root)                        → Our public website (Next.js 16)
│   └── operations-dashboard/         → Backend CRM/ops dashboard
├── LeadGenerationProject/            ← Legacy lead gen project (deprecated)
└── tkvibes-html-backup/             ← Old HTML backup (pre-Next.js)
```

## Two Main Projects

| Project | Purpose | Tech | Port |
|---|---|---|---|
| **tkvibes-agency** (root) | Our public agency website | Next.js 16, Tailwind v4 | 3000 |
| **operations-dashboard/** | Backend CRM & pipeline tracker | Next.js 16, Prisma, SQLite | 3006 |

## Client Projects
Each client in `clients/` has an `AGENTS.md` with their details, generated assets, and pipeline status. The dashboard tracks where each client is in the pipeline and what assets have been generated.

## Commands
- `cd ~/Desktop/tkvibes-agency && npm run dev` — Agency website
- `cd ~/Desktop/tkvibes-agency/operations-dashboard && npm run dev` — Ops dashboard
- `cd ~/Desktop/tkvibes-agency/operations-dashboard && npm run seed` — Re-seed database