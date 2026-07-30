"""Push wa.me click-to-chat links (and contact_channel) into the Google Sheet.

Adds the `contact_channel` + `wa_link` columns if missing, then fills them
for every row whose phone is WhatsApp-reachable. Matches rows by lead_key.

    python -m src.push_wa_links
    python -m src.push_wa_links --dry-run
"""
import argparse
import os

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from .config import load_config
from .models import Lead
from .outreach.phone import classify_number, route_channel, render, wa_link, _has_real_site
from .build_outreach import DEFAULT_TEMPLATE, HAS_SITE_TEMPLATE

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
NEW_COLS = ["contact_channel", "wa_link"]
NOTE_MARK = "MSG:"      # notes prefix so we can rewrite our own text idempotently


def _lead_from_row(header: list, row: list) -> Lead:
    d = {h: (row[i] if i < len(row) else "") for i, h in enumerate(header)}
    l = Lead()
    for k, v in d.items():
        if hasattr(l, k):
            setattr(l, k, v)
    for num in ("rating", "review_count", "lead_score"):
        try:
            setattr(l, num, float(d.get(num) or 0) if num == "rating"
                    else int(float(d.get(num) or 0)))
        except Exception:
            pass
    l.opt_out = str(d.get("opt_out", "")).strip().upper() in ("TRUE", "1", "YES")
    return l


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config(args.config)
    creds = Credentials.from_service_account_file(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"], scopes=SCOPES)
    ws = (gspread.authorize(creds)
          .open_by_key(os.environ["GOOGLE_SHEETS_ID"])
          .worksheet(cfg["sheets"]["worksheet_name"]))

    header = ws.row_values(1)
    added = [c for c in NEW_COLS if c not in header]
    if added and not args.dry_run:
        header += added
        ws.update([header], "A1")
        print(f"added columns: {', '.join(added)}")
    elif added:
        header += added
        print(f"(dry-run) would add columns: {', '.join(added)}")

    ch_col = header.index("contact_channel") + 1
    wa_col = header.index("wa_link") + 1
    nt_col = header.index("notes") + 1

    rows = ws.get_all_values()[1:]
    updates, stats = [], {}

    for idx, row in enumerate(rows, start=2):
        lead = _lead_from_row(header, row)
        if not lead.business_name:
            continue

        msg = ""
        if lead.opt_out:
            channel, link = "opt_out", ""
        else:
            info = classify_number(lead.phone_primary)
            channel = ("email" if lead.email and not info["valid"]
                       else route_channel(lead))
            link = ""
            if channel in ("whatsapp", "sms", "call"):
                tpl = HAS_SITE_TEMPLATE if _has_real_site(lead) else DEFAULT_TEMPLATE
                msg = render(tpl, lead)
            if channel == "whatsapp":
                link = wa_link(info["e164"], msg)

        stats[channel] = stats.get(channel, 0) + 1
        updates.append({"range": gspread.utils.rowcol_to_a1(idx, ch_col),
                        "values": [[channel]]})
        if link:
            updates.append({"range": gspread.utils.rowcol_to_a1(idx, wa_col),
                            "values": [[link]]})
        if msg:
            # preserve any pre-existing human note, replace only our own block
            prev = (row[nt_col - 1] if len(row) >= nt_col else "").strip()
            keep = prev.split(NOTE_MARK)[0].strip(" |") if NOTE_MARK in prev else prev
            note = f"{keep} | {NOTE_MARK} {msg}".strip(" |") if keep else f"{NOTE_MARK} {msg}"
            updates.append({"range": gspread.utils.rowcol_to_a1(idx, nt_col),
                            "values": [[note]]})

    if args.dry_run:
        print(f"(dry-run) {len(updates)} cell updates across {len(rows)} rows")
    else:
        for i in range(0, len(updates), 200):      # stay under API payload limits
            ws.batch_update(updates[i:i + 200], value_input_option="RAW")
        print(f"wrote {len(updates)} cells across {len(rows)} rows")

    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
