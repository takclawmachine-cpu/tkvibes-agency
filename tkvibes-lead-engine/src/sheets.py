import gspread
from google.oauth2.service_account import Credentials
from .models import SCHEMA, Lead

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetWriter:
    def __init__(self, sa_json: str, sheet_id: str, worksheet: str = "Leads"):
        creds = Credentials.from_service_account_file(sa_json, scopes=SCOPES)
        self.gc = gspread.authorize(creds)
        self.sh = self.gc.open_by_key(sheet_id)
        self._default_ws_name = worksheet

    # ── helpers ──────────────────────────────────────────────────────────────

    def _ensure_schema(self, ws):
        """Update header row if the schema has changed (append-only)."""
        current = ws.row_values(1)
        if current != SCHEMA:
            ws.update([SCHEMA], "A1")

    def _existing_keys(self, ws) -> set:
        col = SCHEMA.index("lead_key") + 1
        return set(ws.col_values(col)[1:])

    def _lead_from_row(self, row: list, header: list | None = None) -> Lead | None:
        """Convert a sheet row into a Lead object.  Returns None for empty rows."""
        if not row or not any(cell.strip() for cell in row):
            return None
        h = header or SCHEMA
        d = {}
        for i, key in enumerate(h):
            if i < len(row):
                d[key] = row[i]
            else:
                d[key] = ""
        # Typecast known fields
        for bool_field in ("has_website", "opt_out"):
            v = d.get(bool_field, "")
            d[bool_field] = v in (True, "True", "true", "TRUE", "1", 1)
        for float_field in ("latitude", "longitude", "rating"):
            v = d.get(float_field, "")
            try:
                d[float_field] = float(v) if v else None
            except (ValueError, TypeError):
                d[float_field] = None
        for int_field in ("review_count", "lead_score"):
            v = d.get(int_field, "")
            try:
                d[int_field] = int(v) if v else None
            except (ValueError, TypeError):
                d[int_field] = None
        return Lead(**{k: d.get(k, "") for k in SCHEMA})

    # ── public API ───────────────────────────────────────────────────────────

    def upsert(self, leads: list) -> int:
        """Append new leads (by lead_key) to the default worksheet."""
        try:
            ws = self.sh.worksheet(self._default_ws_name)
        except gspread.WorksheetNotFound:
            ws = self.sh.add_worksheet(self._default_ws_name, rows=1000, cols=len(SCHEMA))
        self._ensure_schema(ws)
        existing = self._existing_keys(ws)
        new_rows = [l.row() for l in leads if l.lead_key not in existing]
        if new_rows:
            ws.append_rows(new_rows, value_input_option="RAW")
        return len(new_rows)

    def write_job(self, leads: list, sheet_name: str) -> int:
        """Create (or reuse) a worksheet named by the job timestamp and write
        all leads fresh into it — one sheet per discovery job."""
        safe = sheet_name.replace(":", "-")
        try:
            ws = self.sh.worksheet(safe)
        except gspread.WorksheetNotFound:
            ws = self.sh.add_worksheet(safe, rows=1000, cols=len(SCHEMA))
        rows = [SCHEMA] + [l.row() for l in leads]
        ws.clear()
        ws.update(rows, "A1", value_input_option="RAW")
        return len(leads)

    def read_all(self) -> list[Lead]:
        """Read all rows from the default worksheet and return as Lead objects."""
        try:
            ws = self.sh.worksheet(self._default_ws_name)
        except gspread.WorksheetNotFound:
            return []
        all_rows = ws.get_all_values()
        if not all_rows or len(all_rows) < 2:
            return []
        header = all_rows[0]
        # Build a header that matches SCHEMA as closely as possible: if the sheet
        # has extra columns (e.g. wa_link in the middle), we keep the full header
        # so that _lead_from_row maps correctly.
        return [
            L for row in all_rows[1:]
            if (L := self._lead_from_row(row, header))
        ]

    def read_recent(self, limit: int = 50) -> list[Lead]:
        """Read the latest N rows from the default worksheet."""
        all_leads = self.read_all()
        return all_leads[-limit:] if len(all_leads) > limit else all_leads