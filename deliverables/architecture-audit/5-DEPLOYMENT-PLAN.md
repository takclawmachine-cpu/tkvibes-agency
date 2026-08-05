# TKVibes AI CRM — Production Deployment Plan

**Target:** Hostinger shared hosting (PHP 8.x + MySQL 8.0)  
**Single Deployment Path:** Code via GitHub Actions FTPS mirror; Data via CRM API  
**Eliminated:** GitHub raw URLs as data source, direct u2.php/u3.php uploads in production

---

## Architecture Decision: Hostinger-Only Deployment

### Why Hostinger Only?

The current system has **5 competing deployment paths**:
1. GitHub Actions FTPS mirror (CI/CD on git push)
2. Lead Engine → git_publish.py → GitHub raw URLs
3. upload_proposals.py → u2.php direct upload
4. deploy_crm.py → u3.php direct upload
5. deploy_proposals.php (server-side URL rewrite)

These create **data inconsistency**: GitHub URLs get overwritten by local paths, which then break `proxy_proposal.php`. The fix is to pick ONE path and make it authoritative.

### Chosen Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐
│  Developer PC   │───▶│  GitHub Repo     │───▶│ Hostinger      │
│  (local dev)    │    │  (source code)   │    │ (runtime)     │
└─────────────────┘    └──────────────────┘    │              │
                                                │  /public_html/    │
┌─────────────────┐    ┌──────────────┐       │  /crm/           │
│  Lead Engine    │───▶│  CRM API     │──────▶│  /proposals/     │
│  (Python local) │    │  (HTTPS)     │       │  MySQL DB        │
│  Runs on local  │    │  sync.php,   │       │  system_logs     │
│  machine only   │    │  proposals.php│      │                  │
└─────────────────┘    └──────────────┘       └──────────────────┘
```

**Key decisions:**
- **GitHub is source code only** — no runtime data flows through GitHub
- **Hostinger is the single runtime** — all PHP, MySQL, and file operations happen here
- **Lead Engine runs locally** — pushes data to CRM via HTTPS API only
- **No direct file uploads in production** — u2.php/u3.php reserved for emergency bootstrap only

---

## Environment Setup

### Production Environment (Hostinger)

**Required PHP extensions:**
- `pdo_mysql` (primary DB driver)
- `openssl` (session encryption, JWT)
- `curl` (Google API calls)
- `json` (API responses)
- `mbstring` (UTF-8 handling)
- `fileinfo` (file type detection)

**Required MySQL configuration:**
- Database: `tkvibes_crm` (or similar, created by Hostinger control panel)
- User: `tkvibes_crm_user` with SELECT/INSERT/UPDATE/DELETE on the database
- Charset: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`

**Required environment variables** (set in `.htaccess` or `config.local.php`):
```
CRM_API_KEY=<generated-secret>
GOOGLE_SERVICE_ACCOUNT_JSON=/home/u990668815/domains/tkvibes.in/crm/credentials/google-service-account.json
GOOGLE_SHEET_ID=1cZ7w4HlN5aGaSAY-m-9EPexqEaCVC52kRELPk1OGiX
```

### Local Development Environment

**Python venv setup:**
```bash
cd tkvibes-lead-engine
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/pip install -e .
```

**Environment variables** (`.env` file — NOT tracked by git):
```bash
GOOGLE_MAPS_API_KEY=<your-key>
GOOGLE_SHEETS_ID=<your-sheet-id>
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/google-service-account.json
OPENROUTER_API_KEY=<your-openrouter-key>
CRM_API_KEY=<same-as-server-above>
CRM_API_URL=https://tkvibes.in/crm
```

---

## Deployment Workflow

### 1. Code Deployment (CI/CD)

**Trigger:** `git push origin main`

