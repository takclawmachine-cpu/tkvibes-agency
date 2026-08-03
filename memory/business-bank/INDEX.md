# TKVibes Agency — Complete Business Memory Bank (Index)

> **Purpose:** Single source of truth for the entire TKVibes digital agency business.
> This profile (Hermes "default") is the **main brain** — orchestrates all agents and subsystems.
> Location: `C:\Users\takcl\Desktop\tkvibes-agency\memory\`

## 📇 Quick Index

| Subsystem | Where | Docs | Status |
|-----------|-------|------|--------|
| **Main website** | `tkvibes.in` → repo root | `memory/architecture.md`, `memory/features.md` | ✅ LIVE |
| **CRM** (employee dashboards) | `tkvibes.in/crm/` | `crm/README.md` | ✅ LIVE |
| **Lead engine** (B2B discovery) | `tkvibes-lead-engine/` | `tkvibes-lead-engine/README.md` | ✅ RUNNING |
| **Proposals pipeline** | lead-engine `data/proposals/` + `~/Desktop/clients/` | `src/push_proposals.py`, `src/scaffold_clients.py` | ✅ RUNNING |
| **Marketing engine** (reels) | `marketing/` | `marketing/README.md` | ✅ READY |
| **Cold-call training** | `cold-call-training.html` | — | ✅ LIVE |
| **Operations dashboard** (old Next.js) | `operations-dashboard/` | — | ⚠️ LEGACY (superseded by CRM) |
| **GSC** (Search Console) | `.hermes/gsc-helper.py` | — | ✅ CONNECTED |
| **Hostinger** (hosting) | API token in memory | hostinger-api skill | ✅ OWNED |

## 🔗 Business Flow (end-to-end)

```
1. DISCOVERY   lead-engine: Google Places (25 India cities + Canada) × 30 categories
       │          → 150+ leads/run, scored HOT/WARM/COLD
2. ENRICHMENT  email_finder.py (crawl site for emails), pain_points.py (per-category pitch)
       │          → contact_channel (email/whatsapp/phone), notes=MSG template
3. ASSIGNMENT  assign.py: CRM API employee→region mapping, round-robin
       │          → push_crm.py webhook → CRM (tkvibes.in/crm)
4. OUTREACH    build_outreach.py → outreach_queue.csv + wa.me links (manual, compliant)
       │          → employees call/WhatsApp leads from CRM dashboard
5. PROPOSALS   scaffold_clients.py → ~/Desktop/clients/<slug>/ briefs
       │          → WEBSITE AGENT builds <slug>-website.html
       │          → DECK AGENT builds <slug>-pitch-deck.html
       │          → push_proposals.py uploads to CRM
6. DELIVERY    website → deploy to client hosting; CRM tracks status
       │
7. GROWTH      marketing engine reels → Instagram/YouTube; GSC → SEO; site → new leads
```

## 🧠 Agent Roles (Hermes subagents)

| Agent | Model | Used For | Fallback |
|-------|-------|----------|----------|
| **Main Brain** (this profile) | deepseek/deepseek-v4-flash (openrouter) | orchestration, decisions, strategy | — |
| **Coder Agent** | qwen2.5-coder-1.5b (LOCAL, :8080) | HTML/CSS/JS edits, PHP, Python scripts | tencent/hy3 (openrouter) |
| **Task Agent** | qwen2.5-1.5b-instruct (LOCAL, :8081) | classification, extraction, summarization, data cleanup | deepseek-v4-flash |
| **Website Builder** | openrouter (best-available) | full client websites from briefs | — |
| **Pitch Deck Builder** | openrouter (best-available) | client pitch decks from briefs | — |
| **Research Agent** | openrouter | market research, competitor analysis | — |

## 🔑 Key Credentials (locations, not values)

- **Google Places API key** → `tkvibes-lead-engine/.env` (`GOOGLE_MAPS_API_KEY`)
- **Google Sheets** → `tkvibes-lead-engine/.env` (`GOOGLE_SHEETS_ID` = lead sheet)
- **Service account** → `tkvibes-lead-engine/credentials/google-service-account.json`
- **CRM API key** → `tkvibes-lead-engine/config.yaml` → `crm.api_key`
- **Hostinger API token** → Hermes memory + hostinger-api skill
- **Hostinger mail order** → `OR07b99a1a670248d8badd48d233bb` (Free Biz Email, 100 seats)
- **GSC OAuth** → `.hermes/gsc-credentials.json` + `gsc-token.json` + `gsc-helper.py`
- **FTP deploy** → GitHub secrets `FTP_USER` / `FTP_PASS` / `FTP_HOST` (NOT in repo)
- **FormSubmit** → contact form → `services@tkvibes.in`

## 🚀 Operations Commands

### Website (repo root: `~/Desktop/tkvibes-agency/`)
```bash
npx serve .                    # local preview
git add -A && git commit -m "x" && git push   # auto-deploys to Hostinger
```

### Lead engine (`~/Desktop/tkvibes-agency/tkvibes-lead-engine/`, venv: `.venv`)
```bash
.venv/Scripts/python -m src.run --cities "Delhi" --categories "dental clinic"  # scoped run
.venv/Scripts/python -m src.run                                                # full sweep (750 queries — costs money)
.venv/Scripts/python -m src.build_outreach --tier HOT                          # build WhatsApp queue
.venv/Scripts/python -m src.push_wa_links                                      # push MSG+links to sheet
.venv/Scripts/python -m src.scaffold_clients --tier HOT --limit 5              # gen client briefs
.venv/Scripts/python -m src.push_proposals                                     # upload proposals to CRM
```
⚠️ Compliance: outreach is MANUAL via wa.me links — no auto-send (TRAI/DND/WABA rules).

### Marketing engine (`~/Desktop/tkvibes-agency/marketing/`)
```bash
python marketing/engine.py status
python marketing/engine.py plan --template brand_showcase
python marketing/engine.py full --template service_spotlight --service "Website Development"
python marketing/engine.py full --voiceover
```

### CRM (`tkvibes.in/crm/`)
- `index.php` login · `dashboard.php` employee view · `admin.php` admin · `cron.php` hourly cleanup
- API: `POST /crm/api/sync.php` (leads) · `GET /crm/api/employees.php` (mapping)

### GSC (in repo `.hermes/`)
```bash
python .hermes/gsc-helper.py --help   # query search performance for tkvibes.in
```

## ⚠️ Hard Rules
1. **No build step** — never add Next.js/Vite/npm build to the website (Hostinger shared hosting)
2. **Relative paths only** in site HTML (`assets/...`, never `/assets/...`)
3. **`styles.css` must stay UTF-8** (Windows editor pitfalls)
4. **No FTP secrets in repo** — GitHub secrets only
5. **Light theme default** — `localStorage` key `tkvibes-theme`
6. **No auto-send outreach** — always human-reviewed queue (legal compliance)
7. **Lead briefs pin facts** — real ratings/reviews only, no invented prices/awards; "Concept by TKVibes" footer
8. **CRM API key is the only auth** for sync endpoints — keep secret

## 🎯 Business Targets
- **Positioning:** Delhi-based digital agency (websites, brand identity, SEO, Google/Meta ads, automation)
- **ICP:** medical/dental clinics, lawyers, CAs, interior designers, salons, spas, real estate — India (25 cities) + Canada (GTA/BC/Alberta)
- **Win strategy:** businesses with NO website or weak website (score +45), phone/WhatsApp-first outreach, free sample site + pitch deck as proposal
- **Phone/WhatsApp:** +91 98182 46938 · **Email:** services@tkvibes.in
