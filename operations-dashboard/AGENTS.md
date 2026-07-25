# Hermes Operations Dashboard

## Identity
This is our **backend CRM and operations dashboard** — tracks leads, pipeline stages, generated assets, communications, and business metrics. It is the central command center for our agency's operations.

## Location
`C:\Users\takcl\Desktop\tkvibes-agency\operations-dashboard\`

## Tech Stack
- Next.js 16.2.10 + React 19 + TypeScript 5 + TailwindCSS v4
- Prisma 7 + SQLite (via `@prisma/adapter-libsql` + `@libsql/client`)
- Recharts (charts), @hello-pangea/dnd (Kanban), Lucide icons

## Architecture
**Agents write data, dashboard reads it.** The dashboard does NOT perform work — it visualizes what Hermes agents have done.

## Pages
| Route | Page | Description |
|---|---|---|
| `/` | Dashboard | Stats cards, charts, activity feed, auto-refresh 30s |
| `/pipeline` | Lead Pipeline | Kanban board with 13 stages, drag-and-drop |
| `/businesses` | Businesses | Filterable table with search, pagination |
| `/businesses/[id]` | Business Profile | Full detail: timeline, comms, tasks, assets |
| `/communications` | Communications | Chronological interaction history |
| `/outreach` | Outreach | Email tracking with status badges |
| `/tasks` | Tasks | Task list with filter tabs, mark complete |
| `/projects` | Projects | Business project management |
| `/websites` | Website Generator | Generated website cards |
| `/pitch-decks` | Pitch Decks | Generated deck cards with preview/export |
| `/analytics` | Analytics | Charts: industry, scores, revenue, funnel |
| `/agents` | Agent Monitor | Agent + skill status cards with heartbeat |
| `/settings` | Settings | Backup, export (JSON/CSV/MD), about |

## API Routes
| Route | Purpose |
|---|---|
| `/api/stats` | Dashboard aggregation |
| `/api/businesses` | CRUD + filter/search/paginate |
| `/api/businesses/[id]` | Detail + PATCH/DELETE with stage logging |
| `/api/communications` | Communication history |
| `/api/emails` | Email tracking |
| `/api/tasks` | Task CRUD |
| `/api/agents` | Agent status reporting |
| `/api/skills` | Skill status reporting |
| `/api/search` | Global search |
| `/api/settings` | Settings, backup, export |

## DB Schema (Prisma/SQLite)
20+ tables: Business, Contact, Communication, Email, Task, Project, GeneratedAsset, Proposal, Meeting, Note, Tag, BusinessTag, StageLog, TimelineEvent, ActivityLog, AgentStatus, SkillStatus, Backup, Setting, User

## Commands
- `npm run dev` — Start on port 3006
- `npm run build` — Production build
- `npm run seed` — Re-seed with real business data
- DB: `prisma/dev.db` (SQLite)

## Key Utils
- `@/lib/utils` — cn(), formatCurrency(), formatDate(), formatRelativeTime(), getStageColor(), getScoreLabel(), getAgentStatusColor(), PIPELINE_STAGES
- CSS classes: card, card-hover, btn, btn-primary, btn-secondary, btn-ghost, badge, badge-*, input, select, skeleton, chart-container, glass

## Client Data
Seeded with 5 real clients from `C:\Users\takcl\Desktop\clients\`:
1. Mita Dental PHL — Meeting Scheduled, Score 92, 4.9★
2. Deep Water Tank Cleaning — Qualified, Score 62, 4.5★
3. Tasty Bites Cafe — Website Generated, Score 74, 4.6★
4. Premium Dental Clinic — Website Generated, Score 80, 4.7★
5. Let's Smile Dental — Proposal Ready, Score 76, 4.8★

## Pipeline Stages
Discovered → Qualified → Website Generated → Proposal Ready → Outreach Sent → Waiting For Reply → Interested → Meeting Scheduled → Quotation Sent → Negotiation → Won → Lost → Archived