**GitHub Actions workflow** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Hostinger
on:
  push:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: deploy-hostinger
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Verify static site
        run: |
          test -f index.html || (echo "::error::index.html not found" && exit 1)
          test -f assets/css/styles.css || (echo "::error::styles.css not found" && exit 1)
          test -f assets/js/main.js || (echo "::error::main.js not found" && exit 1)

      - name: Install lftp
        run: sudo apt-get install -y -qq lftp

      - name: Deploy to Hostinger via lftp (FTPS)
        run: |
          lftp -c "
            set ftp:ssl-allow yes;
            set ftp:ssl-protect-data yes;
            set ftp:ssl-force yes;
            set ssl:verify-certificate no;
            set ftp:passive-mode yes;
            set dns:order 'inet inet6';
            set net:timeout 120;
            set net:max-retries 15;
            set net:reconnect-interval-base 10;
            set net:reconnect-interval-max 60;
            open -u '${{ secrets.FTP_USER }}','${{ secrets.FTP_PASS }}' ${{ secrets.FTP_HOST }};
            mirror --reverse --verbose --overwrite --ignore-time --no-perms --parallel=3
              --exclude-glob=.git*
              --exclude-glob=.github/**
              --exclude-glob=scripts/**
              --exclude-glob=README.md
              --exclude-glob=AGENTS.md
              --exclude-glob=memory/**
              --exclude-glob=.gitignore
              --exclude-glob=tkvibes-lead-engine/**
              --exclude-glob=operations-dashboard/**
              --exclude-glob=local-llm/**
              --exclude-glob=deliverables/**
              ./ /public_html/;
            bye;
          "
```

**Critical change:** Added `--exclude-glob=tkvibes-lead-engine/**` — the Python codebase is NEVER deployed to Hostinger. It runs locally and pushes data via API.

### 2. Database Migration

**Manual step (one-time):**
```bash
# On production server:
cd /home/u990668815/domains/tkvibes.in/crm/
php migrate.php --to=mysql
```

**For subsequent deploys:** The `db.php` boot process auto-runs pending migrations.

### 3. Lead Engine Data Push

**Trigger:** Local cron job or manual execution

**Workflow:**
```
1. Python: python -m src.run_business_job --max-leads 40
   → Discovers leads from Google Places
   → Processes (enrich, score, dedupe, assign)
   → Writes processed_leads.json (local file, trace_id)

2. Python: python -m src.push_crm (batched)
   → POSTs to https://tkvibes.in/crm/api/sync.php
   → Includes idempotency_key + trace_id
   → MySQL stores leads (transactional)

3. Python: python -m src.generate_proposals --limit 40
   → Generates HTML files locally
   → Stores in data/proposals/{slug}/

4. Python: python -m src.git_publish
   → Copies HTML files to "Sample Webpages and pitch deck/"
   → git add + commit + push

5. GitHub Actions: auto-triggers on push
   → FTPS mirrors to Hostinger /public_html/

6. PHP: deploy_proposals.php (runs via cron on Hostinger)
   → Copies from /Sample Webpages/ to /proposals/
   → Updates URLs in DB to local paths

7. Python: python -m src.push_proposals
   → No longer needed — URLs are set by step 2 sync.php
```

**Simplified production flow:**
```
Lead Engine (local) → CRM API (HTTPS) → MySQL (Hostinger)
                     ↓
Proposal Generator (local) → Git push → GitHub Actions → FTPS → Hostinger /public_html/
                                                    ↓
CRM reads /proposals/ via local filesystem path (no GitHub raw URLs)
```

### 4. Cron Jobs (Hostinger)

**Cron entry** (configured in Hostinger control panel):
```
*/30 * * * * php /home/u990668815/domains/tkvibes.in/crm/cron.php >> /home/u990668815/domains/tkvibes.in/logs/cron.log 2>&1
```

**Cron tasks:**
1. Archive `not_qualified` leads older than 24h
2. Delete `lead_activities` older than 90 days
3. **DISABLED:** Sheet sync (no longer needed — CRM is source of truth)
4. **DISABLED:** Sheet write-back (no longer needed)
5. Recover orphaned `running` proposal jobs (>10 min stale)
6. Process pending proposal jobs (calls `process_proposal.php` which triggers local agent)

**Note:** The `process_proposal.php` cron task cannot run the Python proposal generator directly (it's local-only). Instead, it creates a webhook call that the local `process_proposal_jobs.py` agent polls for.

### 5. Lead Engine Cron (Local)

**Cron entry** (local machine, via Task Scheduler or cron):
```
0 * * * * . $HOME/Desktop/tkvibes-agency/tkvibes-lead-engine/.venv/bin/activate && python -m src.run_business_job --max-leads 20
```

This runs every hour, discovers 20 new leads, generates proposals, and pushes everything to Hostinger.

---

## Rollback Procedures

### Code Rollback
```bash
# Revert to previous commit
git revert --no-commit HEAD~3..HEAD
git commit -m "revert: rollback to stable state"
git push origin main
# GitHub Actions auto-deploys within 2 min
```

### Database Rollback
```bash
# MySQL rollback (requires mysqldump backup)
mysql -u tkvibes_crm_user -p tkvibes_crm < backup/tkvibes_crm_2026-08-04.sql
```

**Backup schedule:** Daily mysqldump at 2:00 AM, retained for 30 days.

### Data Rollback (Single Lead)
```bash
# Via CRM admin panel: restore from lead_activities
# Or via SQL:
UPDATE leads SET crm_status='new', crm_notes='', updated_at=NOW() 
WHERE lead_key='ph:+919...' AND trace_id='specific-run-id';
```

---

## Monitoring & Alerting

### Health Checks
- `GET https://tkvibes.in/crm/api/public_proposals.php` — returns JSON, should respond in <2s
- `GET https://tkvibes.in/crm/dashboard.php` — login page should return 200
- `POST https://tkvibes.in/crm/api/sync.php` with bad key — should return 403

