"""Generate human-readable pain points and pitch recommendations for each lead."""

# ── Category → pitch angle ──────────────────────────────────────────────────
_CATEGORY_PITCH = {
    "dental": "Medical website with patient booking + local SEO | highlight online booking, Google reviews, and telehealth",
    "dentist": "Medical website with patient booking + local SEO | highlight online booking, Google reviews, and telehealth",
    "doctor": "Medical website with patient booking + local SEO | highlight online booking, Google reviews, and telehealth",
    "clinic": "Medical website with patient booking + local SEO | highlight online booking, Google reviews, and telehealth",
    "medical": "Medical website with patient booking + local SEO | highlight online booking, Google reviews, and telehealth",
    "hospital": "Full hospital website with doctor profiles + patient portal + SEO",
    "lawyer": "Professional legal website with trust signals + case studies + SEO",
    "law firm": "Professional legal website with trust signals + case studies + SEO",
    "advocate": "Professional legal website with trust signals + case studies + SEO",
    "attorney": "Professional legal website with trust signals + case studies + SEO",
    "solicitor": "Professional legal website with trust signals + case studies + SEO",
    "veterinary": "Veterinary clinic website with pet owner resources + booking + SEO",
    "pet clinic": "Veterinary clinic website with pet owner resources + booking + SEO",
    "veterinarian": "Veterinary clinic website with pet owner resources + booking + SEO",
    "vet": "Veterinary clinic website with pet owner resources + booking + SEO",
    "orthopedic": "Orthopedic clinic website with patient education + booking + SEO",
    "skin clinic": "Dermatology/skin clinic website with before-after gallery + SEO",
    "dermatologist": "Dermatology/skin clinic website with before-after gallery + SEO",
    "cosmetic": "Cosmetic clinic website with before-after gallery + treatment pages + SEO",
    "eye clinic": "Eye clinic website with vision services + booking + SEO",
    "ophthalmologist": "Eye clinic website with vision services + booking + SEO",
    "optometry": "Optometry website with eye exam booking + product showcase + SEO",
    "physiotherapy": "Physiotherapy clinic website with treatment pages + booking + SEO",
    "physiotherapist": "Physiotherapy clinic website with treatment pages + booking + SEO",
    "pediatric": "Pediatric website with parent resources + booking + SEO",
    "cardiology": "Cardiology clinic website with patient education + booking + SEO",
    "fertility": "Fertility clinic website with treatment info + patient stories + SEO",
    "interior designer": "Portfolio website with project gallery + client testimonials + SEO",
    "architect": "Architecture firm website with portfolio + project pages + SEO",
    "architecture": "Architecture firm website with portfolio + project pages + SEO",
    "chartered accountant": "CA firm website with service pages + client portal + local SEO",
    "ca firm": "CA firm website with service pages + client portal + local SEO",
    "financial advisor": "Financial advisor website with service pages + trust signals + SEO",
    "wealth management": "Wealth management website with portfolio showcase + SEO",
    "insurance": "Insurance agency website with quote forms + policy pages + SEO",
    "real estate": "Real estate website with property listings + agent profiles + SEO",
    "boutique": "Boutique e-commerce website with product showcase + SEO",
    "luxury": "Luxury brand website with high-end design + storytelling + SEO",
    "salon": "Salon website with booking + service pages + gallery + SEO",
    "spa": "Spa website with treatment menu + booking + gallery + SEO",
    "jewelry": "Jewelry website with product catalog + high-res gallery + SEO",
    "cafe": "Cafe website with menu + location + online ordering + SEO",
    "restaurant": "Restaurant website with menu + reservations + gallery + SEO",
    "gym": "Gym website with membership plans + class schedule + SEO",
    "home services": "Home services website with service pages + booking + local SEO",
    "coaching": "Coaching website with programs + testimonials + booking + SEO",
    "retail": "E-commerce website with product catalog + payment + SEO",
    # Food & Beverages
    "restaurant": "Restaurant website with online menu + reservations + delivery integration + SEO",
    "cafe": "Cafe website with menu + location + online ordering + SEO",
    "bakery": "Bakery website with product showcase + online ordering + gallery + SEO",
    "cloud kitchen": "Cloud kitchen website with menu + delivery app integration + SEO",
    "caterer": "Catering website with menu packages + event gallery + booking + SEO",
    "brewery": "Brewery website with beer menu + taproom info + events + SEO",
    "bar": "Bar/Pub website with drinks menu + events + reservations + SEO",
    "ice cream": "Ice cream parlor website with flavor menu + locations + SEO",
    "confectionery": "Confectionery website with product catalog + online ordering + SEO",
    "food truck": "Food truck website with schedule + location tracker + menu + SEO",
}

