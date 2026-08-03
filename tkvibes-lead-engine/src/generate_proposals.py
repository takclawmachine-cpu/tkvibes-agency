"""Generate sample websites and pitch decks for leads.

Reads leads from leads_export.json, renders template-v2.html with
lead-specific data, runs competitor research for no-website leads,
runs website analysis for weak-website leads, and generates:
  - data/proposals/<slug>/index.html  (sample website)
  - data/proposals/<slug>/pitch-deck.html  (pitch deck)

Usage:
    python -m src.generate_proposals
    python -m src.generate_proposals --limit 5
    python -m src.generate_proposals --lead-key ph:+919...
"""

import argparse
import json
import os
import re
import sys

from .config import load_config
from .models import Lead
from .visuals import (
    get_visual_config, sanitize_phone, format_phone_display,
    build_hours_html, build_services_html, get_why_items, DEFAULT_CONFIG
)
from .competitor_research import (
    search_competitors, format_competitor_html, format_competitor_pain_slide
)
from .gtmetrix_check import (
    analyze_website, format_website_analysis_html, format_website_analysis_site_section
)

PROPOSALS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "proposals")

# ── Template paths ───────────────────────────────────────────────────────────

TEMPLATE_SAMPLE = os.path.join(PROPOSALS_DIR, "template-v2.html")
TEMPLATE_PITCH = os.path.join(PROPOSALS_DIR, "pitch-deck-template.html")


def slugify(name: str) -> str:
    """Match the slugify in scaffold_clients.py."""
    if not (name or "").strip():
        return "client"
    s = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-{2,}", "-", s)[:60] or "client"


def _load_templates() -> tuple[str, str]:
    """Load both templates. Returns (sample_template, pitch_template)."""
    sample_path = TEMPLATE_SAMPLE
    pitch_path = TEMPLATE_PITCH

    if not os.path.isfile(sample_path):
        print(f"ERROR: Sample template not found at {sample_path}")
        sys.exit(1)

    with open(sample_path, "r", encoding="utf-8") as f:
        sample_html = f.read()

    pitch_html = ""
    if os.path.isfile(pitch_path):
        with open(pitch_path, "r", encoding="utf-8") as f:
            pitch_html = f.read()

    return sample_html, pitch_html


def _name_short(name: str) -> str:
    """Shorten business name for logo display."""
    parts = name.split()
    if len(parts) <= 2:
        return name
    # Take first word + last word
    return f"{parts[0]} {parts[-1]}"


def _address_short(address: str) -> str:
    """Shorten address for footer."""
    if not address:
        return ""
    parts = address.split(",")
    if len(parts) >= 2:
        return ", ".join(p.strip() for p in parts[:2])
    return address[:40]


def _generate_competitor_lead_section(lead: Lead, competitors: list[dict]) -> str:
    """Generate a 'Competitive Gap' section for the sample site for no-website leads."""
    return format_competitor_pain_slide(competitors, lead)


def _generate_analysis_lead_section(lead: Lead, analysis: dict) -> str:
    """Generate a 'Website Issues' section for the sample site for weak-website leads."""
    return format_website_analysis_site_section(analysis, lead)


