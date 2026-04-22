"""Unit tests for the conclusion engine."""

import pytest
from lynx_realestate.models import (
    AnalysisReport, CompanyProfile, CompanyStage, CompanyTier,
    ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics, GrowthMetrics,
    RealEstateQualityIndicators, ShareStructure,
)
from lynx_realestate.core.conclusion import generate_conclusion, _WEIGHTS


@pytest.fixture
def minimal_report():
    return AnalysisReport(profile=CompanyProfile(ticker="TEST", name="Test Corp"))


@pytest.fixture
def stabilized_report():
    p = CompanyProfile(ticker="STAB", name="Stabilized REIT", market_cap=5_000_000_000)
    p.tier = CompanyTier.LARGE
    p.stage = CompanyStage.STABILIZED
    r = AnalysisReport(profile=p)
    r.valuation = ValuationMetrics(
        p_ffo=15.0, p_affo=18.0, p_nav=0.95, implied_cap_rate=0.06,
        ffo_yield=0.067, dividend_yield=0.045, pb_ratio=1.1,
    )
    r.profitability = ProfitabilityMetrics(
        noi=300_000_000, noi_margin=0.60, ffo=180_000_000, affo=140_000_000,
        ffo_margin=0.36, occupancy_rate=0.96,
        same_store_noi_growth=0.03,
    )
    r.solvency = SolvencyMetrics(
        debt_to_equity=1.0, debt_to_gross_assets=0.45,
        fixed_charge_coverage=3.0, weighted_avg_debt_maturity=6.5,
        pct_fixed_rate_debt=0.85, cash_runway_years=3.0,
    )
    r.growth = GrowthMetrics(
        ffo_growth_yoy=0.06, affo_growth_yoy=0.05,
        same_store_noi_growth_yoy=0.03, affo_payout_ratio=0.80,
        ffo_payout_ratio=0.70, distribution_growth_5y=0.04,
        shares_growth_yoy=0.02,
    )
    r.real_estate_quality = RealEstateQualityIndicators(
        quality_score=0.70, competitive_position="Strong Position — High Quality",
    )
    r.share_structure = ShareStructure(
        fully_diluted_shares=100_000_000, insider_ownership_pct=0.12,
    )
    return r


@pytest.fixture
def development_report():
    p = CompanyProfile(ticker="DEV", name="Development REIT", market_cap=100_000_000)
    p.tier = CompanyTier.MICRO
    p.stage = CompanyStage.DEVELOPMENT
    r = AnalysisReport(profile=p)
    r.valuation = ValuationMetrics(pb_ratio=0.8, cash_to_market_cap=0.4)
    r.solvency = SolvencyMetrics(
        cash_runway_years=3.5, current_ratio=4.0,
        debt_to_equity=0.1, cash_burn_rate=-5_000_000,
    )
    r.growth = GrowthMetrics(shares_growth_yoy=0.03)
    r.real_estate_quality = RealEstateQualityIndicators(
        quality_score=65.0,
        competitive_position="Viable Position — Moderate Quality",
    )
    r.share_structure = ShareStructure(
        fully_diluted_shares=80_000_000, insider_ownership_pct=0.15,
    )
    return r


class TestGenerateConclusion:
    def test_minimal_report_produces_verdict(self, minimal_report):
        c = generate_conclusion(minimal_report)
        assert c.verdict in ["Strong Buy", "Buy", "Hold", "Caution", "Avoid"]
        assert 0 <= c.overall_score <= 100
        assert c.summary != ""

    def test_verdict_thresholds(self, minimal_report):
        c = generate_conclusion(minimal_report)
        if c.overall_score >= 75:
            assert c.verdict == "Strong Buy"
        elif c.overall_score >= 60:
            assert c.verdict == "Buy"
        elif c.overall_score >= 45:
            assert c.verdict == "Hold"
        elif c.overall_score >= 30:
            assert c.verdict == "Caution"
        else:
            assert c.verdict == "Avoid"

    def test_stabilized_has_stage_note(self, stabilized_report):
        c = generate_conclusion(stabilized_report)
        assert c.stage_note != ""
        # Stage note should mention relevant REIT concepts
        assert any(kw in c.stage_note for kw in ["Stabilized", "P/FFO", "AFFO", "occupancy"])

    def test_development_has_stage_note(self, development_report):
        c = generate_conclusion(development_report)
        assert c.stage_note != ""
        assert "Development" in c.stage_note or "construction" in c.stage_note.lower()

    def test_category_scores_present(self, stabilized_report):
        c = generate_conclusion(stabilized_report)
        assert "valuation" in c.category_scores
        assert "profitability" in c.category_scores
        assert "solvency" in c.category_scores
        assert "growth" in c.category_scores
        assert "real_estate_quality" in c.category_scores

    def test_screening_checklist_present(self, stabilized_report):
        c = generate_conclusion(stabilized_report)
        assert isinstance(c.screening_checklist, dict)
        assert "insider_ownership" in c.screening_checklist

    def test_strengths_detected(self, stabilized_report):
        c = generate_conclusion(stabilized_report)
        assert len(c.strengths) >= 1

    def test_good_stabilized_scores_well(self, stabilized_report):
        c = generate_conclusion(stabilized_report)
        # With solid metrics this should be at least "Hold" (45+)
        assert c.overall_score >= 45

    def test_extreme_dilution_penalized_more(self):
        """>20% dilution should get -25 penalty, not just -15."""
        from lynx_realestate.core.conclusion import _score_growth
        r = AnalysisReport(
            profile=CompanyProfile(
                ticker="T", name="T", stage=CompanyStage.DEVELOPMENT, tier=CompanyTier.MICRO,
            ),
            growth=GrowthMetrics(shares_growth_yoy=0.25),  # 25% dilution
        )
        score = _score_growth(r)
        # Should be 50 - 25 = 25 (extreme penalty), not 50 - 15 = 35
        assert score == 25


class TestWeightsTable:
    """_WEIGHTS should exist for all (stage, tier) combos."""

    def test_all_stage_tier_combinations(self):
        for stage in CompanyStage:
            for tier in CompanyTier:
                assert (stage, tier) in _WEIGHTS, f"Missing weight for {stage}/{tier}"

    def test_weights_sum_to_one(self):
        for key, weights in _WEIGHTS.items():
            total = sum(weights)
            assert abs(total - 1.0) < 0.01, f"Weights don't sum to 1 for {key}: {total}"
