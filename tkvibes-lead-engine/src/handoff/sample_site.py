"""Sample-site generator hook — builds concept-site spec for downstream agent."""

from ..models import Lead


def build_site_spec(lead: Lead) -> dict:
    return {
        "lead_key": lead.lead_key,
        "business_name": lead.business_name,
        "category": lead.category,
        "address": lead.address,
        "city": lead.city,
        "phone_primary": lead.phone_primary,
        "whatsapp": lead.whatsapp,
        "opening_hours": lead.opening_hours,
        "rating": lead.rating,
        "review_count": lead.review_count,
        "socials": lead.socials,
        "lead_score": lead.lead_score,
        "lead_tier": lead.lead_tier,
        "source_url": lead.source_url,
        "watermark": "Concept by TKVibes — not affiliated",
    }


def spec_to_json(lead: Lead) -> str:
    import json
    return json.dumps(build_site_spec(lead), indent=2, ensure_ascii=False)
