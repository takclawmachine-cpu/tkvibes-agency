"""Process pending proposal generation jobs from CRM.

This is the missing job processor that was a stub. It:
1. Polls the CRM for pending/running jobs (api_pending action)
2. Claims each job (sets to 'running' via api_complete with status='running')
3. Generates proposals using the lead engine
4. Pushes proposals to CRM (API upload)
5. Marks job as 'completed'
6. On failure: marks job as 'failed' with error message

Runs as a daemon: polls every 30 seconds for new jobs.

Usage:
    python -m src.process_proposal_jobs                    # daemon mode
    python -m src.process_proposal_jobs --once               # process one batch
    python -m src.process_proposal_jobs --max-retries 3      # max retries per job
"""
import argparse
import json
import os
import sys
import time
import subprocess
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

from dotenv import load_dotenv

from .log_config import get_logger, configure_logging, set_trace_id
from .config import load_config

logger = get_logger(__name__)

LEAD_ENGINE_DIR = os.path.join(os.path.dirname(__file__), "..")


def get_pending_jobs(api_url: str, api_key: str) -> list[dict]:
    """Get pending/running jobs from CRM that need processing.

    Uses the proposals.php?action=api_pending endpoint which:
    - Returns jobs with status='pending' OR (status='running' AND updated_at < -10 min)
    - Limits to 10 jobs
    """
    url = f"{api_url.rstrip('/')}/api/proposals.php?action=api_pending&key={api_key}"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if data.get("status") == "ok":
            return data.get("jobs", [])
    except (URLError, json.JSONDecodeError) as e:
        logger.error("Failed to poll pending jobs: %s", e)
    return []


def claim_job(api_url: str, api_key: str, job_id: int, trace_id: str) -> bool:
    """Mark a job as 'running' so other processors don't pick it up."""
    url = f"{api_url.rstrip('/')}/api/proposals.php?action=api_complete&key={api_key}&job_id={job_id}&status=running"
    try:
        req = Request(url, headers={"Accept": "application/json", "X-Trace-ID": trace_id})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("status") == "ok"
    except (URLError, json.JSONDecodeError) as e:
        logger.error("Failed to claim job %d: %s", job_id, e)
    return False


def mark_job_completed(api_url: str, api_key: str, job_id: int, trace_id: str) -> bool:
    """Mark a job as 'completed'."""
    url = f"{api_url.rstrip('/')}/api/proposals.php?action=api_complete&key={api_key}&job_id={job_id}&status=completed"
    try:
        req = Request(url, headers={"Accept": "application/json", "X-Trace-ID": trace_id})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("status") == "ok"
    except (URLError, json.JSONDecodeError) as e:
        logger.error("Failed to mark job %d as completed: %s", job_id, e)
    return False


def mark_job_failed(api_url: str, api_key: str, job_id: int, trace_id: str, error: str) -> bool:
    """Mark a job as 'failed' with error details logged to system_logs."""
    url = f"{api_url.rstrip('/')}/api/proposals.php?action=api_complete&key={api_key}&job_id={job_id}&status=failed"
    try:
        # Log the error to CRM system_logs before marking as failed
        log_error_to_crm(api_url, api_key, "proposal_job_failed", {
            "job_id": job_id,
            "trace_id": trace_id,
            "error": error[:500],
        })
        req = Request(url, headers={"Accept": "application/json", "X-Trace-ID": trace_id})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data.get("status") == "ok"
    except (URLError, json.JSONDecodeError) as e:
        logger.error("Failed to mark job %d as failed: %s", job_id, e)
    return False


def log_error_to_crm(api_url: str, api_key: str, source: str, context: dict):
    """Log an error to the CRM system_logs table."""
    url = f"{api_url.rstrip('/')}/api/logs.php"
    payload = json.dumps({
        "key": api_key,
        "level": "error",
        "source": f"proposal-agent:{source}",
        "message": context.get("error", "Unknown error"),
        "context": {k: v for k, v in context.items() if k != "error"},
    }).encode("utf-8")
    try:
        req = Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        urlopen(req, timeout=5)
    except Exception:
        pass


