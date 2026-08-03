"""Publish sample websites and pitch decks to GitHub under the
"Sample Webpages and pitch deck" folder structure.

Copies generated HTML files from data/proposals/<slug>/ to:
  Sample Webpages and pitch deck/sample website/<slug>.html
  Sample Webpages and pitch deck/pitch deck/<slug>.html

Then commits and pushes to GitHub.

Usage:
    python -m src.git_publish
    python -m src.git_publish --dry-run
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

from .config import load_config

REPO_DIR = os.path.expanduser("~/Desktop/tkvibes-agency")
PROPOSALS_DIR = os.path.join(REPO_DIR, "tkvibes-lead-engine", "data", "proposals")

# GitHub folder structure
SAMPLE_DIR = "Sample Webpages and pitch deck/sample website"
PITCH_DIR = "Sample Webpages and pitch deck/pitch deck"


def slugify(name: str) -> str:
    if not (name or "").strip():
        return "client"
    s = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-{2,}", "-", s)[:60] or "client"


def _run_git(args: list[str], workdir: str = REPO_DIR) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, cwd=workdir, timeout=30
    )
    if result.returncode != 0:
        print(f"  git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def publish(lead_key: str = None, dry_run: bool = False) -> list[dict]:
    """Publish generated proposals to GitHub.

    Returns list of dicts with published URLs.
    """
    os.chdir(REPO_DIR)

    # Load generation results to know what was generated
    results_path = os.path.join(PROPOSALS_DIR, "_generation_results.json")
    if not os.path.isfile(results_path):
        # Scan the proposals directory directly
        results = []
        for entry in os.listdir(PROPOSALS_DIR):
            slug_dir = os.path.join(PROPOSALS_DIR, entry)
            if not os.path.isdir(slug_dir) or entry.startswith("."):
                continue
            index = os.path.join(slug_dir, "index.html")
            deck = os.path.join(slug_dir, "pitch-deck.html")
            has_site = os.path.isfile(index)
            has_deck = os.path.isfile(deck)
            if has_site or has_deck:
                results.append({
                    "slug": entry,
                    "index": index if has_site else None,
                    "deck": deck if has_deck else None,
                    "lead_key": "",
                })
    else:
        with open(results_path, encoding="utf-8") as f:
            results = json.load(f)

    if not results:
        print("No proposals found to publish.")
        return []

    # Filter by lead_key if specified
    if lead_key:
        results = [r for r in results if r.get("lead_key") == lead_key]
        if not results:
            print(f"No proposals found for lead_key: {lead_key}")
            return []

    # Ensure we're on main and up to date
    _run_git(["fetch", "origin"])
    _run_git(["checkout", "main"])

    published = []
    for result in results:
        slug = result.get("slug", "")
        if not slug:
            continue

        # Copy sample site
        site_src = result.get("index") or (result.get("index") or "")
        if site_src and os.path.isfile(site_src):
            dest_name = f"{slug}.html"
            dest = os.path.join(REPO_DIR, SAMPLE_DIR, dest_name)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(site_src, dest)
            print(f"  📄 sample website: {slug}.html")
        else:
            dest = None

        # Copy pitch deck
        deck_src = result.get("deck") or (result.get("deck") or "")
        if deck_src and os.path.isfile(deck_src):
            deck_dest_name = f"{slug}.html"
            deck_dest = os.path.join(REPO_DIR, PITCH_DIR, deck_dest_name)
            os.makedirs(os.path.dirname(deck_dest), exist_ok=True)
            shutil.copy2(deck_src, deck_dest)
            print(f"  📄 pitch deck: {slug}.html")
        else:
            deck_dest = None

        # Build GitHub raw URLs
        if dest:
            relative = os.path.relpath(dest, REPO_DIR).replace("\\", "/")
            site_url = f"https://raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/{relative}"
        else:
            site_url = ""

        if deck_dest:
            relative_deck = os.path.relpath(deck_dest, REPO_DIR).replace("\\", "/")
            deck_url = f"https://raw.githubusercontent.com/takclawmachine-cpu/tkvibes-agency/main/{relative_deck}"
        else:
            deck_url = ""

        published.append({
            "slug": slug,
            "lead_key": result.get("lead_key", ""),
            "business_name": result.get("business_name", slug),
            "sample_site_path": dest,
            "pitch_deck_path": deck_dest,
            "sample_site_url": site_url,
            "pitch_deck_url": deck_url,
        })

    if not dry_run:
        # Commit and push
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        # Stage all files in the Sample Webpages directory
        _run_git(["add", SAMPLE_DIR, PITCH_DIR])
        status = _run_git(["status", "--porcelain"])
        if status:
            _run_git(["commit", "-m", f"chore: auto-publish sample sites + pitch decks [{timestamp}]"])
            _run_git(["push", "origin", "main"])
            print(f"\n✅ Pushed {len(published)} proposals to GitHub")
        else:
            print("\nNo changes to commit (files already up to date)")

        # Push GitHub URLs to CRM so they show in lead detail
        _push_urls_to_crm(published)
    else:
        print(f"\n[dry-run] Would publish {len(published)} proposals to GitHub")

    return published


def _push_urls_to_crm(published: list[dict]):
    """Push GitHub URLs to CRM so they show up in lead detail view."""
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    if not os.path.isfile(cfg_path):
        print("  ⚠️  config.yaml not found — skipping CRM URL update")
        return

    cfg = load_config(cfg_path)
    crm_cfg = cfg.get("crm", {}) or {}
    api_url = crm_cfg.get("api_url", "").rstrip("/")
    api_key = crm_cfg.get("api_key", "")

    if not api_url or not api_key:
        print("  ⚠️  CRM API not configured — skipping CRM URL update")
        return

    for p in published:
        lead_key = p.get("lead_key", "")
        if not lead_key:
            continue

        # Update sample_site_url
        if p.get("sample_site_url"):
            try:
                payload = json.dumps({
                    "key": api_key,
                    "lead_key": lead_key,
                    "action": "update",
                    "field": "sample_site_url",
                    "value": p["sample_site_url"],
                }).encode("utf-8")
                req = Request(f"{api_url}/api/leads.php", data=payload, method="POST")
                req.add_header("Content-Type", "application/json")
                with urlopen(req, timeout=15) as resp:
                    json.loads(resp.read().decode())
                print(f"  ✅ CRM: updated sample_site_url for {lead_key}")
            except Exception as e:
                print(f"  ⚠️  CRM: failed to update sample_site_url for {lead_key}: {e}")

        # Update pitch_deck_url
        if p.get("pitch_deck_url"):
            try:
                payload = json.dumps({
                    "key": api_key,
                    "lead_key": lead_key,
                    "action": "update",
                    "field": "pitch_deck_url",
                    "value": p["pitch_deck_url"],
                }).encode("utf-8")
                req = Request(f"{api_url}/api/leads.php", data=payload, method="POST")
                req.add_header("Content-Type", "application/json")
                with urlopen(req, timeout=15) as resp:
                    json.loads(resp.read().decode())
                print(f"  ✅ CRM: updated pitch_deck_url for {lead_key}")
            except Exception as e:
                print(f"  ⚠️  CRM: failed to update pitch_deck_url for {lead_key}: {e}")


def main():
    ap = argparse.ArgumentParser(description="Publish proposals to GitHub")
    ap.add_argument("--lead-key", default=None, help="Publish for one lead")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = ap.parse_args()

    published = publish(lead_key=args.lead_key, dry_run=args.dry_run)

    if published:
        print(f"\nPublished URLs:")
        for p in published:
            name = p.get("business_name") or p["slug"]
            print(f"  {name}:")
            if p["sample_site_url"]:
                print(f"    Site: {p['sample_site_url']}")
            if p["pitch_deck_url"]:
                print(f"    Deck: {p['pitch_deck_url']}")


if __name__ == "__main__":
    main()