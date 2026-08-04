"""
TKVibes — AI Site Generator Tests
"""
import json
from unittest.mock import patch, MagicMock


class TestAISiteGenerator:
    """Test the AI site generator module (most tests with mocked LLM)."""

    def test_module_imports(self):
        from src.ai_site_generator import (
            build_ai_site_spec, render_site, _default_site_spec, LAYOUTS, DEFAULT_LAYOUT
        )
        assert callable(build_ai_site_spec)
        assert callable(render_site)
        assert callable(_default_site_spec)
        assert len(LAYOUTS) >= 3
        assert DEFAULT_LAYOUT in LAYOUTS

    def test_default_spec_no_api_key(self):
        """Without OPENROUTER_API_KEY, should return default spec."""
        from src.ai_site_generator import build_ai_site_spec
        lead = {"business_name": "Test Clinic", "category": "dental clinic",
                "city": "Delhi", "rating": 4.5}
        visuals = {"primary": "#000", "secondary": "#fff", "tagline": "Test"}
        spec = build_ai_site_spec(lead, visuals)
        assert spec["layout"] == "modern-minimal"
        assert spec["primary_color"] == "#000"
        assert spec["tagline"] == "Test"

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test"})
    @patch("src.ai_site_generator._call_llm")
    def test_ai_spec_with_mocked_llm(self, mock_call):
        """With a valid API key and mock LLM, should parse returned JSON."""
        mock_call.return_value = json.dumps({
            "layout": "professional-card",
            "primary_color": "#1e40af",
            "secondary_color": "#3b82f6",
            "tagline": "Expert Legal Counsel You Can Trust",
            "description": "Leading law firm in Delhi...",
            "hero_headline": "Justice Delivered, Trust Earned",
            "hero_subheadline": "20+ years of legal excellence",
            "service_descriptions": ["Civil Litigation", "Corporate Law", "Family Law"],
            "cta_text": "Schedule a Consultation",
            "seo_title": "Law Firm Delhi | Expert Legal Services",
            "seo_description": "Top-rated law firm in Delhi offering civil, corporate, and family law services.",
            "schema_type": "LegalService",
            "color_swap": False,
        })
        from src.ai_site_generator import build_ai_site_spec
        lead = {"business_name": "Kapil & Associates", "category": "lawyer",
                "city": "Delhi", "rating": 4.8, "review_count": 150}
        visuals = {"primary": "#1e40af", "secondary": "#3b82f6",
                   "tagline": "Justice Delivered", "icon": "fa-gavel"}
        spec = build_ai_site_spec(lead, visuals)
        assert spec["layout"] == "professional-card"
        assert spec["primary_color"] == "#1e40af"
        assert spec["cta_text"] == "Schedule a Consultation"

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test"})
    @patch("src.ai_site_generator._call_llm")
    def test_ai_spec_fallback_on_bad_json(self, mock_call):
        """If LLM returns bad JSON, should fall back to default."""
        mock_call.return_value = "This is not JSON at all"
        from src.ai_site_generator import build_ai_site_spec
        lead = {"business_name": "Test", "category": "dental", "city": "Mumbai"}
        visuals = {"primary": "#ff0000", "secondary": "#00ff00", "tagline": "Custom"}
        spec = build_ai_site_spec(lead, visuals)
        assert spec["primary_color"] == "#ff0000"
        assert spec["layout"] == "modern-minimal"

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test"})
    @patch("src.ai_site_generator._call_llm")
    def test_ai_spec_fallback_on_empty_response(self, mock_call):
        """If LLM returns empty, should fall back to default."""
        mock_call.return_value = ""
        from src.ai_site_generator import build_ai_site_spec
        lead = {"business_name": "Test", "category": "dental", "city": "Mumbai"}
        visuals = {"primary": "#ff0000", "secondary": "#00ff00", "tagline": "Custom"}
        spec = build_ai_site_spec(lead, visuals)
        assert spec["layout"] == "modern-minimal"

    def test_render_site_with_default_spec(self):
        """render_site should produce valid HTML with a default spec."""
        from src.ai_site_generator import render_site, _default_site_spec
        lead = {"business_name": "Sunrise Dental", "category": "dental clinic",
                "city": "Delhi", "phone_primary": "+919999999999",
                "rating": 4.5, "review_count": 100, "address": "123 Main St, Delhi"}
        visuals = {"primary": "#8b5cf6", "secondary": "#a78bfa", "tagline": "Your Smile Matters"}
        spec = _default_site_spec(lead, visuals)
        html = render_site(lead, spec)
        assert "<!DOCTYPE html>" in html
        assert "Sunrise Dental" in html
        assert "#8b5cf6" in html
        assert "schema.org" in html
        assert "</html>" in html

    def test_render_site_includes_competitor_html(self):
        """Competitor analysis HTML should be included when provided."""
        from src.ai_site_generator import render_site, _default_site_spec
        lead = {"business_name": "Test Clinic", "category": "dental",
                "city": "Delhi", "phone_primary": "+911234567890",
                "rating": 4.0, "review_count": 50}
        visuals = {"primary": "#0ea5e9", "secondary": "#38bdf8",
                   "tagline": "Expert Care", "icon": "fa-stethoscope"}
        spec = _default_site_spec(lead, visuals)
        comp_html = '<div class="competitor-analysis">3 competitors found nearby</div>'
        html = render_site(lead, spec, competitor_html=comp_html)
        assert "competitor-analysis" in html
        assert "3 competitors found nearby" in html

    def test_render_site_includes_analysis_html(self):
        """Website analysis HTML should be included when provided."""
        from src.ai_site_generator import render_site, _default_site_spec
        lead = {"business_name": "Test", "category": "clinic",
                "city": "Mumbai", "phone_primary": "+91234567890",
                "rating": 3.5, "review_count": 20}
        visuals = {"primary": "#0ea5e9", "secondary": "#06b6d4",
                   "tagline": "Care", "icon": "fa-hospital"}
        spec = _default_site_spec(lead, visuals)
        analysis = '<div class="website-analysis">Slow loading, missing schema</div>'
        html = render_site(lead, spec, analysis_html=analysis)
        assert "website-analysis" in html
        assert "Slow loading" in html

    def test_render_produces_unique_output(self):
        """Two calls with different data should produce different HTML."""
        from src.ai_site_generator import render_site, _default_site_spec
        lead_a = {"business_name": "Alpha Dental", "category": "dental",
                  "city": "Delhi", "phone_primary": "+911111111111",
                  "rating": 4.5, "review_count": 100}
        lead_b = {"business_name": "Beta Legal", "category": "lawyer",
                  "city": "Mumbai", "phone_primary": "+912222222222",
                  "rating": 4.0, "review_count": 50}
        visuals_a = {"primary": "#8b5cf6", "secondary": "#a78bfa", "tagline": "Smile"}
        visuals_b = {"primary": "#1e40af", "secondary": "#3b82f6", "tagline": "Justice"}

        html_a = render_site(lead_a, _default_site_spec(lead_a, visuals_a))
        html_b = render_site(lead_b, _default_site_spec(lead_b, visuals_b))

        assert html_a != html_b
        assert "Alpha Dental" in html_a
        assert "Beta Legal" in html_b

    def test_all_layouts_produce_valid_html(self):
        """Each layout should produce valid HTML."""
        from src.ai_site_generator import render_site, _default_site_spec, LAYOUTS
        lead = {"business_name": "Test", "category": "dental", "city": "Delhi",
                "phone_primary": "+911234567890", "rating": 4.0, "review_count": 30}
        visuals = {"primary": "#000", "secondary": "#fff", "tagline": "Test"}
        for layout_name in LAYOUTS:
            spec = _default_site_spec(lead, visuals)
            spec["layout"] = layout_name
            html = render_site(lead, spec)
            assert "<!DOCTYPE html>" in html, f"Layout {layout_name} failed"
            assert "</html>" in html, f"Layout {layout_name} missing closing"

    def test_phone_digits_extracted(self):
        """Phone number should be stripped of non-digits for tel: links."""
        from src.ai_site_generator import render_site, _default_site_spec
        lead = {"business_name": "Test", "category": "dental", "city": "Delhi",
                "phone_primary": "+91 99999 99999", "rating": 4.0, "review_count": 30}
        visuals = {"primary": "#000", "secondary": "#fff", "tagline": "Test"}
        spec = _default_site_spec(lead, visuals)
        html = render_site(lead, spec)
        # The phone digits should appear in tel: links
        assert "tel:919999999999" in html