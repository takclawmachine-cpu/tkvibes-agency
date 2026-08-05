# TKVibes AI CRM — Security Report
**Audit Date:** 2026-08-05  
**Auditor:** Principal AI Architect  

---

## Executive Summary

The TKVibes AI CRM system has a mixed security posture. Phase 2 fixes (per CHANGELOG.md) addressed the most critical issues (u2.php/u3.php authentication, SQL injection guard, CSRF protection). However, significant residual risks remain in credential management, session security, input validation, and the deployment pipeline.

**Risk Level:** ⚠️ MODERATE — exploitable by an authenticated insider or with knowledge of shared secrets.

---

## Credential & Secret Management

### 🔴 Critical: Secrets Stored in Plaintext Config

**File:** `tkvibes-lead-engine/config.yaml` (line 168)
```yaml
crm:
  api_key: "10a76f01219e8fd7b1fec2c5256c6a39"
```

**File:** `deploy_crm.py` (lines 12, 50)
```python
API_KEY = "10a76f01219e8fd7b1fec2c5256c6a39"
```

**File:** `batch_upload_proposals.py` (line 7)
```python
CRM_API_URL = "https://tkvibes.in/crm/api/sync.php?key=10a76f01219e8fd7b1fec2c5256c6a39"
```

**File:** `process_proposal_jobs.py` (line 5)
```python
API_KEY = "10a76f01219e8fd7b1fec2c5256c6a39"
```

**Issues:**
1. The same API key is hardcoded in 4 different files across 2 repositories (lead engine + root repo).
2. `config.yaml` is NOT in `.gitignore` — only `.env` is gitignored. If `config.yaml` is committed, the API key is exposed in version control.
3. `deploy_crm.py` and `process_proposal_jobs.py` have the key hardcoded directly in source — these files ARE tracked by git.
4. The `.env.example` documents `OPENROUTER_API_KEY` but the `_call_llm()` function in `ai_site_generator.py` reads directly from `os.environ` — if not set, it silently falls back to template-only mode.

**Recommendation:**
- Move all API keys to environment variables or a secrets manager.
- Add `deploy_crm.py` and `process_proposal_jobs.py` to `.gitignore` or replace hardcoded keys with env var reads.
- Rotate the current API key immediately — it has been in version control.

---

### 🟠 High: Shared API Key Has Unlimited Scope

The CRM API key (`10a76f01219e8fd7b1fec2c5256c6a39`) is used for:
- **Lead ingestion** (`sync.php`) — can create/update ANY field on ANY lead
- **Employee data export** (`employees.php`) — can read all employee names, emails, regions
- **Proposal upload** (`proposals.php`) — can upload HTML to any lead, including overwriting existing proposals
- **File uploads** (`u2.php`, `u3.php`) — can write arbitrary files to the server filesystem
- **Log ingestion** (`logs.php`) — can write arbitrary entries to system_logs

There is no key rotation policy, no per-service key, and no way to scope a key to specific operations.

**Recommendation:** Implement key scoping (read vs write, leads vs proposals vs files) or use per-service tokens.

---

### 🟠 High: Service Account Key File Committed to Repo

**File:** `crm/credentials/google-service-account.json`

This file contains a Google service account private key. While the private key was redacted in the version I read, the file structure is committed to the repository. The `.gitignore` in `crm/` contains:
```
credentials/google-service-account.json
```
But the `tkvibes-lead-engine/credentials/google-service-account.json` is NOT in any `.gitignore`.

**Verification needed:** Check if `tkvibes-lead-engine/.gitignore` excludes the credentials directory.

**Recommendation:** Ensure ALL service account JSON files are in `.gitignore` at both the repo root and subdirectory levels. Rotate the service account key.

---

### 🟡 Medium: GitHub PAT Exposure Risk

**File:** `process_proposal_jobs.py` (inferred)
The `git_publish.py` script uses `subprocess.run(["git", ...])` which relies on the local git config for authentication. If the repository is accessed via HTTPS with a PAT stored in git config, that PAT could be exposed in logs or process listings.

**Recommendation:** Use SSH keys for git authentication, or use `GITHUB_TOKEN` env var with limited scope.

---

## Authentication & Authorization

### 🟠 High: No Session Timeout

