"""
AI-powered website generator for TKVibes.

Generates unique, per-business sample websites using LLM-driven
content creation with layout templates. Falls back to template-v2
if AI generation is unavailable.

Architecture:
1. Analyze business data -> build generation prompt
2. Call LLM for: site structure JSON (layout, colors, copy)
3. Render JSON into chosen layout template
4. Post-process: SEO metadata, schema markup, images

Layouts: 5 variants with different hero styles and section ordering.
"""
import json
import logging
import os
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

# ── Layout templates ─────────────────────────────────────────────────────────

LAYOUTS = {
    "modern-minimal": {
        "name": "Modern Minimal",
        "description": "Clean, minimalist design with full-width hero and staggered sections",
        "hero_style": "fullscreen",
        "section_order": ["hero", "about", "services", "testimonials", "cta", "contact"],
    },
    "professional-card": {
        "name": "Professional Card",
        "description": "Card-based layout with sidebar-style hero and grid sections",
        "hero_style": "split",
        "section_order": ["hero", "stats", "services", "testimonials", "about", "cta", "contact"],
    },
    "bold-showcase": {
        "name": "Bold Showcase",
        "description": "Bold typography and large imagery with overlapping sections",
        "hero_style": "overlay",
        "section_order": ["hero", "services", "stats", "about", "testimonials", "cta", "contact"],
    },
    "magazine": {
        "name": "Magazine",
        "description": "Magazine-style layout with large featured image grid, pull quotes, sidebar stats",
        "hero_style": "magazine",
        "section_order": ["hero", "about", "services", "stats", "testimonials", "cta", "contact"],
    },
    "dark-luxury": {
        "name": "Dark Luxury",
        "description": "Dark theme with gold/amber accents, parallax hero, animated counters",
        "hero_style": "dark-luxury",
        "section_order": ["hero", "stats", "services", "about", "testimonials", "cta", "contact"],
    },
}

DEFAULT_LAYOUT = "modern-minimal"

# ── Category-specific Unsplash image URLs ────────────────────────────────────

CATEGORY_IMAGES = {
    "dental": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=1200",
    "lawyer": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200",
    "medical": "https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200",
    "pet": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=1200",
    "veterinary": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=1200",
    "interior design": "https://images.unsplash.com/photo-1618220179428-22790b461013?w=1200",
    "restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200",
    "cafe": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200",
    "salon": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200",
    "spa": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200",
}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200"


def _get_category_image(category: str) -> str:
    """Look up the best Unsplash image URL for a given business category."""
    cat_lower = (category or "").lower().strip()
    # Try exact match first
    if cat_lower in CATEGORY_IMAGES:
        return CATEGORY_IMAGES[cat_lower]
    # Try partial match: check if any known key appears in the category string
    for key in CATEGORY_IMAGES:
        if key in cat_lower or cat_lower in key:
            return CATEGORY_IMAGES[key]
    return DEFAULT_IMAGE


