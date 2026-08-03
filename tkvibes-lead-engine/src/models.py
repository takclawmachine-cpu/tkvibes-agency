from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta

# ── CRM-aware schema ─────────────────────────────────────────────────────────
# 35 original fields + wa_link + region/country/assignment + pain points/pitch.
# Column order is appended so existing sheet rows stay aligned.
SCHEMA = [
    "lead_key","business_name","category","owner_name","phone_primary",
    "phone_secondary","whatsapp","email","address","city","pincode",
    "latitude","longitude","opening_hours","has_website","website_url",
    "website_quality","rating","review_count","years_in_business","socials",
    "source","source_url","place_id","lead_score","lead_tier",
    "data_fetched_at","stale_after","outreach_status","opt_out",
    "sample_site_url","pitch_deck_url","notes","contact_channel","wa_link",
    "region","country","assigned_employee","pain_points","recommended_pitch",
]

@dataclass
class Lead:
    business_name: str = ""
    category: str = ""
    owner_name: str = ""
    phone_primary: str = ""
    phone_secondary: str = ""
    whatsapp: str = ""
    email: str = ""
    address: str = ""
    city: str = ""
    pincode: str = ""
    latitude: float | None = None
    longitude: float | None = None
    opening_hours: str = ""
    has_website: bool = False
    website_url: str = ""
    website_quality: str = "none"
    rating: float | None = None
    review_count: int | None = None
    years_in_business: str = ""
    socials: str = ""
    source: str = ""
    source_url: str = ""
    place_id: str = ""
    lead_score: int = 0
    lead_tier: str = "COLD"
    data_fetched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    stale_after: str = ""
    outreach_status: str = "new"
    opt_out: bool = False
    sample_site_url: str = ""
    pitch_deck_url: str = ""
    notes: str = ""
    contact_channel: str = ""
    wa_link: str = ""
    # ── CRM columns ──
    region: str = ""
    country: str = ""
    assigned_employee: str = ""
    pain_points: str = ""
    recommended_pitch: str = ""
    lead_key: str = ""

    def finalize_dates(self, stale_days: int = 30):
        fetched = datetime.fromisoformat(self.data_fetched_at)
        self.stale_after = (fetched + timedelta(days=stale_days)).isoformat()

    def row(self) -> list:
        d = asdict(self)
        return [d.get(k, "") for k in SCHEMA]

    def to_dict(self) -> dict:
        return asdict(self)