def render_sample_site(lead: Lead, sample_template: str,
                       competitors: list[dict] | None = None,
                       analysis: dict | None = None) -> str:
    """Render the sample site template with lead data.

    Fills all {{PLACEHOLDER}} variables in template-v2.html.
    Optionally injects competitor analysis or website audit sections.
    """
    cfg = get_visual_config(lead.category)
    primary = cfg["primary"]
    secondary = cfg["secondary"]
    icon = cfg.get("icon", "fa-star")
    icon_hero = cfg.get("icon_hero", "fa-building")
    tagline = cfg.get("tagline", "Excellence You Can Trust")
    meta_suffix = cfg.get("meta_suffix", "Services")

    phone = lead.phone_primary or ""
    phone_wa = sanitize_phone(lead.whatsapp or phone)
    phone_display = format_phone_display(phone)
    rating = lead.rating or 0
    reviews = lead.review_count or 0
    address = lead.address or ""
    city = lead.city or ""
    lat = lead.latitude or 28.6139
    lng = lead.longitude or 77.2090
    name = lead.business_name or "Business"
    category = lead.category or "Business"
    category_lower = category.lower()
    name_short = _name_short(name)
    address_short = _address_short(address)
    hours_html = build_hours_html(lead.opening_hours or "")
    services_html = build_services_html(cfg)
    why_items = get_why_items(lead.category)

    # Description
    description = f"Your trusted {category_lower} serving the {city} community with {rating}★ rated service and {reviews}+ happy customers."

    # Google Maps URL
    maps_url = f"https://www.google.com/maps?q={lat},{lng}&z=16"

    # Build competitive gap section if no website
    competitive_section = ""
    if competitors and not lead.has_website:
        competitive_section = _generate_competitor_lead_section(lead, competitors)

    # Build website analysis section if weak website
    website_analysis_section = ""
    if analysis and analysis.get("issues") and lead.website_url:
        website_analysis_section = _generate_analysis_lead_section(lead, analysis)

    # Category-specific icon for nav
    nav_icon = icon_hero

    replacements = {
        "{{BUSINESS_NAME}}": name,
        "{{CATEGORY}}": category,
        "{{CATEGORY_LOWER}}": category_lower,
        "{{CITY}}": city,
        "{{ADDRESS}}": address,
        "{{ADDRESS_SHORT}}": address_short,
        "{{PHONE}}": phone_display,
        "{{PHONE_WA}}": phone_wa,
        "{{PHONE_DISPLAY}}": phone_display,
        "{{RATING}}": str(rating),
        "{{REVIEWS}}": str(reviews),
        "{{PRIMARY}}": primary,
        "{{SECONDARY}}": secondary,
        "{{LAT}}": str(lat),
        "{{LNG}}": str(lng),
        "{{GOOGLE_MAPS_URL}}": maps_url,
        "{{NAME_SHORT}}": name_short,
        "{{DESCRIPTION}}": description,
        "{{SERVICES}}": services_html,
        "{{WHY_ITEMS}}": why_items,
        "{{HOURS_HTML}}": hours_html,
        "{{META_SUFFIX}}": meta_suffix,
        "{{ICON}}": icon,
        "{{ICON_HERO}}": icon_hero,
        "{{NAV_ICON}}": nav_icon,
        "{{TAGLINE}}": tagline,
        "{{COMPETITIVE_SECTION}}": competitive_section,
        "{{WEBSITE_ANALYSIS_SECTION}}": website_analysis_section,
    }

    html = sample_template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))

    # Insert competitive website section before the divider after services
    if competitive_section and "{{COMPETITIVE_SECTION}}" not in sample_template:
        # Insert after the why-us section
        html = html.replace(
            '<div class="divider"></div>',
            competitive_section + '\n<div class="divider"></div>',
            1  # only replace the first occurrence (after why-us)
        )

    # Insert website analysis section similarly
    if website_analysis_section and "{{WEBSITE_ANALYSIS_SECTION}}" not in sample_template:
        html = html.replace(
            '<div class="divider"></div>',
            website_analysis_section + '\n<div class="divider"></div>',
            1 if not competitive_section else 2
        )

    # Remove leftover placeholders
    html = re.sub(r"\{\{[A-Z_]+\}\}", "", html)

    return html


