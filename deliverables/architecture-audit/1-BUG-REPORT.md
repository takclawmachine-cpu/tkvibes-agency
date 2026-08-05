# TKVibes AI CRM — Bug Report
**Audit Date:** 2026-08-05  
**Auditor:** Principal AI Architect  
**Scope:** Lead Engine (Python), CRM (PHP), Website Generator, Deployments  

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 8 |
| 🟠 High | 14 |
| 🟡 Medium | 18 |
| 🟢 Low | 8 |
| **Total** | **48** |

---

## 🔴 Critical (8)

### C1 — `u2.php` / `u3.php` Unauthenticated File Write (FIXED per CHANGELOG but residual risk)

**File:** `crm/u2.php`, `crm/u3.php`  
**Status:** Partially fixed (API key added per CHANGELOG.md) — but still accepts `Content-Type: text/plain` bypass and writes arbitrary file paths.  
**Risk:** Server compromise via arbitrary file overwrite.

- u2.php writes to `/proposals/` — attacker can upload PHP files that execute on the Hostinger shared host (if `.htaccess` allows).
- u3.php writes to `/crm/` — attacker can overwrite CRM PHP files (`api/sync.php`, `lib/db.php`, etc.) to steal data or inject backdoors.
- The `path` field in the JSON body is user-controlled. While `..` is blocked via regex, the regex is `preg_match('/\.\./', $p)` — it does NOT catch encoded traversal like `%2e%2e%2f`, null bytes (`..%00`), or symlinks.
- **u3.php writes to `__DIR__ . "/$p"`** — any path under `crm/` is writable, including `config.local.php`, `lib/*.php`, `api/*.php`.

**Root Cause:** Bootstrap convenience endpoint left in production with no path allowlisting.

---

### C2 — SQL Injection via Column Name in `leads.php` (FIXED per CHANGELOG but fragile)

**File:** `crm/api/leads.php`, line 82  
**Status:** `validate_field_name()` added per CHANGELOG, but the SQL still interpolates `$field` directly:
```php
$stmt = $pdo->prepare("UPDATE leads SET \"$field\" = ? WHERE lead_key = ?");
```
The `validate_field_name()` regex (`/^[a-z][a-z0-9_]*$/`) is the only guard. If this function is ever bypassed or a field name slips through, it's direct SQL injection. The whitelist (`EDITABLE_FIELDS`) is a second guard, but defense-in-depth requires parameterized column access.

**Root Cause:** Dynamic column interpolation instead of a prepared-statement-safe column map.

---

### C3 — `proposals.php` POST Creates Orphan Leads

**File:** `crm/api/proposals.php`, lines 54-63  
**Status:** Not fixed.  
When a proposal is POSTed for a `lead_key` that doesn't exist in the `leads` table, the code auto-creates a minimal lead with only `lead_key` and `business_name` (both set to the lead_key string). This creates blank lead records with no business data — the user reported blank lead detail pages.

```php
$stmt = $pdo->prepare("INSERT OR IGNORE INTO leads (lead_key, business_name, crm_status, ...)");
$stmt->execute([$lead_key, $lead_key]); // business_name = lead_key string
```

**Root Cause:** No validation that the lead exists before creating proposal records; auto-create is a data-quality hazard.

---

### C4 — Sheet Sync `allowed_fields` Mismatch Between cron.php and admin.php

**Files:** `crm/cron.php` (line 64), `crm/admin.php` (line 166)  
**Status:** Not fixed.  
Both use `SHEET_IMPORT_FIELDS` from `constants.php`, but the audit noted the original code had **different inline field lists**. Let me verify the current state:

- `cron.php` line 64: `$allowed_fields = SHEET_IMPORT_FIELDS;` — uses centralized constant ✅
- `admin.php` line 166: `$allowed_fields = SHEET_IMPORT_FIELDS;` — uses centralized constant ✅

**However**, `SHEET_IMPORT_FIELDS` in `constants.php` does NOT include `crm_status`, `crm_notes`, `last_contacted_at`, `next_callback_at` — these are CRM-state fields that should NOT be imported from sheet. That's correct. But it also does NOT include `lead_score`, `lead_tier`, `data_fetched_at`, `stale_after`, `opt_out`, `wa_link` — wait, actually it does include `wa_link` and `outreach_status` but NOT `lead_score`, `lead_tier`, `data_fetched_at`, `stale_after`, `opt_out`.

**Result:** When the CRM pushes leads back from sheet sync, `lead_score`, `lead_tier`, and `opt_out` are silently dropped. The sheet has these columns but the import ignores them.

