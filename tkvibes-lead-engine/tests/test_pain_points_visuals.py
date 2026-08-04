"""
TKVibes — Pain Points and Visuals Tests
"""
from src.models import Lead


class TestPainPoints:
    def test_build_pain_points_returns_string(self):
        from src.pain_points import build_pain_points
        l = Lead(business_name="Test Clinic", category="dental clinic", city="Delhi",
                 lead_key="t1", has_website=False)
        points = build_pain_points(l)
        assert isinstance(points, str)
        assert len(points) > 0
        assert "|" in points

    def test_recommend_pitch_returns_string(self):
        from src.pain_points import recommend_pitch
        l = Lead(business_name="Test", category="lawyer", lead_key="t1")
        pitch = recommend_pitch(l)
        assert isinstance(pitch, str)
        assert len(pitch) > 0

    def test_no_website_has_relevant_pain_point(self):
        from src.pain_points import build_pain_points
        l = Lead(business_name="Test", category="dental clinic", lead_key="t1", has_website=False)
        points = build_pain_points(l)
        has_online_presence = "No website" in points or "without website" in points or "online presence" in points
        assert has_online_presence, f"Pain points should mention missing online presence: {points}"

    def test_unknown_category_fallback(self):
        from src.pain_points import build_pain_points
        l = Lead(business_name="Test", category="very-rare-unknown-category-xyz", lead_key="t1")
        points = build_pain_points(l)
        assert isinstance(points, str)
        assert len(points) > 0


class TestVisuals:
    def test_get_visual_config_returns_dict(self):
        from src.visuals import get_visual_config
        cfg = get_visual_config("dental clinic")
        assert "primary" in cfg
        assert "secondary" in cfg
        assert "icon" in cfg
        assert "tagline" in cfg

    def test_dental_clinic_color(self):
        """'dental clinic' matches 'dental' keyword with purple (#8b5cf6)."""
        from src.visuals import get_visual_config
        cfg = get_visual_config("dental clinic")
        # 'dental' keyword matches: primary=#8b5cf6 (purple)
        assert cfg["primary"] == "#8b5cf6", f"Expected purple, got {cfg['primary']}"

    def test_clinic_keyword_matches_blue(self):
        """'clinic' should match 'clinic' keyword with sky blue."""
        from src.visuals import get_visual_config
        cfg = get_visual_config("medical clinic")
        # 'clinic' matches: primary=#0ea5e9 (sky blue)
        assert cfg["primary"] == "#0ea5e9", f"Expected sky blue, got {cfg['primary']}"

    def test_unknown_category_returns_default(self):
        from src.visuals import get_visual_config, DEFAULT_CONFIG
        cfg = get_visual_config("nonexistent-category-xyz")
        assert cfg == DEFAULT_CONFIG

    def test_sanitize_phone(self):
        from src.visuals import sanitize_phone
        # Removes spaces, keeps digits: +91 99999 99999 → 919999999999
        assert sanitize_phone("+91 99999 99999") == "919999999999"
        assert sanitize_phone("") == ""

    def test_build_hours_html(self):
        from src.visuals import build_hours_html
        html = build_hours_html("Monday: 9-5; Tuesday: 9-5")
        assert isinstance(html, str)

    def test_build_services_html(self):
        """build_services_html expects a dict with 'services' as list of (icon, title, desc) tuples."""
        from src.visuals import build_services_html
        cfg = {
            "services": [
                ("fa-check", "Service A", "Description A"),
                ("fa-star", "Service B", "Description B"),
            ]
        }
        html = build_services_html(cfg)
        assert isinstance(html, str)
        assert "Service A" in html
        assert "Description B" in html

    def test_get_why_items(self):
        from src.visuals import get_why_items
        items = get_why_items("dental clinic")
        assert isinstance(items, str)
        assert len(items) > 0