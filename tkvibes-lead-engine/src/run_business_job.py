"""
TKVibes Business Job Orchestrator.

Runs the full automated business workflow in one command:

1. Pull leads (Google Places discovery → enrich → score → assign)
2. Write leads to Google Sheets (master + job tab)
3. Push leads to CRM (assigned: India→Jashmit, Canada→Tishya)
4. Generate sample websites + pitch decks
5. Push HTML to GitHub under "Sample Webpages and pitch deck"
6. Push proposals to CRM (employees can view/download from lead detail)

Usage:
    python -m src.run_business_job                    # full job, default 20 leads
    python -m src.run_business_job --max-leads 10
    python -m src.run_business_job --lead-key "ph:+919..."  # single existing lead (skip discovery)
    python -m src.run_business_job --cities Delhi --categories "dental clinic"
    python -m src.run_business_job --skip-research    # skip competitor/audit research
    python -m src.run_business_job --skip-github      # skip GitHub publish
    python -m src.run_business_job --skip-crm         # skip CRM push
    python -m src.run_business_job --dry-run          # discover+score+generate only
"""
import argparse
import json
import os
import sys
import subprocess

from dotenv import load_dotenv

from .config import load_config

REPO_DIR = os.path.expanduser("~/Desktop/tkvibes-agency")
VENV_PYTHON = os.path.join(REPO_DIR, "tkvibes-lead-engine", ".venv", "Scripts", "python.exe")
if not os.path.isfile(VENV_PYTHON):
    VENV_PYTHON = os.path.join(REPO_DIR, "tkvibes-lead-engine", ".venv", "Scripts", "python")


def run_script(module: str, args: list[str] | None = None) -> int:
    """Run a lead-engine module in the venv."""
    cmd = [VENV_PYTHON, "-m", f"src.{module}"]
    if args:
        cmd += args
    print(f"\n{'='*70}\n▶ {module}: {' '.join(args or [])}\n{'='*70}")
    result = subprocess.run(cmd, cwd=os.path.join(REPO_DIR, "tkvibes-lead-engine"))
    return result.returncode


def main():
    ap = argparse.ArgumentParser(description="TKVibes Business Job")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--max-leads", type=int, default=None)
    ap.add_argument("--lead-key", default=None,
                    help="Single lead key (bypasses discovery, generates directly)")
    ap.add_argument("--cities", default=None)
    ap.add_argument("--categories", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Discover + score + generate proposals only. No sheet/CRM/GitHub.")
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

    print("🚀 TKVibes Business Job")
    print(f"   Repo: {REPO_DIR}")

    if args.lead_key:
        # ── Single-lead mode: skip discovery, generate directly ──────────
        print(f"   Single lead mode: {args.lead_key}")
        print("   Skipping discovery, sheet write, and CRM push.")

        gen_args = ["--lead-key", args.lead_key]
        if args.force:
            gen_args.append("--force")
        if args.skip_research:
            gen_args.append("--skip-research")

        rc = run_script("generate_proposals", gen_args)
        if rc != 0:
            print("❌ Proposal generation failed")
            sys.exit(rc)

        if not args.dry_run and not args.skip_github:
            rc = run_script("git_publish", ["--lead-key", args.lead_key])
            if rc != 0:
                print("⚠️ GitHub publish had issues")

        if not args.dry_run and not args.skip_crm:
            rc = run_script("push_proposals", ["--lead-key", args.lead_key])
            if rc != 0:
                print("⚠️ CRM proposal push had issues")

        print("\n🎉 Single lead job complete!")
        print(f"   Lead: {args.lead_key} → proposals → GitHub → CRM")
        return

    # ── Normal batch mode: discover + process + generate ────────────────
    run_args = []
    if args.max_leads:
        run_args += ["--max-leads", str(args.max_leads)]
    if args.cities:
        run_args += ["--cities", args.cities]
    if args.categories:
        run_args += ["--categories", args.categories]
    if args.dry_run:
        run_args.append("--dry-run")

    rc = run_script("run", run_args)
    if rc != 0:
        print("❌ Lead engine failed")
        sys.exit(rc)

    # ── Step 2: Generate sample sites + pitch decks ─────────────────────
    gen_args = []
    if args.force:
        gen_args.append("--force")
    if args.tier:
        gen_args += ["--tier", args.tier]
    if args.max_leads:
        gen_args += ["--limit", str(args.max_leads)]

    rc = run_script("generate_proposals", gen_args)
    if rc != 0:
        print("❌ Proposal generation failed")
        sys.exit(rc)

    # ── Step 3: Publish to GitHub ───────────────────────────────────────
    if not args.dry_run and not args.skip_github:
        rc = run_script("git_publish", [])
        if rc != 0:
            print("⚠️ GitHub publish had issues")

    # ── Step 4: Push proposals to CRM ───────────────────────────────────
    if not args.dry_run and not args.skip_crm:
        rc = run_script("push_proposals", [])
        if rc != 0:
            print("⚠️ CRM proposal push had issues")

    print("\n🎉 Business job complete!")
    print("   Leads → Sheets → CRM → sample sites + pitch decks → GitHub → CRM downloads")


if __name__ == "__main__":
    main()