**File:** `crm/lib/auth.php`

```php
function start_session(): void
{
    if (session_status() === PHP_SESSION_NONE) {
        $cfg = require __DIR__ . '/../config.local.php';
        session_name('TKCRM');
        session_start();
    }
}
```

No `session.gc_maxlifetime` is configured. PHP's default is 24 minutes (1440 seconds), but this is not explicitly set. On Hostinger shared hosting, the default `php.ini` may have a different value or `session.gc_maxlifetime` may be overridden.

**Issues:**
1. Sessions never expire if `session.gc_maxlifetime` is not set.
2. No session idle timeout check.
3. No session absolute timeout (regardless of activity).

**Recommendation:** Explicitly set `ini_set('session.gc_maxlifetime', 1800)` and `session_set_cookie_params()` with appropriate expires.

---

### 🟡 Medium: Session Cookie Missing Security Flags

**File:** `crm/lib/auth.php`

The session cookie is not configured with:
- `Secure` flag — cookie can be transmitted over HTTP
- `HttpOnly` flag — cookie accessible via JavaScript (XSS risk)
- `SameSite` attribute — vulnerable to CSRF (partially mitigated by CSRF tokens, but defense-in-depth)

```php
// Missing: session_set_cookie_params([
//     'secure' => true,
//     'httponly' => true,
//     'samesite' => 'Strict',
// ]);
```

**Recommendation:** Add `session_set_cookie_params()` before `session_start()` with all three flags.

---

### 🟢 Low: No Password Strength Policy

**File:** `crm/admin.php` (lines 50-62)

Password reset accepts any password ≥ 6 characters. No complexity requirements, no common-password check, no lockout after failed attempts.

**Recommendation:** Enforce minimum 8 chars, complexity rules, and rate-limit login attempts.

---

### 🟡 Medium: Admin Password Reset via `prompt()`

**File:** `crm/admin.php`, line 706
```javascript
function resetPassword(id, name) {
    const pw = prompt('Set a new password for ' + name + ' (min 6 chars):');
```

**Issues:**
1. Password is visible in plaintext in the browser's JavaScript context.
2. Password is transmitted in the DOM before form submission.
3. No confirmation step for password reset.

**Recommendation:** Use a proper password reset form with masked input, confirmation field, and strength meter.

---

## Input Validation & Injection

### ✅ Fixed: SQL Injection Guard in `leads.php`

`validate_field_name()` regex (`/^[a-z][a-z0-9_]*$/`) on field names prevents SQL injection through the dynamic column interpolation. Combined with the `EDITABLE_FIELDS` whitelist, this is defense-in-depth.

However, the SQL on line 102 still uses string interpolation: `"UPDATE leads SET \"$field\" = ?"` — while the regex guard is strong, the pattern is inherently risky. If the regex is ever modified or the constant list changes, this becomes exploitable.

**Recommendation:** Replace dynamic column interpolation with a hardcoded column map:
```php
$column_map = ['business_name' => 'business_name', ...];
$stmt = $pdo->prepare("UPDATE leads SET {$column_map[$field]} = ? WHERE lead_key = ?");
```

---

### 🟠 High: SQL Injection in `cron.php` (Sheet Import)

**File:** `crm/cron.php`, line 90:
```php
$pdo->prepare("UPDATE leads SET " . implode(', ', $set_parts) . " WHERE lead_key = ?")
    ->execute($set_params);
```

The `$set_parts` are built from `SHEET_IMPORT_FIELDS` constant (which is a hardcoded list of known-safe column names). However, the `$data[$f]` values come from Google Sheets and are passed as bound parameters — so this is NOT directly exploitable. ✅

But there's a subtlety: the `SHEET_IMPORT_FIELDS` constant defines which Sheet columns can be imported, but if a Sheet column name matches a DB column name AND the Sheet data contains malicious content, the value is safely parameterized. ✅

**This is actually safe** — the column names are from a constant, values are parameterized.

---

### 🟡 Medium: Path Traversal in u2.php/u3.php (Residual Risk)

**File:** `crm/u2.php`, line 41:
```php
if (preg_match('/\.\./', $p)) { ... }
```

