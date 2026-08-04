"""Process pending proposal generation jobs from CRM."""
import json, os, sys, urllib.request, re, subprocess

API_URL = "https://tkvibes.in/crm"
API_KEY = "10a76f01219e8fd7b1fec2c5256c6a39"
REPO_DIR = os.path.expanduser("~/Desktop/tkvibes-agency")
VENV_PYTHON = os.path.join(REPO_DIR, "tkvibes-lead-engine", ".venv", "Scripts", "python.exe")

def get_pending_jobs():
    """Get pending generation jobs from CRM."""
    # We can't query jobs via API directly, so check the proposals endpoint
    # Actually, let's check the lead list for leads without sample_site_url
    # and see if they have pending jobs
    pass

def process_lead(lead_key):
    """Run the full pipeline for one lead."""
    print(f"Processing lead: {lead_key}")
    
    # Run the business job for this lead
    cmd = [
        VENV_PYTHON, "-m", "src.run_business_job",
        "--max-leads", "1",
        "--force",
        "--skip-github",
        "--skip-crm",
        "--dry-run",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, 
        cwd=os.path.join(REPO_DIR, "tkvibes-lead-engine"), timeout=300)
    print(result.stdout[-500:])
    if result.returncode != 0:
        print(f"FAILED: {result.stderr[-200:]}")
        return False
    
    # For now, mark as generated
    return True

if __name__ == "__main__":
    # Check if any pending jobs exist
    try:
        req = urllib.request.Request(f"{API_URL}/api/proposals.php?action=status&lead_key=ph:+919****0773")
        resp = urllib.request.urlopen(req, timeout=15)
        print(resp.read().decode())
    except Exception as e:
        print(f"Connection test: {e}")
    
    print("Process pending jobs script ready")