def generate_pitch_deck(lead: Lead, competitors: list[dict] | None = None,
                        analysis: dict | None = None) -> str:
    """Generate a pitch deck HTML from scratch (no template dependency).

    Builds a comprehensive slide deck covering:
    1. Cover slide
    2. The Gap (competitor analysis for no-website, or website audit for weak)
    3. The Solution
    4. Concept Website Preview
    5. Deliverables
    6. Expected Impact
    7. Offer & Next Step
    """
    cfg = get_visual_config(lead.category)
    primary = cfg["primary"]
    secondary = cfg["secondary"]
    icon = cfg.get("icon", "fa-star")
    icon_hero = cfg.get("icon_hero", "fa-building")
    tagline = cfg.get("tagline", "Excellence You Can Trust")

    name = lead.business_name or "Business"
    city = lead.city or ""
    rating = lead.rating or 0
    reviews = lead.review_count or 0
    phone = lead.phone_primary or ""
    phone_wa = sanitize_phone(lead.whatsapp or phone)
    category = lead.category or "Business"
    category_lower = category.lower()
    slug = slugify(name)

    has_website = bool(lead.website_url) and lead.has_website
    website_quality = lead.website_quality or "none"

    # Build slides
    slides = []

    # Slide 1: Cover
    slides.append(f"""<div class="slide active" style="background:radial-gradient(ellipse at 30% 50%,{primary}15 0%,transparent 60%),#0f172a">
<div class="text-center" style="max-width:700px">
<div class="anim-fade-up d1" style="width:80px;height:80px;border-radius:24px;background:linear-gradient(135deg,{primary},{secondary});display:flex;align-items:center;justify-content:center;margin:0 auto 2rem"><i class="fa-solid {icon_hero} text-white" style="font-size:2rem"></i></div>
<h1 class="anim-fade-up d2" style="font-family:'Poppins',sans-serif;font-size:2.8rem;font-weight:800;line-height:1.2;margin-bottom:1rem">{name}</h1>
<p class="anim-fade-up d3" style="font-size:1.2rem;color:#94a3b8;margin-bottom:2rem">{tagline} — A Digital Transformation Proposal</p>
<div class="anim-fade-up d4" style="display:flex;align-items:center;justify-content:center;gap:8px;color:#fbbf24;font-size:1.1rem">{"".join(f'<i class="fa-solid fa-star"></i>' for _ in range(5))}<span style="color:white;font-weight:700;margin-left:8px">{rating}</span><span style="color:#94a3b8">({reviews} reviews)</span></div>
<p class="anim-fade-up d5" style="margin-top:2rem;color:#64748b;font-size:0.85rem">Presented by TKVibes Digital Agency</p>
</div></div>""")

    # Slide 2: The Gap (competitor gap or website audit)
    if competitors and not has_website:
        slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 70% 30%,{primary}10 0%,transparent 60%),#0f172a">
{format_competitor_html(competitors, lead)}
</div>""")
    elif analysis and analysis.get("issues") and has_website:
        slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 70% 30%,{primary}10 0%,transparent 60%),#0f172a">
{format_website_analysis_html(analysis, lead)}
</div>""")
    else:
        # Generic gap slide
        slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 70% 30%,{primary}10 0%,transparent 60%),#0f172a">
<div style="max-width:800px;width:100%"><h2 class="anim-fade-up d1" style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem;text-align:center">The Opportunity</h2>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem">
<div class="glass anim-fade-up d2" style="text-align:center"><div class="stat-value">{rating}</div><p style="color:#94a3b8;margin-top:0.5rem;font-size:0.9rem">Google Rating</p></div>
<div class="glass anim-fade-up d3" style="text-align:center"><div class="stat-value">{reviews}</div><p style="color:#94a3b8;margin-top:0.5rem;font-size:0.9rem">Customer Reviews</p></div>
<div class="glass anim-fade-up d4" style="text-align:center"><div class="stat-value">0</div><p style="color:#94a3b8;margin-top:0.5rem;font-size:0.9rem">Modern Pages</p></div>
</div>
<p class="anim-fade-up d5" style="text-align:center;color:#94a3b8;margin-top:2rem">Your reputation is outstanding — but your online presence doesn't reflect it.</p>
</div></div>""")

    # Slide 3: What You're Missing (pain points)
    pain_points = (lead.pain_points or "").split(" | ")
    pain_items = "".join(
        f'<div class="glass anim-fade-up d{i+2}" style="display:flex;align-items:center;gap:1rem;padding:1.5rem"><i class="fa-solid fa-triangle-exclamation" style="color:#ef4444;font-size:1.2rem;flex-shrink:0"></i><div><span style="font-size:0.9rem">{pp}</span></div></div>'
        for i, pp in enumerate(pain_points[:4])
    )
    fallback_pain_point = '<div class="glass anim-fade-up d2" style="display:flex;align-items:center;gap:1rem;padding:1.5rem"><i class="fa-solid fa-triangle-exclamation" style="color:#ef4444;font-size:1.2rem"></i><div><strong>Online Presence:</strong> Your business needs a strong digital footprint to compete in today\'s market</div></div>'
    slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 50% 50%,#ef444410 0%,transparent 60%),#0f172a">
<div style="max-width:700px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What You're Missing</h2>
<div style="display:flex;flex-direction:column;gap:1rem;text-align:left">
{pain_items if pain_items else fallback_pain_point}
</div></div></div>""")

    # Slide 4: The Solution
    slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 50% 50%,#22c55e10 0%,transparent 60%),#0f172a">
