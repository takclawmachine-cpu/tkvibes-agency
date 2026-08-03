"""Upload proposal HTML files to tkvibes.in via the u2.php endpoint."""
import json, os, sys, base64, urllib.request

UPLOAD_URL = "https://tkvibes.in/crm/u2.php"
PROPOSALS_DIR = os.path.expanduser("~/Desktop/tkvibes-agency/Sample Webpages and pitch deck")
BASE_PATH = "/home/u990668815/domains/tkvibes.in/public_html/proposals"

files = []

# Sample websites
sw_dir = os.path.join(PROPOSALS_DIR, "sample website")
if os.path.isdir(sw_dir):
    for fn in os.listdir(sw_dir):
        if fn.endswith(".html"):
            files.append((os.path.join(sw_dir, fn), f"{BASE_PATH}/sample-website/{fn}"))

# Pitch decks
pd_dir = os.path.join(PROPOSALS_DIR, "pitch deck")
if os.path.isdir(pd_dir):
    for fn in os.listdir(pd_dir):
        if fn.endswith(".html"):
            files.append((os.path.join(pd_dir, fn), f"{BASE_PATH}/pitch-deck/{fn}"))

print(f"Found {len(files)} files to upload ({len([f for f in os.listdir(sw_dir) if f.endswith('.html')])} sample + {len([f for f in os.listdir(pd_dir) if f.endswith('.html')])} deck)")

ok = 0
fail = 0
for local_path, remote_path in files:
    try:
        with open(local_path, "rb") as f:
            content = f.read().decode("utf-8")
        
        payload = json.dumps({"f": remote_path, "c": content}).encode("utf-8")
        req = urllib.request.Request(UPLOAD_URL, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode()
        
        if result == "OK":
            ok += 1
            print(f"  ✅ {os.path.basename(local_path)}")
        else:
            fail += 1
            print(f"  ❌ {os.path.basename(local_path)}: {result}")
    except Exception as e:
        fail += 1
        print(f"  ❌ {os.path.basename(local_path)}: {e}")

print(f"\nDone: {ok} uploaded, {fail} failed")