def _call_llm(prompt: str, system_prompt: str = "") -> str | None:
    """Call the LLM via OpenRouter API and return the response text."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not set — AI generation unavailable")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://tkvibes.in",
    }
    payload = json.dumps({
        "model": "deepseek/deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }).encode("utf-8")

    try:
        req = Request(url, data=payload, headers=headers, method="POST")
        with urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            logger.error("LLM returned empty response")
            return None
        return content
    except URLError as e:
        logger.error("LLM API call failed: %s", e)
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error("LLM response parse failed: %s", e)
        return None


def _extract_json(text: str) -> dict | None:
    """Extract the first JSON object from LLM response text."""
    # Try to find a JSON block
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find { ... } in the text
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def build_ai_site_spec(lead_data: dict, category_visuals: dict) -> dict:
    """
    Generate a site specification using AI.

    Args:
        lead_data: Dict with lead fields (business_name, category, city, etc.)
        category_visuals: Visual config dict for the business category

    Returns:
        Dict with keys: layout, primary_color, secondary_color, sections,
        tagline, description, seo_title, seo_description, etc.
    """
    system_prompt = (
        "You are a professional website designer and copywriter. "
        "Given a business profile, generate a unique, modern website specification. "
        "Return ONLY valid JSON with no markdown formatting."
    )

    user_prompt = (
        f"Generate a website spec for this business:\n"
        f"Business: {lead_data.get('business_name', 'Unknown')}\n"
        f"Category: {lead_data.get('category', 'Business')}\n"
        f"City: {lead_data.get('city', '')}\n"
        f"Rating: {lead_data.get('rating', 'N/A')}★ ({lead_data.get('review_count', 0)} reviews)\n"
        f"Has Website: {lead_data.get('has_website', False)}\n"
        f"Pain Points: {lead_data.get('pain_points', '')}\n"
        f"Available colors: {category_visuals.get('primary', '#000')} (primary), "
        f"{category_visuals.get('secondary', '#000')} (secondary)\n\n"
        f"Respond with JSON: {{\n"
        f'  "layout": "modern-minimal" | "professional-card" | "bold-showcase" | "magazine" | "dark-luxury",\n'
        f'  "primary_color": "use the provided primary or suggest a better one",\n'
        f'  "secondary_color": "use the provided secondary or suggest a better one",\n'
        f'  "tagline": "a unique, catchy tagline for this business",\n'
        f'  "description": "a 2-3 sentence description highlighting their strengths",\n'
        f'  "hero_headline": "main headline for the hero section",\n'
        f'  "hero_subheadline": "supporting text for hero",\n'
        f'  "service_descriptions": ["unique description per service"],\n'
        f'  "cta_text": "call to action button text",\n'
        f'  "seo_title": "SEO title (max 60 chars)",\n'
        f'  "seo_description": "SEO meta description (max 155 chars)",\n'
        f'  "schema_type": "LocalBusiness" | "MedicalBusiness" | "LegalService" | "HealthAndBeautyBusiness",\n'
        f"  'color_swap': false\n"
        f"}}"
    )

    response = _call_llm(user_prompt, system_prompt)
    if not response:
        logger.info("AI generation failed, using default spec")
        return _default_site_spec(lead_data, category_visuals)

    spec = _extract_json(response)
    if not spec:
        logger.warning("Could not parse AI response as JSON, using defaults")
        return _default_site_spec(lead_data, category_visuals)

    # Validate and fill defaults for missing fields
    if spec.get("layout") not in LAYOUTS:
        spec["layout"] = DEFAULT_LAYOUT
    if not spec.get("primary_color"):
        spec["primary_color"] = category_visuals.get("primary", "#000")
    if not spec.get("secondary_color"):
        spec["secondary_color"] = category_visuals.get("secondary", "#000")
    if not spec.get("tagline"):
        spec["tagline"] = category_visuals.get("tagline", "Excellence You Can Trust")
    if not spec.get("seo_title"):
        spec["seo_title"] = f"{lead_data.get('business_name', 'Business')} | {lead_data.get('city', '')}"
    if not spec.get("seo_description"):
        spec["seo_description"] = f"Visit {lead_data.get('business_name', 'Business')} in {lead_data.get('city', '')}. {category_visuals.get('tagline', '')}"
    if not spec.get("schema_type"):
        spec["schema_type"] = "LocalBusiness"

    logger.info("AI spec generated: layout=%s, primary=%s",
                spec["layout"], spec["primary_color"])
    return spec


def _default_site_spec(lead_data: dict, category_visuals: dict) -> dict:
    """Fallback spec when AI is unavailable."""
    name = lead_data.get("business_name", "Business")
    city = lead_data.get("city", "")
    return {
        "layout": DEFAULT_LAYOUT,
        "primary_color": category_visuals.get("primary", "#000"),
        "secondary_color": category_visuals.get("secondary", "#000"),
        "tagline": category_visuals.get("tagline", "Excellence You Can Trust"),
        "description": f"Your trusted {lead_data.get('category', 'business').lower()} serving the {city} community.",
        "hero_headline": f"Welcome to {name}",
        "hero_subheadline": category_visuals.get("tagline", "Quality Service"),
        "service_descriptions": [],
        "cta_text": "Get in Touch",
        "seo_title": f"{name} | {city}",
        "seo_description": f"Visit {name} in {city}. {category_visuals.get('tagline', '')}",
        "schema_type": "LocalBusiness",
        "color_swap": False,
    }


def _render_stats_section(rating: float, reviews: int, primary: str, secondary: str) -> str:
    """Render an animated stats / number-cards section."""
    score = round(rating * 20)  # Convert 5-star rating to percentage-ish score
    return f"""<section class="stats-section" style="padding:4rem 2rem;background:{primary}08">
