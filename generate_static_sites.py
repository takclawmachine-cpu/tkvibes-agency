"""
Instant static site generator — creates a basic sample website + pitch deck
for every lead in the CRM export. No AI calls, works in seconds.
Uses the 5 layout templates from ai_site_generator.py without LLM content.
"""
import json, os, sys, re, random
import urllib.request
import base64

REPO_ROOT = os.path.expanduser("~/Desktop/tkvibes-agency")

# Inline color palettes
CATEGORY_COLORS = {
    "dental":       ["#2d6a9f", "#4a9bc7", "#f4a261"],
    "lawyer":       ["#1b2838", "#3d5a80", "#c9a84c"],
    "medical":      ["#1b4332", "#2d6a4f", "#95d5b2"],
    "pet":          ["#5c4033", "#8b5e3c", "#d4a76a"],
    "interior":     ["#2c1810", "#6b4c3b", "#c9a97c"],
    "restaurant":   ["#6b1d1d", "#9b2226", "#e6b31e"],
    "salon":        ["#4a0e4e", "#7b2d8b", "#d4a0d4"],
    "default":      ["#1a1a2e", "#16213e", "#d4a853"],
}

CATEGORY_IMAGES = {
    "dental": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=1200",
    "lawyer": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200",
    "medical": "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200",
    "pet": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=1200",
    "interior": "https://images.unsplash.com/photo-1618220179428-22790b461013?w=1200",
    "restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200",
    "salon": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200",
    "default": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200",
}


def slugify(name):
    """Match Python slugify from git_publish.py."""
    s = re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()
    s = re.sub(r'\s+', '-', s)
    return re.sub(r'-{2,}', '-', s)[:60]


def get_palette(category):
    """Get color palette for a category."""
    cat = (category or "").lower()
    for key, colors in CATEGORY_COLORS.items():
        if key in cat:
            return colors
    return CATEGORY_COLORS["default"]


def get_hero_image(category):
    """Get hero background image URL for a category."""
    cat = (category or "").lower()
    for key, url in CATEGORY_IMAGES.items():
        if key in cat:
            return url
    return CATEGORY_IMAGES["default"]


LAYOUTS = ["modern-minimal", "professional-card", "bold-showcase", "magazine", "dark-luxury"]


def make_static_site(lead):
    """Generate a simple static site without AI calls."""
    name = lead.get("business_name", "Client") or "Client"
    category = (lead.get("category") or "").lower()
    city = lead.get("city", "")
    phone = lead.get("phone_primary", "")
    rating = lead.get("rating")
    reviews = lead.get("review_count", 0)

    slug = slugify(name)
    layout = random.choice(LAYOUTS)
    palette = get_palette(category)
    primary, accent, secondary = palette[0], palette[1], palette[2]
    hero_img = get_hero_image(category)

    # Build sections
    sections_html = ""

    # Services section
    sections_html += f"""
    <section id="services" style="padding:5rem 2rem;background:#f8f9fa;">
        <div class="container" style="max-width:1100px;margin:0 auto;">
            <h2 style="font-size:2rem;color:{primary};margin-bottom:2rem;text-align:center;">Our Services</h2>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:2rem;">
                <div style="background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                    <h3 style="color:{primary};">Professional Care</h3>
                    <p style="color:#555;">High-quality service tailored to your needs with modern techniques and equipment.</p>
                </div>
                <div style="background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                    <h3 style="color:{primary};">Patient-First Approach</h3>
                    <p style="color:#555;">Your comfort and satisfaction are our top priorities at every visit.</p>
                </div>
                <div style="background:white;padding:2rem;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                    <h3 style="color:{primary};">Convenient Scheduling</h3>
                    <p style="color:#555;">Flexible appointment times to fit your busy schedule.</p>
                </div>
            </div>
        </div>
    </section>"""

    # About section
    sections_html += f"""
    <section id="about" style="padding:5rem 2rem;">
        <div class="container" style="max-width:1100px;margin:0 auto;">
            <h2 style="font-size:2rem;color:{primary};margin-bottom:1rem;">About {name}</h2>
            <p style="font-size:1.1rem;line-height:1.7;color:#555;">{name} is a trusted {category} practice serving the {city} area. We focus on delivering outstanding results through personalized care and attention to detail. Our team combines years of experience with the latest techniques to ensure every client receives the highest standard of service.</p>
        </div>
    </section>"""

    # Stats section (if rating exists)
    if rating:
        sections_html += f"""
    <section id="stats" style="padding:4rem 2rem;background:linear-gradient(135deg,{primary},{accent});color:white;">
        <div class="container" style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:2rem;text-align:center;">
            <div><div style="font-size:2.5rem;font-weight:700;">{rating}</div><div>Star Rating</div></div>
            <div><div style="font-size:2.5rem;font-weight:700;">{reviews}+</div><div>Reviews</div></div>
            <div><div style="font-size:2.5rem;font-weight:700;">{city}</div><div>Location</div></div>
        </div>
    </section>"""

    # Reviews section
    if rating:
        sections_html += f"""
    <section id="reviews" style="padding:5rem 2rem;background:#f8f9fa;">
        <div class="container" style="max-width:1100px;margin:0 auto;">
            <h2 style="font-size:2rem;color:{primary};margin-bottom:2rem;text-align:center;">What Our Clients Say</h2>
            <div style="text-align:center;">
                <div style="font-size:3rem;color:{accent};margin-bottom:1rem;">{'⭐' * int(rating)}</div>
                <p style="font-size:1.2rem;"><strong>{rating}</strong> / 5 — {reviews} reviews</p>
            </div>
        </div>
    </section>"""

    # Contact section
    sections_html += f"""
    <section id="contact" style="padding:5rem 2rem;">
        <div class="container" style="max-width:1100px;margin:0 auto;text-align:center;">
            <h2 style="font-size:2rem;color:{primary};margin-bottom:1rem;">Get In Touch</h2>
            <p style="font-size:1.1rem;margin-bottom:1.5rem;">Ready to get started? Contact us today for a consultation.</p>
            <a href="tel:{phone}" style="display:inline-block;background:{primary};color:white;padding:1rem 2.5rem;border-radius:50px;text-decoration:none;font-size:1.1rem;">📞 Call Now</a>
        </div>
    </section>"""

    hero_style = f"background:linear-gradient(135deg,rgba(0,0,0,0.5),rgba(0,0,0,0.3)),url({hero_img});background-size:cover;background-position:center;"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | {category.title()}</title>
    <meta name="description" content="{name} — Trusted {category} serving {city}. Professional, personalized care.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Inter',sans-serif; line-height:1.6; color:#333; }}
        .container {{ max-width:1100px; margin:0 auto; padding:0 1rem; }}
        @media (max-width:768px) {{ .container {{ padding:0 1.5rem; }} }}
    </style>
    <script type="application/ld+json">{{
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "{name}",
        "address": {{{{ "@type": "PostalAddress", "addressLocality": "{city}" }}}},
        "aggregateRating": {{{{ "@type": "AggregateRating", "ratingValue": "{rating}", "reviewCount": "{reviews}" }}}}
    }}</script>
