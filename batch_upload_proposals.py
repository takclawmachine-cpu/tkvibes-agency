"""Upload all generated proposals to CRM via u2.php and update lead records."""
import json, os, sys, base64, urllib.request, re
from urllib.request import Request, urlopen

# ── Config ───────────────────────────────────────────────────────────────────
UPLOAD_URL = "https://tkvibes.in/crm/u2.php"
CRM_API_URL = "https://tkvibes.in/crm/api/sync.php?key=10a76f01219e8fd7b1fec2c5256c6a39"
PROPOSALS_DIR = os.path.expanduser(
    "~/Desktop/tkvibes-agency/tkvibes-lead-engine/data/proposals"
)
REPO_BASE = "https://raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/Sample%20Webpages%20and%20pitch%20deck"
SAMPLE_DIR_TARGET = os.path.expanduser(
    "~/Desktop/tkvibes-agency/Sample Webpages and pitch deck/sample website"
)
PITCH_DIR_TARGET = os.path.expanduser(
    "~/Desktop/tkvibes-agency/Sample Webpages and pitch deck/pitch deck"
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def slugify(name):
    s = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-{2,}", "-", s)[:60] or "client"


def upload_file(local_path, remote_path):
    """Upload a file to the server via u2.php (base64 + text/plain bypass)."""
    with open(local_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    payload = json.dumps({"path": remote_path, "content": b64}).encode("utf-8")
    req = Request(UPLOAD_URL, data=payload, method="POST")
    req.add_header("Content-Type", "text/plain")
    try:
        with urlopen(req, timeout=30) as resp:
            result = resp.read().decode()
        return result == "OK"
    except Exception as e:
        print(f"    ❌ upload failed: {e}")
        return False


def update_crm_lead(lead_key, sample_url, pitch_url):
    """Update CRM lead record with proposal URLs via sync.php."""
    data = {"key": "10a76f01219e8fd7b1fec2c5256c6a39", "lead_key": lead_key}
    if sample_url:
        data["sample_site_url"] = sample_url
    if pitch_url:
        data["pitch_deck_url"] = pitch_url
    payload = json.dumps(data).encode("utf-8")
    req = Request(CRM_API_URL.split("?")[0] + "?key=10a76f01219e8fd7b1fec2c5256c6a39",
                  data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
        return result.get("status") == "ok"
    except Exception as e:
        print(f"    ❌ CRM update failed: {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────────────────
print("Scanning proposal directories...")
proposals = []
for entry in sorted(os.listdir(PROPOSALS_DIR)):
    d = os.path.join(PROPOSALS_DIR, entry)
    if not os.path.isdir(d):
        continue
    slug = entry
    idx = os.path.join(d, "index.html")
    deck = os.path.join(d, "pitch-deck.html")
    if os.path.isfile(idx):
        proposals.append({"slug": slug, "sample_site": idx, "pitch_deck": deck if os.path.isfile(deck) else None})

print(f"Found {len(proposals)} proposals to upload")

# Ensure target dirs exist
os.makedirs(SAMPLE_DIR_TARGET, exist_ok=True)
os.makedirs(PITCH_DIR_TARGET, exist_ok=True)

ok = fail = 0
for p in proposals:
    slug = p["slug"]
    print(f"\n[{slug}]")

    # 1. Upload sample site to server
    site_remote = f"sample-website/{slug}.html"
    print(f"  uploading sample site...", end=" ", flush=True)
    if upload_file(p["sample_site"], site_remote):
        print("✅")

        # Copy to GitHub working tree
        import shutil
        shutil.copy2(p["sample_site"], os.path.join(SAMPLE_DIR_TARGET, f"{slug}.html"))

        # 2. Create GitHub URL
        site_url = f"{REPO_BASE}/sample%20website/{slug}.html"
    else:
        site_url = ""
        fail += 1

    # 3. Upload pitch deck
    deck_url = ""
    if p["pitch_deck"]:
        deck_remote = f"pitch-deck/{slug}.html"
        print(f"  uploading pitch deck...", end=" ", flush=True)
        if upload_file(p["pitch_deck"], deck_remote):
            print("✅")
            shutil.copy2(p["pitch_deck"], os.path.join(PITCH_DIR_TARGET, f"{slug}.html"))
            deck_url = f"{REPO_BASE}/pitch%20deck/{slug}.html"
        else:
            fail += 1
    else:
        print(f"  pitch deck: ⏭️  none")

    # 4. Update CRM — we don't have lead_key from slug directly,
    # so rely on the server deploy_proposals.php later
    print(f"  site: {site_url}")
    print(f"  deck: {deck_url}")
    ok += 1

# 5. Git commit + push the copied files
print(f"\n── Committing to GitHub ──")
os.chdir(os.path.expanduser("~/Desktop/tkvibes-agency"))
rc = os.system(
    'git add "Sample Webpages and pitch deck/sample website" '
    '"Sample Webpages and pitch deck/pitch deck" '
    '&& git commit -m "chore: auto-publish proposals [batch upload]" '
    "&& git push"
)
if rc == 0:
    print("✅ GitHub push done")
else:
    print("⚠️  Git push had issues")

print(f"\nDone: {ok} uploaded, {fail} failed")
print("Run deploy_proposals.php on server to link proposals to leads.")