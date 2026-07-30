import csv
import os
from rapidfuzz import fuzz

_DNC_CACHE: set[str] | None = None


def _dnc_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "data", "do_not_contact.csv")


def load_dnc() -> set[str]:
    """Load Do-Not-Contact list (business names + normalized phones)."""
    global _DNC_CACHE
    if _DNC_CACHE is not None:
        return _DNC_CACHE
    dnc = set()
    path = _dnc_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("opt_out", "").upper() == "TRUE":
                    name = (row.get("business_name") or "").strip().lower()
                    phone = (row.get("phone") or "").strip()
                    if name:
                        dnc.add(name)
                    if phone:
                        dnc.add(phone)
    _DNC_CACHE = dnc
    return dnc


def lead_key(lead) -> str:
    if lead.phone_primary:
        return "ph:" + lead.phone_primary
    if lead.place_id:
        return "pid:" + lead.place_id
    return "nm:" + (lead.business_name + lead.pincode).lower().replace(" ", "")


def dedupe(leads: list) -> list:
    seen, out = {}, []
    for l in leads:
        l.lead_key = lead_key(l)
        if l.lead_key in seen:
            _merge(seen[l.lead_key], l)
            continue
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
    return out


def _merge(keep, other):
    for fld in ("email", "whatsapp", "owner_name", "website_url", "opening_hours"):
        if not getattr(keep, fld) and getattr(other, fld):
            setattr(keep, fld, getattr(other, fld))


def apply_dnc(leads: list) -> list:
    """Mark leads on the DNC list as opt_out=True."""
    dnc = load_dnc()
    for l in leads:
        name = (l.business_name or "").strip().lower()
        if name in dnc or l.phone_primary in dnc:
            l.opt_out = True
            l.outreach_status = "opt_out"
    return leads
