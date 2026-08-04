# TKVibes Platform — Changelog

All notable changes to the TKVibes AI CRM platform are documented here.

## [Unreleased] — 2026-08-04

### Added
- Initial architecture audit (`.hermes/ARCHITECTURE-AUDIT.md`) — 48 issues found
- Test suite for lead engine Python modules (71 tests across 5 files)
- CRM smoke test script (`tests/smoke_crm.sh`) — verifies 8 API endpoints
- Test runner wrapper (`tests/run_tests.sh`)
- CHANGELOG.md — project changelog
- CSRF protection system: `csrf_token()`, `verify_csrf()`, `csrf_field()` helpers
- CSRF hidden fields on all lead detail forms (tag, note, called)
- CSRF token passed in AJAX proposal generation calls
- API key authentication on `u2.php` and `u3.php` upload endpoints
- Path traversal protection on `u2.php` and `u3.php` (regex + realpath)
- Field name validation guard (`validate_field_name()`) in `leads.php` (defense-in-depth against SQL injection)
- `upload_proposals.py` now reads API key from config.yaml or CRM_API_KEY env var

### Fixed
- **C1 (Critical)**: u2.php/u3.php — no authentication → now requires config.local.php api_key
- **C2 (Critical)**: leads.php — SQL injection in column name → added `validate_field_name()` regex guard
- **H2 (High)**: leads.php — `$_POST` fallback for JSON body clients → now reads from `$body` first with `$_POST` fallback
- **H8 (High)**: No CSRF protection on session-authenticated endpoints → added token generation + verification

### Changed
- `crm/lib/auth.php` — added `csrf_token()`, `verify_csrf()`, session_regenerate_id on login
- `crm/lib/functions.php` — added `csrf_field()` helper
- `crm/api/leads.php` — CSRF verification for session mode, JSON body parameter reads, field name validation
- `crm/api/proposals.php` — CSRF verification on `generate` action
- `crm/dashboard.php` — CSRF_TOKEN injected for JS use
- `crm/assets/js/crm.js` — CSRF token appended to proposal generation fetch calls
- `crm/templates/lead_detail.php` — CSRF hidden fields on all forms
- `crm/u2.php`, `crm/u3.php` — API key auth + realpath path traversal guard + error messages
- `upload_proposals.py` — API key resolution from config/env, error handling, dry-run mode

### Security
- All file upload endpoints now require authentication
- SQL injection defense-in-depth for dynamic column names
- CSRF protection on all state-changing session-authenticated actions
- Session ID regeneration on login (session fixation prevention)