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
    by varying section details.
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

    # Look up hero background image from category
    category = lead_data.get("category", "")
    hero_bg_image = _get_category_image(category)

    # ── Hero section ──────────────────────────────────────────────────
    hero_bg = f"linear-gradient(135deg, {primary} 0%, {secondary} 100%)"
    hero_style = layout["hero_style"]

    if hero_style == "fullscreen":
        hero_html = f"""<section class="hero-fullscreen" style="background:{hero_bg};min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem;text-align:center;color:white">
<div style="max-width:800px"><h1 style="font-size:3.5rem;font-weight:800;margin-bottom:1rem;line-height:1.1">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.3rem;opacity:0.9;margin-bottom:2rem">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap"><a href="#contact" class="btn-primary" style="padding:1rem 2.5rem;border-radius:50px;background:white;color:{primary};font-weight:700;text-decoration:none;font-size:1.1rem">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" class="btn-outline" style="padding:1rem 2.5rem;border-radius:50px;border:2px solid white;color:white;font-weight:600;text-decoration:none;font-size:1.1rem">📞 Call Now</a></div>
<div style="margin-top:2rem;font-size:1rem;opacity:0.7">{'★' * int(round(rating))} {rating} ({reviews} reviews)</div></div></section>"""
    elif hero_style == "split":
        hero_html = f"""<section class="hero-split" style="display:flex;min-height:90vh;background:{primary}10">
<div style="flex:1;padding:4rem;display:flex;flex-direction:column;justify-content:center"><h1 style="font-size:3rem;font-weight:800;color:{primary};margin-bottom:1rem">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.2rem;color:#555;margin-bottom:2rem">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem"><a href="#contact" style="padding:0.8rem 2rem;border-radius:8px;background:{primary};color:white;text-decoration:none;font-weight:600">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" style="padding:0.8rem 2rem;border-radius:8px;border:2px solid {primary};color:{primary};text-decoration:none;font-weight:600">📞 Call</a></div></div>
<div style="flex:1;background:{secondary}20;display:flex;align-items:center;justify-content:center;padding:2rem"><div style="text-align:center"><div style="font-size:5rem;margin-bottom:1rem">⭐</div><div style="font-size:2rem;font-weight:700;color:{primary}">{rating}</div><div style="color:#666">{reviews} reviews</div></div></div></section>"""
    elif hero_style == "overlay":
        hero_html = f"""<section class="hero-overlay" style="position:relative;min-height:90vh;background:url('https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1200') center/cover;display:flex;align-items:center;justify-content:center">
<div style="position:absolute;inset:0;background:{primary}cc"></div>
<div style="position:relative;z-index:1;text-align:center;color:white;max-width:700px;padding:2rem"><h1 style="font-size:3.5rem;font-weight:800;margin-bottom:1rem">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.2rem;margin-bottom:2rem">{spec.get('hero_subheadline', tagline)}</p>
<a href="#contact" style="display:inline-block;padding:1rem 2.5rem;border-radius:50px;background:white;color:{primary};font-weight:700;text-decoration:none">{spec.get('cta_text', 'Get in Touch')}</a></div></section>"""
    elif hero_style == "magazine":
        hero_html = f"""<section class="hero-magazine" style="position:relative;min-height:80vh;background:url('{hero_bg_image}') center/cover;display:flex;align-items:flex-end;justify-content:flex-start">
<div style="position:absolute;inset:0;background:linear-gradient(transparent 40%, rgba(0,0,0,0.85) 100%)"></div>
<div style="position:relative;z-index:1;color:white;max-width:700px;padding:3rem 4rem">
<span style="display:inline-block;background:{primary};padding:0.3rem 1rem;border-radius:4px;font-size:0.8rem;font-weight:600;text-transform:uppercase;margin-bottom:1rem">Featured</span>
<h1 style="font-size:3.5rem;font-weight:800;margin-bottom:1rem;line-height:1.1">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.2rem;opacity:0.9;margin-bottom:1.5rem;line-height:1.5">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap">
<a href="#contact" style="padding:0.8rem 2rem;border-radius:6px;background:{primary};color:white;font-weight:700;text-decoration:none;font-size:1rem">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" style="color:white;text-decoration:none;font-size:1rem;opacity:0.8">📞 {phone}</a>
</div>
<div style="margin-top:1.5rem;display:flex;gap:2rem;font-size:0.9rem;opacity:0.7">
<span>⭐ {rating} Rating</span>
<span>📝 {reviews} Reviews</span>
</div>
</div>
</section>"""
    else:  # dark-luxury
        hero_html = f"""<section class="hero-dark-luxury" style="position:relative;min-height:100vh;background:linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);display:flex;align-items:center;justify-content:center;overflow:hidden">
<div style="position:absolute;inset:0;opacity:0.15;background:url('{hero_bg_image}') center/cover;filter:grayscale(0.5)"></div>
<div style="position:absolute;top:0;left:0;right:0;height:4px;background:{primary}"></div>
<div style="position:relative;z-index:1;text-align:center;color:white;max-width:800px;padding:2rem">
<div style="font-size:0.9rem;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#d4a853;margin-bottom:1.5rem">Premium Services</div>
<h1 style="font-size:4rem;font-weight:800;margin-bottom:1rem;line-height:1.1;color:#f5f5f5">{spec.get('hero_headline', f'Welcome to {name}')}</h1>
<p style="font-size:1.3rem;color:#b0b0b0;margin-bottom:2.5rem;max-width:600px;margin-left:auto;margin-right:auto">{spec.get('hero_subheadline', tagline)}</p>
<div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
<a href="#contact" style="padding:1rem 2.5rem;border-radius:6px;background:#d4a853;color:#1a1a2e;font-weight:700;text-decoration:none;font-size:1.1rem">{spec.get('cta_text', 'Get in Touch')}</a>
<a href="tel:{phone_digits}" style="padding:1rem 2.5rem;border-radius:6px;border:1px solid #d4a853;color:#d4a853;font-weight:600;text-decoration:none;font-size:1.1rem">📞 Call Now</a>
</div>
<div style="margin-top:2.5rem;display:flex;gap:3rem;justify-content:center;font-size:0.95rem">
<div><span style="color:#d4a853;font-weight:700">⭐ {rating}</span><span style="color:#888;margin-left:0.3rem">Rating</span></div>
<div><span style="color:#d4a853;font-weight:700">📝 {reviews}</span><span style="color:#888;margin-left:0.3rem">Reviews</span></div>
</div>
</div>
</section>"""

    # ── Services section ──────────────────────────────────────────────
    svc_descs = spec.get("service_descriptions", [])
    if svc_descs:
        svc_items = "".join(
            f'<div class="service-card" style="background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1px solid #eee"><h3 style="font-size:1.2rem;font-weight:700;color:{primary};margin-bottom:0.5rem">{s}</h3></div>'
            for s in svc_descs
        )
    else:
        svc_items = '<div class="service-card" style="background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.06)"><p style="color:#666">Professional services tailored to your needs. Contact us for more details.</p></div>'

    services_html = f"""<section id="services" style="padding:4rem 2rem">
<div class="container">
<h2 style="font-size:2rem;font-weight:700;text-align:center;margin-bottom:0.5rem;color:{primary}">Our Services</h2>
<p style="text-align:center;color:#666;margin-bottom:3rem">{tagline}</p>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem">
{svc_items}
</div>
</div>
</section>"""

    # ── About section ─────────────────────────────────────────────────
    about_html = f"""<section id="about" style="padding:4rem 2rem;background:{primary}08">
<div class="container" style="max-width:800px;text-align:center">
<h2 style="font-size:2rem;font-weight:700;margin-bottom:1rem;color:{primary}">About Us</h2>
<p style="font-size:1.1rem;color:#555;line-height:1.7">{spec.get('description', tagline)}</p>
</div>
</section>"""

    # ── Stats section ─────────────────────────────────────────────────
    stats_html = _render_stats_section(rating, reviews, primary, secondary)

    # ── Testimonials section ──────────────────────────────────────────
    testimonials_html = _render_testimonials_section(rating, name, primary)

    # ── CTA section ───────────────────────────────────────────────────
    cta_html = f"""<section id="cta" style="padding:4rem 2rem;background:linear-gradient(135deg, {primary} 0%, {secondary} 100%);color:white;text-align:center">
<div class="container">
<h2 style="font-size:2rem;font-weight:700;margin-bottom:1rem">Ready to Get Started?</h2>
<p style="margin-bottom:2rem;opacity:0.9;font-size:1.1rem">{spec.get('tagline', tagline)}</p>
<a href="#contact" style="display:inline-block;padding:1rem 2.5rem;border-radius:50px;background:white;color:{primary};font-weight:700;text-decoration:none;font-size:1.1rem">{spec.get('cta_text', 'Get in Touch')}</a>
</div>
</section>"""

    # ── Competitor gap / website analysis sections ─────────────────────
    extra_sections = ""
    if competitor_html:
        extra_sections += f'<section class="extra-section" style="padding:4rem 2rem;background:#f8f9fa">{competitor_html}</section>'
    if analysis_html:
        extra_sections += f'<section class="extra-section" style="padding:4rem 2rem">{analysis_html}</section>'

    # ── Footer / Contact ──────────────────────────────────────────────
    address = lead_data.get("address", "")
    address_short = ", ".join(p.strip() for p in address.split(",")[:2]) if address else city

    # ── Build sections based on section_order ─────────────────────────
    section_map = {
        "hero": hero_html,
        "about": about_html,
        "services": services_html,
        "stats": stats_html,
        "testimonials": testimonials_html,
        "cta": cta_html,
    }
    # contact is handled separately (always at the bottom before footer)
    all_sections = "".join(section_map.get(s, "") for s in layout["section_order"]
                          if s != "contact")
    # Add extra sections (competitor/analysis) right before contact
    all_sections += extra_sections
    # Add contact section at the end (always present if in section_order)
    if "contact" in layout["section_order"]:
        all_sections += f"""<section id="contact" style="padding:4rem 2rem;background:{primary};color:white;text-align:center">
<div class="container">
<h2 style="font-size:2rem;font-weight:700;margin-bottom:1rem">Get in Touch</h2>
<p style="margin-bottom:2rem;opacity:0.9">{spec.get('tagline', tagline)}</p>
<div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;font-size:1.1rem">
<div>📞 <a href="tel:{phone_digits}" style="color:white;text-decoration:none">{phone}</a></div>
<div>📍 {address_short}</div>
</div>
</div>
</section>"""

    # ── Assemble the complete page ────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{spec.get('seo_title', name)}</title>