</head>
<body>
    <header style="{hero_style}min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:2rem;position:relative;">
        <div style="position:relative;z-index:1;max-width:800px;">
            <h1 style="font-size:3rem;font-weight:800;color:white;margin-bottom:1rem;text-shadow:0 2px 10px rgba(0,0,0,0.3);">{name}</h1>
            <p style="font-size:1.25rem;color:rgba(255,255,255,0.9);margin-bottom:2rem;">Your Trusted {category.title()} Partner in {city}</p>
            <a href="tel:{phone}" style="display:inline-block;background:{accent};color:white;padding:1rem 2.5rem;border-radius:50px;text-decoration:none;font-size:1.1rem;font-weight:600;box-shadow:0 4px 15px rgba(0,0,0,0.2);">Book an Appointment</a>
        </div>
    </header>
    {sections_html}
    <footer style="padding:2rem;text-align:center;background:#222;color:rgba(255,255,255,0.7);font-size:0.9rem;">
        <p>&copy; 2025 {name}. All rights reserved.</p>
    </footer>
</body>
</html>"""
    return html


def make_static_deck(lead):
    """Generate a simple pitch deck without AI calls."""
    name = lead.get("business_name", "Client") or "Client"
    category = (lead.get("category") or "").title()
    city = lead.get("city", "")
    phone = lead.get("phone_primary", "")
    rating = lead.get("rating")
    reviews = lead.get("review_count", 0)

    deck_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pitch Deck — {name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Inter',sans-serif; line-height:1.6; color:#fff; background:#1a1a2e; }}
        .slide {{ min-height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:3rem 2rem; text-align:center; }}
        h1 {{ font-size:3rem; font-weight:800; margin-bottom:1rem; }}
        h2 {{ font-size:2rem; font-weight:700; margin-bottom:1rem; }}
        p {{ font-size:1.1rem; max-width:700px; margin:0 auto 1.5rem; color:rgba(255,255,255,0.8); }}
        .gold {{ color:#d4a853; }}
        .badge {{ display:inline-block; padding:0.5rem 1.5rem; border-radius:50px; background:#d4a853; color:#1a1a2e; font-weight:700; font-size:1.1rem; }}
        @media (max-width:768px) {{ h1 {{ font-size:2rem; }} h2 {{ font-size:1.5rem; }} }}
    </style>
</head>
<body>
    <div class="slide" style="background:linear-gradient(135deg,#1a1a2e,#16213e);">
        <span class="badge" style="margin-bottom:2rem;">Pitch Deck</span>
        <h1>{name}</h1>
        <p>Professional {category} Services in {city}</p>
    </div>
    <div class="slide" style="background:linear-gradient(135deg,#16213e,#0f3460);">
        <h2>About Us</h2>
        <p>{name} is a premier {category.lower()} practice dedicated to providing exceptional care and outstanding results to every client in {city}.</p>
    </div>
    <div class="slide" style="background:linear-gradient(135deg,#0f3460,#1a1a2e);">
        <h2>Our Services</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2rem;max-width:900px;width:100%;margin-top:2rem;">
            <div style="background:rgba(255,255,255,0.1);padding:2rem;border-radius:12px;"><h3 style="color:#d4a853;margin-bottom:1rem;">Quality</h3><p>Premium care using the latest techniques and technology</p></div>
            <div style="background:rgba(255,255,255,0.1);padding:2rem;border-radius:12px;"><h3 style="color:#d4a853;margin-bottom:1rem;">Care</h3><p>Compassionate, patient-focused approach to every treatment</p></div>
            <div style="background:rgba(255,255,255,0.1);padding:2rem;border-radius:12px;"><h3 style="color:#d4a853;margin-bottom:1rem;">Convenience</h3><p>Flexible hours and easy appointment scheduling</p></div>
        </div>
    </div>"""

    if rating:
        deck_html += f"""
    <div class="slide" style="background:linear-gradient(135deg,#1a1a2e,#16213e);">
        <h2>Social Proof</h2>
        <div style="font-size:3rem;margin-bottom:1rem;">{'⭐' * int(rating)}</div>
        <p class="gold" style="font-size:2rem;font-weight:700;">{rating} / 5</p>
        <p>Based on {reviews} verified client reviews</p>
    </div>"""

    deck_html += f"""
    <div class="slide" style="background:linear-gradient(135deg,#16213e,#0f3460);">
        <h2>Ready to Get Started?</h2>
        <p>Contact us today for a free consultation and discover how we can help transform your smile and confidence.</p>
        <a href="tel:{phone}" style="display:inline-block;background:#d4a853;color:#1a1a2e;padding:1rem 2.5rem;border-radius:50px;text-decoration:none;font-size:1.2rem;font-weight:700;margin-top:1rem;">Call Now</a>
    </div>
</body>
</html>"""
    return deck_html


