import csv
import os
from rapidfuzz import fuzz
from .log_config import get_logger

logger = get_logger(__name__)

_DNC_CACHE: set[str] | None = None
_DNC_CACHE_PATH = None  # track which file was cached


def _dnc_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "data", "do_not_contact.csv")


def load_dnc() -> set[str]:
    """Load Do-Not-Contact list (business names + normalized phones)."""
    global _DNC_CACHE, _DNC_CACHE_PATH
    path = _dnc_path()
    if _DNC_CACHE is not None and _DNC_CACHE_PATH == path:
        return _DNC_CACHE
    dnc: set[str] = set()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("opt_out", "").upper() == "TRUE":
                        name = (row.get("business_name") or "").strip().lower()
                        phone = (row.get("phone") or "").strip()
                        if name:
                            dnc.add(name)
                        if phone:
                            dnc.add(phone)
        except (OSError, csv.Error) as e:
            logger.error("Failed to load DNC list from %s: %s", path, e)
    else:
        logger.debug("DNC file not found at %s", path)
    _DNC_CACHE = dnc
    _DNC_CACHE_PATH = path
    return dnc


def invalidate_dnc_cache():
    """Force reload of DNC on next call (useful for hot-reload scenarios)."""
    global _DNC_CACHE
    _DNC_CACHE = None
    _DNC_CACHE_PATH = None


def lead_key(lead) -> str:
    if lead.phone_primary:
        return "ph:" + lead.phone_primary
    if lead.place_id:
        return "pid:" + lead.place_id
    return "nm:" + (lead.business_name + lead.pincode).lower().replace(" ", "")


def dedupe(leads: list) -> list:
    """Deduplicate leads by exact key match, then fuzzy name match within same city."""
    seen, out = {}, []
    for l in leads:
        l.lead_key = lead_key(l)
        if l.lead_key in seen:
            _merge(seen[l.lead_key], l)
            continue
        # Fuzzy match: same city + name similarity > 92%
        dup = next(
            (
                k
                for k in out
                if k.city == l.city
                and fuzz.token_sort_ratio(k.business_name, l.business_name) > 92
            ),
            None,
        )
        if dup:
            _merge(dup, l)
            continue
        seen[l.lead_key] = l
        out.append(l)
    if len(leads) != len(out):
        logger.info("Deduped %d → %d leads", len(leads), len(out))
    return out


def _merge(keep, other):
    for fld in ("email", "whatsapp", "owner_name", "website_url", "opening_hours"):
        if not getattr(keep, fld) and getattr(other, fld):
            setattr(keep, fld, getattr(other, fld))


def apply_dnc(leads: list) -> list:
    """Mark leads on the DNC list as opt_out=True."""
    dnc = load_dnc()
    if not dnc:
        logger.debug("DNC list empty, no filtering applied")
        return leads
    marked = 0
    for l in leads:
        name = (l.business_name or "").strip().lower()
        phone = (l.phone_primary or "").strip()
        if name in dnc or phone in dnc:
            l.opt_out = True
            l.outreach_status = "opt_out"
            marked += 1
    if marked:
        logger.info("DNC filter marked %d leads as opt_out", marked)
    return leads
