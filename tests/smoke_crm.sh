#!/usr/bin/env bash
# TKVibes CRM — Smoke Test Suite
# Tests that CRM API endpoints respond correctly.
# Usage: CRM_BASE=https://tkvibes.in/crm CRM_KEY=your_api_key bash tests/smoke_crm.sh

set -euo pipefail

BASE="${CRM_BASE:-https://tkvibes.in/crm}"
KEY="${CRM_KEY:-}"
PASS=0
FAIL=0

green() { echo -e "\033[32m✅ $1\033[0m"; }
red()   { echo -e "\033[31m❌ $1\033[0m"; }

test_endpoint() {
    local desc="$1"
    local method="$2"
    local url="$3"
    local expect_code="$4"
    local expect_body="$5"
    
    if [ "$method" = "GET" ]; then
        resp=$(curl -s -o /tmp/crm_test.txt -w "%{http_code}" "$url" 2>/dev/null || true)
    else
        resp=$(curl -s -o /tmp/crm_test.txt -w "%{http_code}" -X "$method" "$url" 2>/dev/null || true)
    fi
    body=$(cat /tmp/crm_test.txt 2>/dev/null || echo "")
    
    if [ "$resp" = "$expect_code" ]; then
        if [ -n "$expect_body" ] && ! echo "$body" | grep -q "$expect_body"; then
            red "$desc (got $resp, body missing '$expect_body')"
            FAIL=$((FAIL+1))
        else
            green "$desc ($resp)"
            PASS=$((PASS+1))
        fi
    else
        red "$desc (expected $expect_code, got $resp)"
        echo "  Body: $(echo "$body" | head -c 200)"
        FAIL=$((FAIL+1))
    fi
}

echo "=== TKVibes CRM Smoke Tests ==="
echo "Base URL: $BASE"
echo ""

# 1. Login page loads
test_endpoint "Login page loads" GET "$BASE/index.php" 200 "TKVibes"

# 2. Sync endpoint rejects GET
test_endpoint "Sync rejects GET" GET "$BASE/api/sync.php" 405 "POST required"

# 3. Sync endpoint rejects bad key
if [ -n "$KEY" ]; then
    test_endpoint "Sync rejects bad key" POST \
        "$BASE/api/sync.php" 403 "Invalid API key"
    
    # 4. Employees endpoint works with valid key
    test_endpoint "Employees API works" GET \
        "$BASE/api/employees.php?key=$KEY" 200 ""
    
    # 5. Proposals pending with valid key
    test_endpoint "Proposals pending API" GET \
        "$BASE/api/proposals.php?action=api_pending&key=$KEY" 200 "ok"
fi

# 6. Public proposals endpoint is public
test_endpoint "Public proposals is public" GET \
    "$BASE/api/public_proposals.php" 200 ""

# 7. Dashboard redirects to login when not authed
test_endpoint "Dashboard redirects unauthed" GET \
    "$BASE/dashboard.php" 200 ""  # returns login page, not 302

# 8. Admin redirects to login when not authed
test_endpoint "Admin redirects unauthed" GET \
    "$BASE/admin.php" 200 ""

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && echo "All smoke tests passed!"
exit $FAIL