# TKVibes AI CRM — Production Refactoring Plan

**Phase Duration:** 5 Weeks (20 work days)  
**Target State:** Single MySQL database, structured logging with trace IDs, AI agents with clear boundaries, Hostinger-only deployment

---

## Decision: Single Deployment Target — Hostinger

**Eliminating GitHub Actions/FTPS mirror as a deployment path.**  
**Rationale:** The current system has 5 competing deployment paths creating data inconsistency. GitHub is retained as the **source code repository only** — not as a deployment target or data store. All runtime data flows through Hostinger's MySQL database + filesystem.

**GitHub stays for:** source code versioning, the `Sample Webpages and pitch deck` static assets (served by Hostinger's web server).
**Hostinger is the single deployment target for:** CRM PHP code, MySQL data, proposal HTML files.

---

## Phase 1: Security Hardening (Days 1-3)

### Day 1: Credential Management & Secret Rotation

**Tasks:**
1. **Rotate API key** — generate new key, update ALL locations:
   - `crm/config.local.php` → `api_key` (NEW)
   - All Python config → `.env` file (environment variable `CRM_API_KEY`)
   - `deploy_crm.py`, `process_proposal_jobs.py`, `batch_upload_proposals.py` → read from env

2. **Fix hardcoded secrets in Python scripts:**
   ```python
   # BEFORE (deploy_crm.py line 12):
   API_KEY = "10a76f01219e8fd7b1fec2c5256c6a39"
   
   # AFTER:
   API_KEY = os.environ.get("CRM_API_KEY", "")
   if not API_KEY:
       print("ERROR: CRM_API_KEY not set in environment")
       sys.exit(1)
   ```

3. **Add all credential files to `.gitignore`:**
   ```gitignore
   # Credentials
   crm/config.local.php
   crm/credentials/
   tkvibes-lead-engine/.env
   tkvibes-lead-engine/credentials/
   ```

4. **Add `.env` check to config loader** — refuse to load if `CRM_API_KEY` is in `config.yaml`.

### Day 2: Secure Upload Endpoints (u2.php/u3.php)

**Tasks:**
1. **Strict path allowlisting** in u2.php:
   ```php
   // Only allow these subdirectories
   $allowed_dirs = ['sample-website/', 'pitch-deck/'];
   $subpath = substr($p, 0, strpos($p, '/') + 1);
   if (!in_array($subpath, $allowed_dirs)) {
       http_response_code(403);
       echo 'Forbidden path';
       exit;
   }
   ```

2. **File type validation** — only `.html` files allowed in u2.php.

3. **Audit logging** — log every file write to `system_logs`:
   ```php
   log_system('info', 'deploy', 'File uploaded via u2.php', 
       ['path' => $p, 'size' => $written, 'ip' => $_SERVER['REMOTE_ADDR']]);
   ```

4. **Restrict u3.php** — only allow writes to specific PHP files (no directory creation):
   ```php
   $allowed_files = ['lib/constants.php', 'lib/functions.php', 'lib/auth.php', ...];
   if (!in_array($p, $allowed_files)) {
       http_response_code(403);
       echo 'Forbidden file';
       exit;
   }
   ```

### Day 3: Session & Cookie Hardening

**Tasks:**
1. **Fix session cookie flags** in `auth.php`:
   ```php
   session_set_cookie_params([
       'lifetime' => 0,
       'path' => '/',
       'secure' => true,
       'httponly' => true,
       'samesite' => 'Strict',
   ]);
   session_name('TKCRM');
   session_start();
   ini_set('session.gc_maxlifetime', 1800); // 30 min
   ```

2. **Add session activity tracking** — store last activity timestamp, check on each request:
   ```php
   if (isset($_SESSION['last_activity']) && time() - $_SESSION['last_activity'] > 1800) {
       session_unset();
       session_destroy();
       header('Location: index.php?timeout=1');
       exit;
   }
   $_SESSION['last_activity'] = time();
   ```

3. **Add rate limiting** to API endpoints (shared API key):
   ```php
   // Simple in-memory rate limiter (file-based for shared hosting)
   $rate_file = sys_get_temp_dir() . "/tkvibes_rate_{$ip}_{$endpoint}";
   // 60 requests per minute per IP
   ```

4. **Force HTTPS** in `.htaccess`:
   ```apache
   RewriteEngine On
   RewriteCond %{HTTPS} off
   RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
   Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
   ```

---

## Phase 2: Database Migration (Days 4-7)

### Day 4: MySQL Schema & Migration System

**Tasks:**
1. **Create MySQL migration script** (`crm/data/migration_002_mysql.sql`):
   - Add ENUM columns for `crm_status`, `lead_tier`, `action`
   - Fix `assigned_employee` / `assigned_employee_id` — consolidate to `assigned_employee_id` only (drop the TEXT column)
   - Move proposal HTML storage to file paths (new column `proposal_path`)
   - Add `trace_id` column to `leads`, `proposal_generation_jobs`, `system_logs`
   - Add `created_by` / `updated_by` columns to `leads`
   - Add UNIQUE constraint on `(phone_primary, country)` for business uniqueness
   - Add NOT NULL constraint on `lead_key`

2. **Create migration runner** (`crm/migrate.php`):
   ```bash
   php migrate.php --to=mysql --dry-run
   php migrate.php --to=mysql
   ```

3. **Update `db.php`** to handle both SQLite (local dev) and MySQL (production):
   - Use `config.local.php` `db.dsn` to select driver
   - Auto-run pending migrations on startup

### Day 5: Database Normalization & Indexing

**Tasks:**
1. **Split `leads` table** (optional — if going for full normalization):
   ```
   leads_core:     lead_key (PK), business_name, category, phone_primary, email, address, city, pincode, latitude, longitude, region, country
   leads_enrichment: lead_key (FK), owner_name, whatsapp, opening_hours, has_website, website_url, website_quality, rating, review_count, years_in_business, socials, source, source_url, place_id
   leads_scoring:  lead_key (FK), lead_score, lead_tier, data_fetched_at, stale_after, outreach_status, opt_out, contact_channel, wa_link, pain_points, recommended_pitch
   leads_crm:      lead_key (FK), assigned_employee_id, crm_status, crm_notes, last_contacted_at, next_callback_at, sample_site_url, pitch_deck_url, notes, created_by, updated_by, trace_id, created_at, updated_at
   ```

   **OR keep as single table** (simpler, acceptable for <100K leads) with proper constraints.

2. **Add indexes:**
   - `idx_leads_phone_country` on `(phone_primary, country)` — for dedup
   - `idx_leads_trace_id` on `trace_id` — for log correlation
   - `idx_leads_assigned_id` on `assigned_employee_id` — for dashboard filters
   - `idx_jobs_trace_id` on `proposal_generation_jobs(trace_id)`
   - `idx_logs_trace_id` on `system_logs(trace_id)`

3. **Proposal storage migration:**
   - Add `proposal_path` column (TEXT) to `proposals` table
   - Migrate existing HTML content to files: `proposals/{lead_key}/{type}.html`
   - Future inserts store path only, not HTML

### Day 6-7: Transactional Sync & Data Consistency

**Tasks:**
1. **Rewrite `sync.php`** with transactions:
   ```php
   $pdo->beginTransaction();
   try {
       foreach ($leads as $l) {
           // Upsert lead
           // Create proposal job if new
       }
       $pdo->commit();
   } catch (Exception $e) {
       $pdo->rollBack();
       // Log error with trace_id
   }
   ```

2. **Add idempotency keys:**
   ```php
   $idempotency_key = $body['idempotency_key'] ?? '';
   // Check if this key was already processed within 5 minutes
   $stmt = $pdo->prepare("SELECT 1 FROM sync_log WHERE idempotency_key = ? AND processed_at > datetime('now', '-5 minutes')");
   if ($stmt->fetch()) {
       json_response(['status' => 'duplicate', 'added' => 0, 'updated' => 0]);
   }
   ```

3. **Remove Google Sheets sync** — with MySQL as source of truth, the Sheets sync becomes unidirectional (CRM reads from DB, Sheets is for reporting only via a read-only export).

---

## Phase 3: Structured Logging & Trace IDs (Days 8-10)

### Day 8: Python Logging Overhaul

**Tasks:**
1. **Update `log_config.py`** to include trace_id in all log records:
   ```python
   import uuid
   from contextvars import ContextVar
   
   _trace_id: ContextVar[str] = ContextVar('trace_id', default='')
   
   class TraceFormatter(logging.Formatter):
       def format(self, record):
           record.trace_id = _trace_id.get() or 'N/A'
           return super().format(record)
   
   def set_trace_id(tid=None):
       tid = tid or str(uuid.uuid4())
       _trace_id.set(tid)
       return tid
   ```

2. **Replace ALL `print()` in `run.py` with logger calls:**
   ```python
   # BEFORE:
   print(f"   discovered {len(raw)} raw leads")
   
   # AFTER:
   logger.info("Discovery complete", extra={
       "raw_lead_count": len(raw),
       "trace_id": _trace_id.get(),
   })
   ```

3. **Add trace_id to all data payloads:**
   - `lead.to_dict()` includes `_trace_id`
   - `sync.php` receives and stores `trace_id`
   - `proposal_generation_jobs` stores `trace_id`

### Day 9: PHP Structured Logging

**Tasks:**
1. **Create `log_system_structured()` helper:**
   ```php
   function log_structured(string $level, string $source, string $message, array $context = []): void {
       $entry = [
           'timestamp' => now_iso(),
           'level' => $level,
           'trace_id' => $context['trace_id'] ?? $_SERVER['HTTP_X_TRACE_ID'] ?? '',
           'source' => $source,
           'message' => $message,
           'context' => json_encode($context, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
           'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
           'user_agent' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 255),
       ];
       // Insert into system_logs
   }
   ```

2. **Add `X-Trace-ID` header passthrough** in all API endpoints.

3. **Add trace_id column** to all relevant tables.

### Day 10: Centralized Logging API

**Tasks:**
1. **Enhance `logs.php`** to accept structured JSON logs with trace_id.
2. **Add log aggregation endpoint** — Python engine forwards critical errors.
3. **Create admin UI** for log viewing with trace_id filtering.

---

## Phase 4: Agent Decomposition & Responsibility Boundaries (Days 11-15)

### Day 11: Agent 1 — Lead Discovery Agent

**Responsibilities:** Google Places API calls only. No writes to any system.

**Changes:**
1. **Extract `discover_all()`** from `run.py` into `lead_discovery_agent.py`.
2. **Add trace_id propagation** — each `discover()` call gets a trace_id.
3. **Add retry with exponential backoff** (already has tenacity on GooglePlacesConnector).
4. **Output:** `leads_batch.json` with `_trace_id` field.

### Day 12: Agent 2 — Lead Processing Agent

**Responsibilities:** enrich, score, dedupe, assign. No writes to DB or Sheets.

**Changes:**
1. **Extract `process_leads()` and `apply_crm_fields()`** from `run.py` into `lead_processing_agent.py`.
2. **Replace `print()` with structured logging.**
3. **Fix `_filter_phone_country()` dead code** — remove it.
4. **Output:** `processed_leads.json` with `_trace_id`.

### Day 13: Agent 3 — Proposal Generation Agent

**Responsibilities:** Generate HTML files. No writes to DB.

**Changes:**
1. **Fix `_generation_results.json`** — ensure `lead_key` is always populated.
2. **Use AI site generator** as primary (fallback to template).
3. **Write proposals to filesystem only** — `proposals/{lead_key}/{type}.html`.
4. **Output:** file paths + metadata JSON with `_trace_id`.

### Day 14: Agent 4 — CRM Sync Agent

**Responsibilities:** Write to MySQL DB only. No file system access.

**Changes:**
1. **Rewrite `push_crm.py`** to use async/batched POST with idempotency keys.
2. **Add transaction support** — if batch fails, rollback.
3. **Store trace_id** in `leads` and `proposal_generation_jobs` tables.
4. **Remove SheetWriter dependency** — CRM is the single source of truth.

### Day 15: Agent 5 — Deployment Agent

**Responsibilities:** Deploy files to Hostinger. Update CRM URLs via API.

**Changes:**
1. **Consolidate all file uploads** through u2.php (with security fixes from Phase 1).
2. **Remove `batch_upload_proposals.py`** — redundant with `push_proposals.py`.
3. **Fix `deploy_proposals.php`** — don't overwrite GitHub URLs in DB. Use local proxy instead.
4. **Fix `proxy_proposal.php`** — allow local `/proposals/` paths in addition to GitHub raw URLs.

---

## Phase 5: Proposal Job Queue Implementation (Days 16-17)

### Day 16: Job Processor

**Tasks:**
1. **Implement `process_proposal_jobs.py`** — replace stub:
   ```python
   def get_pending_jobs():
       # Call proposals.php?action=api_pending
       # Returns jobs with lead_key, feedback
       # Returns [] on error
   
   def process_job(job):
       # Set job status to 'running' via api_complete
       # Call generate_proposals.py --lead-key {job.lead_key} --force
       # Call push_proposals.py --lead-key {job.lead_key}
       # Mark job as 'completed' via api_complete
       # On failure: mark as 'failed' with error message
   ```

2. **Add heartbeat mechanism** — job processor updates `updated_at` every 30s.

3. **Add timeout** — if job processes >30 min, mark as failed.

### Day 17: Cron Integration

**Tasks:**
1. **Update cron.php** task #5 to actually dispatch jobs:
   - Instead of just marking as `running`, call the job processor.
   - On Hostinger shared hosting, use `exec()` or `curl` to trigger the processor.
   - Or use a separate `process_proposal_jobs.php` that runs via cron.

2. **Add job result tracking** — store generation output in `proposal_generation_jobs.feedback`.

---

## Phase 6: Data Pipeline Reliability (Days 18-19)

### Day 18: Transactional Pipeline

**Tasks:**
1. **Rewrite `run_business_job.py`** with clear phases and rollback:
   ```python
   # Phase 1: Discover + Process → processed_leads.json (trace_id: {uuid})
   # Phase 2: Push to CRM (transactional, idempotent) 
   # Phase 3: Generate proposals (file output only)
   # Phase 4: Deploy to Hostinger
   # Phase 5: Update CRM URLs (via sync.php)
   
   # If any phase fails, log error with trace_id and stop
   # No partial state
   ```

2. **Add `--lead-key` support** to `run_business_job.py`:
   - Skip discovery phase
   - Load lead from CRM DB (via employees.php or a new `get_lead` API)
   - Generate proposals for that lead only

3. **Add locking** — file-based lock to prevent concurrent pipeline runs:
   ```python
   lock_file = /tmp/tkvibes_pipeline.lock
   ```

### Day 19: Error Handling & Retry Architecture

**Tasks:**
1. **Add retry policy** to all external API calls:
   - Google Places API: 3 retries, exponential backoff (tenacity already used in GooglePlacesConnector)
   - CRM sync: 3 retries, 5s delay
   - Google Sheets: 3 retries, exponential backoff

2. **Add circuit breaker** pattern for CRM API:
   - If 3 consecutive failures, stop trying for 60 seconds
   - Log circuit breaker state changes

3. **Add dead-letter queue** for failed proposals:
   - After 3 retries, move lead to `proposal_generation_jobs` with status='failed'
   - Admin can review and re-queue

---

## Phase 7: Testing & Verification (Day 20)

### Final Integration Tests

**Tasks:**
1. **Run full pipeline end-to-end** with a test lead.
2. **Verify trace_id** propagation through all components.
3. **Verify rollback** — kill pipeline mid-way, confirm no partial state.
4. **Verify concurrent execution** — run 2 pipelines, confirm no race conditions.
5. **Verify security** — attempt path traversal on u2.php, SQL injection on leads.php.
6. **Run existing test suite** — 82 Python tests + 8 CRM smoke tests.

---

## Implementation Priority Matrix

| Priority | Issue IDs | Description | Effort |
|----------|-----------|-------------|--------|
| **P0** | C1, C3, C4, C8 | Server compromise, orphan leads, data inconsistency, dead job queue | Days 1-3 |
| **P1** | H5, H6, H10, H14 | Non-transactional writes, duplicate columns, HTML in DB, sheet race | Days 4-7 |
| **P2** | H1, H3, H7, H9, H11, H12 | Logging, orphaned jobs, JWT caching, monolith, dashboard perf, slow file search | Days 8-15 |
| **P3** | C5, C6, C7, H4, M1-M18 | Job targeting, empty lead_key, hardcoded URLs, empty fallback, technical debt | Days 16-19 |
| **P4** | L1-L8, RC1-RC5, DA1-DA5, AC1-AC4, DD1-DD3 | Race conditions, duplicate calls, agent conflicts, deployment conflicts | Days 20+ |

---

## File Change Summary

| File | Action | Description |
|------|--------|-------------|
| `deploy_crm.py` | **Modify** | Read API key from env, add audit logging |
| `process_proposal_jobs.py` | **Rewrite** | Implement actual job polling + processing |
| `tkvibes-lead-engine/config.yaml` | **Modify** | Remove `api_key`, use env var |
| `tkvibes-lead-engine/.env` | **Update** | Add all secrets, add comments |
| `crm/config.sample.php` | **Modify** | Document MySQL config, env var usage |
| `crm/lib/db.php` | **Modify** | Add migration runner, trace_id columns |
| `crm/lib/auth.php` | **Modify** | Add session timeout, cookie flags |
| `crm/u2.php` | **Modify** | Add path allowlisting, file type restriction, audit log |
| `crm/u3.php` | **Modify** | Restrict to allowlisted files only |
| `crm/api/sync.php` | **Modify** | Add transaction, idempotency, trace_id |
| `crm/api/proposals.php` | **Modify** | Remove orphan lead auto-create, fix hardcoded URLs |
| `crm/lib/constants.php` | **Modify** | Add trace_id to SHEET_IMPORT_FIELDS, add PROPOSAL_STATUSES |
| `crm/cron.php` | **Modify** | Add file-based locking, implement job dispatch |
| `tkvibes-lead-engine/src/run.py` | **Modify** | Replace print() with logging, add trace_id |
| `tkvibes-lead-engine/src/run_business_job.py` | **Modify** | Add phases with rollback, fix --lead-key |
| `tkvibes-lead-engine/src/generate_proposals.py` | **Modify** | Fix lead_key in results JSON |
| `tkvibes-lead-engine/src/git_publish.py` | **Modify** | Read repo from env, batch CRM URL push |
| `tkvibes-lead-engine/src/push_crm.py` | **Modify** | Add batch mode, idempotency keys |
| `tkvibes-lead-engine/src/push_proposals.py` | **Modify** | Fix file search paths, add trace_id |
| `tkvibes-lead-engine/src/assign.py` | **Modify** | Add logging for assignment failures |
| `tkvibes-lead-engine/src/log_config.py` | **Modify** | Add trace_id support, ContextVar |
| `tkvibes-lead-engine/src/models.py` | **Modify** | Add trace_id field to Lead dataclass |
| `batch_upload_proposals.py` | **Delete** | Redundant with push_proposals.py |
| `crm/deploy_proposals.php` | **Delete** | Redundant, causes URL conflicts |
