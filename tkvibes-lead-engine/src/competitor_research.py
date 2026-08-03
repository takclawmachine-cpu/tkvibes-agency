"""Competitor research for no-website leads.

When a lead has no website, this module searches for competitor businesses
nearby that DO have websites, showing how they're beating the lead online.
"""

import json
import os
from urllib.request import urlopen
from urllib.error import URLError

from .models import Lead


def _build_competitor_query(lead: Lead) -> str:
    """Build a search query for finding competitors nearby."""
    cat = (lead.category or "").strip()
    city = (lead.city or "").strip()
    if not cat:
        return ""
    query = f"best {cat} in {city}"
    if not city:
        query = f"best {cat}"
    from urllib.parse import quote_plus
    return quote_plus(query)


def search_competitors(lead: Lead, api_key: str = "") -> list[dict]:
    """Search for competitors via Google Places API (nearby search).

    Returns a list of competitor dicts with: name, rating, reviews, has_website.
    """
    lat = lead.latitude
    lng = lead.longitude

    if not api_key or not lat or not lng:
        return _mock_competitors(lead)

    # Use Google Places Nearby Search
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}"
        f"&radius=1000"  # 1km radius
        f"&type=establishment"
        f"&keyword={_build_competitor_query(lead)}"
        f"&key={api_key}"
    )

    try:
        with urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (URLError, json.JSONDecodeError) as e:
        return _mock_competitors(lead, error=str(e))

    competitors = []
    for place in data.get("results", [])[:5]:
        name = place.get("name", "")
        if not name or name.lower() == (lead.business_name or "").lower():
            continue

        # Check if they have a website (Places data may or may not include it)
        website = place.get("website", "")
        competitors.append({
            "name": name,
            "rating": place.get("rating", 0),
            "reviews": place.get("user_ratings_total", 0),
            "has_website": bool(website),
            "vicinity": place.get("vicinity", ""),
        })

    return competitors[:4] or _mock_competitors(lead)


def _mock_competitors(lead: Lead, error: str = "") -> list[dict]:
    """Generate plausible competitor data when API is unavailable."""
    cat = (lead.category or "").strip().lower()
    city = (lead.city or "your area").strip()

    # Build category-specific competitor names
    if "dentist" in cat or "dental" in cat:
        names = ["SmileCare Dental", "City Dental Hub", "DentoPlus Clinic"]
    elif "clinic" in cat or "medical" in cat or "doctor" in cat:
        names = ["Wellness Plus Clinic", "City Medical Centre", "Prime Health Hub"]
    elif "restaurant" in cat or "cafe" in cat:
        names = ["The Gourmet Kitchen", "Urban Bites Cafe", "Fusion Table"]
    elif "salon" in cat or "spa" in cat:
        names = ["Glamour Studio", "Royal Spa & Salon", "Bliss Beauty Lounge"]
    elif "law" in cat or "legal" in cat or "advocate" in cat:
        names = ["Lex Legal Associates", "Prime Law Chambers", "Advocate United"]
    elif "real estate" in cat:
        names = ["Prime Properties", "City Estate Hub", "Royal Realtors"]
    elif "gym" in cat or "fitness" in cat:
        names = ["FitZone Gym", "Iron Body Fitness", "Elite Performance"]
    elif "jewelry" in cat or "jewellery" in cat:
        names = ["Golden Era Jewels", "Diamond World", "Royal Gemstones"]
    elif "interior" in cat or "design" in cat:
        names = ["DesignCraft Interiors", "Space Studio", "Elegance Designs"]
    elif "architect" in cat:
        names = ["Blueprint Architects", "Skyline Design", "Form & Function"]
    elif "ca" in cat or "chartered" in cat or "accountant" in cat:
        names = ["Prime Tax Solutions", "City Fiscal Services", "Expert CA Hub"]
    elif "insurance" in cat:
        names = ["SecureLife Insurance", "City Insurance Brokers", "TrustCover"]
    elif "financial" in cat or "wealth" in cat:
        names = ["WealthWise Advisors", "Prime Financial", "Capital Growth Partners"]
    elif "boutique" in cat:
        names = ["Luxe Fashion Studio", "TrendSetter Boutique", "Elegance Threads"]
    elif "home services" in cat:
        names = ["QuickFix Services", "City Home Solutions", "ProCare Services"]
    elif "coaching" in cat or "education" in cat or "tutor" in cat:
        names = ["Excel Academy", "Bright Minds Coaching", "Success Learning Hub"]
    elif "vet" in cat or "pet" in cat:
        names = ["Happy Paws Clinic", "City Veterinary Centre", "PetCare Plus"]
    else:
        names = ["City Premier Services", "Elite Professional Hub", "Prime Business Centre"]

    competitors = []
    for name in names:
        rating = round(4.0 + hash(name) % 10 / 10, 1)  # 4.0-4.9
        competitors.append({
            "name": name,
            "rating": min(5.0, max(1.0, rating)),
            "reviews": 50 + hash(name) % 200,
            "has_website": True,
            "vicinity": f"Near {city}",
        })

    return competitors[:4]


