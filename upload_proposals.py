"""Upload proposal HTML files to tkvibes.in via u2.php (base64 encoded).

Usage:
    python upload_proposals.py                               # from repo root
    python upload_proposals.py --dry-run                     # preview only
    python upload_proposals.py --key YOUR_API_KEY            # explicit key

The API key is loaded from tkvibes-lead-engine/config.yaml → crm.api_key,
or can be passed via --key or the CRM_API_KEY env var.
"""
import argparse
import json
import os
import sys
import urllib.request
import base64

try:
    import yaml
except ImportError:
    yaml = None

UPLOAD_URL = "https://tkvibes.in/crm/u2.php"
PROPOSALS_DIR = os.path.expanduser("~/Desktop/tkvibes-agency/Sample Webpages and pitch deck")


def get_api_key(cli_key: str | None) -> str:
    """Resolve API key: CLI arg → env var → config.yaml."""
    if cli_key:
        return cli_key
    env_key = os.environ.get("CRM_API_KEY", "")
    if env_key:
        return env_key
    # Try config.yaml
    config_paths = [
        os.path.expanduser("~/Desktop/tkvibes-agency/tkvibes-lead-engine/config.yaml"),
        "tkvibes-lead-engine/config.yaml",
        "../tkvibes-lead-engine/config.yaml",
    ]
    for cp in config_paths:
        if os.path.isfile(cp) and yaml:
            try:
                with open(cp) as f:
                    cfg = yaml.safe_load(f) or {}
                key = cfg.get("crm", {}).get("api_key", "")
                if key:
                    return key
            except Exception:
                continue
    print("WARNING: No API key found. Set CRM_API_KEY env var, pass --key, "
          "or ensure tkvibes-lead-engine/config.yaml has crm.api_key.")
    return ""


def main():
    ap = argparse.ArgumentParser(description="Upload proposals to tkvibes.in")
    ap.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    ap.add_argument("--key", default=None, help="CRM API key (overrides config.yaml)")
    args = ap.parse_args()

    api_key = get_api_key(args.key)
    if not api_key:
        print("ERROR: No API key available. Upload would fail.")
        sys.exit(1)

    files = []
    sw_dir = os.path.join(PROPOSALS_DIR, "sample website")
    if os.path.isdir(sw_dir):
        for fn in sorted(os.listdir(sw_dir)):
            if fn.endswith(".html"):
                files.append((os.path.join(sw_dir, fn), f"sample-website/{fn}"))

    pd_dir = os.path.join(PROPOSALS_DIR, "pitch deck")
    if os.path.isdir(pd_dir):
        for fn in sorted(os.listdir(pd_dir)):
            if fn.endswith(".html"):
                files.append((os.path.join(pd_dir, fn), f"pitch-deck/{fn}"))

    if not files:
        print("No HTML files found in Sample Webpages directory.")
        return

    print(f"Found {len(files)} files to upload")

    if args.dry_run:
        print("Dry-run mode — no files uploaded")
        for _, remote_path in files:
            print(f"  Would upload: {remote_path}")
        return

    ok = fail = 0
    for local_path, remote_path in files:
        try:
            with open(local_path, "rb") as f:
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


if __name__ == "__main__":
    main()