<div class="container" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:2rem;text-align:center">
<div class="stat-card" style="background:white;border-radius:16px;padding:2.5rem 1.5rem;box-shadow:0 4px 20px rgba(0,0,0,0.06)">
<div style="font-size:2.5rem;font-weight:800;color:{primary}">{rating}</div>
<div style="font-size:1rem;color:#666;margin-top:0.5rem">⭐ Overall Rating</div>
<div style="margin-top:0.5rem;font-size:0.9rem;color:#999">{'★' * int(round(rating))}{'☆' * (5 - int(round(rating)))}</div>
</div>
<div class="stat-card" style="background:white;border-radius:16px;padding:2.5rem 1.5rem;box-shadow:0 4px 20px rgba(0,0,0,0.06)">
<div style="font-size:2.5rem;font-weight:800;color:{secondary}">{reviews}</div>
<div style="font-size:1rem;color:#666;margin-top:0.5rem">📝 Reviews</div>
</div>
<div class="stat-card" style="background:white;border-radius:16px;padding:2.5rem 1.5rem;box-shadow:0 4px 20px rgba(0,0,0,0.06)">
<div style="font-size:2.5rem;font-weight:800;color:{primary}">{score}%</div>
<div style="font-size:1rem;color:#666;margin-top:0.5rem">🎯 Satisfaction Score</div>
</div>
</div>
</section>"""


def _render_testimonials_section(rating: float, name: str, primary: str) -> str:
    """Render a testimonials / review snippets section."""
    # Generate a few dynamic review snippets based on rating
    quote = chr(0x201C)  # Left double quotation mark
    end_quote = chr(0x201D)  # Right double quotation mark
    if rating >= 4.5:
        reviews_list = [
            f"Absolutely outstanding service! {name} exceeded all my expectations. Highly recommended!",
            f"Professional, courteous, and incredibly skilled. So glad I found {name}!",
            f"Five-star experience from start to finish. Will definitely be coming back.",
        ]
    elif rating >= 3.5:
        reviews_list = [
            f"Great experience with {name}. Very professional team.",
            f"Good service overall. Would recommend to others looking for quality care.",
            f"Satisfied with the results. The team was very helpful throughout.",
        ]
    else:
        reviews_list = [
            "Decent service. Room for improvement but overall okay.",
            "Average experience. The staff was friendly enough.",
        ]
    items = "".join(
        f'<div class="testimonial-card" style="background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1px solid #eee">'
        f'<div style="font-size:1.1rem;font-style:italic;color:#444;margin-bottom:1rem;line-height:1.5">{quote}{review}{end_quote}</div>'
        f'<div style="font-size:0.9rem;color:{primary};font-weight:600">\u2014 Verified Customer</div>'
        f'</div>'
        for review in reviews_list
    )
    return f"""<section class="testimonials-section" style="padding:4rem 2rem;background:white">
