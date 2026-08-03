from .log_config import get_logger

logger = get_logger(__name__)


def score_lead(lead, high_fit: list[str]) -> None:
    s = 0
    s += {
        "none": 45,
        "social_only": 40,
        "directory_microsite": 35,
        "weak": 20,
        "ok": 0,
    }.get(lead.website_quality or "", 0)

    if lead.phone_primary:
        s += 15
    if lead.whatsapp:
        s += 5
    if lead.email:
        s += 5

    rc = lead.review_count or 0
    s += 10 if rc >= 10 else 5 if rc >= 3 else 0

    rating = lead.rating
    if rating is not None and 3.5 <= rating <= 5:
        s += 5
    if lead.years_in_business:
        s += 5
    if high_fit and any(
        h in (lead.category or "").lower() for h in high_fit
    ):
        s += 10

    lead.lead_score = min(s, 100)
    lead.lead_tier = "HOT" if s >= 70 else "WARM" if s >= 45 else "COLD"

    logger.debug(
        "Score %s: %d points → %s",
        lead.business_name,
        lead.lead_score,
        lead.lead_tier,
    )
