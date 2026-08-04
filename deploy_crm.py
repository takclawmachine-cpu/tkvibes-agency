"""
Deploy all modified CRM PHP files to Hostinger via u2.php.
Run from repo root: python deploy_crm.py
"""
import json
import os
import sys
import urllib.request
import base64

UPLOAD_URL = "https://tkvibes.in/crm/u3.php"
API_KEY = "10a76f01219e8fd7b1fec2c5256c6a39"
REPO_ROOT = os.path.expanduser("~/Desktop/tkvibes-agency")

# Files to deploy: (local_path, remote_path_relative_to_crm/)
# u3.php writes to __DIR__ . '/' + path, so paths are relative to /crm/
FILES = [
    ("crm/lib/constants.php", "lib/constants.php"),
    ("crm/lib/functions.php", "lib/functions.php"),
    ("crm/lib/auth.php", "lib/auth.php"),
    ("crm/lib/db.php", "lib/db.php"),
    ("crm/lib/sheets_sync.php", "lib/sheets_sync.php"),
    ("crm/api/sync.php", "api/sync.php"),
    ("crm/api/leads.php", "api/leads.php"),
    ("crm/api/proposals.php", "api/proposals.php"),
    ("crm/api/logs.php", "api/logs.php"),
    ("crm/api/employees.php", "api/employees.php"),
    ("crm/api/public_proposals.php", "api/public_proposals.php"),
    ("crm/cron.php", "cron.php"),
    ("crm/admin.php", "admin.php"),
    ("crm/dashboard.php", "dashboard.php"),
    ("crm/templates/lead_detail.php", "templates/lead_detail.php"),
    ("crm/u2.php", "u2.php"),
    ("crm/u3.php", "u3.php"),
    ("crm/assets/js/crm.js", "assets/js/crm.js"),
]

ok = fail = 0
for local_path, remote_path in FILES:
    abs_path = os.path.join(REPO_ROOT, local_path)
    if not os.path.isfile(abs_path):
        print(f"  SKIP {local_path} (not found)")
        fail += 1
        continue
    try:
        with open(abs_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        # u2.php writes to dirname(__DIR__) . '/proposals/' + path
        # So '../crm/lib/functions.php' becomes /home/.../public_html/crm/lib/functions.php
        payload = json.dumps({"key": API_KEY, "path": remote_path, "content": b64}).encode("utf-8")
        req = urllib.request.Request(UPLOAD_URL, data=payload, method="POST")
        req.add_header("Content-Type", "text/plain")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode()
        if result == "OK":
            ok += 1
            print(f"  ✅ {remote_path}")
        else:
            fail += 1
            print(f"  ❌ {remote_path}: {result}")
    except urllib.error.HTTPError as e:
        fail += 1
        body = e.read().decode() if e.fp else str(e)
        print(f"  ❌ {remote_path}: HTTP {e.code} — {body.strip()}")
    except Exception as e:
        fail += 1
        print(f"  ❌ {remote_path}: {e}")

print(f"\nDone: {ok} uploaded, {fail} failed")
if fail > 0:
    sys.exit(1)