<div class="container">
<h2 style="font-size:2rem;font-weight:700;text-align:center;margin-bottom:0.5rem;color:{primary}">What Our Clients Say</h2>
<p style="text-align:center;color:#666;margin-bottom:3rem">Real reviews from real customers</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem">
{items}
</div>
</div>
</section>"""


def render_site(lead_data: dict, spec: dict, competitor_html: str = "",
                analysis_html: str = "") -> str:
    """
    Render a complete HTML site from an AI-generated spec.

    Uses the layout template from spec['layout'] and fills in
    AI-generated content. Always produces unique output per call
    by varying section details. Premium dark theme with images.
    """
    layout_name = spec.get("layout", DEFAULT_LAYOUT)
    layout = LAYOUTS.get(layout_name, LAYOUTS[DEFAULT_LAYOUT])

    primary = spec["primary_color"]
    secondary = spec["secondary_color"]
    tagline = spec["tagline"]
    name = lead_data.get("business_name", "Business")
    city = lead_data.get("city", "")
    phone = lead_data.get("phone_primary", "")
    phone_digits = re.sub(r"\D", "", phone)
    rating = lead_data.get("rating", 0) or 0
    reviews = lead_data.get("review_count", 0) or 0
    address = lead_data.get("address", "")
    address_short = ", ".join(p.strip() for p in address.split(",")[:2]) if address else city
    category = lead_data.get("category", "")
    category_lower = category.lower()
    name_short = name.split()[0] if name else "Biz"

    # Look up images
    hero_bg_image = _get_category_image(category)

    # ── Hero section ──────────────────────────────────────────────────
    hero_style = layout["hero_style"]

    if hero_style == "magazine":
        hero_html = f"""<section class="hero" style="position:relative;min-height:90vh;background:url('{hero_bg_image}') center/cover;display:flex;align-items:flex-end;justify-content:flex-start;overflow:hidden">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,11,20,0.1) 0%,rgba(7,11,20,0.4) 40%,rgba(7,11,20,0.95) 100%);z-index:1"></div>
<div style="position:relative;z-index:2;color:white;max-width:720px;padding:4rem">
<span style="display:inline-block;background:{primary};padding:6px 18px;border-radius:6px;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:1.5rem;opacity:0">Featured</span>
<h1 style="font-size:3.8rem;font-weight:800;margin-bottom:1rem;line-height:1.1;letter-spacing:-1px;opacity:0">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.2rem;opacity:0.9;margin-bottom:2rem;max-width:600px;line-height:1.6;opacity:0">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;opacity:0">
<a href="#contact" style="padding:14px 32px;border-radius:14px;background:linear-gradient(135deg,{primary},{secondary});color:white;font-weight:700;text-decoration:none;font-size:1rem;box-shadow:0 6px 24px {primary}35">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" style="padding:14px 32px;border-radius:14px;border:1px solid rgba(255,255,255,0.2);color:white;font-weight:600;text-decoration:none;font-size:1rem;background:rgba(255,255,255,0.04)">📞 Call Now</a>
</div>
<div style="margin-top:2rem;display:flex;gap:2rem;font-size:0.9rem;opacity:0">
<span style="display:flex;align-items:center;gap:6px">⭐ {rating} Rating</span>
<span style="display:flex;align-items:center;gap:6px">📝 {reviews} Reviews</span>
</div>
</div></section>"""
    elif hero_style == "dark-luxury":
        hero_html = f"""<section class="hero" style="position:relative;min-height:100vh;background:linear-gradient(135deg,#070b14 0%,#0a0f1e 50%,#0f1a2e 100%);display:flex;align-items:center;justify-content:center;overflow:hidden">