<div style="max-width:800px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">The Solution</h2>
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1.5rem;text-align:left">
<div class="glass anim-fade-up d2"><i class="fa-solid fa-mobile-screen-button" style="color:#22c55e;font-size:1.2rem;margin-bottom:0.5rem"></i><h3 style="font-weight:700;margin-bottom:0.5rem">Premium Website</h3><p style="color:#94a3b8;font-size:0.85rem">Modern, mobile-first design with stunning visuals</p></div>
<div class="glass anim-fade-up d3"><i class="fa-solid fa-magnifying-glass" style="color:#22c55e;font-size:1.2rem;margin-bottom:0.5rem"></i><h3 style="font-weight:700;margin-bottom:0.5rem">SEO Optimized</h3><p style="color:#94a3b8;font-size:0.85rem">Rank higher for {category_lower} searches in {city}</p></div>
<div class="glass anim-fade-up d4"><i class="fa-brands fa-whatsapp" style="color:#22c55e;font-size:1.2rem;margin-bottom:0.5rem"></i><h3 style="font-weight:700;margin-bottom:0.5rem">WhatsApp Integration</h3><p style="color:#94a3b8;font-size:0.85rem">One-tap booking and customer communication</p></div>
<div class="glass anim-fade-up d5"><i class="fa-solid fa-calendar-check" style="color:#22c55e;font-size:1.2rem;margin-bottom:0.5rem"></i><h3 style="font-weight:700;margin-bottom:0.5rem">Online Booking</h3><p style="color:#94a3b8;font-size:0.85rem">Customers book appointments 24/7</p></div>
</div></div></div>""")

    # Slide 5: Concept Website Preview
    slides.append(f"""<div class="slide" style="background:#0f172a">
<div style="max-width:900px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1.5rem">Your Concept Website</h2>
<p class="anim-fade-up d2" style="color:#94a3b8;margin-bottom:2rem">Built specifically for {name}</p>
<div class="anim-fade-up d3 glass" style="padding:8px;border-radius:16px;overflow:hidden">
<div style="background:#0a0f1e;border-radius:12px;height:400px;display:flex;align-items:center;justify-content:center">
<div style="text-align:center"><i class="fa-solid fa-globe" style="font-size:4rem;color:{primary};opacity:0.5;margin-bottom:1rem;display:block"></i>
<a href="../{slug}/index.html" target="_blank" style="display:inline-block;padding:12px 32px;border-radius:12px;background:linear-gradient(135deg,{primary},{secondary});color:white;text-decoration:none;font-weight:600"><i class="fa-solid fa-external-link-alt" style="margin-right:8px"></i>View Live Preview</a></div>
</div></div></div></div>""")

    # Slide 6: Deliverables
    deliverables = [
        ("Premium responsive design", "fa-mobile-screen-button"),
        ("SEO meta tags & schema", "fa-magnifying-glass"),
        ("Google Maps integration", "fa-map-location-dot"),
        ("WhatsApp click-to-chat", "fa-brands fa-whatsapp"),
        ("Contact form & booking", "fa-calendar-check"),
        ("Google Reviews showcase", "fa-star"),
        ("Fast loading (optimized)", "fa-bolt"),
        ("Analytics integration", "fa-chart-line"),
    ]
    deliv_items = "".join(
        f'<div class="anim-fade-up d{i%5+2}" style="display:flex;align-items:center;gap:0.75rem;padding:1rem"><i class="fa-solid fa-check-circle" style="color:#22c55e"></i><span style="font-size:0.9rem">{title}</span></div>'
        for i, (title, ic) in enumerate(deliverables)
    )
    slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 50% 50%,{primary}10 0%,transparent 60%),#0f172a">
<div style="max-width:800px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:2rem">What TKVibes Delivers</h2>
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;text-align:left">
{deliv_items}
</div></div></div>""")

    # Slide 7: Expected Impact
    slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 50% 50%,#22c55e10 0%,transparent 60%),#0f172a">