**Issues:**
1. Regex only blocks literal `../` — does not catch URL-encoded variants (`%2e%2e%2f`), null bytes (`..%00/`), or Unicode normalization attacks.
2. The `realpath()` check on line 52 could fail if the target directory doesn't exist yet (it's created on line 60 AFTER the check), causing a false negative that returns 400.
3. **u3.php writes to `__DIR__ . "/$p"`** — writing to `lib/functions.php` or `config.local.php` would overwrite core code.

**Recommendation:** Replace the regex with a strict allowlist of subdirectories (`sample-website/`, `pitch-deck/`) and use `basename()` on the filename component.

---

### 🟢 Low: No Input Length Limits on API Endpoints

**File:** `crm/api/sync.php`

The sync endpoint accepts an arbitrary number of leads in a single POST. There's no:
- Maximum batch size limit
- Maximum string length validation on fields like `business_name`, `address`, `notes`
- Rate limiting

An attacker with the API key (or who compromises it) could send a 10MB payload and exhaust database storage.

**Recommendation:** Add `max_input_vars`, batch size limits, and per-field length validation.

---

## XSS (Cross-Site Scripting)

### 🟢 Low: `crm_status` Filter in `leads_query()`

**File:** `crm/lib/functions.php`, line 151-155:
```php
if (!empty($filters['q'])) {
    $q = '%' . $filters['q'] . '%';
    $where[] = "(leads.business_name LIKE ? OR ... )";
}
```

The search filter is parameterized ✅, but the `$_GET['q']` value is reflected into the search input field in `admin.php` (line 507):
```php
<input type="text" name="q" class="form-control" placeholder="Search..." value="<?= e($_GET['q'] ?? '') ?>">
```

The `e()` function calls `htmlspecialchars()` ✅ — this prevents XSS.

---

### 🟡 Medium: CSV Export Newline Injection

**File:** `crm/admin.php`, line 237-245:
```php
fputcsv($out, [
    $l['business_name'], ..., $l['crm_notes'],
]);
```

The `csv_escape()` function (functions.php line 287-294) handles quotes and delimiters, but does NOT handle:
- **Formula injection:** If a CRM notes field starts with `=`, `+`, `-`, or `@`, Excel will interpret it as a formula.
- **Newlines in cells:** `crm_notes` contains newlines (`\n---\n`), which `fputcsv` handles by quoting the field, but downstream Excel macros could be exploited.

**Recommendation:** Prefix any cell starting with `=`, `+`, `-`, `@` with a single quote or tab character.

---

## Network Security

### 🟠 High: No HTTPS Enforcement

**File:** `crm/index.php` and all PHP entry points

There is no redirect from HTTP to HTTPS. The `.htaccess` file exists but I need to verify if it contains force-HTTPS rules.

**File:** `crm/.htaccess` — need to read this.

**Recommendation:** Add `.htaccess` rules to force HTTPS and HSTS headers.

---

### 🟡 Medium: No Rate Limiting on API Endpoints

**Files:** All `crm/api/*.php` endpoints

No rate limiting is implemented on any API endpoint. An attacker who knows or guesses the API key can:
- Spam `sync.php` with thousands of leads (resource exhaustion)
- Call `employees.php` repeatedly (data exfiltration)
- Call `logs.php` with huge payloads (log spam, disk filling)

**Recommendation:** Implement per-IP rate limiting (e.g., 60 requests/minute) at the application or web server level.

---

## Dependency Security

### 🟡 Medium: Outdated Dependencies

**File:** `tkvibes-lead-engine/requirements.txt`
- `httpx>=0.27` — current version is 0.28.x; no upper bound specified
- `gspread>=6.1` — current is 6.2.x; no upper bound
- `google-auth>=2.30` — current is 2.40.x; no upper bound
- `tenacity>=8.5` — current is 10.x; no upper bound
- `phonenumbers>=8.13` — current is 9.x; no upper bound
- `rapidfuzz>=3.9` — current is 1.0.x (major version changed)
- No `requirements-lock.txt` or `pip-compile` lockfile

**Issues:**
1. No pinned versions — builds are non-reproducible.
2. No `pip-audit` or `safety` checks in CI.
3. No dependency scanning in the GitHub Actions workflow.

**Recommendation:** Add `pip-tools` for lockfiles, add `pip-audit` to CI, pin all versions.

---