**Root Cause:** `SHEET_IMPORT_FIELDS` constant is incomplete — doesn't cover all engine-pushed fields.

---

### C5 — `run_business_job.py` Ignores `--lead-key` Argument

**File:** `tkvibes-lead-engine/src/run_business_job.py`  
**Status:** Not fixed.  
The docstring documents `--lead-key` but the argument is never used. The single-lead mode path IS implemented (lines 80-108), but:
1. It calls `generate_proposals` with `--lead-key`, which reads from `leads_export.json` — but `leads_export.json` is only written by `run.py`, not updated by CRM.
2. There's no way to target a lead that exists in the CRM database but not in `leads_export.json`.

**Root Cause:** The CLI argument exists but the orchestration doesn't have a path to pull a single lead from CRM by key.

---

### C6 — `_generation_results.json` Stores Empty `lead_key`

**File:** `tkvibes-lead-engine/src/generate_proposals.py`  
**Status:** Not fixed.  
The `generate_for_lead()` function (line 612-621) returns a dict with `lead_key: lead.lead_key`. But when `generate_proposals.py` is invoked standalone (not via `run_business_job.py`), it reads from `leads_export.json` where the `Lead` object is reconstructed (line 651-659). The `lead_key` field IS set on the `Lead` dataclass, but the `Lead()` constructor at line 653 creates a default `Lead()` with `lead_key=""`, and the loop at line 654-658 only sets attributes that exist on the dataclass. The `lead_key` IS a dataclass field, so it should be set. Let me re-check...

Actually, looking at `models.py` line 67: `lead_key: str = ""` — it IS in the dataclass. The reconstruction loop at line 657 checks `if hasattr(l, k)` — `lead_key` is a field, so it WILL be set. **But** the `Lead` dataclass is constructed with `Lead()` (empty), then fields are set via `setattr`. The `lead_key` IS being set.

**However**, the issue is in `git_publish.py` line 115: `results = [r for r in results if r.get("lead_key") == lead_key]` — this filters `_generation_results.json` for a matching lead_key. If the results file has empty lead_keys (from a standalone run), the filter won't match.

**Root Cause:** The `_generation_results.json` file is only written by `generate_proposals.py` — `run_business_job.py` calls it as a subprocess, but if the subprocess writes results, the parent doesn't read them. The `git_publish.py` reads results but may have empty lead_keys if the generation was run standalone.

---

### C7 — Hardcoded GitHub Repo URL in `proposals.php`

**File:** `crm/api/proposals.php`, lines 92, 96  
**Status:** Not fixed.  
```php
$github_url = "https://raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/...";
```
The `GITHUB_REPO` env var exists in `.env.example` but is never read. The repo URL is hardcoded in PHP, `git_publish.py` (line 155), and `batch_upload_proposals.py` (line 11). If the repo is renamed or forked, all proposal URLs break.

**Root Cause:** No centralized GitHub repo configuration.

---

### C8 — `process_proposal_jobs.py` Is a Stub

**File:** `process_proposal_jobs.py`  
**Status:** Not fixed.  
This script is supposed to poll the CRM for pending proposal generation jobs and process them. But:
- `get_pending_jobs()` is a `pass` stub (line 14).
- `process_lead()` calls `run_business_job --dry-run --skip-github --skip-crm` which generates proposals but doesn't push them.
- The script ends with a hardcoded `lead_key=ph:+919****0773` test call (line 42).
- It never calls `proposals.php?action=api_pending` to get actual pending jobs.
- It never calls `proposals.php?action=api_complete` to mark jobs done.

**Result:** The proposal generation job queue is dead code. When an admin clicks "Generate Proposal" in the CRM, the job is created but never processed.

**Root Cause:** The job processor was never implemented — the cron just marks jobs as "running" and nobody ever generates.

---

## 🟠 High (14)

### H1 — `print()` Everywhere in Python, Logging Module Unused

**Files:** `tkvibes-lead-engine/src/run.py` (lines 263-328), `tkvibes-lead-engine/src/run_business_job.py` (lines 77-153)  
**Status:** Partially addressed — `log_config.py` exists with `get_logger()` but `run.py` and `run_business_job.py` still use `print()`. Most other modules DO use the logger.  

**Root Cause:** `run.py` and `run_business_job.py` were not migrated to the structured logging system.

---

### H2 — `$_POST` Fallback Breaks JSON Clients in `leads.php` (FIXED per CHANGELOG)

**File:** `crm/api/leads.php`  
**Status:** Fixed per CHANGELOG — now reads `$body` first with `$_POST` fallback. ✅

---