<div style="max-width:700px;text-align:center"><h2 class="anim-fade-up d1" style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:1rem">Expected Impact</h2>
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1.5rem;margin-bottom:2rem">
<div class="glass anim-fade-up d3" style="text-align:center"><div class="stat-value">3x</div><p style="color:#94a3b8;font-size:0.85rem;margin-top:0.5rem">More Customer Inquiries</p></div>
<div class="glass anim-fade-up d4" style="text-align:center"><div class="stat-value">60%</div><p style="color:#94a3b8;font-size:0.85rem;margin-top:0.5rem">Customers Search Online First</p></div>
</div>
<div class="roi-compare anim-fade-up d5">
<div class="roi-bar gradient-red" style="height:40px"><span>₹0</span><span class="roi-label">Current</span></div>
<div class="roi-bar gradient-green" style="height:140px"><span>₹20K+</span><span class="roi-label">With Website</span></div>
</div>
<p style="color:#64748b;font-size:0.8rem;margin-top:1rem">Estimated monthly revenue from new online customers</p>
</div></div>""")

    # Slide 8: Offer
    has_wa = bool(phone_wa)
    slides.append(f"""<div class="slide" style="background:radial-gradient(ellipse at 50% 50%,{primary}15 0%,transparent 60%),#0f172a">
