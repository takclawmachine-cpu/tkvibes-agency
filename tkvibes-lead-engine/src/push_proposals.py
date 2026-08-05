"""Push generated proposal files (sample sites + pitch decks) to the CRM.

After the website generator produces HTML files in data/proposals/<slug>/, run this script
to push them to the CRM so employees can view/download them.

This version uses `_generation_results.json` as the authoritative list of proposals
to push, rather than scanning ALL proposal directories (which includes stale/old proposals).

Usage:
    python -m src.push_proposals                  # push all from current run results
    python -m src.push_proposals --dry-run        # show what would be pushed
    python -m src.push_proposals --lead-key KEY   # push for one lead
    python -m src.push_proposals --file FILE --type TYPE --lead-key KEY  # single file
"""
import argparse
import json
import os
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

from dotenv import load_dotenv
from urllib.parse import urlparse

from .config import load_config
from .models import Lead
from .log_config import get_logger, set_trace_id, get_trace_id
from .generate_proposals import slugify

logger = get_logger(__name__)

PROPOSALS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "proposals")


def push_to_crm(lead_key: str, type_: str, html: str, filename: str,
                api_url: str, api_key: str, trace_id: str = "") -> dict:
    """POST a proposal to the CRM proposals.php endpoint."""
    if not trace_id:
        trace_id = get_trace_id() or set_trace_id()

    payload = json.dumps({
        "key": api_key,
        "trace_id": trace_id,
        "lead_key": lead_key,
        "type": type_,
        "html": html,
        "file_name": filename,
    }).encode("utf-8")

    url = f"{api_url.rstrip('/')}/api/proposals.php"
    req = Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Trace-ID", trace_id)

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        return result
    except URLError as e:
        return {"status": "error", "reason": str(e)}
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"bad response: {e}"}


def find_proposal_files(lead_key: str, slug: str) -> dict:
    """Find sample site and pitch deck files for a lead.

    Looks in data/proposals/<slug>/ for index.html and pitch-deck.html.
    """
    results = {}
    slug_dir = os.path.join(PROPOSALS_DIR, slug)

    index_path = os.path.join(slug_dir, "index.html")
    if os.path.isfile(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            results["sample_site"] = {"html": f.read(), "path": index_path}

    deck_path = os.path.join(slug_dir, "pitch-deck.html")
    if os.path.isfile(deck_path):
        with open(deck_path, "r", encoding="utf-8") as f:
            results["pitch_deck"] = {"html": f.read(), "path": deck_path}

    return results


def load_generation_results() -> list[dict]:
    """Load the _generation_results.json file from the current run."""
    results_path = os.path.join(PROPOSALS_DIR, "_generation_results.json")
    if not os.path.isfile(results_path):
        logger.error("No _generation_results.json found at %s", results_path)
        return []
    try:
        with open(results_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to read _generation_results.json: %s", e)
        return []


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

    trace_id = set_trace_id()

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
                             os.path.basename(args.file), api_url, api_key, trace_id)
        print(f"  Push: {result.get('status', 'error')} — {args.type}")
        if result.get("status") != "ok":
            print(f"  Error: {result.get('reason', 'unknown')}")
        return

    # Batch mode: load generation results (authoritative list of what to push)
    results = load_generation_results()
    if not results:
        print("No generation results found. Run generate_proposals.py first.")
        return

    # Filter by lead_key if specified
    if args.lead_key:
        results = [r for r in results if r.get("lead_key") == args.lead_key]
        if not results:
            print(f"No proposals found for lead_key: {args.lead_key}")
            return

    pushed = 0
    errors = 0
    skipped = 0

    for result in results:
        if result.get("status") != "generated":
            logger.debug("Skipping %s: status=%s", result.get("slug"), result.get("status"))
            skipped += 1
            continue

        lead_key = result.get("lead_key", "")
        slug = result.get("slug", "")
        if not lead_key:
            logger.warning("Skipping %s: no lead_key", slug)
            skipped += 1
            continue

        # Find proposal files
        proposals = find_proposal_files(lead_key, slug)
        if not proposals:
            logger.warning("Skipping %s: no proposal files found", slug)
            skipped += 1
            continue

        for type_, info in proposals.items():
            filename = os.path.basename(info["path"])
            if args.dry_run:
                logger.info("[dry-run] %s → %s (%s, %d chars)",
                           lead_key, type_, filename, len(info["html"]))
                continue
            result = push_to_crm(lead_key, type_, info["html"],
                                 filename, api_url, api_key, trace_key)
            if result.get("status") == "ok":
                pushed += 1
                logger.info("✅ %s → %s (%s)", lead_key, type_, filename)
            else:
                errors += 1
                logger.error("❌ %s → %s: %s", lead_key, type_, result.get('reason', 'error'))

    if not args.dry_run:
        logger.info("Done: %d pushed, %d errors, %d skipped", pushed, errors, skipped)
    else:
        logger.info("Dry-run: %d would be pushed, %d skipped", pushed + errors, skipped)


if __name__ == "__main__":
    main()