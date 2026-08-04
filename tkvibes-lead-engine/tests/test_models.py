"""
TKVibes — Lead Model Tests
"""
from src.models import Lead, SCHEMA


class TestLeadDefaults:
    """Lead dataclass should have sensible defaults."""

    def test_empty_lead(self):
        l = Lead()
        assert l.business_name == ""
        assert l.lead_tier == "COLD"
        assert l.lead_score == 0
        assert l.has_website is False
        assert l.opt_out is False
        assert l.lead_key == ""

    def test_lead_key_is_first_field_in_schema(self):
        assert SCHEMA[0] == "lead_key"
        assert SCHEMA[-1] == "next_callback_at"

    def test_row_matches_schema_length(self):
        l = Lead(business_name="Test Clinic", lead_key="ph:+911234567890")
        row = l.row()
        assert len(row) == len(SCHEMA), f"row has {len(row)} fields, schema has {len(SCHEMA)}"

    def test_row_contains_expected_values(self):
        l = Lead(business_name="Test Clinic", lead_key="ph:+911234567890", lead_score=85, lead_tier="HOT")
        row = l.row()
        idx_key = SCHEMA.index("lead_key")
        idx_name = SCHEMA.index("business_name")
        idx_score = SCHEMA.index("lead_score")
        assert row[idx_key] == "ph:+911234567890"
        assert row[idx_name] == "Test Clinic"
        assert row[idx_score] == 85


class TestLeadTypeCoercion:
    """__post_init__ should coerce types correctly."""

    def test_rating_float(self):
        l = Lead(rating="4.5")
        assert l.rating == 4.5
        assert isinstance(l.rating, float)

    def test_rating_none(self):
        l = Lead(rating=None)
        assert l.rating is None

    def test_rating_invalid(self):
        l = Lead(rating="N/A")
        assert l.rating is None

    def test_review_count_int(self):
        l = Lead(review_count="150")
        assert l.review_count == 150
        assert isinstance(l.review_count, int)

    def test_has_website_string_true(self):
        l = Lead(has_website="true")
        assert l.has_website is True

    def test_has_website_string_false(self):
        l = Lead(has_website="false")
        assert l.has_website is False

    def test_has_website_bool(self):
        l = Lead(has_website=True)
        assert l.has_website is True

    def test_opt_out_string(self):
        l = Lead(opt_out="1")
        assert l.opt_out is True

    def test_lead_score_from_string(self):
        l = Lead(lead_score="75")
        assert l.lead_score == 75
        assert isinstance(l.lead_score, int)

    def test_latitude_from_string(self):
        l = Lead(latitude="28.6139")
        assert l.latitude == 28.6139

    def test_longitude_none(self):
        l = Lead(longitude=None)
        assert l.longitude is None


class TestLeadFinalizeDates:
    """finalize_dates should set stale_after based on stale_days."""

    def test_stale_after_set(self):
        l = Lead()
        l.finalize_dates(stale_days=30)
        assert l.stale_after != ""
        assert "T" in l.stale_after  # ISO format

    def test_data_fetched_at_auto(self):
        l = Lead()
        assert l.data_fetched_at != ""
        assert "T" in l.data_fetched_at  # ISO format with timezone


class TestLeadToDict:
    """to_dict should return a serializable dict."""

    def test_to_dict_has_all_fields(self):
        l = Lead(business_name="Test", lead_key="k1")
        d = l.to_dict()
        for key in SCHEMA:
            assert key in d, f"Missing key: {key}"

    def test_to_dict_types(self):
        l = Lead(rating=4.5, review_count=100, lead_score=85)
        d = l.to_dict()
        assert d["rating"] == 4.5
        assert d["review_count"] == 100
        assert d["lead_score"] == 85