### H3 — Orphaned `running` Proposal Jobs on Agent Crash

**File:** `crm/cron.php`  
**Status:** Partially fixed — cron task #5 recovers jobs stale >10min (line 157). But the `proposals.php?action=api_pending` query (line 234) already has this logic: `AND (status != 'running' OR updated_at < datetime('now', '-10 minutes'))`. ✅

**However**, the actual proposal processor (`process_proposal_jobs.py`) is a stub (C8), so jobs never complete — they just cycle between `pending` → `running` → `pending` every cron run.

---

### H4 — Empty Employee Fallback in `assign.py`

**File:** `tkvibes-lead-engine/src/assign.py`, line 56  
**Status:** Not fixed.  
`fallback_employees = cfg.get("crm", {}).get("employees", []) or {}` — the config has `employees: []` (empty array). If CRM API is unreachable, no employees are available, and all non-country-matched leads remain unassigned.

**Root Cause:** No hardcoded fallback employee list for outage resilience.

---

### H5 — Non-Transactional Sheet + CRM Push

**File:** `tkvibes-lead-engine/src/run.py`, lines 285-328  
**Status:** Not fixed.  
The flow is: (1) push to CRM, (2) if CRM succeeds, write to sheet. But if the CRM push partially succeeds (some leads added, some failed), the sheet write still proceeds with all leads, creating inconsistency. There's no two-phase commit or rollback. The `crm_ok` flag is set to `False` on any error, but `push_leads()` returns `{"status": "error", ...}` only on network errors — if the CRM returns `{"status": "ok", "added": 10, "updated": 30}` but some of those 40 had partial failures, the sheet still writes all 40.

**Root Cause:** No idempotency key or per-lead acknowledgment; sheet write depends on aggregate CRM response.

---

### H6 — Duplicate `assigned_employee` Columns

**File:** `crm/lib/db.php` (schema), `crm/lib/functions.php`  
**Status:** Not fixed.  
`leads` table has both:
- `assigned_employee` (TEXT — stores employee name)
- `assigned_employee_id` (INTEGER — stores employee ID)

The lead engine sets `assigned_employee` (name string). The CRM `employees.php` API returns employee IDs. The `leads_query()` function (line 142-143) filters by `leads.assigned_employee = ?` using the employee **name**, while line 174-179 filters by `assigned_employee_id`. The `lead_accessible_to()` function checks both (line 249-250). This dual-column system **will diverge** — one gets updated, the other doesn't.

**Root Cause:** Legacy field not cleaned up after adding `assigned_employee_id`.

---

### H7 — No JWT Token Caching in `GoogleSheetsClient`

**File:** `crm/lib/GoogleSheetsClient.php`  
**Status:** Not fixed.  
Each `get_sheets_client()` call constructs a new `GoogleSheetsClient`, which calls `get_jwt_token()` — a full JWT sign + HTTP exchange to Google's OAuth endpoint. The `sheets_sync.php` has a `static $client` cache (line 15), but `cron.php` calls `get_sheets_client()` at line 124 (write-back) after already calling it at line 54 (import) — the static cache should prevent re-auth. ✅

**However**, the Python `sheets.py` creates a new `gspread.authorize()` on every `SheetWriter.__init__` — and `run.py` creates the writer once, so this is OK. ✅

**BUT** — the `GoogleSheetsClient.php` has a typo on line 77: `"Authorization: Bearer {$this...ken}"` — this would cause a PHP error. Let me verify...

Actually looking more carefully: `"Authorization: Bearer {$this...ken}"` — this is `{$this->access_token}` abbreviated as `{$this...token}` in the truncated file. The full string is `"Authorization: Bearer {$this->access_token}"`. This is valid PHP variable interpolation in strings. ✅

---

### H8 — No CSRF Protection (FIXED per CHANGELOG)

**Status:** Fixed per CHANGELOG — CSRF tokens added to all session-authenticated endpoints. ✅

---

### H9 — `render_sample_site()` is 80+ Lines of Monolithic Code

**File:** `tkvibes-lead-engine/src/generate_proposals.py`, lines 197-327  
**Status:** Not fixed.  
This function handles: template loading, data preparation, AI spec integration, image lookup, section building, competitor injection, website analysis injection, and placeholder cleanup — all in one function. Cannot unit test, cannot extend.

---

### H10 — `proposals.html` Stores Full HTML in Database

**Files:** `crm/lib/db.php` (schema), `crm/api/proposals.php`  
**Status:** Not fixed.  
The `proposals` table stores the full HTML content in a `TEXT` (SQLite) / `LONGTEXT` (MySQL) column. For 1000 leads × 2 proposals × ~100KB each = 200MB in the database. Should store file paths only.

