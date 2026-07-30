"""Phone-channel outreach for leads.

Most leads in this segment have no website and no email, but 100% have a
phone number. This module makes those numbers actually usable:

  1. classify  — mobile vs fixed-line (you cannot SMS/WhatsApp a landline)
  2. route     — pick sms / whatsapp / call per lead
  3. compose   — render a personalised message from a template
  4. export    — write a send-queue (CSV + JSON) for the sending tool

COMPLIANCE (read before sending anything to Indian numbers):
  * TRAI TCCCPA: commercial SMS to Indian subscribers must go through a
    DLT-registered header + pre-approved template via an Indian aggregator
    (MSG91, Gupshup, Kaleyra...). Sending marketing SMS from a raw gateway
    is illegal and gets the number blacklisted.
  * DND/NCPR: numbers on the National Customer Preference Register must be
    scrubbed for promotional traffic. Transactional/service-explicit
    messages are treated differently.
  * WhatsApp: business-initiated marketing requires the WhatsApp Business
    API with a Meta-approved *template*. Bulk-messaging from a personal
    app violates ToS and gets the number banned, usually fast.

Because of the above this module DOES NOT auto-send. It produces a
reviewed queue plus click-to-chat links, so a human stays in the loop.
Wire an approved provider in `providers.py` when you have DLT/WABA set up.
"""

from __future__ import annotations

import csv
import json
import os
import re
import urllib.parse

import phonenumbers

# Channels a lead can be reached on, best-effort first
CHANNEL_SMS = "sms"
CHANNEL_WHATSAPP = "whatsapp"
CHANNEL_CALL = "call"
CHANNEL_NONE = "none"

_MOBILEISH = {
    phonenumbers.PhoneNumberType.MOBILE,
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
}


def classify_number(raw: str) -> dict:
    """Return {valid, e164, type, region, sms_capable}."""
    out = {"valid": False, "e164": "", "type": "unknown",
           "region": "", "sms_capable": False}
    if not raw:
        return out
    try:
        n = phonenumbers.parse(raw, None if raw.startswith("+") else "IN")
    except Exception:
        return out
    if not phonenumbers.is_valid_number(n):
        return out

    t = phonenumbers.number_type(n)
    names = {
        phonenumbers.PhoneNumberType.MOBILE: "mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "fixed_line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_or_mobile",
        phonenumbers.PhoneNumberType.VOIP: "voip",
        phonenumbers.PhoneNumberType.TOLL_FREE: "toll_free",
    }
    out.update(
        valid=True,
        e164=phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164),
        type=names.get(t, "other"),
        region=phonenumbers.region_code_for_number(n) or "",
        sms_capable=t in _MOBILEISH,
    )
    return out


def route_channel(lead) -> str:
    """Pick the best phone channel for a lead."""
    info = classify_number(lead.phone_primary)
    if not info["valid"]:
        return CHANNEL_NONE
    if info["sms_capable"]:
        # WhatsApp penetration in IN is near-universal on mobile
        return CHANNEL_WHATSAPP if info["region"] == "IN" else CHANNEL_SMS
    return CHANNEL_CALL


def clean_name(raw: str) -> str:
    """Google Maps names are SEO-stuffed ("X Clinic - Dr Y - Best Doctor in Z").
    Take the first meaningful segment so messages read like a human wrote them."""
    if not raw:
        return "there"
    name = re.split(r"\s+[-|–—]\s+|\s*\|\s*", raw)[0].strip()
    name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
    # Drop trailing marketing tails even without a separator
    name = re.sub(r"\b(best|top|no\.?\s*1|#1)\b.*$", "", name,
                  flags=re.IGNORECASE).strip(" -–—,")
    return name or raw.strip()


def clean_category(raw: str) -> str:
    """Lowercase a Places category for mid-sentence use ("Doctor" -> "clinic")."""
    c = (raw or "").strip().lower()
    return c or "business"


def render(template: str, lead) -> str:
    """Fill a message template with lead fields. Unknown keys stay blank."""
    class _Blank(dict):
        def __missing__(self, k):
            return ""

    return template.format_map(_Blank(
        business_name=clean_name(lead.business_name),
        city=lead.city,
        category=clean_category(lead.category),
        rating=lead.rating or "",
        review_count=lead.review_count or "",
        sample_site_url=lead.sample_site_url,
    )).strip()


def wa_link(e164: str, message: str) -> str:
    """Click-to-chat link — opens WhatsApp with the message pre-filled.
    Human presses send, so this stays inside WhatsApp's ToS."""
    return (f"https://wa.me/{e164.lstrip('+')}?text="
            f"{urllib.parse.quote(message)}")


def _has_real_site(lead) -> bool:
    """Re-derive from the URL rather than trusting has_website/website_quality —
    older exported rows carry has_website=False alongside a real URL."""
    from ..enrich import classify_website
    real, _ = classify_website(getattr(lead, "website_url", "") or "")
    return real


def build_queue(leads: list, template: str, include_landline: bool = False,
                template_has_site: str = "") -> list[dict]:
    """Build a reviewable outreach queue. Skips opt-outs and invalid numbers.

    `template` is used for leads with no real website; `template_has_site`
    (if given) for leads that already have one — never tell a business you
    "couldn't find their website" when they have one.
    """
    queue = []
    for l in leads:
        if l.opt_out:
            continue
        info = classify_number(l.phone_primary)
        if not info["valid"]:
            continue
        channel = route_channel(l)
        if channel == CHANNEL_CALL and not include_landline:
            continue

        tpl = template
        if template_has_site and _has_real_site(l):
            tpl = template_has_site
        msg = render(tpl, l)
        queue.append({
            "lead_key": l.lead_key,
            "business_name": l.business_name,
            "city": l.city,
            "category": l.category,
            "phone": info["e164"],
            "number_type": info["type"],
            "channel": channel,
            "lead_tier": l.lead_tier,
            "lead_score": l.lead_score,
            "message": msg,
            "wa_link": wa_link(info["e164"], msg) if channel == CHANNEL_WHATSAPP else "",
            "status": "pending_review",
        })
    queue.sort(key=lambda r: -r["lead_score"])
    return queue


def export_queue(queue: list[dict], csv_path: str, json_path: str = "") -> None:
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    cols = ["lead_key", "business_name", "city", "category", "phone",
            "number_type", "channel", "lead_tier", "lead_score",
            "message", "wa_link", "status"]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(queue)
    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
