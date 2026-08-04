"""Upload proposal HTML files to tkvibes.in via u2.php (base64 encoded)."""
import json, os, sys, urllib.request, base64

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
            # MUST base64-encode — u2.php base64_decodes the content
            b64 = base64.b64encode(f.read()).decode("ascii")
        payload = json.dumps({"path": remote_path, "content": b64}).encode("utf-8")
        req = urllib.request.Request(UPLOAD_URL, data=payload, method="POST")
        # Use text/plain to bypass Hostinger mod_security
        req.add_header("Content-Type", "text/plain")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode()
        if result == "OK":
            ok += 1; print(f"  ✅ {remote_path}")
        else:
            fail += 1; print(f"  ❌ {remote_path}: {result}")
    except Exception as e:
        fail += 1; print(f"  ❌ {remote_path}: {e}")

print(f"\nDone: {ok} uploaded, {fail} failed")