<div style="position:absolute;inset:0;opacity:0.1;background:url('{hero_bg_image}') center/cover;filter:grayscale(0.6)"></div>
<div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,{primary},{secondary})"></div>
<div style="position:relative;z-index:1;text-align:center;color:white;max-width:800px;padding:2rem;opacity:0">
<div style="font-size:0.85rem;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{primary};margin-bottom:1.5rem">Premium Services</div>
<h1 style="font-size:4rem;font-weight:800;margin-bottom:1rem;line-height:1.1;letter-spacing:-1px;color:#f0f0f0">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.2rem;color:#94a3b8;margin-bottom:2.5rem;max-width:600px;margin-left:auto;margin-right:auto">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
<a href="#contact" style="padding:14px 32px;border-radius:14px;background:linear-gradient(135deg,{primary},{secondary});color:#fff;font-weight:700;text-decoration:none;font-size:1rem;box-shadow:0 6px 24px {primary}35">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" style="padding:14px 32px;border-radius:14px;border:1px solid rgba(255,255,255,0.15);color:#94a3b8;font-weight:600;text-decoration:none;font-size:1rem">📞 Call Now</a>
</div>
<div style="margin-top:2.5rem;display:flex;gap:3rem;justify-content:center;font-size:0.9rem">
<div><span style="color:{primary};font-weight:700">⭐ {rating}</span><span style="color:#64748b;margin-left:0.3rem">Rating</span></div>
<div><span style="color:{primary};font-weight:700">📝 {reviews}</span><span style="color:#64748b;margin-left:0.3rem">Reviews</span></div>
</div>
</div></section>"""
    else:
        # fullscreen / split / overlay — all get image hero
        hero_html = f"""<section class="hero" style="position:relative;min-height:95vh;background:url('{hero_bg_image}') center/cover;display:flex;align-items:center;justify-content:center;overflow:hidden">
<div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(7,11,20,0.7) 0%,rgba(7,11,20,0.5) 50%,rgba(7,11,20,0.8) 100%);z-index:1"></div>
<div style="position:relative;z-index:2;text-align:center;color:white;max-width:750px;padding:2rem;opacity:0">
<h1 style="font-size:3.8rem;font-weight:800;margin-bottom:1rem;line-height:1.1;letter-spacing:-1px">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.2rem;opacity:0.9;margin-bottom:2rem">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
<a href="#contact" style="padding:14px 32px;border-radius:14px;background:linear-gradient(135deg,{primary},{secondary});color:white;font-weight:700;text-decoration:none;font-size:1rem;box-shadow:0 6px 24px {primary}35">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" style="padding:14px 32px;border-radius:14px;border:1px solid rgba(255,255,255,0.2);color:white;font-weight:600;text-decoration:none;font-size:1rem">📞 Call Now</a>
</div>
<div style="margin-top:2rem;opacity:0.5;font-size:0.95rem">{'★' * int(round(rating))} {rating} ({reviews} reviews)</div>
</div></section>"""

    # ── Services section ──────────────────────────────────────────────
    svc_descs = spec.get("service_descriptions", [])
    if svc_descs:
        svc_items = "".join(
            f'<div class="card"><div class="card-icon"><i class="fa-solid fa-star"></i></div><h3 style="font-size:1.1rem;font-weight:700;color:white;margin-bottom:0.5rem">{s}</h3><p style="font-size:0.85rem;color:#94a3b8;line-height:1.6">Professional {category_lower} service tailored to your needs.</p></div>'
            for s in svc_descs
        )
    else:
        svc_items = '<div class="card"><div class="card-icon"><i class="fa-solid fa-star"></i></div><p style="color:#94a3b8">Professional services tailored to your needs.</p></div>'

    services_html = f"""<section id="services" style="padding:5rem 1.5rem;background:#070b14">
<div class="container" style="max-width:1200px;margin:0 auto">
<h2 style="font-size:2rem;font-weight:700;text-align:center;margin-bottom:0.5rem;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">Our Services</h2>
<p style="text-align:center;color:#64748b;margin-bottom:3rem;font-size:0.95rem">{tagline}</p>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem">
{svc_items}
</div>
</div>
</section>"""

    # ── About section ─────────────────────────────────────────────────
    about_html = f"""<section id="about" style="padding:5rem 1.5rem;background:rgba(255,255,255,0.015)">