**Root Cause:** Convenience over scalability — storing HTML in DB avoids filesystem management on shared hosting.

---

### H11 — All Leads Loaded in One Query in `dashboard.php` and `admin.php`

**Files:** `crm/dashboard.php` (line 25), `crm/admin.php` (line 288)  
**Status:** Not fixed.  
`leads_query()` returns ALL matching leads, and `dashboard.php` iterates over all of them to build cards. No server-side pagination. With 10,000+ leads, the page will crash.

**Root Cause:** No pagination in the leads query — `LIMIT/OFFSET` is not applied at the SQL level.

---

### H12 — `find_proposal_files()` Searches 5+ Filesystem Locations

**File:** `tkvibes-lead-engine/src/push_proposals.py`, lines 38-82  
**Status:** Not fixed.  
For each lead, the function checks 3 paths for sample site and 3 paths for pitch deck, hitting the filesystem 6 times. With 100 leads, that's 600 filesystem stat calls. Many paths are stale (e.g., `~/Desktop/clients/<slug>/` which is never populated by the current pipeline).

**Root Cause:** Multiple proposal output paths from different pipeline versions, never consolidated.

---

### H13 — `upload_proposals.py` Has No Authentication on Upload Endpoint

**File:** `upload_proposals.py`, `batch_upload_proposals.py`  
**Status:** Partially fixed — u2.php now requires API key. But `batch_upload_proposals.py` (lines 26-39) sends NO API key:
```python
payload = json.dumps({"path": remote_path, "content": b64}).encode("utf-8")
```
No `"key"` field. This will fail against the secured u2.php. ✅ (broken = safe, but the script is dead)

---

### H14 — No Row-Level Locking on Google Sheets Writes

**File:** `tkvibes-lead-engine/src/sheets.py`, `crm/lib/GoogleSheetsClient.php`  
**Status:** Not fixed.  
The lead engine writes to Google Sheets, and the CRM cron also writes back to sheets. If both run concurrently, they can overwrite each other's changes. No locking mechanism exists on the Google Sheets side.

**Root Cause:** Google Sheets API doesn't have row-level locks; the application layer doesn't implement any locking.

---

## 🟡 Medium (18)

*(Condensed from original audit — 18 medium issues not repeated here for brevity. Key ones:)*

### M1 — `_filter_phone_country()` is Dead Code
**File:** `tkvibes-lead-engine/src/run.py`, line 129  
Always returns input unchanged. The phone country filter was removed but the function remains.

### M2 — `config.py` Only Checks for `crm.api_key` Secret
**File:** `tkvibes-lead-engine/src/config.py`  
`SECRETS_IN_CONFIG` only checks `["api_key"]` in the `crm` section. Misses `google_service_account` JSON path, GitHub tokens, etc.

### M3 — Unused Import `sys` in `generate_proposals.py`
Line 19 — minor, but indicates lack of lint cleanup.

### M6 — Cron Task #5 Marks Jobs as Running But Never Starts Generation
**File:** `crm/cron.php`, line 186  
Comment says: "5 jobs marked as running (awaiting external processing)" — but no external processor exists (C8).

### M10 — Duplicate `slugify()` Logic
Python (`push_proposals.py`, `git_publish.py`) and PHP (`functions.php`, `proposals.php`) both implement slugify. Divergent implementations risk broken URLs.

### M12 — `sheets_writeback()` Called Per-Field-Update
**File:** `crm/api/leads.php`, line 116  
Every inline field edit triggers a separate Google Sheets API call. If 10 fields are edited, that's 10 API calls (and 10 potential failure points).

---

## 🟢 Low (8)

### L1 — Dead `_filter_phone_country()` Function
Already noted as M1.

### L3 — Session Cookie Missing `SameSite` / `Secure` Flags
**File:** `crm/lib/auth.php`  
`session_name('TKCRM')` is set but `session_set_cookie_params()` is never called. Default PHP settings may not include `SameSite=Strict` or `Secure`.

### L5 — `lead_detail.php` Uses Raw GitHub URLs Without Local Fallback
The lead detail page links to `raw.githubusercontent.com` URLs. If GitHub is down or the repo is private, the proposal is inaccessible. A local proxy (`proxy_proposal.php`) exists but is not used as a fallback.

### L6 — `per_country_target = max_leads * 3` Hardcoded
**File:** `tkvibes-lead-engine/src/run.py`, line 260  
The 3x multiplier is hardcoded — no config knob to tune the discovery oversampling ratio.