<div style="max-width:600px;text-align:center">
<div class="anim-fade-up d1" style="width:80px;height:80px;border-radius:24px;background:linear-gradient(135deg,{primary},{secondary});display:flex;align-items:center;justify-content:center;margin:0 auto 2rem"><i class="fa-solid fa-rocket text-white" style="font-size:2rem"></i></div>
<h2 class="anim-fade-up d2" style="font-family:'Poppins',sans-serif;font-size:2.5rem;font-weight:800;margin-bottom:1rem">Let's Build Your<br>Digital Future</h2>
<p class="anim-fade-up d3" style="color:#94a3b8;margin-bottom:2.5rem">Your website is ready. Just one click to go live.</p>
<div class="anim-fade-up d4 glass" style="text-align:left;padding:2rem">
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem"><i class="fa-solid fa-envelope" style="color:{primary}"></i><span>services@tkvibes.in</span></div>
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem"><i class="fa-solid fa-phone" style="color:{primary}"></i><span>+91 98182 46938</span></div>
{"<div style='display:flex;align-items:center;gap:1rem'><i class='fa-brands fa-whatsapp' style='color:#25D366'></i><span>WhatsApp Available</span></div>" if has_wa else ""}
</div>
<p class="anim-fade-up d5" style="margin-top:2rem;font-size:0.8rem;color:#64748b">Concept by TKVibes — not affiliated with {name}</p>
</div></div>""")

    slides_str = "\n".join(slides)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pitch Deck — {name}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#0f172a;color:#e2e8f0;overflow:hidden;height:100vh}}
.slide{{width:100vw;height:100vh;display:none;align-items:center;justify-content:center;position:relative;overflow:hidden;padding:40px}}
.slide.active{{display:flex}}
.glass{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:20px;backdrop-filter:blur(16px);padding:2.5rem}}
.anim-fade-up{{opacity:0;transform:translateY(24px)}}
.anim-fade-up.visible{{animation:fadeUp 0.6s ease forwards}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(24px)}}to{{opacity:1;transform:translateY(0)}}}}
.d1{{animation-delay:0s}}.d2{{animation-delay:0.1s}}.d3{{animation-delay:0.2s}}.d4{{animation-delay:0.3s}}.d5{{animation-delay:0.4s}}.d6{{animation-delay:0.5s}}.d7{{animation-delay:0.6s}}
.stat-value{{font-size:3.5rem;font-weight:800;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'Poppins',sans-serif}}
.nav-btn{{position:fixed;bottom:30px;z-index:100;width:48px;height:48px;border-radius:50%;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:white;font-size:1.2rem;cursor:pointer;backdrop-filter:blur(8px);transition:all 0.3s}}
.nav-btn:hover{{background:rgba(255,255,255,0.1)}}
#prev{{left:30px}}#next{{right:30px}}
.dots{{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);display:flex;gap:8px;z-index:100}}
.dot{{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,0.2);cursor:pointer;transition:all 0.3s}}
.dot.active{{background:{primary};width:30px;border-radius:5px}}
.progress{{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,{primary},{secondary});transition:width 0.3s;z-index:100}}
.roi-compare{{display:flex;gap:24px;align-items:flex-end;justify-content:center;margin-top:1.5rem}}
.roi-bar{{width:80px;border-radius:8px 8px 0 0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:12px;font-size:0.85rem;font-weight:700;color:white}}
.roi-label{{font-size:0.7rem;color:#94a3b8;margin-top:6px;font-weight:400}}
.gradient-red{{background:linear-gradient(90deg,#ef4444,#f87171)}}
.gradient-green{{background:linear-gradient(90deg,#22c55e,#4ade80)}}
.text-center{{text-align:center}}
@media (max-width:767px){{.slide{{padding:20px}}h1{{font-size:2rem !important}}h2{{font-size:1.5rem !important}}.stat-value{{font-size:2.5rem}}.glass{{padding:1.5rem}}.nav-btn{{width:40px;height:40px}}}}
</style>
</head>
<body>
<div class="progress" id="progress"></div>
<button class="nav-btn" id="prev" onclick="changeSlide(-1)"><i class="fa-solid fa-chevron-left"></i></button>
<button class="nav-btn" id="next" onclick="changeSlide(1)"><i class="fa-solid fa-chevron-right"></i></button>
<div class="dots" id="dots"></div>

{slides_str}

<script>
let currentSlide=0;const slides=document.querySelectorAll('.slide');const dots=document.getElementById('dots');const progress=document.getElementById('progress');
slides.forEach((_,i){{const d=document.createElement('div');d.className='dot'+(i===0?' active':'');d.onclick=()=>{{currentSlide=i;updateSlide()}};dots.appendChild(d)}});
function updateSlide(){{slides.forEach((s,i)=>{{s.classList.toggle('active',i===currentSlide);if(i===currentSlide){{const items=s.querySelectorAll('.anim-fade-up:not(.visible)');items.forEach((el,idx)=>{{setTimeout(()=>el.classList.add('visible'),idx*80)}})}}}});dots.querySelectorAll('.dot').forEach((d,i)=>d.classList.toggle('active',i===currentSlide));progress.style.width=((currentSlide+1)/slides.length*100)+'%'}}
function changeSlide(dir){{const next=currentSlide+dir;if(next>=0&&next<slides.length){{slides[currentSlide].querySelectorAll('.anim-fade-up').forEach(el=>el.classList.remove('visible'));currentSlide=next;updateSlide()}}}}
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight'||e.key==='ArrowDown')changeSlide(1);if(e.key==='ArrowLeft'||e.key==='ArrowUp')changeSlide(-1)}});
let touchStartX=0;document.addEventListener('touchstart',e=>{{touchStartX=e.changedTouches[0].screenX}},{{passive:true}});document.addEventListener('touchend',e=>{{const dx=touchStartX-e.changedTouches[0].screenX;if(Math.abs(dx)>50)changeSlide(dx>0?1:-1)}},{{passive:true}});
let wheelTimeout;document.addEventListener('wheel',e=>{{clearTimeout(wheelTimeout);wheelTimeout=setTimeout(()=>changeSlide(e.deltaY>0?1:-1),120)}},{{passive:true}});
updateSlide();
</script>
</body>
</html>"""


