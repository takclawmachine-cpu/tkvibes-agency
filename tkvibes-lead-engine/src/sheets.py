import gspread
from google.oauth2.service_account import Credentials
from .models import SCHEMA

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetWriter:
    def __init__(self, sa_json: str, sheet_id: str, worksheet: str = "Leads"):
        creds = Credentials.from_service_account_file(sa_json, scopes=SCOPES)
        self.gc = gspread.authorize(creds)
        self.sh = self.gc.open_by_key(sheet_id)
        self._default_ws_name = worksheet

    def _existing_keys(self, ws) -> set:
        col = SCHEMA.index("lead_key") + 1
        return set(ws.col_values(col)[1:])

    def upsert(self, leads: list) -> int:
        try:
            ws = self.sh.worksheet(self._default_ws_name)
        except gspread.WorksheetNotFound:
            ws = self.sh.add_worksheet(self._default_ws_name, rows=1000, cols=len(SCHEMA))
        if ws.row_values(1) != SCHEMA:
            ws.update([SCHEMA], "A1")
        existing = self._existing_keys(ws)
        new_rows = [l.row() for l in leads if l.lead_key not in existing]
        if new_rows:
            ws.append_rows(new_rows, value_input_option="RAW")
        return len(new_rows)

    def write_job(self, leads: list, sheet_name: str) -> int:
        """Create (or reuse) a worksheet named by date/time and write all leads
        fresh into it — one sheet per discovery job."""
        # Google Sheets tab names may not contain : / ? * [ ]
        safe = sheet_name.replace(":", "-")
        try:
            ws = self.sh.worksheet(safe)
        except gspread.WorksheetNotFound:
            ws = self.sh.add_worksheet(safe, rows=1000, cols=len(SCHEMA))
        rows = [SCHEMA] + [l.row() for l in leads]
        ws.clear()
        ws.update(rows, "A1", value_input_option="RAW")
        return len(leads)
