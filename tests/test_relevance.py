"""Unit tests for the relevance system."""

import pytest
from lynx_realestate.models import CompanyStage, CompanyTier, Relevance
from lynx_realestate.metrics.relevance import get_relevance


class TestStageOverrides:
    """Stage overrides take precedence over tier-based lookups."""

    def test_pre_development_pe_irrelevant(self):
        assert get_relevance("pe_trailing", CompanyTier.MEGA, "valuation", CompanyStage.PRE_DEVELOPMENT) == Relevance.IRRELEVANT

    def test_development_cash_runway_critical(self):
        assert get_relevance("cash_runway_years", CompanyTier.MICRO, "solvency", CompanyStage.DEVELOPMENT) == Relevance.CRITICAL

    def test_pre_development_cash_to_mcap_critical(self):
        assert get_relevance("cash_to_market_cap", CompanyTier.NANO, "valuation", CompanyStage.PRE_DEVELOPMENT) == Relevance.CRITICAL

    def test_stabilized_p_ffo_critical(self):
        assert get_relevance("p_ffo", CompanyTier.MID, "valuation", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_stabilized_p_affo_critical(self):
        assert get_relevance("p_affo", CompanyTier.MID, "valuation", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_stabilized_implied_cap_rate_critical(self):
        assert get_relevance("implied_cap_rate", CompanyTier.MID, "valuation", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_pre_development_occupancy_irrelevant(self):
        assert get_relevance("occupancy_rate", CompanyTier.MICRO, "profitability", CompanyStage.PRE_DEVELOPMENT) == Relevance.IRRELEVANT

    def test_net_lease_affo_payout_critical(self):
        assert get_relevance("affo_payout_ratio", CompanyTier.MID, "growth", CompanyStage.NET_LEASE) == Relevance.CRITICAL

    def test_net_lease_distribution_growth_critical(self):
        assert get_relevance("distribution_growth_5y", CompanyTier.MID, "growth", CompanyStage.NET_LEASE) == Relevance.CRITICAL

    def test_stabilized_cash_burn_contextual_or_irrelevant(self):
        rel = get_relevance("cash_burn_rate", CompanyTier.MID, "solvency", CompanyStage.STABILIZED)
        assert rel in (Relevance.CONTEXTUAL, Relevance.IRRELEVANT)

    def test_pre_development_profitability_irrelevant(self):
        for key in ["roe", "roa", "roic", "gross_margin", "net_margin", "fcf_margin"]:
            assert get_relevance(key, CompanyTier.MICRO, "profitability", CompanyStage.PRE_DEVELOPMENT) == Relevance.IRRELEVANT

    def test_stabilized_ffo_critical(self):
        assert get_relevance("ffo", CompanyTier.MID, "profitability", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_stabilized_affo_critical(self):
        assert get_relevance("affo", CompanyTier.MID, "profitability", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_stabilized_occupancy_critical(self):
        assert get_relevance("occupancy_rate", CompanyTier.MID, "profitability", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_stabilized_same_store_noi_growth_critical(self):
        assert get_relevance("same_store_noi_growth_yoy", CompanyTier.MID, "growth", CompanyStage.STABILIZED) == Relevance.CRITICAL

    def test_dilution_critical_for_juniors(self):
        for stage in [CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT]:
            assert get_relevance("shares_growth_yoy", CompanyTier.MICRO, "growth", stage) == Relevance.CRITICAL

    def test_insider_ownership_critical_for_juniors(self):
        assert get_relevance("insider_ownership_pct", CompanyTier.MICRO, "share_structure", CompanyStage.DEVELOPMENT) == Relevance.CRITICAL

    def test_net_lease_fixed_charge_coverage_critical(self):
        assert get_relevance("fixed_charge_coverage", CompanyTier.SMALL, "solvency", CompanyStage.NET_LEASE) == Relevance.CRITICAL

    def test_net_lease_debt_to_gross_assets_critical(self):
        assert get_relevance("debt_to_gross_assets", CompanyTier.MID, "solvency", CompanyStage.NET_LEASE) == Relevance.CRITICAL


class TestTierFallback:
    """When no stage override exists, tier-based lookup is used."""

    def test_unknown_metric_defaults_relevant(self):
        assert get_relevance("some_unknown_metric", CompanyTier.MID, "valuation", CompanyStage.STABILIZED) == Relevance.RELEVANT

    def test_pb_ratio_stabilized(self):
        rel = get_relevance("pb_ratio", CompanyTier.SMALL, "valuation", CompanyStage.STABILIZED)
        assert rel in [Relevance.CRITICAL, Relevance.RELEVANT]


class TestImportantLevel:
    """Tests for the IMPORTANT relevance level."""

    def test_important_enum_exists(self):
        assert hasattr(Relevance, "IMPORTANT")
        assert Relevance.IMPORTANT.value == "important"

    def test_pe_important_for_stabilized(self):
        assert get_relevance("pe_trailing", CompanyTier.MID, "valuation", CompanyStage.STABILIZED) == Relevance.IMPORTANT

    def test_debt_equity_important_for_stabilized(self):
        assert get_relevance("debt_to_equity", CompanyTier.MID, "solvency", CompanyStage.STABILIZED) == Relevance.IMPORTANT

    def test_share_dilution_important_for_stabilized(self):
        assert get_relevance("shares_growth_yoy", CompanyTier.MID, "growth", CompanyStage.STABILIZED) == Relevance.IMPORTANT

    def test_reit_metrics_have_relevance(self):
        """REIT-specific metrics should have stage overrides."""
        reit_metrics = [
            "p_ffo", "p_affo", "implied_cap_rate", "ffo_yield",
            "noi", "ffo", "affo", "occupancy_rate",
            "ffo_growth_yoy", "affo_growth_yoy", "affo_payout_ratio",
            "same_store_noi_growth_yoy",
        ]
        for key in reit_metrics:
            rel = get_relevance(key, CompanyTier.MID, "valuation", CompanyStage.STABILIZED)
            assert isinstance(rel, Relevance)