def generate_for_lead(lead: Lead, config: dict, sample_template: str,
                      force: bool = False) -> dict:
    """Generate sample site + pitch deck for a single lead.

    Returns dict with paths to generated files.
    """
    slug = slugify(lead.business_name)
    out_dir = os.path.join(PROPOSALS_DIR, slug)
    index_path = os.path.join(out_dir, "index.html")
    deck_path = os.path.join(out_dir, "pitch-deck.html")

    # Skip if already generated and not forced
    if not force and os.path.isfile(index_path) and os.path.isfile(deck_path):
        return {"status": "skipped", "slug": slug, "index": index_path, "deck": deck_path}

    # ── Research phase ────────────────────────────────────────────────────
    competitors = None
    analysis = None

    # For no-website leads: search competitors
    if not lead.has_website:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
        try:
            competitors = search_competitors(lead, api_key)
            if competitors:
                print(f"    [research] Found {len(competitors)} nearby competitors for {lead.business_name}")
        except Exception as e:
            print(f"    [research] Competitor search failed: {e}")

    # For weak website leads: analyze website
    if lead.has_website and lead.website_url and lead.website_quality in ("weak", "social_only", "directory_microsite"):
        try:
            analysis = analyze_website(lead)
            if analysis and analysis.get("issues"):
                print(f"    [audit] Found {len(analysis['issues'])} website issues for {lead.business_name}")
        except Exception as e:
            print(f"    [audit] Website analysis failed: {e}")

    # ── Generation phase ──────────────────────────────────────────────────
    os.makedirs(out_dir, exist_ok=True)

    # Generate sample site
    sample_html = render_sample_site(lead, sample_template, competitors, analysis)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(sample_html)

    # Generate pitch deck
    deck_html = generate_pitch_deck(lead, competitors, analysis)
    with open(deck_path, "w", encoding="utf-8") as f:
        f.write(deck_html)

    size_site = len(sample_html)
    size_deck = len(deck_html)

    print(f"    ✅ {slug}: sample site ({size_site:,} chars) + pitch deck ({size_deck:,} chars)")

    return {
        "status": "generated",
        "slug": slug,
        "lead_key": lead.lead_key,
        "business_name": lead.business_name,
        "index": index_path,
        "deck": deck_path,
        "competitors": bool(competitors),
        "analysis": bool(analysis),
    }


def main():
    ap = argparse.ArgumentParser(description="Generate sample sites + pitch decks")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--limit", type=int, default=None, help="Max leads to process")
    ap.add_argument("--lead-key", default=None, help="Process a single lead by lead_key")
    ap.add_argument("--force", action="store_true", help="Regenerate even if files exist")
    ap.add_argument("--tier", default=None, help="Filter by tier: HOT, WARM, COLD")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    cfg = load_config(args.config)

    # Load templates
    sample_template, _ = _load_templates()

    # Load leads
    export_path = cfg["handoff"]["export_json"]
    if not os.path.isfile(export_path):
        print(f"ERROR: No leads export at {export_path}")
        print("Run the lead engine first: python -m src.run --max-leads 20")
        sys.exit(1)

    with open(export_path, encoding="utf-8") as f:
        leads_data = json.load(f)

    leads = []
    for d in leads_data:
        l = Lead()
        for k, v in d.items():
            if k.startswith("_"):
                continue
            if hasattr(l, k):
                setattr(l, k, v)
        leads.append(l)

    # Filter
    if args.lead_key:
        leads = [l for l in leads if l.lead_key == args.lead_key]
    if args.tier:
        leads = [l for l in leads if l.lead_tier == args.tier.upper()]
    if args.limit:
        leads = leads[:args.limit]

    if not leads:
        print("No leads to process")
        return

    print(f"Generating proposals for {len(leads)} leads...")
    results = []
    for i, lead in enumerate(leads, 1):
        print(f"  [{i}/{len(leads)}] {lead.business_name} ({lead.lead_tier})")
        try:
            result = generate_for_lead(lead, cfg, sample_template, force=args.force)
            results.append(result)
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({"status": "error", "lead_key": lead.lead_key, "error": str(e)})

    generated = sum(1 for r in results if r.get("status") == "generated")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    errors = sum(1 for r in results if r.get("status") == "error")
    print(f"\nDone: {generated} generated, {skipped} skipped, {errors} errors")

    # Save results for downstream scripts
    results_path = os.path.join(PROPOSALS_DIR, "_generation_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()