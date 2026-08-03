"""Upload proposal HTML files to tkvibes.in via u2.php."""
import json, os, sys, urllib.request

UPLOAD_URL = "https://tkvibes.in/crm/u2.php"
PROPOSALS_DIR = os.path.expanduser("~/Desktop/tkvibes-agency/Sample Webpages and pitch deck")

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

print(f"Found {len(files)} files")
ok = fail = 0
for local_path, remote_path in files:
    try:
        with open(local_path, "rb") as f:
            content = f.read().decode("utf-8")
        payload = json.dumps({"path": remote_path, "content": content}).encode("utf-8")
        req = urllib.request.Request(UPLOAD_URL, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode()
        if result == "OK":
            ok += 1; print(f"  ✅ {remote_path}")
        else:
            fail += 1; print(f"  ❌ {remote_path}: {result}")
    except Exception as e:
        fail += 1; print(f"  ❌ {remote_path}: {e}")

print(f"\nDone: {ok} uploaded, {fail} failed")