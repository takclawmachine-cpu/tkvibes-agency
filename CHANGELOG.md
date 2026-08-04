# TKVibes Platform — Changelog

All notable changes to the TKVibes AI CRM platform are documented here.

## [Unreleased] — 2026-08-04

### Added
- Initial architecture audit (`.hermes/ARCHITECTURE-AUDIT.md`) — 48 issues found
- Test suite for lead engine Python modules:
  - `tests/test_models.py` — 17 tests for Lead dataclass (defaults, type coercion, dates, serialization)
  - `tests/test_score.py` — 19 tests for scoring logic (baselines, modifiers, tier assignment, edge cases)
  - `tests/test_config.py` — 9 tests for YAML config loader (valid/invalid, missing sections/keys, empty lists)
  - `tests/test_assign.py` — 10 tests for employee assignment (country config, CRM API, mixed countries, edge cases)
  - `tests/test_pain_points_visuals.py` — 12 tests for pain points generation and visual config (categories, colors, phone sanitization, services HTML)
- CRM smoke test script (`tests/smoke_crm.sh`) — verifies 8 API endpoints respond correctly
- Test runner wrapper (`tests/run_tests.sh`) — runs all Python + optional CRM smoke tests
- CHANGELOG.md — project changelog

### Fixed
- (nothing yet — Phase 1: test infrastructure complete)

### Changed
- (nothing yet — Phase 1: no production code modified)