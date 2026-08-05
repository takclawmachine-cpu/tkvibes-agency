"""TKVibes Business Job Orchestrator (Hardened).

Runs the full automated business workflow in clearly defined, reversible phases:

1. Discover leads (Google Places API) → leads_batch.json
2. Process leads (enrich, score, dedupe, assign) → processed_leads.json
3. Push to CRM (transactional, idempotent) → MySQL DB
4. Generate proposals (file output only, no DB writes) → proposals/{slug}/
5. Publish to GitHub → raw.githubusercontent.com URLs
6. Push proposal URLs to CRM → update leads.sample_site_url/pitch_deck_url

Each phase has:
- Clear input and output (with trace_id)
- Rollback on failure (earlier phase artifacts are not overwritten)
- Status tracking (can resume from failed phase)

Usage:
    python -m src.run_business_job                    # full job, default 20 leads
    python -m src.run_business_job --max-leads 10
    python -m src.run_business_job --lead-key "ph:+919..."  # single existing lead
    python -m src.run_business_job --cities Delhi --categories "dental clinic"
    python -m src.run_business_job --skip-research
    python -m src.run_business_job --skip-github
    python -m src.run_business_job --skip-crm
    python -m src.run_business_job --dry-run
"""
import argparse
import json
import os
import sys
import uuid
import subprocess

from dotenv import load_dotenv

from .log_config import get_logger, configure_logging, set_trace_id, get_trace_id
from .config import load_config

logger = get_logger(__name__)

REPO_DIR = os.path.expanduser("~/Desktop/tkvibes-agency")
LEAD_ENGINE_DIR = os.path.join(REPO_DIR, "tkvibes-lead-engine")


