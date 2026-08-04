#!/usr/bin/env bash
# TKVibes — Run All Tests
#
# Python unit tests (lead engine):
#     bash tests/run_tests.sh
#
# Python + CRM smoke tests:
#     CRM_KEY=your_key bash tests/run_tests.sh
set -euo pipefail

LEAD_ENGINE_DIR="$(cd "$(dirname "$0")/../tkvibes-lead-engine" && pwd)"
VENV_PYTHON="$LEAD_ENGINE_DIR/.venv/Scripts/python"

echo "=== TKVibes Test Suite ==="
echo ""

# ── Python unit tests ──
echo "--- Lead Engine Unit Tests ---"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: Venv Python not found at $VENV_PYTHON"
    echo "Run: cd tkvibes-lead-engine && python -m venv .venv && .venv/Scripts/pip install -e ."
    exit 1
fi

cd "$LEAD_ENGINE_DIR"
"$VENV_PYTHON" -m pytest tests/ -v --tb=short
PY_EXIT=$?
echo ""

# ── CRM Smoke Tests (optional, needs live server) ──
if [ -n "${CRM_KEY:-}" ]; then
    echo "--- CRM Smoke Tests ---"
    CRM_BASE="${CRM_BASE:-https://tkvibes.in/crm}"
    CRM_KEY="$CRM_KEY" bash "$(cd "$(dirname "$0")" && pwd)/smoke_crm.sh"
    CRM_EXIT=$?
else
    echo "--- CRM Smoke Tests (skipped, set CRM_KEY env var) ---"
    CRM_EXIT=0
fi

echo ""
echo "=== Summary ==="
echo "  Python unit tests: $([ $PY_EXIT -eq 0 ] && echo 'PASS' || echo 'FAIL')"
echo "  CRM smoke tests:   $([ $CRM_EXIT -eq 0 ] && echo 'PASS' || echo 'SKIPPED/FAIL')"

exit $((PY_EXIT + CRM_EXIT))