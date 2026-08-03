"""Push generated proposal files (sample sites + pitch decks) to the CRM.

After the website agent and deck agent generate HTML files in
data/proposals/<slug>/ or ~/Desktop/clients/<slug>/, run this script
to push them to the CRM so employees can view/download them.

Usage:
    python -m src.push_proposals                  # push all from data/proposals/
    python -m src.push_proposals --lead-key KEY   # push for one lead
    python -m src.push_proposals --dry-run        # show what would be pushed
"""

import argparse
import json
import os
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

from dotenv import load_dotenv

from .config import load_config
from .models import Lead

PROPOSALS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "proposals")


def slugify(name: str) -> str:
    """Match the slugify in scaffold_clients.py."""
    if not (name or "").strip():
        return "client"
    s = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-{2,}", "-", s)[:60] or "client"


def find_proposal_files(lead_key: str, slug: str) -> dict:
    """Find sample site and pitch deck files for a lead.

    Looks in:
      data/proposals/<slug>-website.html
      data/proposals/<slug>/index.html
      data/proposals/<slug>/pitch-deck.html
      ~/Desktop/clients/<slug>/<slug>-website.html
      ~/Desktop/clients/<slug>/<slug>-pitch-deck.html
    """
    results = {}
    proposals_dir = PROPOSALS_DIR
    clients_dir = os.path.expanduser("~/Desktop/clients")

    # Sample site — flat file
    paths = [
        os.path.join(proposals_dir, f"{slug}-website.html"),
        os.path.join(proposals_dir, f"{slug}.html"),
        os.path.join(clients_dir, slug, f"{slug}-website.html"),
    ]
    for p in paths:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                results["sample_site"] = {"html": f.read(), "path": p}
            break

    # Sample site — folder/index.html
    folder_idx = os.path.join(proposals_dir, slug, "index.html")
    if "sample_site" not in results and os.path.isfile(folder_idx):
        with open(folder_idx, "r", encoding="utf-8") as f:
            results["sample_site"] = {"html": f.read(), "path": folder_idx}

    # Pitch deck
    paths = [
        os.path.join(proposals_dir, f"{slug}-pitch-deck.html"),
        os.path.join(proposals_dir, slug, "pitch-deck.html"),
        os.path.join(clients_dir, slug, f"{slug}-pitch-deck.html"),
    ]
    for p in paths:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                results["pitch_deck"] = {"html": f.read(), "path": p}
            break

    return results


def push_to_crm(lead_key: str, type_: str, html: str, filename: str,
                api_url: str, api_key: str) -> dict:
    """POST a proposal to the CRM."""
    payload = json.dumps({
        "key": api_key,
        "lead_key": lead_key,
        "type": type_,
        "html": html,
        "file_name": filename,
    }).encode("utf-8")

    url = f"{api_url.rstrip('/')}/api/proposals.php"
    req = Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        return result
    except URLError as e:
        return {"status": "error", "reason": str(e)}
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"bad response: {e}"}


def main():
    ap = argparse.ArgumentParser(description="Push proposals to CRM")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--lead-key", default=None, help="Push for one lead (by lead_key)")
    ap.add_argument("--slug", default=None, help="Slug (if lead_key is ambiguous)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--file", default=None, help="Push a single file (with --type)")
    ap.add_argument("--type", default=None, help="Type: sample_site or pitch_deck (with --file)")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config(args.config)
    crm_cfg = cfg.get("crm", {}) or {}
    api_url = crm_cfg.get("api_url", "")
    api_key = crm_cfg.get("api_key", "")

    if not api_url or not api_key:
        print("ERROR: CRM API URL/KEY not configured in config.yaml")
        sys.exit(1)

    # Single file mode
    if args.file and args.type:
        if not os.path.isfile(args.file):
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            html = f.read()
        if args.dry_run:
            print(f"[dry-run] would push {args.type} from {args.file} for lead {args.lead_key or '?'}")
            return
        result = push_to_crm(args.lead_key or "", args.type, html,
                             os.path.basename(args.file), api_url, api_key)
        print(f"  Push: {result.get('status', 'error')} — {args.type}")
        if result.get("status") != "ok":
            print(f"  Error: {result.get('reason', 'unknown')}")
        return

    # Batch mode: scan data/proposals/ directory
    if not os.path.isdir(PROPOSALS_DIR):
        print(f"No proposals directory at {PROPOSALS_DIR}")
        return

    # Try to load handoff JSON to map slug → lead_key
    export_path = cfg["handoff"]["export_json"]
    lead_map = {}  # slug → lead_key
    if os.path.isfile(export_path):
        with open(export_path, encoding="utf-8") as f:
            leads_data = json.load(f)
        for ld in leads_data:
            slug = slugify(ld.get("business_name", ""))
            lead_map[slug] = ld.get("lead_key", "")

    # Also check wa_links.json
    wa_path = os.path.join(PROPOSALS_DIR, "wa_links.json")
    if os.path.isfile(wa_path):
        with open(wa_path, encoding="utf-8") as f:
            wa_data = json.load(f)
        for item in wa_data:
            slug = slugify(item.get("business_name", ""))
            if slug not in lead_map:
                lead_map[slug] = item.get("lead_key", "")

    pushed = 0
    errors = 0

    # Scan the proposals directory
    for entry in os.listdir(PROPOSALS_DIR):
        if entry.startswith(".") or entry in ("template.html", "template-v2.html", "wa_links.json"):
            continue

        # Determine slug
        slug = entry
        if entry.endswith(".html"):
            slug = slug[:-5]  # remove .html

        lead_key = lead_map.get(slug, "")
        if not lead_key and args.lead_key:
            lead_key = args.lead_key

        if not lead_key:
            print(f"  SKIP {entry}: no lead_key mapping for slug '{slug}'")
            continue

        # Find proposal files
        proposals = find_proposal_files(lead_key, slug)
        if not proposals:
            print(f"  SKIP {entry}: no proposal files found")
            continue

        for type_, info in proposals.items():
            filename = os.path.basename(info["path"])
            if args.dry_run:
                print(f"  [dry-run] {lead_key} → {type_} ({filename}, {len(info['html'])} chars)")
                continue
            result = push_to_crm(lead_key, type_, info["html"], filename, api_url, api_key)
            if result.get("status") == "ok":
                pushed += 1
                print(f"  ✅ {lead_key} → {type_} ({filename})")
            else:
                errors += 1
                print(f"  ❌ {lead_key} → {type_}: {result.get('reason', 'error')}")

    if not args.dry_run:
        print(f"\nDone: {pushed} pushed, {errors} errors")
    else:
        print(f"\nDry-run: would push proposals")


if __name__ == "__main__":
    main()