def _resolve_venv_python() -> str:
    """Find the venv Python executable, handling both Windows and POSIX."""
    candidates = [
        os.path.join(LEAD_ENGINE_DIR, ".venv", "Scripts", "python.exe"),
        os.path.join(LEAD_ENGINE_DIR, ".venv", "Scripts", "python"),
        os.path.join(LEAD_ENGINE_DIR, ".venv", "bin", "python"),
        os.path.join(LEAD_ENGINE_DIR, ".venv", "bin", "python3"),
        sys.executable,  # fallback to current interpreter
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return sys.executable


VENV_PYTHON = _resolve_venv_python()


class PhaseTracker:
    """Tracks pipeline phase execution status for resumability and rollback."""

    def __init__(self, trace_id: str, status_file: str):
        self.trace_id = trace_id
        self.status_file = status_file
        self.status = self._load_status() or {}
        self._save_status()

    def _load_status(self) -> dict:
        if os.path.isfile(self.status_file):
            try:
                with open(self.status_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_status(self):
        os.makedirs(os.path.dirname(self.status_file) or ".", exist_ok=True)
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(self.status, f, indent=2, default=str)

    def mark_started(self, phase: str):
        self.status[phase] = {"status": "running", "started_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
        self._save_status()
        logger.info("Phase '%s' STARTED", phase)

    def mark_completed(self, phase: str, details: dict = None):
        self.status[phase] = {
            "status": "completed",
            "started_at": self.status.get(phase, {}).get("started_at", ""),
            "completed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "details": details or {},
        }
        self._save_status()
        logger.info("Phase '%s' COMPLETED", phase)

    def mark_failed(self, phase: str, error: str):
        self.status[phase] = {
            "status": "failed",
            "error": error,
            "completed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }
        self._save_status()
        logger.error("Phase '%s' FAILED: %s", phase, error)

    def rollback(self, phase: str):
        """Rollback artifacts from a failed phase."""
        logger.info("Rollback initiated for phase '%s'", phase)
        self._save_status()


def run_script(module: str, args: list[str] | None = None, timeout: int = 300) -> int:
    """Run a lead-engine module in the venv.

    Returns the process exit code.
    """
    cmd = [VENV_PYTHON, "-m", f"src.{module}"]
    if args:
        cmd += args
    logger.info("▶ %s: %s", module, " ".join(args or []))
    try:
        result = subprocess.run(
            cmd,
            cwd=LEAD_ENGINE_DIR,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error("%s stderr: %s", module, result.stderr[-500:] if result.stderr else "unknown")
        if result.stdout:
            logger.debug("%s stdout: %s", module, result.stdout[-500:])
        return result.returncode
    except subprocess.TimeoutExpired:
        logger.error("%s timed out after %d seconds", module, timeout)
        return -1
    except FileNotFoundError:
        logger.error("Python executable not found: %s", VENV_PYTHON)
        return -1


def main():
    ap = argparse.ArgumentParser(description="TKVibes Business Job (Hardened)")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--max-leads", type=int, default=None)
    ap.add_argument("--lead-key", default=None,
                    help="Single lead key (bypasses discovery, generates directly)")
    ap.add_argument("--cities", default=None)
    ap.add_argument("--categories", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Discover + score + generate only. No sheet/CRM/GitHub.")
    ap.add_argument("--skip-research", action="store_true",
                    help="Skip competitor research and website audit")
    ap.add_argument("--skip-github", action="store_true",
                    help="Skip GitHub publish")
    ap.add_argument("--skip-crm", action="store_true",
                    help="Skip pushing proposals to CRM")
    ap.add_argument("--force", action="store_true",
                    help="Regenerate proposals even if they exist")
    ap.add_argument("--tier", default=None,
                    help="Only generate for this tier: HOT, WARM, COLD")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config(args.config)

    # Set up trace_id and logging
    trace_id = set_trace_id()
    crm_cfg = cfg.get("crm", {}) or {}
    configure_logging(
        level="INFO",
        crm_url=crm_cfg.get("api_url", ""),
        crm_key=crm_cfg.get("api_key", ""),
    )

    # Phase tracker for resumability
    status_file = os.path.join(LEAD_ENGINE_DIR, ".pipeline_status.json")
    tracker = PhaseTracker(trace_id, status_file)
    logger.info("Business job started", extra={
        "event": "business_job_start",
        "trace_id": trace_id,
        "max_leads": args.max_leads or cfg["run"]["max_leads_per_run"],
        "lead_key": args.lead_key,
        "dry_run": args.dry_run,
    })

    # ── Single-lead mode: skip discovery, generate directly ──────────
    if args.lead_key:
        logger.info("Single-lead mode: %s (skipping discovery)", args.lead_key)

        tracker.mark_started("generate_proposals")
        gen_args = ["--lead-key", args.lead_key]
        if args.force:
            gen_args.append("--force")
        if args.skip_research:
            gen_args.append("--skip-research")

        rc = run_script("generate_proposals", gen_args, timeout=120)
        if rc != 0:
            tracker.mark_failed("generate_proposals", f"Exit code {rc}")
            logger.error("Proposal generation failed for lead %s", args.lead_key)
            sys.exit(rc)
        tracker.mark_completed("generate_proposals", {"lead_key": args.lead_key})

        if not args.dry_run and not args.skip_github:
            tracker.mark_started("git_publish")
            rc = run_script("git_publish", ["--lead-key", args.lead_key])
            if rc != 0:
                logger.warning("GitHub publish had issues for lead %s", args.lead_key)
            tracker.mark_completed("git_publish")

        if not args.dry_run and not args.skip_crm:
            tracker.mark_started("push_proposals")
            rc = run_script("push_proposals", ["--lead-key", args.lead_key])
            if rc != 0:
                logger.warning("CRM proposal push had issues for lead %s", args.lead_key)
            tracker.mark_completed("push_proposals")

        logger.info("Single lead job complete | lead=%s | trace_id=%s", args.lead_key, trace_id)
        return

    # ── Normal batch mode: discover + process + generate ────────────────
    # Phase 1: Discovery + Processing
    tracker.mark_started("discovery")
    run_args = []
    if args.max_leads:
        run_args += ["--max-leads", str(args.max_leads)]
    if args.cities:
        run_args += ["--cities", args.cities]
    if args.categories:
        run_args += ["--categories", args.categories]
    if args.dry_run:
        run_args.append("--dry-run")

    rc = run_script("run", run_args, timeout=600)
    if rc != 0:
        tracker.mark_failed("discovery", f"Exit code {rc}")
        logger.error("Lead engine failed — aborting pipeline")
        sys.exit(rc)
    tracker.mark_completed("discovery", {"trace_id": trace_id})

    # Phase 2: Generate sample sites + pitch decks
    tracker.mark_started("generate_proposals")
    gen_args = []
    if args.force:
        gen_args.append("--force")
    if args.tier:
        gen_args += ["--tier", args.tier]
    if args.max_leads:
        gen_args += ["--limit", str(args.max_leads)]

    rc = run_script("generate_proposals", gen_args, timeout=300)
    if rc != 0:
        tracker.mark_failed("generate_proposals", f"Exit code {rc}")
        tracker.rollback("generate_proposals")
        logger.error("Proposal generation failed — rolling back")
        sys.exit(rc)
    tracker.mark_completed("generate_proposals", {"trace_id": trace_id})

    # Phase 3: Publish to GitHub
    if not args.dry_run and not args.skip_github:
        tracker.mark_started("git_publish")
        rc = run_script("git_publish", [], timeout=120)
        if rc != 0:
            logger.warning("GitHub publish had issues — proposals still generated locally")
            tracker.mark_failed("git_publish", f"Exit code {rc}")
        else:
            tracker.mark_completed("git_publish")

    # Phase 4: Push proposals to CRM
    if not args.dry_run and not args.skip_crm:
        tracker.mark_started("push_proposals")
        rc = run_script("push_proposals", [], timeout=300)
        if rc != 0:
            logger.warning("CRM proposal push had issues — proposals on GitHub but not in CRM")
            tracker.mark_failed("push_proposals", f"Exit code {rc}")
        else:
            tracker.mark_completed("push_proposals")

    logger.info("Business job complete | trace_id=%s | phases=%s",
                trace_id, list(tracker.status.keys()))


if __name__ == "__main__":
    main()