# ── Pain point builders ──────────────────────────────────────────────────────


def _pain_website(lead) -> str | None:
    """Return a website-related pain point or None."""
    q = lead.website_quality or ""
    if q == "none":
        return "No website — losing customers to competitors with online presence"
    if q == "social_only":
        return "Only social media presence — no dedicated website limits credibility"
    if q == "directory_microsite":
        return "Relies on directory listing only — cannot control brand image or capture leads"
    if q == "weak":
        return "Outdated/basic website — poor first impression, likely losing mobile visitors"
    return None


def _pain_reviews(lead) -> str | None:
    """Return a review-related pain point or None."""
    rc = lead.review_count or 0
    rating = lead.rating or 0
    if 0 < rc < 5:
        return "Very few reviews — potential customers find it hard to trust"
    if rc < 1:
        return "No online reviews — lost credibility against competitors with ratings"
    if rating and rating < 3.5:
        return "Below-average online reviews — reputation management needed"
    return None


def _pain_contact(lead) -> str | None:
    """Return a contact-related pain point or None."""
    if not lead.email and not lead.phone_primary:
        return "No contact info listed — missed customer inquiries"
    if not lead.email:
        return "No email listed — missed lead capture opportunities"
    return None


def _pain_age(lead) -> str | None:
    """Return a business-age pain point or None."""
    yib = (lead.years_in_business or "").strip()
    if not yib:
        return None
    try:
        years = float(yib.split()[0])
        if years < 2:
            return "New business — needs to establish online presence fast"
    except (ValueError, IndexError):
        pass
    return None


def _pain_category(lead) -> str | None:
    """Return a category-specific pain point or None."""
    cat = (lead.category or "").lower()
    if "dental" in cat or "dentist" in cat:
        return "Patients search for 'dentist near me' — losing local search traffic without a site"
    if "lawyer" in cat or "law" in cat or "advocate" in cat or "legal" in cat:
        return "Clients research lawyers online before calling — no website = lost cases"
    if "clinic" in cat or "medical" in cat or "doctor" in cat:
        return "Patients expect online booking and doctor profiles — missing without a website"
    if "real estate" in cat:
        return "Property buyers search online first — missing listings and virtual tours"
    if "restaurant" in cat or "cafe" in cat:
        return "Diners check menus and reviews online — no website = lost customers"
    if "bakery" in cat or "confectionery" in cat:
        return "Customers search for bakeries online — no website = missed orders and foot traffic"
    if "cloud kitchen" in cat or "food truck" in cat:
        return "Online ordering is everything — no website means no discoverability"
    if "caterer" in cat or "catering" in cat:
        return "Event planners search for caterers online — no website = lost contracts"
    if "brewery" in cat or "bar" in cat:
        return "Nightlife seekers check menus and events online — no website = missed walk-ins"
    return None


def build_pain_points(lead) -> str:
    """Build a concise, human-readable pain-points string for this lead."""
    points = []
    for builder in (_pain_website, _pain_reviews, _pain_contact, _pain_age, _pain_category):
        p = builder(lead)
        if p and p not in points:
            points.append(p)

    if not points:
        if lead.website_quality == "ok":
            return "Existing website needs SEO optimization to outperform competitors"
        return "Needs stronger online presence to grow in a competitive market"

    # Take top 2-3
    return " | ".join(points[:3])


def recommend_pitch(lead) -> str:
    """Return a pitch recommendation based on the lead's category and pain points."""
    cat = (lead.category or "").lower()

    # Find best matching category pitch
    base = None
    for kw, pitch in _CATEGORY_PITCH.items():
        if kw in cat:
            base = pitch
            break

    if not base:
        base = "Modern website + local SEO package | tailored to your industry"

    # Adjust based on website quality
    wq = lead.website_quality or "none"
    if wq == "none":
        base = "Lead-gen website + local SEO | " + base
    elif wq == "social_only":
        base = "Professional website + social media integration | " + base
    elif wq == "directory_microsite":
        base = "Standalone website + SEO | " + base
    elif wq == "weak":
        base = "Website redesign + SEO optimization | " + base
    elif wq == "ok":
        base = "SEO + review generation + conversion optimization | " + base

    return base