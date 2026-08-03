import re
import phonenumbers
from .log_config import get_logger

logger = get_logger(__name__)

SOCIAL_ONLY = ("facebook.com", "instagram.com", "linktr.ee", "wa.me", "google.com/maps")
MICROSITE = ("indiamart.com", "justdial.com", "sulekha.com", "tradeindia.com")


def normalize_phone(raw: str, region: str | None = None) -> str:
    """Normalize a phone number to E.164. Auto-detects region if not provided."""
    if not raw:
        return ""
    raw = raw.strip()
    if raw.startswith("+"):
        region = None
    elif region is None:
        if raw.startswith("91") or raw.startswith("0"):
            region = "IN"
        elif raw.startswith("1"):
            region = "US"
        elif raw.startswith("44"):
            region = "GB"
        elif raw.startswith("61"):
            region = "AU"
        elif raw.startswith("971"):
            region = "AE"
        elif raw.startswith("65"):
            region = "SG"
        else:
            region = "IN"
    try:
        num = phonenumbers.parse(raw, region)
        if phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        logger.debug("Could not parse phone: %s", raw)
    except Exception:
        logger.debug("Unexpected phone parse error: %s", raw)
    return raw


def classify_website(url: str) -> tuple[bool, str]:
    """Returns (has_real_website, quality)."""
    if not url:
        return False, "none"
    u = url.lower()
    if any(s in u for s in SOCIAL_ONLY):
        return False, "social_only"
    if any(m in u for m in MICROSITE):
        return False, "directory_microsite"
    if u.startswith("http://") and not u.startswith("https://"):
        return True, "weak"
    return True, "ok"


def enrich(lead):
    lead.phone_primary = normalize_phone(lead.phone_primary)
    lead.phone_secondary = normalize_phone(lead.phone_secondary)
    lead.has_website, lead.website_quality = classify_website(lead.website_url)
    if re.search(r"wa\.me|whatsapp", lead.socials.lower()):
        lead.whatsapp = lead.phone_primary
    return lead