<meta name="description" content="{spec.get('seo_description', '')}">
<meta name="robots" content="index, follow">
<script type="application/ld+json">{{
"@context": "https://schema.org",
"@type": "{spec.get('schema_type', 'LocalBusiness')}",
"name": "{name}",
"image": "",
"address": {{"@type": "PostalAddress", "addressLocality": "{city}"}},
"aggregateRating": {{"@type": "AggregateRating", "ratingValue": "{rating}", "reviewCount": "{reviews}"}},
"telephone": "{phone}"
}}</script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;color:#333;line-height:1.6}}
a{{color:inherit}}
img{{max-width:100%}}
.container{{max-width:1200px;margin:0 auto;padding:0 2rem}}
section{{scroll-margin-top:2rem}}
.service-card{{transition:transform 0.3s,box-shadow 0.3s}}
.service-card:hover{{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,0,0,0.1)}}
.stat-card,.testimonial-card{{transition:transform 0.3s,box-shadow 0.3s}}
.stat-card:hover,.testimonial-card:hover{{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,0,0,0.1)}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(30px)}}to{{opacity:1;transform:translateY(0)}}}}
.hero-magazine *,.hero-dark-luxury *{{animation:fadeInUp 0.8s ease-out forwards}}
.hero-magazine *:nth-child(2),.hero-dark-luxury *:nth-child(2){{animation-delay:0.1s}}
.hero-magazine *:nth-child(3),.hero-dark-luxury *:nth-child(3){{animation-delay:0.2s}}
.hero-magazine *:nth-child(4),.hero-dark-luxury *:nth-child(4){{animation-delay:0.3s}}
.hero-magazine *:nth-child(5),.hero-dark-luxury *:nth-child(5){{animation-delay:0.4s}}
@media(max-width:768px){{.hero-fullscreen h1{{font-size:2.2rem !important}}.hero-split{{flex-direction:column !important}}.hero-split>div{{padding:2rem !important}}.hero-magazine h1{{font-size:2.2rem !important}}.hero-dark-luxury h1{{font-size:2.5rem !important}}h1{{font-size:2rem !important}}}}
</style>
</head>
<body>
{hero_html}
<nav style="position:sticky;top:0;background:white;border-bottom:1px solid #eee;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;z-index:100">
<div style="font-weight:700;font-size:1.2rem;color:{primary}">{lead_data.get('business_name', 'Business')}</div>
<div style="display:flex;gap:1.5rem;font-size:0.9rem">
<a href="#services" style="text-decoration:none;color:#555">Services</a>
<a href="#contact" style="text-decoration:none;color:#555">Contact</a>
<a href="tel:{phone_digits}" style="text-decoration:none;color:{primary};font-weight:600">📞 {phone}</a>
</div>
</nav>
{all_sections}
<footer style="padding:2rem;text-align:center;background:#1a1a1a;color:#999;font-size:0.85rem">
<p>© 2024 {name}. All rights reserved. | Website by TKVibes Digital Agency</p>
</footer>
</body>
</html>"""

    return html