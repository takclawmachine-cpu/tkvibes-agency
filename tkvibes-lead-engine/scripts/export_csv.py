"""Export all leads from Google Sheets to a complete CSV file."""
import os, sys, csv
from pathlib import Path

# Project root
os.chdir(os.path.expanduser("~/Desktop/tkvibes-agency/tkvibes-lead-engine"))
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

from src.sheets import SheetWriter
from src.models import SCHEMA

sheet_id = os.environ["GOOGLE_SHEETS_ID"]
sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials/google-service-account.json")

print(f"Sheet ID: {sheet_id}")
print(f"Service account: {sa_json}")

writer = SheetWriter(sa_json, sheet_id)
all_leads = writer.read_all()
print(f"Read {len(all_leads)} leads from Google Sheets")

csv_path = Path("data/leads_complete.csv")
csv_path.parent.mkdir(parents=True, exist_ok=True)

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(SCHEMA)
    for lead in all_leads:
        w.writerow(lead.row())

print(f"Exported to {csv_path.absolute()} ({csv_path.stat().st_size} bytes, {len(all_leads)} leads)")