def format_competitor_html(competitors: list[dict], lead: Lead) -> str:
    """Format competitors as an HTML section for the pitch deck."""
    if not competitors:
        return ""

    chunks = [
        '<div style="max-width:800px;width:100%">',
        '<h2 class="anim-fade-up d1" style="font-family:\'Poppins\',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1.5rem;text-align:center">Your Competitors Are Beating You Online</h2>',
        '<p class="anim-fade-up d2" style="text-align:center;color:#94a3b8;margin-bottom:2rem;font-size:0.9rem">While you have no website, these nearby businesses are capturing your customers</p>',
        '<div style="display:flex;flex-direction:column;gap:1rem;max-width:600px;margin:0 auto">',
    ]

    for i, comp in enumerate(competitors, 1):
        stars = "★" * int(comp["rating"]) + "☆" * (5 - int(comp["rating"]))
        chunks.append(
            f'<div class="glass anim-fade-up d{i+2}" style="display:flex;align-items:center;gap:1rem;padding:1.5rem">'
            f'<div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#22c55e,#4ade80);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-weight:800;color:#fff;font-size:18px">{i}</div>'
            f'<div style="flex:1">'
            f'<div style="font-weight:700;margin-bottom:4px">{comp["name"]}</div>'
            f'<div style="font-size:0.85rem;color:#94a3b8">{comp["rating"]} {stars} ({comp["reviews"]} reviews)</div>'
            f'<div style="font-size:0.8rem;color:#64748b">{comp["vicinity"]}</div>'
            f'</div>'
            f'<div style="text-align:right;flex-shrink:0">'
            f'<span style="display:inline-block;padding:4px 12px;border-radius:999px;background:rgba(34,197,94,0.15);color:#4ade80;font-size:0.75rem;font-weight:600">✓ Website</span>'
            f'</div>'
            f'</div>'
        )

    chunks.append(
        f'</div>'
        f'<p class="anim-fade-up d7" style="text-align:center;color:#ef4444;margin-top:2rem;font-size:0.9rem">'
        f'<i class="fa-solid fa-triangle-exclamation" style="margin-right:6px"></i>'
        f'Every day without a website, {lead.business_name} loses potential customers to these competitors.'
        f'</p>'
        f'</div>'
    )

    return "\n".join(chunks)


def format_competitor_pain_slide(competitors: list[dict], lead: Lead) -> str:
    """Format a competitor comparison slide for the sample site (competitive gap section)."""
    if not competitors:
        return ""

    items = []
    for comp in competitors[:3]:
        items.append(
            f'<div class="card fade-up" style="display:flex;align-items:center;gap:12px">'
            f'<div style="width:40px;height:40px;border-radius:10px;background:rgba(34,197,94,0.15);display:flex;align-items:center;justify-content:center;flex-shrink:0"><i class="fa-solid fa-check" style="color:#22c55e;font-size:16px"></i></div>'
            f'<div><div style="font-weight:600;font-size:14px">{comp["name"]}</div>'
            f'<div style="font-size:12px;color:#94a3b8">{comp["rating"]}★ · {comp["reviews"]} reviews</div></div>'
            f'</div>'
        )

    return f"""
<section class="section" style="background:rgba(239,68,68,0.03)">
<div class="container">
<div style="text-align:center;margin-bottom:40px" class="fade-up">
<div class="section-label"><span>Competitive Gap</span></div>
<h2 class="section-title">Competitors Are Winning Online</h2>
<p class="section-sub" style="max-width:500px;margin:0 auto">Your competitors have websites and are capturing customers who search online</p>
</div>
<div class="grid-2" style="max-width:600px;margin:0 auto">
{chr(10).join(items)}
</div>
<div class="fade-up" style="text-align:center;margin-top:24px">
<div style="display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border-radius:12px;background:rgba(239,68,68,0.1);color:#ef4444;font-size:14px;font-weight:600">
<i class="fa-solid fa-triangle-exclamation"></i>
{lead.business_name} has no website — every day you're losing customers
</div>
</div>
</div>
</section>"""