### Log Monitoring
- CRM `system_logs` table — check for `error` and `critical` level entries
- Lead engine logs forwarded to CRM via `logs.php` API
- Monitor `proposal_generation_jobs` table for stuck `running` jobs

### Alert Thresholds
- CRITICAL: `system_logs` has >5 `critical` entries in 1 hour
- WARNING: `proposal_generation_jobs` has >10 `failed` jobs in 24 hours
- WARNING: `leads` with `crm_status='new'` > 100 (stale leads)

---

## Security Checklist

| Item | Status | Notes |
|------|--------|-------|
| ✅ API key in .env, not config.yaml | Done | Phase 1 Day 1 |
| ✅ u2.php path allowlisting | Done | Phase 1 Day 2 |
| ✅ u3.php file allowlisting | Done | Phase 1 Day 2 |
| ✅ Session cookie flags (Secure, HttpOnly, SameSite) | Done | Phase 1 Day 3 |
| ✅ Session timeout (30 min) | Done | Phase 1 Day 3 |
| ✅ Rate limiting on API endpoints | Done | Phase 1 Day 3 |
| ✅ HTTPS forced via .htaccess | Done | Phase 1 Day 3 |
| ✅ HSTS header | Done | Phase 1 Day 3 |
| ✅ Service account keys in .gitignore | Done | Phase 1 Day 1 |
| ✅ MySQL prepared statements everywhere | Done | Existing + fix sync.php addslashes |
| ✅ Input validation (length, type, format) | Done | sync.php, leads.php |
| ✅ Audit logging for file uploads | Done | u2.php, u3.php |
| ✅ CSRF tokens on all POST forms | Done | Already in CHANGELOG |

---

## Post-Deployment Verification

1. **Verify CRM API endpoints:**
   ```bash
   curl -s https://tkvibes.in/crm/api/public_proposals.php | python -m json.tool
   curl -s -X POST https://tkvibes.in/crm/api/sync.php -H "Content-Type: application/json" -d '{"key":"bad","leads":[]}'
   # Expect: {"status":"error","code":"","message":"Invalid API key"}
   ```

2. **Verify database migration:**
   ```sql
   SHOW COLUMNS FROM leads LIKE 'trace_id';
   SHOW COLUMNS FROM leads LIKE 'assigned_employee_id';
   SHOW INDEX FROM leads WHERE Column_name = 'assigned_employee_id';
   ```

3. **Verify proposal generation pipeline:**
   ```bash
   cd tkvibes-lead-engine
   python -m src.run_business_job --max-leads 3 --dry-run
   # Check: processed_leads.json has 3 leads with trace_id
   # Check: data/proposals/{slug}/index.html exists for each
   ```

4. **Verify deployment sync:**
   ```bash
   # After git push, verify files on Hostinger:
   curl -s https://tkvibes.in/proposals/sample-website/dental-clinic.html | head -5
   ```

5. **Verify cron execution:**
   ```bash
   # Check cron log after 30 min:
   tail -20 /home/u990668815/domains/tkvibes.in/logs/cron.log
   ```
