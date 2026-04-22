"""Unit tests for metric explanations."""

import pytest
from lynx_realestate.metrics.explanations import (
    get_explanation, list_metrics, get_section_explanation,
    get_conclusion_explanation, SECTION_EXPLANATIONS, CONCLUSION_METHODOLOGY,
)


class TestGetExplanation:
    def test_known_metric(self):
        e = get_explanation("cash_to_market_cap")
        assert e is not None
        assert e.full_name == "Cash-to-Market-Cap Ratio"
        assert e.category == "valuation"

    def test_unknown_metric(self):
        assert get_explanation("nonexistent") is None

    def test_all_metrics_have_required_fields(self):
        for m in list_metrics():
            assert m.key != ""
            assert m.full_name != ""
            assert m.description != ""
            assert m.formula != ""
            assert m.category != ""

    def test_reit_specific_valuation_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "p_ffo" in keys
        assert "p_affo" in keys
        assert "p_nav" in keys
        assert "implied_cap_rate" in keys
        assert "ffo_yield" in keys
        assert "nav_per_share" in keys

    def test_reit_specific_profitability_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "noi" in keys
        assert "noi_margin" in keys
        assert "ffo" in keys
        assert "ffo_per_share" in keys
        assert "affo" in keys
        assert "affo_per_share" in keys
        assert "ffo_margin" in keys
        assert "occupancy_rate" in keys
        assert "same_store_noi_growth" in keys

    def test_reit_specific_growth_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "ffo_growth_yoy" in keys
        assert "affo_growth_yoy" in keys
        assert "ffo_cagr_3y" in keys
        assert "same_store_noi_growth_yoy" in keys
        assert "acquisition_growth_yoy" in keys
        assert "affo_payout_ratio" in keys
        assert "ffo_payout_ratio" in keys
        assert "distribution_growth_5y" in keys

    def test_reit_specific_solvency_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "debt_to_gross_assets" in keys
        assert "fixed_charge_coverage" in keys
        assert "weighted_avg_debt_maturity" in keys
        assert "pct_fixed_rate_debt" in keys

    def test_reit_specific_quality_metrics_exist(self):
        keys = [m.key for m in list_metrics()]
        assert "portfolio_quality" in keys
        assert "portfolio_diversification" in keys
        assert "occupancy_assessment" in keys
        assert "lease_duration_assessment" in keys
        assert "tenant_concentration" in keys
        assert "same_store_noi_trend" in keys
        assert "cap_rate_assessment" in keys

    def test_common_metrics_still_present(self):
        keys = [m.key for m in list_metrics()]
        assert "cash_to_market_cap" in keys
        assert "quality_score" in keys
        assert "shares_growth_yoy" in keys

    def test_list_by_category(self):
        valuation = list_metrics("valuation")
        assert len(valuation) > 0
        assert all(m.category == "valuation" for m in valuation)


class TestSectionExplanations:
    def test_all_sections_have_title(self):
        for key, sec in SECTION_EXPLANATIONS.items():
            assert "title" in sec
            assert "description" in sec

    def test_real_estate_quality_section_exists(self):
        sec = get_section_explanation("real_estate_quality")
        assert sec is not None
        assert "Real Estate" in sec["title"] or "REIT" in sec["title"]

    def test_share_structure_section_exists(self):
        sec = get_section_explanation("share_structure")
        assert sec is not None

    def test_valuation_section_mentions_reit_metrics(self):
        sec = get_section_explanation("valuation")
        assert sec is not None
        desc = sec["description"].lower()
        assert any(kw in desc for kw in ["ffo", "affo", "nav", "cap rate"])

    def test_unknown_section(self):
        assert get_section_explanation("nonexistent") is None


class TestConclusionMethodology:
    def test_overall_exists(self):
        ce = get_conclusion_explanation("overall")
        assert ce is not None
        # Description should mention real estate or REIT concepts
        desc = ce["description"].lower()
        assert any(kw in desc for kw in [
            "real estate", "real-estate", "reit", "ffo", "nav",
        ])

    def test_real_estate_quality_category(self):
        ce = get_conclusion_explanation("real_estate_quality")
        assert ce is not None

    def test_unknown_category(self):
        assert get_conclusion_explanation("nonexistent") is None