def upload_file(remote_path, content):
    """Upload a file to tkvibes.in/proposals/ via w.php."""
    b64 = base64.b64encode(content.encode('utf-8')).decode()
    payload = json.dumps({'f': remote_path, 'd': b64}).encode('utf-8')
    req = urllib.request.Request('https://tkvibes.in/crm/w.php', data=payload, method='POST')
    req.add_header('Content-Type', 'text/plain')
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode() == 'OK'


def main():
    export_path = os.path.join(REPO_ROOT, "tkvibes-lead-engine", "data", "leads_export.json")
    with open(export_path) as f:
        leads = json.load(f)

    ok = 0
    for lead in leads:
        name = lead.get("business_name", "") or ""
        if not name:
            continue
        slug = slugify(name)
        if not slug:
            continue

        site_remote = f"sample-website/{slug}.html"
        deck_remote = f"pitch-deck/{slug}.html"

        # Check if already exists on server
        site_exists = False
        try:
            req = urllib.request.Request(f"https://tkvibes.in/proposals/{site_remote}")
            with urllib.request.urlopen(req, timeout=5) as resp:
                site_exists = resp.getcode() == 200
        except Exception:
            pass

        if site_exists:
            print(f"  ⏭️  {name[:30]}: already exists")
            continue

        site_html = make_static_site(lead)
        deck_html = make_static_deck(lead)

        # Save locally
        sw_dir = os.path.join(REPO_ROOT, "Sample Webpages and pitch deck", "sample website")
        pd_dir = os.path.join(REPO_ROOT, "Sample Webpages and pitch deck", "pitch deck")
        os.makedirs(sw_dir, exist_ok=True)
        os.makedirs(pd_dir, exist_ok=True)
        with open(os.path.join(sw_dir, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(site_html)
        with open(os.path.join(pd_dir, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(deck_html)

        # Upload using u2.php (which writes to /proposals/)
        site_ok = upload_file(f"../proposals/{site_remote}", site_html)
        deck_ok = upload_file(f"../proposals/{deck_remote}", deck_html)
        if site_ok and deck_ok:
            ok += 1
            print(f"  ✅ {name[:30]}: site={len(site_html)}b deck={len(deck_html)}b")
        else:
            print(f"  ❌ {name[:30]}: upload failed")

    print(f"\nDone: {ok} leads generated and uploaded")


if __name__ == '__main__':
    main()