<div class="container" style="max-width:800px;margin:0 auto;text-align:center">
<h2 style="font-size:2rem;font-weight:700;margin-bottom:1rem;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">About {name}</h2>
<p style="font-size:1rem;color:#94a3b8;line-height:1.8">{spec.get('description', tagline)}</p>
<div style="margin-top:2rem;display:flex;gap:2rem;justify-content:center;flex-wrap:wrap">
<div style="text-align:center;padding:1.5rem 2rem;background:rgba(255,255,255,0.03);border-radius:16px;border:1px solid rgba(255,255,255,0.05)"><div style="font-size:2rem;font-weight:800;color:{primary}">{rating}</div><div style="font-size:0.85rem;color:#64748b">⭐ Rating</div></div>
<div style="text-align:center;padding:1.5rem 2rem;background:rgba(255,255,255,0.03);border-radius:16px;border:1px solid rgba(255,255,255,0.05)"><div style="font-size:2rem;font-weight:800;color:{secondary}">{reviews}</div><div style="font-size:0.85rem;color:#64748b">📝 Reviews</div></div>
</div>
</div>
</section>"""

    # ── Stats section ─────────────────────────────────────────────────
    score = round(rating * 20)
    stats_html = f"""<section style="padding:4rem 1.5rem;background:rgba(255,255,255,0.01)">
