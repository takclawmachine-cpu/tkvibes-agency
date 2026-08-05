"""Publish sample websites and pitch decks to GitHub.

Reads generated HTML from data/proposals/<slug>/ directories, copies them to
the "Sample Webpages and pitch deck" folder, commits, and pushes to GitHub.
Then batch-updates CRM with the GitHub raw URLs.

Security improvements:
- GitHub repo URL read from env var (GITHUB_REPO) or git config
- Batched CRM URL push (one POST instead of per-lead)
- trace_id propagation for log correlation
- Proper error handling with context
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

from .config import load_config
from .log_config import get_logger, set_trace_id, get_trace_id

logger = get_logger(__name__)

REPO_DIR = os.path.expanduser("~/Desktop/tkvibes-agency")
PROPOSALS_DIR = os.path.join(REPO_DIR, "tkvibes-lead-engine", "data", "proposals")

# GitHub folder structure
SAMPLE_DIR = "Sample Webpages and pitch deck/sample website"
PITCH_DIR = "Sample Webpages and pitch deck/pitch deck"


def _get_github_repo() -> str:
    """Get the GitHub repo URL from env var or git config.
    
    GITHUB_REPO env var format: "owner/repo-name" (without .git)
    """
    repo = os.environ.get("GITHUB_REPO", "")
    if repo:
        return repo
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=REPO_DIR, timeout=10
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse owner/repo from HTTPS or SSH URL
            match = re.search(r'[:/]([^/]+/[^/]+?)(?:\.git)?$', url)
            if match:
                return match.group(1)
    except Exception:
        pass
    logger.warning("Could not determine GitHub repo — using default")
    return "takclawmachine-cpu/tkvibes-agency"


# Build repo URL once
_GITHUB_REPO = None
_GITHUB_BRANCH = "main"


def slugify(name: str) -> str:
    """Match the slugify in scaffold_clients.py and functions.php."""
    if not (name or "").strip():
        return "client"
    s = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-{2,}", "-", s)[:60] or "client"


def _build_slug_to_key_map() -> dict[str, str]:
    """Build a map of slug -> lead_key from leads_export.json for fallback lookups."""
    export_path = os.path.join(PROPOSALS_DIR, "..", "data", "leads_export.json")
    if not os.path.isfile(export_path):
        return {}
    try:
        with open(export_path, encoding="utf-8") as f:
            leads_data = json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}
    slug_map = {}
    for ld in leads_data:
        name = ld.get("business_name", "") or ""
        key = ld.get("lead_key", "") or ""
        if key:
            slug_map[slugify(name)] = key
    return slug_map


def _run_git(args: list[str], workdir: str = REPO_DIR) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args, capture_output=True, text=True, cwd=workdir, timeout=30
    )
    if result.returncode != 0:
        logger.warning("git %s failed: %s", " ".join(args), result.stderr.strip())
    return result.stdout.strip()


def publish(lead_key: str = None, dry_run: bool = False) -> list[dict]:
    """Publish generated proposals to GitHub.

    Returns list of dicts with published URLs.
    """
    os.chdir(REPO_DIR)
    trace_id = get_trace_id() or set_trace_id()
    github_repo = _get_github_repo()

    # Load generation results to know what was generated
    results_path = os.path.join(PROPOSALS_DIR, "_generation_results.json")
    if not os.path.isfile(results_path):
        # Scan the proposals directory directly with slug→key fallback
        slug_to_key = _build_slug_to_key_map()
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
                lk = slug_to_key.get(entry, "")
                if not lk:
                    logger.warning("No lead_key match for slug '%s'", entry)
                results.append({
                    "slug": entry,
                    "index": index if has_site else None,
                    "deck": deck if has_deck else None,
                    "lead_key": lk,
                })
    else:
        with open(results_path, encoding="utf-8") as f:
            results = json.load(f)

    if not results:
        logger.info("No proposals found to publish.")
        return []

    # Filter by lead_key if specified
    if lead_key:
        results = [r for r in results if r.get("lead_key") == lead_key]
        if not results:
            logger.info("No proposals found for lead_key: %s", lead_key)
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
        site_src = result.get("index") or ""
        if site_src and os.path.isfile(site_src):
            dest_name = f"{slug}.html"
            dest = os.path.join(REPO_DIR, SAMPLE_DIR, dest_name)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(site_src, dest)
            logger.info("  sample website: %s.html", slug)
        else:
            dest = None

        # Copy pitch deck
        deck_src = result.get("deck") or ""
        if deck_src and os.path.isfile(deck_src):
            deck_dest_name = f"{slug}.html"
            deck_dest = os.path.join(REPO_DIR, PITCH_DIR, deck_dest_name)
            os.makedirs(os.path.dirname(deck_dest), exist_ok=True)
            shutil.copy2(deck_src, deck_dest)
            logger.info("  pitch deck: %s.html", slug)
        else:
            deck_dest = None

        # Build GitHub raw URLs (branch=main, repo=owner/repo)
        if dest:
            relative = os.path.relpath(dest, REPO_DIR).replace("\\", "/")
            site_url = f"https://raw.githubusercontent.com/{github_repo}/{_GITHUB_BRANCH}/{relative.replace(' ', '%20')}"
        else:
            site_url = ""

        if deck_dest:
            relative_deck = os.path.relpath(deck_dest, REPO_DIR).replace("\\", "/")
            deck_url = f"https://raw.githubusercontent.com/{github_repo}/{_GITHUB_BRANCH}/{relative_deck.replace(' ', '%20')}"
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
        _run_git(["add", SAMPLE_DIR, PITCH_DIR])
        status = _run_git(["status", "--porcelain"])
        if status:
            _run_git([
                "commit", "-m",
                f"chore: auto-publish sample sites + pitch decks [{timestamp}]",
            ])
            _run_git(["push", "origin", "main"])
            logger.info("Pushed %d proposals to GitHub", len(published))
        else:
            logger.info("No changes to commit (files already up to date)")

        # Push GitHub URLs to CRM (BATCHED — one request for all leads)
        _push_urls_to_crm_batch(published)
    else:
        logger.info("[dry-run] Would publish %d proposals to GitHub", len(published))

    return published


def _push_urls_to_crm_batch(published: list[dict]):
    """Push GitHub URLs to CRM via sync.php (single batched request).

    Replaces the old per-lead POST approach (~50 HTTP calls) with a single
    batched request containing all lead URL updates.
    """
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    if not os.path.isfile(cfg_path):
        logger.warning("config.yaml not found — skipping CRM URL update")
        return

    cfg = load_config(cfg_path)
    crm_cfg = cfg.get("crm", {}) or {}
    api_url = crm_cfg.get("api_url", "").rstrip("/")
    api_key = crm_cfg.get("api_key", "")

    if not api_url or not api_key:
        logger.warning("CRM API not configured — skipping CRM URL update")
        return

    # Build a single batch payload with all lead URL updates
    batch_leads = []
    for p in published:
        lead_key = p.get("lead_key", "")
        if not lead_key:
            name = p.get("business_name") or p.get("slug", "?")
            logger.warning("Skipping CRM URL push for '%s' (no lead_key)", name)
            continue

        lead = {"lead_key": lead_key}
        if p.get("sample_site_url"):
            lead["sample_site_url"] = p["sample_site_url"]
        if p.get("pitch_deck_url"):
            lead["pitch_deck_url"] = p["pitch_deck_url"]

        if "sample_site_url" in lead or "pitch_deck_url" in lead:
            batch_leads.append(lead)

    if not batch_leads:
        logger.info("No URL updates to push to CRM")
        return

    try:
        payload = json.dumps({
            "key": api_key,
            "trace_id": get_trace_id() or str(uuid.uuid4()),
            "idempotency_key": f"urls-{uuid.uuid4().hex[:12]}",
            "leads": batch_leads,
        }).encode("utf-8")
        req = Request(f"{api_url}/api/sync.php", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        if result.get("status") == "ok":
            logger.info("CRM: batch-synced %d lead URL updates (%d added, %d updated)",
                        len(batch_leads), result.get("added", 0), result.get("updated", 0))
        else:
            logger.warning("CRM: batch sync returned %s", result.get("status", "?"))
    except Exception as e:
        logger.error("CRM: failed to batch-update URLs: %s", e)


def main():
    ap = argparse.ArgumentParser(description="Publish proposals to GitHub")
    ap.add_argument("--lead-key", default=None, help="Publish for one lead")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = ap.parse_args()

    published = publish(lead_key=args.lead_key, dry_run=args.dry_run)
    if published:
        logger.info("Published URLs:")
        for p in published:
            name = p.get("business_name") or p["slug"]
            logger.info("  %s:", name)
            if p["sample_site_url"]:
                logger.info("    Site: %s", p["sample_site_url"])
            if p["pitch_deck_url"]:
                logger.info("    Deck: %s", p["pitch_deck_url"])


if __name__ == "__main__":
    main()
