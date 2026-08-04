"""Backfill emails for leads already in the Google Sheet / export JSON.

Usage:
    python -m src.backfill_emails            # sheet + JSON
    python -m src.backfill_emails --json-only
"""
import argparse
import json
import os

from dotenv import load_dotenv

from .config import load_config
from .log_config import get_logger
from .email_finder import find_emails_for_site
from .models import SCHEMA

logger = get_logger(__name__)


def backfill_json(path: str, delay: float) -> dict:
    if not os.path.exists(path):
        return {"found": 0, "total": 0}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    found = 0
    targets = [d for d in data if not d.get("email") and d.get("website_url")]
    logger.info("[json] %d leads with a website and no email", len(targets))
    for i, d in enumerate(targets, 1):
        emails = find_emails_for_site(d["website_url"], delay=delay)
        if emails:
            d["email"] = emails[0]
            if len(emails) > 1:
                d["notes"] = (d.get("notes", "") +
                              f" | alt_emails: {', '.join(emails[1:4])}").strip(" |")
            found += 1
            logger.info("[%d/%d] %s: %s", i, len(targets), d["business_name"], emails[0])
        else:
            logger.info("[%d/%d] %s: -", i, len(targets), d["business_name"])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return {"found": found, "total": len(targets)}


def backfill_sheet(sa_path: str, sheet_id: str, worksheet: str, delay: float) -> dict:
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_file(
        sa_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    ws = gspread.authorize(creds).open_by_key(sheet_id).worksheet(worksheet)

    header = ws.row_values(1) or SCHEMA
    e_col = header.index("email") + 1
    w_col = header.index("website_url") + 1
    n_col = header.index("notes") + 1

    rows = ws.get_all_values()[1:]
    updates, found, checked = [], 0, 0

    for idx, row in enumerate(rows, start=2):
        def cell(c):
            return row[c - 1] if len(row) >= c else ""
        if cell(e_col).strip():
            continue
        site = cell(w_col).strip()
        if not site:
            continue
        checked += 1
        emails = find_emails_for_site(site, delay=delay)
        name = row[header.index("business_name")] if len(row) > 1 else f"row{idx}"
        if emails:
            found += 1
            updates.append({"range": gspread.utils.rowcol_to_a1(idx, e_col),
                            "values": [[emails[0]]]})
            if len(emails) > 1:
                note = (cell(n_col) + f" | alt_emails: {', '.join(emails[1:4])}").strip(" |")
                updates.append({"range": gspread.utils.rowcol_to_a1(idx, n_col),
                                "values": [[note]]})
            logger.info("row %d %s: %s", idx, name, emails[0])
        else:
            logger.info("row %d %s: -", idx, name)

    if updates:
        ws.batch_update(updates, value_input_option="RAW")
    return {"found": found, "total": checked}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--sheet-only", action="store_true")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config(args.config)
    delay = (cfg.get("email_finder") or {}).get("per_site_delay_seconds", 0.8)

    if not args.sheet_only:
        r = backfill_json(cfg["handoff"]["export_json"], delay)
        print(f"[json] {r['found']}/{r['total']} emails filled")

    if not args.json_only:
        sa = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        sid = os.environ.get("GOOGLE_SHEETS_ID", "")
        if not sa or not sid:
            print("[sheet] GOOGLE_SERVICE_ACCOUNT_JSON / GOOGLE_SHEETS_ID not set — skipped")
        else:
            r = backfill_sheet(sa, sid, cfg["sheets"]["worksheet_name"], delay)
            print(f"[sheet] {r['found']}/{r['total']} emails filled")


if __name__ == "__main__":
    main()