def run_in_venv(module: str, args: list[str], timeout: int = 120) -> int:
    """Run a lead-engine module in the venv."""
    venv_python = os.path.join(LEAD_ENGINE_DIR, ".venv", "Scripts", "python.exe")
    if not os.path.isfile(venv_python):
        venv_python = sys.executable

    cmd = [venv_python, "-m", module] + args
    logger.info("  Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=LEAD_ENGINE_DIR, timeout=timeout,
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("  stderr: %s", result.stderr[-500:] if result.stderr else "unknown")
        return result.returncode
    except Exception as e:
        logger.error("  Failed to run: %s", e)
        return -1


def process_job(api_url: str, api_key: str, job: dict, cfg: dict, max_retries: int = 3) -> bool:
    """Process a single proposal generation job.

    Returns True if the job was successfully completed.
    """
    job_id = job.get("id")
    lead_key = job.get("lead_key", "")
    trace_id = set_trace_id(f"prop-{job_id}")

    logger.info("Processing job #%d for lead %s (trace_id=%s)", job_id, lead_key, trace_id)

    if not lead_key:
        logger.error("Job #%d has no lead_key — skipping", job_id)
        return False

    # Claim the job
    if not claim_job(api_url, api_key, job_id, trace_id):
        logger.warning("Job #%d was claimed by another process — skipping", job_id)
        return False

    # Retry loop
    for attempt in range(1, max_retries + 1):
        try:
            # Run proposal generation for this single lead
            rc = run_in_venv("src.generate_proposals", ["--lead-key", lead_key, "--force"])
            if rc != 0:
                raise RuntimeError(f"generate_proposals failed (exit {rc})")

            # Push to CRM
            rc = run_in_venv("src.push_proposals", ["--lead-key", lead_key])
            if rc != 0:
                raise RuntimeError(f"push_proposals failed (exit {rc})")

            # Mark job as completed
            mark_job_completed(api_url, api_key, job_id, trace_id)
            logger.info("Job #%d completed successfully (trace_id=%s)", job_id, trace_id)
            return True

        except Exception as e:
            logger.error("Job #%d attempt %d failed: %s", job_id, attempt, e)
            if attempt < max_retries:
                logger.info("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                mark_job_failed(api_url, api_key, job_id, trace_id, str(e))
                return False

    return False


def main():
    ap = argparse.ArgumentParser(description="Process pending proposal generation jobs")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--once", action="store_true",
                    help="Process one batch and exit (daemon mode otherwise)")
    ap.add_argument("--max-retries", type=int, default=3,
                    help="Max retries per job before marking as failed")
    ap.add_argument("--poll-interval", type=int, default=30,
                    help="Seconds between polls in daemon mode")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config(args.config)
    crm_cfg = cfg.get("crm", {}) or {}
    api_url = crm_cfg.get("api_url", "")
    api_key = crm_cfg.get("api_key", "")

    if not api_url or not api_key:
        print("ERROR: CRM_API_URL and CRM_API_KEY must be configured")
        sys.exit(1)

    configure_logging(
        level="INFO",
        crm_url=api_url,
        crm_key=api_key,
    )

    logger.info("Proposal job processor started (mode=%s)", "once" if args.once else "daemon")

    if args.once:
        jobs = get_pending_jobs(api_url, api_key)
        if not jobs:
            logger.info("No pending jobs")
            return

        completed = 0
        failed = 0
        for job in jobs:
            if process_job(api_url, api_key, job, cfg, max_retries=args.max_retries):
                completed += 1
            else:
                failed += 1

        logger.info("Batch complete: %d completed, %d failed", completed, failed)
        return

    # Daemon mode
    logger.info("Running in daemon mode, polling every %d seconds", args.poll_interval)
    while True:
        jobs = get_pending_jobs(api_url, api_key)
        if jobs:
            logger.info("Found %d pending jobs", len(jobs))
            for job in jobs:
                process_job(api_url, api_key, job, cfg, max_retries=args.max_retries)
        else:
            logger.info("No pending jobs")
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