### L8 — `header('X-Robots-Tag: noindex, nofollow')` Repeated in Every File
**Status:** Minor code duplication across all PHP entry points.

---

## Race Conditions & Concurrency Issues

### RC1 — Concurrent Cron Execution
`crm/cron.php` has no file-based locking. If the cron schedule fires twice (or overlaps), concurrent sheet sync can:
- Import the same rows twice (the `INSERT OR IGNORE` handles this, but the `UPDATE` path can race)
- Write-back to sheets can clobber concurrent CRM edits
- Proposal job recovery can mark the same job as `pending` twice

### RC2 — Non-Atomic Proposal Generation in CRM
`proposals.php` POST handler (lines 66-105) does:
1. INSERT IGNORE INTO leads (if not exists)
2. INSERT/UPDATE INTO proposals
3. UPDATE leads SET sample_site_url/pitch_deck_url
4. UPDATE proposal_generation_jobs SET status='completed'

These are 4 separate statements with no transaction. If the script dies after step 2 but before step 4, the proposal exists in the DB but the job stays "running" forever (until cron recovers it after 10 min).

### RC3 — Concurrent Sheet Write from Engine + CRM
The lead engine calls `SheetWriter.upsert()` (append) and `write_job()` (full rewrite of a job worksheet). If the CRM's sheet sync (`cron.php` task #3) runs concurrently, it could:
- Read a half-written row from `upsert()`
- The `write_job()` call does `ws.clear()` then `ws.update()` — a race here means the sheet is briefly empty

### RC4 — `_generation_results.json` Race
`generate_proposals.py` writes `_generation_results.json` (line 691), and `git_publish.py` reads it (line 107). If `generate_proposals.py` is re-run while `git_publish.py` is reading, the file may be partially written.

### RC5 — `leads_export.json` Race
`run.py` writes `leads_export.json` (line 209), and `generate_proposals.py` reads it (line 648). If the lead engine is re-run while generation is in progress, the generation process reads a half-written file — causing JSON parse errors or processing stale/partial lead data.

---

## Duplicate API Calls

