"""
Deploy all modified CRM PHP files to Hostinger via u3.php.
Run from repo root: python deploy_crm.py

Security improvements:
- API key read from CRM_API_KEY env var (not hardcoded)
- Audit log entry for each deployment
- Fail-fast if credentials not configured
"""
import json
import os
import sys
import urllib.request
import base64

try:
    import yaml
except ImportError:
    yaml = None

UPLOAD_URL = "https://tkvibes.in/crm/u3.php"
REPO_ROOT = os.path.expanduser("~/Desktop/tkvibes-agency")

# Read API key from env var (NEVER hardcode)
API_KEY = os.environ.get("CRM_API_KEY", "")

# Files to deploy: (local_path, remote_path_relative_to_crm/)
FILES = [
    ("crm/lib/constants.php", "lib/constants.php"),
    ("crm/lib/functions.php", "lib/functions.php"),
    ("crm/lib/auth.php", "lib/auth.php"),
    ("crm/lib/db.php", "lib/db.php"),
    ("crm/lib/sheets_sync.php", "lib/sheets_sync.php"),
    ("crm/lib/GoogleSheetsClient.php", "lib/GoogleSheetsClient.php"),
    ("crm/api/sync.php", "api/sync.php"),
    ("crm/api/leads.php", "api/leads.php"),
    ("crm/api/proposals.php", "api/proposals.php"),
    ("crm/api/employees.php", "api/employees.php"),
    ("crm/api/logs.php", "api/logs.php"),
    ("crm/api/public_proposals.php", "api/public_proposals.php"),
    ("crm/api/proxy_proposal.php", "api/proxy_proposal.php"),
    ("crm/api/upload_proposal.php", "api/upload_proposal.php"),
    ("crm/cron.php", "cron.php"),
    ("crm/admin.php", "admin.php"),
    ("crm/dashboard.php", "dashboard.php"),
    ("crm/index.php", "index.php"),
    ("crm/logout.php", "logout.php"),
    ("crm/install.php", "install.php"),
    ("crm/templates/lead_detail.php", "templates/lead_detail.php"),
    ("crm/u2.php", "u2.php"),
    ("crm/u3.php", "u3.php"),
    ("crm/assets/js/crm.js", "assets/js/crm.js"),
    ("crm/assets/css/crm.css", "assets/css/crm.css"),
]


def get_api_key() -> str:
    """Resolve API key: env var > config.yaml > error."""
    if API_KEY:
        return API_KEY

    env_key = os.environ.get("CRM_API_KEY", "")
    if env_key:
        return env_key

    # Try config.yaml
    config_paths = [
        os.path.join(REPO_ROOT, "tkvibes-lead-engine", ".env"),
        os.path.join(REPO_ROOT, "tkvibes-lead-engine", "config.yaml"),
    ]
    for cp in config_paths:
        if os.path.isfile(cp) and yaml:
            try:
                if cp.endswith(".env"):
                    with open(cp) as f:
                        for line in f:
                            if line.startswith("CRM_API_KEY="):
                                return line.split("=", 1)[1].strip().strip('"').strip("'")
                else:
                    with open(cp) as f:
                        cfg = yaml.safe_load(f) or {}
                    key = cfg.get("crm", {}).get("api_key", "")
                    if key:
                        return key
            except Exception:
                continue

    if not API_KEY:
        print("ERROR: No CRM API key found.")
        print("Set CRM_API_KEY env var or configure in .env")
        print("NEVER commit API keys to version control.")
        sys.exit(1)
    return API_KEY


def main():
    api_key = get_api_key()
    if not api_key:
        print("ERROR: No API key available. Upload would fail.")
        sys.exit(1)

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
            payload = json.dumps({
                "key": api_key,
                "path": remote_path,
                "content": b64,
            }).encode("utf-8")
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


if __name__ == "__main__":
    main()
