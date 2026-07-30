"""Pitch-deck generator hook — builds deck spec for downstream agent."""

import json
from ..models import Lead


def build_deck_spec(lead: Lead) -> dict:
    return {
        "lead_key": lead.lead_key,
        "business_name": lead.business_name,
        "category": lead.category,
        "city": lead.city,
        "phone_primary": lead.phone_primary,
        "email": lead.email,
        "rating": lead.rating,
        "review_count": lead.review_count,
        "website_quality": lead.website_quality,
        "lead_score": lead.lead_score,
        "lead_tier": lead.lead_tier,
        "slides": [
            {
                "type": "cover",
                "title": f"A better online presence for {lead.business_name}",
                "subtitle": "TKVibes Digital Agency",
            },
            {
                "type": "gap",
                "title": "The gap",
                "body": (
                    f"You're on Google with a {lead.rating or 'N/A'} star rating "
                    f"and {lead.review_count or 0} reviews, "
                    "but customers can't find a real website."
                ),
            },
            {
                "type": "concept",
                "title": "Your concept site",
                "body": "(screenshot of the generated sample site)",
            },
            {
                "type": "deliverables",
                "title": "What TKVibes delivers",
                "body": "Web design, brand identity, SEO, automation",
            },
            {
                "type": "proof",
                "title": "Proof",
                "body": "50+ projects, 98% satisfaction",
            },
            {
                "type": "offer",
                "title": "Offer & next step",
                "body": (
                    "Book a free consultation\n"
                    "services@tkvibes.in | +91 98182 46938 | WhatsApp"
                ),
            },
        ],
        "watermark": "Concept by TKVibes — not affiliated",
    }


def spec_to_json(lead: Lead) -> str:
    return json.dumps(build_deck_spec(lead), indent=2, ensure_ascii=False)