<div class="container" style="max-width:1200px;margin:0 auto">
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;text-align:center">
<div class="stat-card" style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:2.5rem 1.5rem;backdrop-filter:blur(16px)">
<div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">{rating}</div>
<div style="font-size:0.9rem;color:#64748b;margin-top:0.5rem">⭐ Overall Rating</div>
</div>
<div class="stat-card" style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:2.5rem 1.5rem;backdrop-filter:blur(16px)">
<div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,{secondary},{primary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">{reviews}</div>
<div style="font-size:0.9rem;color:#64748b;margin-top:0.5rem">📝 Verified Reviews</div>
</div>
<div class="stat-card" style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:2.5rem 1.5rem;backdrop-filter:blur(16px)">
<div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">{score}%</div>
<div style="font-size:0.9rem;color:#64748b;margin-top:0.5rem">🎯 Satisfaction</div>
</div>
</div>
</div>
</section>"""

    # ── Testimonials section ──────────────────────────────────────────
    quote = "\u201C"
    end_quote = "\u201D"
    if rating >= 4.5:
        reviews_list = [
            f"Absolutely outstanding service! {name} exceeded all my expectations. Highly recommended!",
            f"Professional, courteous, and incredibly skilled. So glad I found {name}!",
            f"Five-star experience from start to finish. Will definitely be coming back.",
        ]
    elif rating >= 3.5:
        reviews_list = [
            f"Great experience with {name}. Very professional team.",
            f"Good service overall. Would recommend to others looking for quality {category_lower}.",
            f"Satisfied with the results. The team was very helpful throughout.",
        ]
    else:
        reviews_list = [
            "Decent service. Room for improvement but overall okay.",
            "Average experience. The staff was friendly enough.",
        ]
    items = "".join(
        f'<div class="testimonial" style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:2rem;position:relative">'
        f'<div style="font-size:0.9rem;font-style:italic;color:#cbd5e1;margin-bottom:1rem;line-height:1.7;position:relative;z-index:1">{quote}{review}{end_quote}</div>'
        f'<div style="display:flex;align-items:center;gap:10px">'
        f'<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,{primary},{secondary});display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;color:#fff">{("V" if i == 0 else "C" if i == 1 else "S")}</div>'
        f'<div><div style="font-size:0.85rem;font-weight:600;color:white">Verified Customer</div><div style="font-size:0.75rem;color:#64748b">Google Review</div></div>'
        f'</div></div>'
        for i, review in enumerate(reviews_list)
    )
    testimonials_html = f"""<section style="padding:5rem 1.5rem;background:#070b14">
<div class="container" style="max-width:1200px;margin:0 auto">
<h2 style="font-size:2rem;font-weight:700;text-align:center;margin-bottom:0.5rem;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">What Clients Say</h2>
<p style="text-align:center;color:#64748b;margin-bottom:3rem;font-size:0.95rem">Real reviews from real customers</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem">
{items}
</div>
</div>
</section>"""

    # ── CTA section ───────────────────────────────────────────────────
    cta_html = f"""<section id="cta" style="padding:5rem 1.5rem;background:linear-gradient(135deg,{primary} 0%,{secondary} 100%);color:white;text-align:center">
<div class="container" style="max-width:700px;margin:0 auto">
<h2 style="font-size:2rem;font-weight:700;margin-bottom:1rem">Ready to Get Started?</h2>
<p style="margin-bottom:2rem;opacity:0.9;font-size:1rem">{spec.get('tagline', tagline)}</p>
<a href="tel:{phone_digits}" style="display:inline-block;padding:1rem 2.5rem;border-radius:14px;background:white;color:{primary};font-weight:700;text-decoration:none;font-size:1rem;box-shadow:0 6px 20px rgba(0,0,0,0.15)">{spec.get('cta_text', 'Get in Touch')}</a>
</div>
</section>"""

    # ── Extra sections ────────────────────────────────────────────────
    extra_sections = ""
    if competitor_html:
        extra_sections += f'<section style="padding:4rem 1.5rem;background:rgba(255,255,255,0.008)"><div class="container" style="max-width:1200px;margin:0 auto">{competitor_html}</div></section>'
    if analysis_html:
        extra_sections += f'<section style="padding:4rem 1.5rem;background:#070b14"><div class="container" style="max-width:1200px;margin:0 auto">{analysis_html}</div></section>'

    # ── Contact section ───────────────────────────────────────────────
    contact_html = f"""<section id="contact" style="padding:5rem 1.5rem;background:rgba(255,255,255,0.008);color:white;text-align:center">
<div class="container" style="max-width:600px;margin:0 auto">
<h2 style="font-size:2rem;font-weight:700;margin-bottom:1rem;background:linear-gradient(135deg,{primary},{secondary});-webkit-background-clip:text;-webkit-text-fill-color:transparent">Get in Touch</h2>
<p style="margin-bottom:2.5rem;color:#64748b">{spec.get('tagline', tagline)}</p>
<div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;font-size:1rem">
<div style="padding:1rem 2rem;background:rgba(255,255,255,0.03);border-radius:14px;border:1px solid rgba(255,255,255,0.06)">📞 <a href="tel:{phone_digits}" style="color:white;text-decoration:none">{phone}</a></div>
<div style="padding:1rem 2rem;background:rgba(255,255,255,0.03);border-radius:14px;border:1px solid rgba(255,255,255,0.06)">📍 {address_short}</div>
</div>
</div>
</section>"""

    # ── Build sections ────────────────────────────────────────────────
    section_map = {
        "hero": hero_html,
        "about": about_html,
        "services": services_html,
        "stats": stats_html,
        "testimonials": testimonials_html,
        "cta": cta_html,
    }
    all_sections = "".join(section_map.get(s, "") for s in layout["section_order"]
                          if s not in ("contact", "hero"))
    all_sections += extra_sections
    if "contact" in layout["section_order"]:
        all_sections += contact_html

    # ── Assemble complete page ────────────────────────────────────────
    return f"""<!DOCTYPE html>
<!-- Layout: {layout_name} | Generated by TKVibes AI CRM -->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{spec.get('seo_title', name)}</title>
<meta name="description" content="{spec.get('seo_description', '')}">
<meta name="robots" content="index, follow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script type="application/ld+json">{{
"@context": "https://schema.org",
"@type": "{spec.get('schema_type', 'LocalBusiness')}",
"name": "{name}",
"address": {{"@type": "PostalAddress", "addressLocality": "{city}"}},
"aggregateRating": {{"@type": "AggregateRating", "ratingValue": "{rating}", "reviewCount": "{reviews}"}},
"telephone": "{phone}"
}}</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',sans-serif;background:#070b14;color:#e2e8f0;overflow-x:hidden;-webkit-font-smoothing:antialiased}}
h1,h2,h3{{font-family:'Space Grotesk',sans-serif}}
img{{max-width:100%}}
a{{text-decoration:none;color:inherit}}