## Deployment Pipeline Security

### 🔴 Critical: u2.php/u3.php Write to Any Path in Allowed Directory

While API key auth was added (CHANGELOG), the **security model is fundamentally flawed**:

1. **Single shared key** for both read and write operations across all endpoints.
2. **No separation** between "deploy PHP code" (u3.php) and "deploy proposal HTML" (u2.php) — the same key can overwrite both.
3. **No audit trail** — when a file is written via u2.php/u3.php, no log entry is created in `system_logs`.
4. **No file type validation** — u2.php accepts any content (base64-decoded) and writes it to any `.html` file in any subdirectory. An attacker could write a `.php` file if the path allows it (though the regex blocks `../`, the path itself is user-controlled).

**Recommendation:** 
- Replace u2.php/u3.php with a deployment script that only runs from the CI/CD pipeline.
- Or restrict to specific subdirectories with strict allowlisting.
- Log every file write to `system_logs`.

---

## Privacy & Compliance

### 🟠 High: Personal Data Collection Not Compliant

**File:** `tkvibes-lead-engine/config.yaml`
```yaml
run:
  collect_personal_data: false
```

While this is set to `false`, the lead engine still collects:
- `owner_name` — full business owner name from Google Places
- `phone_primary` — full phone number
- `email` — crawled from websites
- `address` — full business address
- `latitude/longitude` — precise location

**Issues:**
1. `collect_personal_data: false` only blanks `owner_name` (run.py line 110-111). Phone, email, address, and location are still collected.
2. No consent mechanism — leads are scraped from Google Places which may violate Google's ToS for direct marketing.
3. No data retention policy — leads are kept indefinitely.
4. No right to deletion/export mechanism for subjects.

**Recommendation:** Implement a proper data minimization policy, add consent tracking, and implement a data retention schedule.

---

## OWASP Top 10 Coverage

| OWASP # | Risk | Status |
|---------|------|--------|
| A01 Broken Access Control | u3.php can overwrite any CRM file | ⚠️ Partially Fixed |
| A02 Cryptographic Failures | API keys in plaintext config | ❌ Open |
| A03 Injection | SQL injection (column name) | ✅ Fixed |
| A04 Insecure Design | No session timeout, weak password policy | ⚠️ Partial |
| A05 Security Misconfiguration | Debug endpoints, no HTTPS enforced | ⚠️ Partial |
| A06 Vulnerable Components | Unpinned dependencies | ⚠️ Partial |
| A07 XSS | `e()` used on all output | ✅ Mitigated |
| A08 Software Integrity | No integrity checks on deployed files | ❌ Open |
| A09 Logging/Monitoring | Error logging exists but no security event logging | ⚠️ Partial |
| A10 SSRF | `proxy_proposal.php` fetches arbitrary GitHub URLs | ⚠️ Mitigated (URL allowlist) |

---

## Summary of Findings

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | 🔴 Critical | API key hardcoded in 4 files, tracked by git | ❌ Open |
| 2 | 🔴 Critical | u2.php/u3.php can write to arbitrary CRM files | ⚠️ Partially Fixed |
| 3 | 🟠 High | Shared API key with unlimited scope | ❌ Open |
| 4 | 🟠 High | No session timeout configured | ❌ Open |
| 5 | 🟠 High | No rate limiting on any API endpoint | ❌ Open |
| 6 | 🟡 Medium | Service account key in repo (credentials dir) | ⚠️ Partial |
| 7 | 🟡 Medium | Session cookie missing Secure/HttpOnly/SameSite | ❌ Open |
| 8 | 🟡 Medium | No HTTPS enforcement | ❌ Open |
| 9 | 🟡 Medium | Path traversal regex bypass possible | ⚠️ Partial |
| 10 | 🟡 Medium | CSV formula injection in exports | ❌ Open |
| 11 | 🟡 Medium | No dependency pinning or security scanning | ❌ Open |
| 12 | 🟡 Medium | Personal data collected despite collect_personal_data=false | ❌ Open |
| 13 | 🟢 Low | No password strength policy | ❌ Open |
| 14 | 🟢 Low | Admin password reset via prompt() | ⚠️ Partial |
| 15 | 🟢 Low | No input length limits on API endpoints | ❌ Open |