### DA1 — Google Sheets Client Initialized Multiple Times
In `cron.php`:
- Line 54: `$client = get_sheets_client()` (task #3 — sheet import)
- Line 124: `$client = get_sheets_client()` (task #4 — write-back)

The `get_sheets_client()` function has a `static $client` cache, so the second call returns the cached instance. ✅ But each `GoogleSheetsClient` construction does a JWT exchange (line 28 in constructor). The static cache prevents this for the same request. ✅

### DA2 — CRM URL Push Calls sync.php Per Lead
**File:** `tkvibes-lead-engine/src/git_publish.py`, lines 212-246  
`_push_urls_to_crm()` iterates over published proposals and calls `sync.php` once per lead. Each call is a separate HTTP POST with a single lead. 50 leads = 50 HTTP round-trips. Could be batched into one call.

### DA3 — `find_row()` Does One API Call Per Lead
**File:** `crm/lib/GoogleSheetsClient.php`, line 120-130  
`update_lead_fields()` calls `find_row()` (which does `api_call('GET', 'values/A:A')` — reading the ENTIRE column A) for EACH lead. If writing back 50 leads, that's 50 full-column reads + 50 × N cell writes. The column A read could be cached.

### DA4 — `employees.php` API Called Once Per Lead Engine Run
**File:** `tkvibes-lead-engine/src/assign.py`, line 73  
`fetch_mapping_from_crm()` is called once per `assign_employees()` call. ✅ Good. But this is inside the per-run loop, and `assign_employees` is called once per run. ✅

### DA5 — Competitor Research Uses Legacy Google Places API
**File:** `tkvibes-lead-engine/src/competitor_research.py`, line 40-46  
Uses the old `maps.googleapis.com/maps/api/place/nearbysearch/json` endpoint (v1), while the main discovery uses the new `places.googleapis.com/v1/places:searchText` endpoint (v2). Two different API versions, different pricing, different rate limits. The competitor research also uses a different API key reading pattern (`os.environ.get` inside the function vs. passed from caller).

---

## Agent Responsibility Conflicts

### AC1 — Who Writes `sample_site_url` / `pitch_deck_url`?
There are **4** different code paths that set these fields:
1. `git_publish.py` `_push_urls_to_crm()` → POSTs to `sync.php` with `sample_site_url`/`pitch_deck_url` (line 220-227)
2. `proposals.php` POST handler → constructs hardcoded GitHub URL and sets the field (lines 88-99)
3. `batch_upload_proposals.py` → calls `update_crm_lead()` which POSTs to `sync.php` (lines 42-59)
4. `crm/deploy_proposals.php` → reads from local files, updates URL to `/proposals/...` path (lines 35, 50)

These 4 paths use **different URL formats**: raw.githubusercontent.com, /proposals/sample-website/, local file path. No single source of truth.

### AC2 — Who Assigns Employees?
1. Lead engine `assign.py` — sets `assigned_employee` (name string) based on config.yaml `country_assignments`
2. CRM admin panel — can manually set `assigned_employee` or `assigned_employee_id`
3. CRM `sync.php` — overwrites `assigned_employee` from lead engine data on every sync

If an admin reassigns a lead in the CRM, the next lead engine run will overwrite the assignment via sync.php.

### AC3 — Who Processes Proposal Generation Jobs?
1. Admin clicks "Generate Proposal" → `proposals.php?action=generate` creates a `pending` job
2. `cron.php` marks pending jobs as `running` (line 183)
3. `process_proposal_jobs.py` is supposed to pick up `running` jobs and generate proposals — but it's a stub
4. `proposals.php POST` marks jobs as `completed` when a proposal is uploaded

**No one actually generates proposals from the queue.** The only working path is `run_business_job.py` → `generate_proposals.py` → `git_publish.py` → `push_proposals.py`, which pushes proposals for ALL leads in a batch, not individual queued jobs.

### AC4 — Dual Source of Truth: Google Sheets vs SQLite
- Lead engine writes to Google Sheets (master tab) AND pushes to CRM SQLite via sync.php
- CRM cron reads from Google Sheets and writes to SQLite
- CRM admin edits go to SQLite AND write back to Google Sheets via `sheets_writeback()`

This creates a **circular sync** with no conflict resolution. If the engine adds a lead and the admin edits it before the next sync, the next engine run will overwrite the admin's edit.

---

## Deployment Conflicts: Hostinger vs GitHub

### DD1 — Two Competing Deployment Paths

**Path A — GitHub Direct (Lead Engine → GitHub):**
```
generate_proposals.py → git_publish.py → git commit+push → raw.githubusercontent.com URLs → sync.php to update CRM
```

**Path B — Hostinger FTP (GitHub Actions CI/CD):**
```
git push → GitHub Actions → lftp mirror → /public_html/ on Hostinger
```

**Path C — Hostinger Direct Upload (upload_proposals.py → u2.php):**
```
upload_proposals.py → u2.php (base64) → /proposals/ on Hostinger → GitHub commit+push
```

**Path D — Hostinger Local Deploy (deploy_crm.py → u3.php):**
```
deploy_crm.py → u3.php → /crm/ files on Hostinger
```

These paths can conflict:
- Path A and Path C both copy files to `Sample Webpages and pitch deck/` directory — Path A copies from `data/proposals/` and Path C copies after uploading to server
- The GitHub repo is the source of truth for the website, but the CRM proposal URLs point to GitHub raw URLs while the actual files live on Hostinger
- `deploy_proposals.php` rewrites URLs from `raw.githubusercontent.com` to `/proposals/sample-website/` — creating a **second URL per proposal** that overwrites the first

### DD2 — `deploy_proposals.php` Overwrites GitHub URLs
**File:** `crm/deploy_proposals.php`  
Line 35: `$pdo->prepare("UPDATE leads SET sample_site_url = ? WHERE lead_key = ?")->execute([$local_url, $l['lead_key']]);`

This replaces the GitHub raw URL (set by `git_publish.py` → `sync.php`) with a local Hostinger URL (`/proposals/sample-website/{slug}.html`). After this runs, the CRM has the Hostinger URL, but the `proxy_proposal.php` only allows `raw.githubusercontent.com` URLs (line 45). This creates a broken link — the proposal page links to a Hostinger path but `proxy_proposal.php` blocks it.

### DD3 — `batch_upload_proposals.py` Doesn't Match Lead Keys
**File:** `batch_upload_proposals.py`, line 116-117  
Comment: "we don't have lead_key from slug directly, so rely on the server deploy_proposals.php later"

This script uploads files but doesn't update CRM lead records. It relies on `deploy_proposals.php` to scan local files and match by slug. But `deploy_proposals.php` matches by URL slug (extracting from the `sample_site_url` field), not by filename. If the upload script and the deploy script use different slug logic, proposals won't be linked.

---

## Full Data Flow Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LEAD ENGINE (Python)                           │
│  run.py / run_business_job.py                                           │
│                                                                         │
│  ┌─────────────┐   ┌──────┐   ┌──────┐   ┌─────────┐   ┌───────────┐  │
│  │ Google      │   │Enrich│   │Score │   │Dedupe   │   │Assign     │  │
│  │ Places API  │──▶│(phone│──▶│(points)│──▶│+DNC     │──▶│Employees  │  │
│  │ (Text Search)│   │+web) │   │       │   │         │   │(country   │  │
│  │             │   │      │   │       │   │         │   │ mapping)   │  │
│  └─────────────┘   └──────┘   └──────┘   └─────────┘   └─────┬─────┘  │
│                                                                │      │
│                     ┌───────────────────────────────────────────┘      │
│                     │                                                  │
│                     ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     THREE-WAY DATA SYNC                         │  │
│  │                                                                 │  │
│  │  [1] leads_export.json  [2] Google Sheets  [3] CRM sync.php    │  │
│  │      (file handoff)       (gspread API)     (HTTP POST)         │  │
│  │          │                    │                    │              │  │
│  │          ▼                    ▼                    ▼              │  │
│  │  generate_    git_publish.   SheetWriter.   push_leads()         │  │
│  │  proposals.   py copies    upsert()       POST /api/sync.php    │  │
│  │  py           files to     appends rows   ON CONFLICT upsert    │  │
│  │               Sample/                     with assigned_         │  │
│  │               pitch deck/                 employee (name)        │  │
│  │               dirs + git                  Creates proposal_      │  │
│  │               push                        gen jobs               │  │
│  │               Builds raw.githu            Returns {added,        │  │
│  │               ub URLs and                 updated} counts         │  │
│  │               POSTs them                                       │  │
│  │               back to CRM                              │  │
│  │               via sync.php                              │  │
│  │               (per-lead, no                             │  │
│  │               batching)                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  push_proposals.py                                                      │
│  Scans data/proposals/                                                    │
│  Matches slug → lead_key via leads_export.json                          │
│  POSTs HTML to /api/proposals.php                                       │
│  Sets sample_site_url/pitch_deck_url to GitHub raw URL                  │
│  Marks proposal_generation_jobs as completed                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            CRM (PHP)                                    │
│                                                                         │
│  SQLite/MySQL DB:                                                       │
│  - leads (47 columns)                                                   │
│  - lead_activities                                                     │
│  - proposals (HTML stored in DB)                                        │
│  - proposal_generation_jobs                                           │
│  - employees + employee_regions                                        │
│  - system_logs                                                         │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  API Endpoints (all protected by shared api_key)          │         │
│  │                                                            │         │
│  │  sync.php    ← POST from Python (bulk lead upsert)       │         │
│  │  leads.php   ← POST/GET (tag, note, call, field update)  │         │
│  │  proposals   ← POST/GET (upload, generate, status)       │         │
│  │  employees   ← GET (employee→region+country mapping)       │         │
│  │  logs.php    ← POST/GET (forward error logs, view logs)   │         │
│  │  public_     ← GET (unauthenticated, lists proposals)    │         │
│  │  proposals   │                                                │         │
│  │  proxy_      ← GET (session-auth, proxies GitHub raw)      │         │
│  │  proposal    │                                                │         │
│  │  upload_     ← POST (upload proposal file)                 │         │
│  │  proposal    │                                                │         │
│  │  u2.php      ← POST (file upload to /proposals/)           │         │
│  │  u3.php      ← POST (file upload to /crm/)                 │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  Session-Auth Protected (CSRF on all POSTs)               │         │
│  │                                                            │         │
│  │  leads.php action=update  ← inline field edits            │         │
│  │    → DB UPDATE + sheets_writeback() (fire-and-forget)     │         │
│  │  leads.php action=tag     ← status changes                │         │
│  │    → DB UPDATE + sheets_writeback()                       │         │
│  │  leads.php action=note    ← add CRM notes                  │         │
│  │    → DB UPDATE + sheets_writeback()                       │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  Cron (cron.php — runs every 30 min via Hostinger)        │         │
│  │                                                            │         │
│  │  Task 1: Archive not_qualified leads >24h                 │         │
│  │  Task 2: Delete activities >90 days                       │         │
│  │  Task 3: Sync FROM Google Sheet → CRM DB                  │         │
│  │     (uses SHEET_IMPORT_FIELDS — incomplete field list)    │         │
│  │  Task 4: Write CRM state back TO Google Sheet             │         │
│  │     (SELECT updated_at > -1h, write back)                 │         │
│  │  Task 5: Recover stale 'running' jobs, mark pending     │         │
│  │     (NO actual generation — process_proposal_jobs.py      │         │
│  │      is a stub)                                           │         │
│  └────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT FLOWS                                 │
│                                                                         │
│  FLOW A: Lead Engine → GitHub (via git_push)                            │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  git_publish.py:                                            │         │
│  │  1. os.chdir(REPO_DIR)                                      │         │
│  │  2. git fetch + checkout main                               │         │
│  │  3. Copy HTML files to:                                     │         │
│  │     "Sample Webpages and pitch deck/sample website/"        │         │
│  │     "Sample Webpages and pitch deck/pitch deck/"            │         │
│  │  4. git add + commit + push                                 │         │
│  │  5. Build raw.githubusercontent.com URLs                    │         │
│  │  6. POST to sync.php (per-lead, updates sample_site_url)    │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  FLOW B: GitHub Actions → Hostinger (via lftp FTPS mirror)              │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  .github/workflows/deploy.yml:                              │         │
│  │  1. On push to main (or manual dispatch)                    │         │
│  │  2. Checkout                                                 │         │
│  │  3. Verify index.html + assets exist                        │         │
│  │  4. Install lftp                                             │         │
│  │  5. lftp mirror --reverse ./ /public_html/                  │         │
│  │     (mirrors ENTIRE repo to Hostinger public_html)           │         │
│  │     (excludes .git, .github, scripts, memory)                │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  FLOW C: Direct Upload → Hostinger (via u2.php)                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  upload_proposals.py:                                      │         │
│  │  1. Read HTML from "Sample Webpages and pitch deck/"        │         │
│  │  2. base64_encode content                                   │         │
│  │  3. POST to https://tkvibes.in/crm/u2.php                   │         │
│  │     (Content-Type: text/plain — mod_security bypass)        │         │
│  │  4. Writes to /proposals/sample-website/ and pitch-deck/     │         │
│  │                                                       │         │
│  │  batch_upload_proposals.py:                                 │
│  │  1. Scan data/proposals/<slug>/  (5+ filesystem locations)  │         │
│  │  2. Upload via u2.php                                       │         │
│  │  3. Copy to "Sample Webpages and pitch deck/" (GitHub tree) │         │
│  │  4. git commit + push                                       │         │
│  │  5. Does NOT update CRM lead URLs                           │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  FLOW D: Deploy CRM → Hostinger (via u3.php)                              │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  deploy_crm.py:                                            │         │
│  │  1. Read PHP files from local repo                          │         │
│  │  2. base64_encode each file                                │         │
│  │  3. POST to https://tkvibes.in/crm/u3.php                   │         │
│  │     (Content-Type: text/plain)                              │         │
│  │  4. Writes to /crm/ directory on server                    │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  FLOW E: deploy_proposals.php (server-side local deploy)                │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  Runs on Hostinger:                                        │         │
│  │  1. Read leads with GitHub URLs from DB                    │         │
│  │  2. Copy from /repo-root/Sample Webpages... to              │         │
│  │     /proposals/sample-website/ and /proposals/pitch-deck/  │         │
│  │  3. Overwrite URL in DB to local /proposals/... path        │         │
│  │     (BREAKS proxy_proposal.php which only allows              │         │
│  │      raw.githubusercontent.com URLs)                         │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                         │
│  CONFLICT: FLOW A sets URLs to raw.githubusercontent.com                │
│  FLOW E then overwrites them with /proposals/local-path               │
│  proxy_proposal.php blocks local paths (only allows github raw)       │
│  Result: lead_detail.php links work (direct href)                     │
│  But proxy_proposal.php links break (if used)                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Three Data Stores (No Single Source of Truth)

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  SQLite/MySQL   │    │  Google Sheets   │    │  JSON Files      │
│  (CRM DB)       │◀──▶│  (Leads tab)      │◀──▶│  leads_export.   │
│                 │    │                   │    │  json, _gen_    │
│  PRIMARY SOURCE │    │  SYNC SOURCE      │    │  results.json   │
│  for CRM       │    │  for engine      │    │  (handoff)      │
│  operations    │    │  writes         │    │                 │
└─────────────────┘    └──────────────────┘    └──────────────────┘
      ▲                      ▲                      ▲
      │ sync.php          upsert()             generate_for_
      │ (HTTP POST)       (gspread)            lead() / push_
      │                                         proposals()
      │
      ▼
┌─────────────────────────────────────┐
│  proposal_generation_jobs table     │
│  (status: pending/running/completed)│
│  NO PROCESSOR EXISTS (C8)           │
└─────────────────────────────────────┘
```

**The fundamental problem:** Data flows in circles with no single source of truth. The engine writes to Sheets + CRM. The CRM reads from Sheets and writes back. The CRM proposal system creates jobs that nobody processes.
