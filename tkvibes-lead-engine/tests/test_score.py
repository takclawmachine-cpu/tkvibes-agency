"""
TKVibes — Lead Scoring Tests
"""
import pytest
from src.models import Lead
from src.score import score_lead


def make_lead(website_quality="none", phone_primary="", whatsapp="", email="",
              review_count=0, rating=None, years_in_business="", category="",
              lead_key="test:1"):
    return Lead(
        lead_key=lead_key,
        business_name="Test Business",
        category=category,
        phone_primary=phone_primary,
        whatsapp=whatsapp,
        email=email,
        review_count=review_count,
        rating=rating,
        years_in_business=years_in_business,
        website_quality=website_quality,
    )


class TestScoreBaseline:
    def test_no_website_adds_45(self):
        l = make_lead(website_quality="none")
        score_lead(l, high_fit=[])
        assert l.lead_score >= 45

    def test_social_only_adds_40(self):
        l = make_lead(website_quality="social_only")
        score_lead(l, high_fit=[])
        assert l.lead_score == 40

    def test_weak_adds_20(self):
        l = make_lead(website_quality="weak")
        score_lead(l, high_fit=[])
        assert l.lead_score == 20

    def test_ok_adds_0(self):
        l = make_lead(website_quality="ok")
        score_lead(l, high_fit=[])
        assert l.lead_score == 0


class TestScoreModifiers:
    def test_phone_adds_15(self):
        l = make_lead(website_quality="none", phone_primary="+911234567890")
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 15

    def test_whatsapp_adds_5(self):
        l = make_lead(website_quality="none", whatsapp="+919999999999")
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 5

    def test_email_adds_5(self):
        l = make_lead(website_quality="none", email="test@example.com")
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 5

    def test_review_count_10plus(self):
        l = make_lead(website_quality="none", review_count=15)
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 10

    def test_review_count_3plus(self):
        l = make_lead(website_quality="none", review_count=5)
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 5

    def test_review_count_under_3(self):
        l = make_lead(website_quality="none", review_count=2)
        score_lead(l, high_fit=[])
        assert l.lead_score == 45  # no review bonus

    def test_high_rating_adds_5(self):
        l = make_lead(website_quality="none", rating=4.5)
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 5

    def test_low_rating_no_bonus(self):
        l = make_lead(website_quality="none", rating=2.0)
        score_lead(l, high_fit=[])
        assert l.lead_score == 45

    def test_years_in_business_adds_5(self):
        l = make_lead(website_quality="none", years_in_business="10 years")
        score_lead(l, high_fit=[])
        assert l.lead_score == 45 + 5

    def test_high_fit_category_adds_10(self):
        l = make_lead(website_quality="none", category="dental clinic")
        score_lead(l, high_fit=["dental clinic", "dentist"])
        assert l.lead_score == 45 + 10

    def test_non_high_fit_category_no_bonus(self):
        l = make_lead(website_quality="none", category="restaurant")
        score_lead(l, high_fit=["dental clinic"])
        assert l.lead_score == 45


class TestScoreTier:
    def test_hot_threshold(self):
        l = make_lead(website_quality="none", phone_primary="+911234567890",
                      whatsapp="+919999999999", email="t@e.com",
                      review_count=20, rating=4.5, years_in_business="5 years")
        score_lead(l, high_fit=[])
        assert l.lead_tier == "HOT"
        assert l.lead_score >= 70

    def test_warm_at_45(self):
        l = make_lead(website_quality="none")
        score_lead(l, high_fit=[])
        assert l.lead_tier == "WARM"  # 45 is WARM threshold

    def test_cold_below_45(self):
        l = make_lead(website_quality="ok")
        score_lead(l, high_fit=[])
        assert l.lead_tier == "COLD"

    def test_score_capped_at_100(self):
        l = make_lead(website_quality="none", phone_primary="+911234567890",
                      whatsapp="+919999999999", email="t@e.com",
                      review_count=999, rating=5.0, years_in_business="20 years",
                      category="dental")
        score_lead(l, high_fit=["dental"])
        assert l.lead_score <= 100


class TestScoreEdgeCases:
    def test_none_website_quality(self):
        l = make_lead()
        l.website_quality = None
        score_lead(l, high_fit=[])
        assert l.lead_score == 0

    def test_high_fit_is_none(self):
        l = make_lead(category="dental")
        score_lead(l, high_fit=None)
        assert l.lead_score == 45

    def test_rating_is_none(self):
        l = make_lead(rating=None)
        score_lead(l, high_fit=[])
        assert l.lead_score == 45