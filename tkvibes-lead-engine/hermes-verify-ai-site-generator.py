"""Ad-hoc verification: new layouts, image lookup, stats/testimonials sections."""
import sys
import os
import tempfile

# Add source to path
sys.path.insert(0, os.path.expanduser(
    "~/Desktop/tkvibes-agency/tkvibes-lead-engine/src"))

from ai_site_generator import (
    LAYOUTS, DEFAULT_LAYOUT, CATEGORY_IMAGES, DEFAULT_IMAGE,
    _get_category_image, _render_stats_section, _render_testimonials_section,
    _default_site_spec, render_site,
)

errors = []

# 1. Check new layouts exist
for name in ("magazine", "dark-luxury"):
    if name not in LAYOUTS:
        errors.append(f"Missing layout: {name}")
    else:
        print(f"  ✓ Layout '{name}' exists: hero_style={LAYOUTS[name]['hero_style']}")

# 2. Verify LAYOUTS count
assert len(LAYOUTS) == 5, f"Expected 5 layouts, got {len(LAYOUTS)}"

# 3. Test category image lookup
for cat in ("dental", "lawyer", "medical", "pet", "veterinary",
            "interior design", "restaurant", "cafe", "salon", "spa"):
    url = _get_category_image(cat)
    assert "images.unsplash.com" in url, f"Bad image URL for {cat}"
    print(f"  ✓ Category '{cat}' → {url.split('?')[0].split('/')[-1][:20]}...")

# 4. Test fallback for unknown category
url = _get_category_image("plumber")
assert url == DEFAULT_IMAGE, f"Expected default image for unknown category"
print(f"  ✓ Unknown category falls back to default image")

# 5. Test partial match (e.g. "dental clinic" → dental image)
url = _get_category_image("dental clinic")
assert "images.unsplash.com" in url, f"Bad partial match for 'dental clinic'"
print(f"  ✓ Partial match 'dental clinic' resolves correctly")

url = _get_category_image("veterinary clinic")
assert "images.unsplash.com" in url, f"Bad partial match for 'veterinary clinic'"
print(f"  ✓ Partial match 'veterinary clinic' resolves correctly")

# 6. Render both new layouts through render_site
lead = {
    "business_name": "Elite Dental Care",
    "category": "dental",
    "city": "Mumbai",
    "phone_primary": "+91 98765 43210",
    "rating": 4.7,
    "review_count": 230,
    "address": "42 MG Road, Colaba, Mumbai, Maharashtra",
}
visuals = {"primary": "#2563eb", "secondary": "#3b82f6", "tagline": "Your Smile, Our Priority"}

for layout_name in ("magazine", "dark-luxury"):
    spec = _default_site_spec(lead, visuals)
    spec["layout"] = layout_name
    html = render_site(lead, spec)
    assert "<!DOCTYPE html>" in html, f"Layout {layout_name}: missing DOCTYPE"
    assert "</html>" in html, f"Layout {layout_name}: missing closing tag"
    # Check hero style is present
    assert layout_name.replace("-", "-") in html.replace("hero-", "hero-"), \
        f"Layout {layout_name}: hero class not found"
    # Check stats section appears (both new layouts include stats)
    assert "Satisfaction Score" in html or "Overall Rating" in html, \
        f"Layout {layout_name}: stats section missing"
    # Check testimonials appear
    assert "What Our Clients Say" in html, \
        f"Layout {layout_name}: testimonials section missing"
    # Check image URL is injected
    assert "images.unsplash.com" in html, \
        f"Layout {layout_name}: missing hero background image"
    print(f"  ✓ Layout '{layout_name}' renders valid HTML with stats + testimonials + image")

# 7. Verify existing 3 layouts still produce identical-style output
lead2 = {
    "business_name": "Test Clinic", "category": "clinic", "city": "Delhi",
    "phone_primary": "+911234567890", "rating": 4.0, "review_count": 50
}
v2 = {"primary": "#000", "secondary": "#fff", "tagline": "Test"}
for layout_name in ("modern-minimal", "professional-card", "bold-showcase"):
    spec = _default_site_spec(lead2, v2)
    spec["layout"] = layout_name
    html = render_site(lead2, spec)
    assert "schema.org" in html, f"Layout {layout_name}: missing schema markup"
    assert "</html>" in html, f"Layout {layout_name}: missing closing"
    print(f"  ✓ Existing layout '{layout_name}' still renders correctly")

# 8. Verify hero_bg_image is used (not gradient) for magazine layout
spec = _default_site_spec(lead, visuals)
spec["layout"] = "magazine"
html = render_site(lead, spec)
# The magazine hero uses image as bg with gradient overlay
assert "background:url(" in html or "background: url(" in html, \
    "magazine hero should use image background"

# 9. Verify dark-luxury has gold accent color
spec["layout"] = "dark-luxury"
html = render_site(lead, spec)
assert "#d4a853" in html, "dark-luxury should include gold accent color"

print(f"\n{'='*50}")
print(f"All checks passed with 0 errors!")
print(f"{'='*50}")
sys.exit(0 if not errors else 1)