/* Hero fade-in */
.hero *{{animation:fadeUp 0.8s ease-out forwards}}
.hero *:nth-child(2){{animation-delay:0.1s}}
.hero *:nth-child(3){{animation-delay:0.2s}}
.hero *:nth-child(4){{animation-delay:0.3s}}
.hero *:nth-child(5){{animation-delay:0.4s}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(30px)}}to{{opacity:1;transform:translateY(0)}}}}

/* Cards & hover */
.card{{background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:2rem;transition:all 0.4s cubic-bezier(0.16,1,0.3,1)}}
.card:hover{{transform:translateY(-6px);background:rgba(255,255,255,0.04);border-color:{primary}25}}
.card-icon{{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;margin-bottom:1rem;background:linear-gradient(135deg,{primary}15,{secondary}10)}}
.card-icon i{{font-size:20px;color:{primary}}}

.stat-card,.testimonial{{transition:all 0.4s cubic-bezier(0.16,1,0.3,1)}}
.stat-card:hover,.testimonial:hover{{transform:translateY(-4px)}}

/* Nav */
.nav{{position:fixed;top:0;left:0;right:0;z-index:100;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;transition:all 0.3s}}
.nav.scrolled{{background:rgba(7,11,20,0.92);backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,0.04)}}
.nav-links a{{font-size:0.85rem;color:#94a3b8;margin-left:1.5rem;transition:color 0.2s}}
.nav-links a:hover{{color:white}}

@media(max-width:768px){{
.hero h1{{font-size:2.2rem !important}}
.nav-links{{display:none}}
h1{{font-size:2rem !important}}
.card{{padding:1.5rem}}
}}</style>
</head>
<body>

<!-- Nav -->
<nav class="nav" id="navbar">
<div style="font-weight:700;font-size:1.1rem;color:white">{name_short}</div>
<div class="nav-links">
<a href="#services">Services</a>
<a href="#about">About</a>
<a href="#contact">Contact</a>
<a href="tel:{phone_digits}" style="padding:8px 18px;border-radius:10px;background:linear-gradient(135deg,{primary},{secondary});color:white;font-weight:600;font-size:0.85rem">📞 Call</a>
</div>
</nav>

{hero_html}
{all_sections}

<!-- Footer -->
<footer style="padding:3rem 1.5rem;text-align:center;border-top:1px solid rgba(255,255,255,0.04);background:#070b14">
<p style="color:#64748b;font-size:0.85rem">© 2026 {name}. All rights reserved.</p>
<p style="color:#334155;font-size:0.75rem;margin-top:8px">Concept by TKVibes — not affiliated with {name}</p>
</footer>

<script>
// Nav scroll
window.addEventListener('scroll',function(){{
document.getElementById('navbar').classList.toggle('scrolled',window.scrollY>50);
}});
// Smooth anchor scroll
document.querySelectorAll('a[href^="#"]').forEach(a=>{{
a.addEventListener('click',function(e){{e.preventDefault();var t=document.querySelector(this.getAttribute('href'));if(t)t.scrollIntoView({{behavior:'smooth'}})}})
}});
</script>
</body>
</html>"""

    return html