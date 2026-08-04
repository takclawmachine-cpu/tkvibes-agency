# TKVibes AI CRM — Complete Architecture Audit

**Audit Date:** 2026-08-04
**Auditor:** Principal AI Architect
**Platform:** Hostinger shared hosting (PHP 8.x) + Local Windows (Python 3.11)
**Stack:** PHP 8.x, SQLite/MySQL, Python 3.11, Google Places API, Google Sheets API, GitHub Pages

---

## Table of Contents

1. [Current Architecture Overview](#1-current-architecture-overview)
2. [Database Schema & Issues](#2-database-schema--issues)
3. [Component-by-Component Audit](#3-component-by-component-audit)
4. [Complete API Surface](#4-complete-api-surface)
5. [Data Flow Analysis](#5-data-flow-analysis)
6. [AI Workflow Audit](#6-ai-workflow-audit)
7. [Issues Catalog (48 issues)](#7-issues-catalog-48-issues)
8. [Root Cause Analysis](#8-root-cause-analysis)
9. [Refactoring Plan](#9-refactoring-plan)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Current Architecture Overview

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LEAD GENERATION ENGINE                           │
│  Python 3.11 - tkvibes-lead-engine/src/                              │
│                                                                      │
│  config.yaml → discover_all() [Google Places API]                    │
│                        ↓                                             │
│  process_leads(): enrich() → score_lead() → dedupe() → apply_dnc()   │
│                        ↓                                             │
│  apply_crm_fields(): region/country → pain_points → assign_employees │
│                        ↓                                             │
│  ┌──────────────┬──────────────────┬──────────────────┐              │
│  ▼              ▼                  ▼                  ▼              │
│ Sheets      leads_export.json   CRM sync.php      Proposal Gen     │
│ (gspread)    (file handoff)     (HTTP POST)       (template fill)  │
│                                                      │              │
│                                          ┌───────────┴──────────┐   │
│                                          ▼                      ▼   │
│                                     data/proposals/        GitHub   │
│                                     <slug>/index.html    raw URLs   │
│                                     <slug>/pitch-deck.html          │
│                                                                      │
│ ┌────────────────────────────────────────────────────────────┐       │
│ │                   BIDIRECTIONAL SHEET SYNC                   │       │
│ │   Engine → Sheet (Python gspread)                           │       │
│ │   Sheet → CRM (cron.php + admin.php "Sync from Sheet")     │       │
│ │   CRM → Sheet (leads.php real-time writeback)               │       │
│ └────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         CRM (PHP - sqlite/mysql)                     │
│                                                                      │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐         │
│  │ index.php │  │dashboard  │  │ admin.php │  │ cron.php │         │
│  │ (login)   │  │.php       │  │           │  │ (5 jobs) │         │
│  └───────────┘  └─────┬─────┘  └─────┬─────┘  └──────────┘         │
│                       │              │                              │
│              ┌────────▼────────┐     │                              │
│              │ templates/      │     │                              │
│              │ lead_detail.php │     │                              │
│              └─────────────────┘     │                              │
│                                      ▼                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     API ENDPOINTS                             │   │
│  │  sync.php  │  leads.php  │  proposals.php  │  employees.php  │   │
│  │  u2.php    │  u3.php     │  public_         │  proxy_         │   │
│  │            │             │  proposals.php   │  proposal.php   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  DB TABLES: employees | employee_regions | leads | lead_activities  │
│             proposals | proposal_generation_jobs                     │
│                                                                      │
│  EXTERNAL: Google Sheets (read + write) via custom JWT auth          │
└─────────────────────────────────────────────────────────────────────┘
```

### File Inventory (by layer)

**Lead Engine (Python) — 33 source files:**
- `src/run.py` — Main discovery pipeline orchestrator
- `src/run_business_job.py` — Full business flow orchestrator (NO `--lead-key` support)
- `src/generate_proposals.py` — Template-based site + deck generation (560 lines)
- `src/git_publish.py` — GitHub commit/push + CRM URL update
- `src/push_crm.py` — POST leads to CRM sync.php (39 lines, simple)
- `src/push_proposals.py` — POST HTML to CRM proposals.php (218 lines)
- `src/assign.py` — Employee assignment logic (127 lines)
- `src/score.py` — Lead scoring (44 lines)
- `src/models.py` — Lead dataclass + SCHEMA (110 lines)
- `src/sheets.py` — Google Sheets writer via gspread (104 lines)
- `src/config.py` — YAML config loader (74 lines)
- `src/dedupe.py` — Dedup + DNC filter
- `src/pain_points.py` — Per-category pitch templates
- `src/visuals.py` — Category→color/icon/services (30+ categories)
- `src/competitor_research.py` — Google Places competitor search
- `src/gtmetrix_check.py` — Website performance analysis
- `src/log_config.py` — Centralised logging (54 lines)
- `src/email_finder.py`, `src/email_search.py` — Email crawling
- `src/regions.py` — City→region/country mapping
- `src/scaffold_clients.py` — Client brief generator
- `src/build_outreach.py`, `src/push_wa_links.py` — WhatsApp outreach
- `src/connectors/google_places.py` — Places API client
- `src/connectors/indiamart.py`, `src/connectors/justdial.py` — (disabled)

**CRM (PHP) — 23 files:**
- `crm/index.php` — Login page
- `crm/dashboard.php` — Employee dashboard (162 lines)
- `crm/admin.php` — Admin dashboard (648 lines)
- `crm/cron.php` — 5 cron tasks (183 lines)
- `crm/templates/lead_detail.php` — Lead detail view (244 lines)
- `crm/api/sync.php` — Lead upsert endpoint (166 lines)
- `crm/api/leads.php` — Lead actions: tag/note/call/update (155 lines)
- `crm/api/proposals.php` — Proposal CRUD + job queue (361 lines)
- `crm/api/employees.php` — Employee→region/country mapping
- `crm/api/u2.php`, `u3.php` — File upload (no auth, base64, mod_security bypass)
- `crm/lib/db.php` — PDO + schema auto-creation (262 lines)
- `crm/lib/auth.php` — Session auth (87 lines)
- `crm/lib/functions.php` — Helpers (280 lines)
- `crm/lib/GoogleSheetsClient.php` — Custom JWT client (239 lines)
- `crm/lib/sheets_sync.php` — Write-back helper (52 lines)

**Other:**
- `upload_proposals.py` — Upload to Hostinger via u2.php (39 lines)

---

## 2. Database Schema & Issues

### Current Tables (auto-created in init_schema())

#### `employees`
| Column | Type | Issues |
|--------|------|--------|
| id | INTEGER PK AUTO | ✅ |
| name | TEXT NOT NULL | ✅ |
| email | TEXT NOT NULL UNIQUE | ✅ |
| password | TEXT NOT NULL | **⚠️ No password rotation policy** |
| role | TEXT NOT NULL DEFAULT 'employee' | MySQL uses ENUM, SQLite uses TEXT — inconsistency |
| active | INTEGER NOT NULL DEFAULT 1 | ✅ |
| created_at | TEXT DEFAULT datetime('now') | ✅ |
| updated_at | TEXT DEFAULT datetime('now') | ✅ |

#### `employee_regions`
| Column | Type | Issues |
|--------|------|--------|
| id | INTEGER PK AUTO | ✅ |
| employee_id | INTEGER FK → employees CASCADE | **⚠️ No index on employee_id** |
| region | TEXT NOT NULL | ✅ |
| country | TEXT NOT NULL DEFAULT 'India' | ✅ |
| UNIQUE(employee_id, region, country) | ✅ |

#### `leads` (BIGGEST PROBLEM TABLE — 35+ columns)
| Column | Type | Issues |
|--------|------|--------|
| lead_key | TEXT PRIMARY KEY | ✅ |
| business_name | TEXT NOT NULL DEFAULT '' | ✅ |
| category | TEXT NOT NULL DEFAULT '' | ✅ |
| owner_name | TEXT NOT NULL DEFAULT '' | ✅ |
| phone_primary | TEXT NOT NULL DEFAULT '' | ✅ |
| phone_secondary | TEXT NOT NULL DEFAULT '' | ✅ |
| whatsapp | TEXT NOT NULL DEFAULT '' | ✅ |
| email | TEXT NOT NULL DEFAULT '' | ✅ |
| address | TEXT NOT NULL DEFAULT '' | ✅ |
| city | TEXT NOT NULL DEFAULT '' | ✅ |
| pincode | TEXT NOT NULL DEFAULT '' | ✅ |
| latitude | REAL | ✅ |
| longitude | REAL | ✅ |
| opening_hours | TEXT NOT NULL DEFAULT '' | ✅ |
| has_website | INTEGER NOT NULL DEFAULT 0 | ✅ |
| website_url | TEXT NOT NULL DEFAULT '' | ✅ |
| website_quality | TEXT NOT NULL DEFAULT 'none' | ✅ |
| rating | REAL | ✅ |
| review_count | INTEGER | ✅ |
| years_in_business | TEXT NOT NULL DEFAULT '' | ✅ |
| socials | TEXT NOT NULL DEFAULT '' | ✅ |
| source | TEXT NOT NULL DEFAULT '' | ✅ |
| source_url | TEXT NOT NULL DEFAULT '' | ✅ |
| place_id | TEXT NOT NULL DEFAULT '' | ✅ |
| lead_score | INTEGER NOT NULL DEFAULT 0 | ✅ |
| lead_tier | TEXT NOT NULL DEFAULT 'COLD' | **⚠️ No ENUM constraint in SQLite** |
| data_fetched_at | TEXT NOT NULL DEFAULT '' | ✅ |
| stale_after | TEXT NOT NULL DEFAULT '' | ✅ |
| outreach_status | TEXT NOT NULL DEFAULT 'new' | ✅ |
| opt_out | INTEGER NOT NULL DEFAULT 0 | ✅ |
| sample_site_url | TEXT NOT NULL DEFAULT '' | ✅ |
| pitch_deck_url | TEXT NOT NULL DEFAULT '' | ✅ |
| notes | TEXT NOT NULL DEFAULT '' | ✅ |
| contact_channel | TEXT NOT NULL DEFAULT '' | ✅ |
| wa_link | TEXT NOT NULL DEFAULT '' | ✅ |
| region | TEXT NOT NULL DEFAULT '' | ✅ |
| country | TEXT NOT NULL DEFAULT '' | ✅ |
| assigned_employee | TEXT NOT NULL DEFAULT '' | ✅ |
| pain_points | TEXT NOT NULL DEFAULT '' | ✅ |
| recommended_pitch | TEXT NOT NULL DEFAULT '' | ✅ |
| crm_status | TEXT NOT NULL DEFAULT 'new' | **⚠️ MySQL ENUM(new,qualified,callback,not_qualified)** — SQLite just TEXT |
| crm_notes | TEXT NOT NULL DEFAULT '' | ✅ |
| last_contacted_at | TEXT | ✅ |
| next_callback_at | TEXT | ✅ |
| assigned_employee_id | INTEGER | **⚠️ Duplicate of assigned_employee (name)** |
| removed_at | TEXT | ✅ |
| created_at | TEXT DEFAULT datetime('now') | ✅ |
| updated_at | TEXT DEFAULT datetime('now') | ✅ |

**Indexes:** 4 (region, crm_status, assigned_employee_id, removed_at)
**Missing indexes:** city, country, lead_tier, phone_primary, category — all frequently filtered

#### `lead_activities`
| Column | Type | Issues |
|--------|------|--------|
| id | INTEGER PK AUTO | ✅ |
| lead_key | TEXT FK → leads CASCADE | ✅ |
| employee_id | INTEGER FK → employees SET NULL | ✅ |
| action | TEXT NOT NULL | **⚠️ Free text, no ENUM — action values from PHP match() are unvalidated at DB level** |
| old_value | TEXT | ✅ |
| new_value | TEXT | ✅ |
| description | TEXT NOT NULL DEFAULT '' | ✅ |
| created_at | TEXT DEFAULT datetime('now') | ✅ |
| **Missing:** INDEX on created_at for cron cleanup performance |

#### `proposals`
| Column | Type | Issues |
|--------|------|--------|
| id | INTEGER PK AUTO | ✅ |
| lead_key | TEXT FK → leads CASCADE | ✅ |
| type | TEXT NOT NULL | **⚠️ No ENUM constraint (sample_site|pitch_deck)** |
| html | TEXT NOT NULL | **⚠️ Stores FULL HTML in DB — will bloat with proposals** |
| file_name | TEXT NOT NULL DEFAULT '' | ✅ |
| created_at | TEXT DEFAULT datetime('now') | ✅ |
| updated_at | TEXT DEFAULT datetime('now') | ✅ |
| UNIQUE(lead_key, type) | ✅ |

**ISSUE:** `proposals.html` stores full HTML content. For 1000 leads with 2 proposals each, this could be 500MB+ in the DB. Should reference file paths instead.

#### `proposal_generation_jobs`
| Column | Type | Issues |
|--------|------|--------|
| id | INTEGER PK AUTO | ✅ |
| lead_key | TEXT NOT NULL FK → leads CASCADE | ✅ |
| feedback | TEXT NOT NULL DEFAULT '' | ✅ |
| status | TEXT NOT NULL DEFAULT 'pending' | **⚠️ No ENUM constraint — relies on app logic** |
| created_at | TEXT DEFAULT datetime('now') | ✅ |
| updated_at | TEXT DEFAULT datetime('now') | ✅ |

### ⚡ Critical Database Issues

1. **DUPLICATE COLUMN:** `assigned_employee` (TEXT name) AND `assigned_employee_id` (INTEGER FK). Two different systems track assignment — this WILL diverge.

2. **NO UNIQUE CONSTRAINT on phone_primary/email** — same business can appear multiple times if minor address differences exist.

3. **MISSING ENUM CONSTRAINTS** in SQLite — `crm_status`, `lead_tier`, `action` all rely on app-level validation.

4. **MASSIVE WIDE TABLE** — leads has 47+ columns. Violates Single Responsibility Principle for a DB table.

5. **NO CREATED_BY/UPDATED_BY** — no audit trail for who changed what (separate from lead_activities).

6. **proposals.html stores full HTML** — should be stored as files with DB as path reference.

7. **No CASCADE cleanup** — `proposal_generation_jobs` has FK to leads but no auto-cleanup when lead is deleted.

---

## 3. Component-by-Component Audit

### 3.1 Lead Engine (run.py)

**Strengths:**
- Categories-outer loop ensures diverse category coverage
- Per-country targets prevent geographic bias
- Lead dataclass with __post_init__ type coercion
- .get() patterns for config access (guarded)

**Weaknesses:**
- ❌ **No logging integration** — uses `print()` throughout (lines 46, 51, 61, 67, 69, etc.), despite having `log_config.py`
- ❌ **No transaction** on CRM push — if sync.php fails mid-batch, some leads go to sheets but not CRM
- ❌ **email_finder runs synchronously** — blocks the entire pipeline on slow sites (3-5 min delay)
- ❌ `per_country_target = max_leads * 3` — hardcoded multiplier; no config knob
- ❌ `_filter_phone_country()` is a dead pass-through function (kept for signature compatibility)
- ❌ Sheet write and CRM push are NOT transactional — partial failures leave inconsistent state

### 3.2 Business Job Orchestrator (run_business_job.py)

- ❌ **NO `--lead-key` parameter** — orchestration can only discover new leads via Places API, cannot target an existing CRM lead
- ❌ **Sequential execution** — all 4 steps run linearly; if step 2 fails, step 1's work (sheet, CRM) is orphaned
- ❌ **No rollback** — if GitHub publish fails, CRM already has leads with no proposals
- ❌ **Hardcoded VENV_PYTHON path** — `~/Desktop/tkvibes-agency/tkvibes-lead-engine/.venv/Scripts/python.exe`
- ❌ **No status tracking** — no way to know if a job ran partially

### 3.3 Proposal Generator (generate_proposals.py)

- ❌ **Single template (template-v2.html)** — all generated sites look the same, just different {{PLACEHOLDER}} fill
- ❌ **Template placeholder approach** — fragile; uses string replace, breaks if HTML contains `{{...}}` patterns
- ❌ **`render_sample_site()` is 80+ lines** — monolithic function mixing template loading, data prep, post-processing
- ❌ **Pitch deck (generate_pitch_deck) builds inline HTML** — 200+ lines of f-strings; impossible to maintain or theme
- ❌ **No AI generation** — despite being called "AI Website Generator Agent", it's pure template substitution
- ❌ **Competitor research has no retry/fallback** — fails silently with `except Exception`
- ❌ **`_generation_results.json` stores empty `lead_key`** — downstream git_publish can't match → CRM URLs never update
- ❌ **Google Maps API key for competitor search is re-read from env var inside loop** — should be passed from caller

### 3.4 Git Publisher (git_publish.py)

- ❌ **`site_src = result.get("index") or (result.get("index") or "")`** — nonsensical duplicate get
- ❌ **Hardcoded GitHub repo URL** — `raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/...`
- ❌ **No git stash check** — `_run_git(["checkout", "main"])` can fail if there are uncommitted changes
- ❌ **`_push_urls_to_crm` silently skips leads with empty lead_key** — no warning logged
- ❌ **No tag/version on commits** — `chore: auto-publish sample sites + pitch decks [{timestamp}]` is not searchable
- ❌ **CRM URL push uses sync.php** (correct) but the lead_key slug mapping may fail for duplicate business names

### 3.5 CRM — sync.php

- ❌ **MySQL compatibility hack** — lines 57-62 show `INSERT OR IGNORE` SQLite syntax with fallback to `INSERT IGNORE` MySQL with manual `addslashes()` (XSS risk in the slug)
- ❌ **ON CONFLICT SET clause uses `excluded.column_name`** — this was FIXED from the old `:param_name` bug, but the fix is only correct for SQLite. MySQL uses `ON DUPLICATE KEY UPDATE` with `VALUES()` syntax which is deprecated in MySQL 8.0+
- ❌ **No input validation** beyond type checks — no regex validation on phone, email, URL
- ❌ **Error logging is sparse** — single `error_log()` with no context
- ❌ **No duplicate detection** within a single POST batch — if the same lead appears twice, both get processed

### 3.6 CRM — leads.php

- ❌ **Dual auth mode is fragile** — API key mode only activates for `sample_site_url`/`pitch_deck_url` fields. Any other field update from API key silently falls through to `require_auth()` which returns 302 redirect → broken for headless clients
- ❌ **`body_json()` reads php://input once** but `$_POST` read falls through if JSON parse fails — the fallback to `$_POST` on line 34 works ONLY for form-encoded data, not JSON. JSON clients for `update` action will fail silently
- ❌ **SQL injection in column name** — line 82: `"UPDATE leads SET \"$field\" = ?` — $field is from the whitelist, but if the whitelist is bypassed (or a bug allows it), this becomes injection
- ❌ **`sheets_writeback()` is fire-and-forget** — no retry, no queue, no backpressure

### 3.7 CRM — proposals.php

- ❌ **POST creates lead if not exists** — `INSERT OR IGNORE INTO leads` with lead_key as business_name. This creates orphaned lead records with no useful data
- ❌ **Hardcoded GitHub URL construction** — lines 92, 96: hardcoded repo owner/name. Deploying to a different repo breaks everything
- ❌ **Duplicate slug logic** — `$slug = preg_replace(...)` on line 88 duplicates the Python `slugify()` function. If they diverge, URL resolution breaks
- ❌ **`api_complete` marks jobs completed but doesn't update leads** — lead's `sample_site_url`/`pitch_deck_url` is only set by the POST handler slug logic, not by `api_complete`
- ❌ **No rate limiting** — API key endpoints are open to unlimited calls

### 3.8 CRM — cron.php

- ❌ **Cron task #5 marks jobs as 'running' but never handles timeout** — if the Hermes agent crashes, jobs stay 'running' forever (orphaned)
- ❌ **No dedup on sheet sync** — if sheet has duplicate rows for the same lead_key, duplicates are imported
- ❌ **Sheet sync has inconsistent field mapping** — `allowed_fields` in cron.php (line 63) doesn't include `lead_score`, `lead_tier`, `data_fetched_at`, `stale_after`, `opt_out` — these are in admin.php's `allowed_fields` but NOT in cron.php's. Different code paths sync different columns!
- ❌ **Sheet columns `allowed_fields` differ between cron.php and admin.php** — leads to data inconsistency depending on whether sync was triggered by cron or admin button click

### 3.9 CRM — auth.php

- ❌ **Session name hardcoded** — `session_name('TKCRM')` — no prefix support for multi-instance
- ❌ **No session timeout** — no `session.gc_maxlifetime` configuration
- ❌ **No CSRF protection** — all session-authenticated endpoints are vulnerable to CSRF
- ❌ **Password reset prompt is JavaScript `prompt()`** — admin.php line 635: `const pw = prompt(...)` — passwords visible on screen, stored in JS variables

### 3.10 CRM — GoogleSheetsClient.php

- ❌ **No token caching** — gets a fresh JWT on every `get_sheets_client()` call (which is called on EVERY `sheets_writeback()` invocation)
- ❌ **`get_header()` caches but never invalidates** — if sheet structure changes mid-session, stale cache persists
- ❌ **`find_row()` scans column A linearly** — O(n) per lookup, no caching. With 1000+ leads, write-back of N fields becomes O(n*m)
- ❌ **No exponential backoff** — Google API quota errors cause immediate failures
- ❌ **Timeouts are fixed at 10s/30s** — no configurable timeout

### 3.11 Lead Engine — assign.py

- ❌ **`assign_employees()` applies country_assignments FIRST** — but then processes *all* leads (including already-assigned ones) through the unassigned filter. Already-assigned leads are excluded by the `unassigned` list comprehension on line 70 — this works but is confusing.
- ❌ **CRM API fallback employees from config.yaml is loaded but `employees: []` in config** — the fallback is always empty. If CRM API is down, assignment falls through silently.
- ❌ **No logging of assignment failures** — if no match found, lead remains unassigned with no log entry

### 3.12 CRM — u2.php / u3.php

- ❌ **NO AUTHENTICATION** — these endpoints accept ANY POST with `Content-Type: text/plain` and write files to the server filesystem. u2.php writes to `/proposals/`, u3.php writes to `/crm/`. An attacker can overwrite any PHP file on the server.
- ❌ **Path traversal** — if `$body["path"]` is `../../../../etc/passwd`, the server writes to arbitrary locations (mitigated only by `json_decode` with `Content-Type: text/plain` bypass, but still vulnerable)
- ❌ **Designed as convenience, deployed as permanent** — meant for bootstrap but still active

---

## 4. Complete API Surface

### CRM Internal APIs

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/crm/api/sync.php` | POST | API key | Bulk lead upsert from engine |
| `/crm/api/leads.php` | POST | Session/API key | Tag, note, call, field update |
| `/crm/api/proposals.php` | GET/POST | Session/API key | Proposal CRUD + job queue |
| `/crm/api/employees.php` | GET | API key | Employee→region+country mapping |
| `/crm/api/public_proposals.php` | GET | None | Public proposal JSON listing |
| `/crm/api/proxy_proposal.php` | GET | Session | Proxy GitHub raw URLs |
| `/crm/api/upload_proposal.php` | POST | API key | Upload proposal file |
| `/crm/u2.php` | POST | **NONE** | File upload to /proposals/ |
| `/crm/u3.php` | POST | **NONE** | File upload to /crm/ |

### Lead Engine Internal APIs

| Call | Auth | Purpose |
|------|------|---------|
| Google Places API | API key in .env | Business discovery |
| Google Sheets API v4 | JWT service account | Read/write master sheet |
| CRM sync.php (HTTP POST) | Shared API key | Push leads |
| CRM proposals.php (HTTP POST) | Shared API key | Upload proposals |

---

## 5. Data Flow Analysis

### Normal Flow (Success Path)
```
Google Places API → discover_all() → process_leads() → enrich() → score()
→ assign_employees() → export_for_handoff() → SheetWriter.upsert()
→ push_leads() [POST sync.php] → generate_proposals() → git_publish()
→ upload_proposals.py → push_proposals() [POST proposals.php]
```

### Failure Points (by frequency analysis)

1. **Sheet → CRM sync mismatch** — `allowed_fields` lists differ between cron.php and admin.php
2. **Proposal generation → _generation_results.json empty lead_key** — git_publish silently skips leads
3. **CRM proposal upload 403** — mod_security blocks HTML with `<script>` tags (mitigated by u2.php text/plain bypass)
4. **run_business_job has no `--lead-key`** — cannot target specific leads from CRM queue
5. **Competitor research mock fallback** — silently returns empty data when Google Places API key is missing
6. **Git checkouts fail** — uncommitted changes in working directory
7. **Slug mismatch** — `slugify()` in Python vs `preg_replace()` in PHP produce different slugs for edge cases

---

## 6. AI Workflow Audit

### Claimed AI Workflows vs Actual Implementation

| Workflow | Claimed | Actual | Gap |
|----------|---------|--------|-----|
| Website Generator | AI generates unique sites per niche | Template-v2.html with 30 {{PLACEHOLDER}} replacements | **Critical** — No AI at all |
| Pitch Deck Generator | AI analyzes business + creates deck | Hardcoded f-string HTML slides with lead data injection | **Critical** — Template-only |
| Competitor Research | AI finds + analyzes competitors | Google Places API search + formatted HTML | No AI, but functional |
| Website Audit | AI analyzes site performance | URL heuristics + simulated GTmetrix fallback | No AI, but functional |
| Lead Scoring | AI scores lead quality | Point-based algorithm (45+15+5+10+5+5+10) | No AI, but deterministic |
| Pain Points | AI identifies business pain | `pain_points.py` per-category template strings | No AI — static templates |
| Proposal Generation | AI custom-crafts proposals | Template fill + field injection | **Critical** — No AI |

### Determinism Assessment
- All "AI" workflows are actually **deterministic template-based** — no LLM calls, no prompt chaining
- This means they are **reliable** but **not adaptive or unique**
- The website generator produces near-identical sites; only color palette and services text vary

---

## 7. Issues Catalog (48 issues)

### 🔴 CRITICAL (8)

| ID | Component | Issue | Impact |
|----|-----------|-------|--------|
| C1 | u2.php/u3.php | **No authentication, arbitrary file write** | Complete server compromise |
| C2 | leads.php | **SQL injection in column name** — whitelist is the only guard | Data exfiltration/theft |
| C3 | proposals.php POST | **Creates orphan leads** via INSERT OR IGNORE with no business data | Blank lead detail pages (reported by user) |
| C4 | cron.php/admin.php | **Sheet sync field lists differ** | Data inconsistency between sheet and CRM |
| C5 | run_business_job.py | **No --lead-key parameter** | CRM queue jobs never process the right lead |
| C6 | generate_proposals.py | **AI websites are template copies** | Every site looks identical, not custom/per-niche |
| C7 | git_publish.py | **_generation_results.json stores empty lead_key** | Proposal URLs never update in CRM |
| C8 | proposals.php | **Hardcoded GitHub repo URL** | Breaks if repo is renamed or forked |

### 🟠 HIGH (14)

| ID | Component | Issue | Impact |
|----|-----------|-------|--------|
| H1 | All Python | **`print()` everywhere, logging module unused** | No traceability, can't debug failures |
| H2 | leads.php | **$_POST fallback breaks JSON clients** | Update field API fails silently for JSON body clients |
| H3 | cron.php | **proposal jobs stay 'running' on agent crash** | Orphaned jobs block re-generation |
| H4 | assign.py | **Fallback employees config is empty array** | CRM API failure = no employee assignment |
| H5 | run.py | **Sheet + CRM push not transactional** | Partial state on failure |
| H6 | DB Schema | **assigned_employee + assigned_employee_id duplication** | Divergent assignment tracking |
| H7 | GoogleSheetsClient | **No token caching — new JWT per call** | 2+ extra HTTP calls per write-back |
| H8 | auth.php | **No CSRF protection on any endpoint** | Cross-site request forgery |
| H9 | generate_proposals.py | **`render_sample_site()` 80-line monolith** | Unmaintainable, fragile |
| H10 | DB Schema | **proposals.html stores full HTML** | DB bloat with hundreds of proposals |
| H11 | dashboard.php | **All leads loaded in one query** | Will crash on 10K+ leads |
| H12 | push_proposals.py | **`find_proposal_files()` searches 5+ filesystem locations** | Slow, uses stale paths |
| H13 | upload_proposals.py | **No authentication on upload endpoint** | Anyone can upload to server |
| H14 | sheets.py | **No row-level locking** | Concurrent engine+cron writes can conflict |

### 🟡 MEDIUM (18)

| ID | Component | Issue |
|----|-----------|-------|
| M1 | score.py | No coverage for `lead_score` None case (fallback at 83-84 has try/except) |
| M2 | config.py | `_check_secrets_in_config()` only checks `crm.api_key` — misses other secrets |
| M3 | generate_proposals.py | Unused import `sys` on line 19 |
| M4 | generate_proposals.py | `_name_short()` can produce single-word names for 2-word businesses |
| M5 | git_publish.py | `site_src = result.get("index") or (result.get("index") or "")` — dead code |
| M6 | cron.php | Cron task #5 marks jobs running but doesn't start any generation |
| M7 | DB Schema | lead_activities has no cascade delete on employee_id SET NULL — could strand orphan employee references |
| M8 | functions.php | `log_activity()` accepts action as free string — no validation |
| M9 | sheets.py | `_lead_from_row()` silently drops extra sheet columns beyond SCHEMA |
| M10 | proposals.php | Duplicate `slugify()` logic — Python and PHP implementations may differ |
| M11 | admin.php | Export CSV includes `$l['crm_notes']` which could contain unescaped newlines breaking CSV format |
| M12 | leads.php | `sheets_writeback()` called for every field update — if lead has 10 fields, 10 sheets API calls |
| M13 | Generate proposals | Template-v2.html is 2000+ lines — hard to edit |
| M14 | Generate proposals | No fallback images — just placeholder text when no Unsplash image loads |
| M15 | run_business_job | VENV_PYTHON path uses hardcoded `.exe` — fails on Linux |
| M16 | sync.php | `rowCount()` unreliable for UPDATE queries in some MySQL/SQLite drivers |
| M17 | Proposal queue | Feedback modal (feedback feature) is stored but never used by processor |
| M18 | GoogleSheetsClient | `base64url_encode()` is a global function — namespace pollution |

### 🟢 LOW (8)

| ID | Component | Issue |
|----|-----------|-------|
| L1 | run.py | `_filter_phone_country()` is dead code — always returns input unchanged |
| L2 | score.py | Comment says "no website = +45" but hardcoded value could be configurable |
| L3 | auth.php | Session cookie doesn't set `SameSite` or `Secure` flags |
| L4 | admin.php | Password reset via `prompt()` is visible on screen |
| L5 | lead_detail.php | Sample site deck URLs use `//raw.githubusercontent.com` — no local fallback proxy |
| L6 | run.py | `per_country_target` hardcoded as `max_leads * 3` |
| L7 | config.py | `REQUIRED_CONFIG_KEYS` doesn't validate nested types |
| L8 | all PHP | `header('X-Robots-Tag: noindex, nofollow')` repeated in every file — should be centralized |

---

## 8. Root Cause Analysis

### Root Cause #1: No Centralized Architecture
The system evolved organically — Python lead engine, PHP CRM, template-based website generator, all loosely connected by HTTP calls and file handoffs. Each component was built to solve an immediate need, not as part of a designed system.

**Evidence:**
- 3 different data stores (SQLite, Google Sheets, JSON files) with no source of truth
- 4 different "lead_key" → slug resolution paths that can diverge
- No shared configuration schema
- No state machine or workflow engine

### Root Cause #2: Template-Only "AI"
The website generator was marketed/designed as AI-powered but is actually a string template with 30 `{{PLACEHOLDER}}` variables. This explains:
- "Every site looks the same" — same template, different colors
- "No unique layouts" — only 1 template
- "Copywriting is repetitive" — static descriptions

### Root Cause #3: No Error Handling Architecture
Errors are handled ad-hoc:
- Python: bare `print()` everywhere, generic `except Exception: pass`
- PHP: `try/catch` with `error_log()` (sparse context), no structured error response format
- No centralized error tracking
- No retry/backoff strategy on external API calls (except tenacity on 3 Python modules)

### Root Cause #4: No State Management
- Lead processing has no state machine — can't tell if a lead is "discovered but not enriched" vs "enriched but not pushed to CRM"
- Proposal generation jobs have status but no timeout/cleanup
- No idempotency keys — duplicate webhook calls create duplicate leads
- Cron jobs run without locking — concurrent executions collide

### Root Cause #5: Security by Convenience
- u2.php/u3.php have no auth — "convenient for deployment"
- API key stored in config.yaml alongside config (gitignored, but still)
- No rate limiting on any API endpoint
- No request logging on write operations
- `addslashes()` used instead of prepared statements in one code path

---

## 9. Refactoring Plan

### Phase A: Security Hardening (Day 1-2)

1. **🔴 Remove or secure u2.php/u3.php** — add basic auth (static token) or disable after bootstrap
2. **🔴 Fix SQL injection vector in leads.php** — add defensive check even within whitelist
3. **Add CSRF tokens** to all state-changing session-authenticated endpoints
4. **Add rate limiting** to all API endpoints (50 req/min per IP for API-key endpoints)
5. **Add SameSite=Strict + Secure + HttpOnly** to session cookies
6. **Remove hardcoded secrets from config.yaml** — move API key to .env only
7. **Add path traversal guard** to u2.php/u3.php file writes

### Phase B: Database Consolidation (Day 2-3)

1. **Normalize `leads` table** — split into `leads` (core identity: lead_key, name, phone, email, address) and `lead_extras` (scores, URLs, notes, CRM state)
2. **Add indexes** on: `city`, `country`, `lead_tier`, `phone_primary`, `category`
3. **Add UNIQUE constraint** on `phone_primary + country` (business uniqueness)
4. **Drop `assigned_employee_id`** — consolidate to `assigned_employee` only
5. **Add ENUM/tables** for: `crm_status`, `lead_tier`, `action` constants
6. **Move `proposals.html` to file storage** — store path only in DB
7. **Add CASCADE + cleanup triggers** for proposal_generation_jobs on lead deletion

### Phase C: Unified Data Pipeline (Day 3-5)

1. **Add `--lead-key` to `run_business_job.py`** — skip discovery, use existing leads_export.json
2. **Standardize `allowed_fields`** — single source of truth in config or a shared constant
3. **Add transaction/rollback** for sheet+CRM writes
4. **Add idempotency key** to sync.php — reject duplicate POSTs within 5 minutes
5. **Add locking to cron.php** — file-based lock to prevent concurrent execution
6. **Fix `_generation_results.json`** — ensure lead_key is always populated

### Phase D: Real AI Website Generator (Day 5-10)

1. **Replace template-v2.html with actual AI generation** — use an LLM to generate unique HTML per lead
2. **Build prompt pipeline:** business niche → layout selection → color palette → section generation
3. **Add AI prompt for unique copywriting** — generate description, tagline, service descriptions per business
4. **Implement section diversity** — randomly select from 5+ section layout patterns
5. **Add AI-driven competitor gap analysis** in website copy
6. **Generate JSON schema for site structure** — then render to HTML via templates

### Phase E: Logging & Observability (Day 8-10)

1. **Replace all `print()` with structured logging** in Python lead engine
2. **Add structured JSON logging to PHP** — custom error handler with context
3. **Create centralized activity log API** — separate from lead_activities
4. **Add timing/logging to every workflow step** — start, running, waiting, retrying, completed, failed
5. **Create dashboard for workflow failures** — admin tab showing recent errors

### Phase F: Reliability & Queueing (Day 10-14)

1. **Implement proper job queue for proposal generation** — worker pool with timeout/retry
2. **Add heartbeat to 'running' jobs** — Hermes agent updates `heartbeat_at` every 30s; if missing >5min, job resets to 'pending'
3. **Add exponential backoff to sheets_writeback** — retry up to 3 times with delay
4. **Add background worker for email_finder** — decouple from main pipeline
5. **Add crash recovery to cron.php** — on startup, reset 'running' proposal jobs back to 'pending'

### Phase G: Architectural Cleanup (Day 14-20)

1. **Introduce service layer in PHP CRM** — separate business logic from HTTP handlers
2. **Introduce repository pattern for DB access** — single query interface
3. **Create shared constants file** for both Python and PHP (lead statuses, tiers, etc.)
4. **Standardize error response format** across all APIs: `{"status": "error", "code": "...", "message": "..."}`
5. **Add proper migration system** — versioned schema changes (currently everything is auto-create)
6. **Replace `addslashes()` with prepared statements everywhere** — verify all paths

---

## 10. Implementation Roadmap

```
Week 1: SECURITY + DATABASE
  Day 1:  🔴 C1 (secure u2/u3), C2 (SQL injection fix), H8 (CSRF)
  Day 2:  🔴 C4 (unify sheet fields), H6/H10 (DB normalization)
  Day 3:  H7 (JWT caching), H3 (job heartbeat/cleanup)

Week 2: PIPELINE FIXES
  Day 4:  🔴 C5 (--lead-key on run_business_job), C7 (fix generation results)
  Day 5:  H1 (structured logging everywhere)
  Day 6:  H2 (JSON body fix), H5 (transactional writes), H4 (assignment fallback)

Week 3: AI WEBSITE GENERATOR
  Day 7-8:  Build AI prompt pipeline for unique website generation
  Day 9:    Implement layout diversity + dynamic section selection
  Day 10:   Integrate with proposal pipeline, replace template-v2

Week 4: OBSERVABILITY + RELIABILITY
  Day 11:  Centralized logging + error tracking
  Day 12:  Job queue with timeout/retry for proposal generation
  Day 13:  Crash recovery + concurrency protection
  Day 14:  Testing + verification

Week 5: ARCHITECTURE CLEANUP
  Day 15-16: Refactor CRM into service layer + repository pattern
  Day 17-18: Migration system + API standardization
  Day 19-20: Final testing, documentation, deployment
```

---

## Summary

The TKVibes AI CRM platform has **48 identified issues** (8 critical, 14 high, 18 medium, 8 low).

**Most critical action:** Secure u2.php/u3.php (C1) — an unauthenticated file write endpoint on the public internet is an existential risk.

**Most impactful architectural change:** Replace the template-based "AI" website generator with actual AI generation (C6) — this is the core value proposition and currently does not deliver it.

**Most common failure pattern:** Data inconsistency between the three storage systems (sheets, SQLite, JSON files) caused by differing field lists, missing keys, and non-transactional writes.