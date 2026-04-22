"""Unit tests for data models and classification functions."""

import pytest
from lynx_realestate.models import (
    CompanyProfile, CompanyStage, CompanyTier, PropertyType,
    JurisdictionTier, Relevance, AnalysisReport,
    ValuationMetrics, SolvencyMetrics, GrowthMetrics,
    RealEstateQualityIndicators, ShareStructure, MarketIntelligence,
    FinancialStatement, AnalysisConclusion,
    classify_tier, classify_stage, classify_property_type, classify_jurisdiction,
)


class TestClassifyTier:
    def test_mega_cap(self):
        assert classify_tier(300_000_000_000) == CompanyTier.MEGA

    def test_large_cap(self):
        assert classify_tier(50_000_000_000) == CompanyTier.LARGE

    def test_mid_cap(self):
        assert classify_tier(5_000_000_000) == CompanyTier.MID

    def test_small_cap(self):
        assert classify_tier(1_000_000_000) == CompanyTier.SMALL

    def test_micro_cap(self):
        assert classify_tier(100_000_000) == CompanyTier.MICRO

    def test_nano_cap(self):
        assert classify_tier(10_000_000) == CompanyTier.NANO

    def test_none_returns_nano(self):
        assert classify_tier(None) == CompanyTier.NANO

    def test_zero_returns_nano(self):
        assert classify_tier(0) == CompanyTier.NANO

    def test_negative_returns_nano(self):
        assert classify_tier(-100) == CompanyTier.NANO


class TestClassifyStage:
    def test_stabilized_with_revenue(self):
        assert classify_stage("stabilized portfolio operating reit", 50_000_000) == CompanyStage.STABILIZED

    def test_lease_up(self):
        assert classify_stage("lease-up phase recently completed property", 0) == CompanyStage.LEASE_UP

    def test_development(self):
        assert classify_stage("under construction development pipeline", 0) == CompanyStage.DEVELOPMENT

    def test_pre_development(self):
        assert classify_stage("land banking site selection pre-development", 0) == CompanyStage.PRE_DEVELOPMENT

    def test_net_lease(self):
        assert classify_stage("triple net lease single-tenant portfolio", 20_000_000) == CompanyStage.NET_LEASE

    def test_revenue_without_keywords_defaults_stabilized(self):
        """Revenue-generating REIT with no stage keywords defaults to Stabilized."""
        assert classify_stage("generic real estate company", 50_000_000) == CompanyStage.STABILIZED

    def test_none_description(self):
        assert classify_stage(None, None) == CompanyStage.PRE_DEVELOPMENT

    def test_empty_description(self):
        assert classify_stage("", 0) == CompanyStage.PRE_DEVELOPMENT

    def test_industry_hint(self):
        assert classify_stage("company overview", 0, {"industry": "REIT—Residential"}) == CompanyStage.DEVELOPMENT


class TestClassifyPropertyType:
    def test_residential(self):
        assert classify_property_type("apartment multifamily residential", "Residential REITs") == PropertyType.RESIDENTIAL

    def test_office(self):
        assert classify_property_type("office tower commercial", "Office REITs") == PropertyType.OFFICE

    def test_retail(self):
        assert classify_property_type("shopping center mall outlet", "Retail REITs") == PropertyType.RETAIL

    def test_industrial(self):
        assert classify_property_type("warehouse logistics distribution", "Industrial REITs") == PropertyType.INDUSTRIAL

    def test_hotel(self):
        assert classify_property_type("hotel hospitality lodging resort", "Hotel REITs") == PropertyType.HOTEL

    def test_healthcare(self):
        assert classify_property_type("medical office senior housing healthcare", "Healthcare REITs") == PropertyType.HEALTHCARE

    def test_self_storage(self):
        assert classify_property_type("self-storage storage facility", None) == PropertyType.SELF_STORAGE

    def test_data_center(self):
        assert classify_property_type("data center colocation hyperscale", None) == PropertyType.DATA_CENTER

    def test_infrastructure(self):
        assert classify_property_type("cell tower communications infrastructure", None) == PropertyType.INFRASTRUCTURE

    def test_net_lease(self):
        assert classify_property_type("triple net single-tenant net-lease", None) == PropertyType.NET_LEASE

    def test_diversified(self):
        assert classify_property_type("diversified real estate portfolio", None) == PropertyType.DIVERSIFIED

    def test_other_when_no_match(self):
        assert classify_property_type("generic company", None) == PropertyType.OTHER

    def test_none_inputs(self):
        assert classify_property_type(None, None) == PropertyType.OTHER


class TestClassifyJurisdiction:
    def test_canada_tier1(self):
        assert classify_jurisdiction("Canada") == JurisdictionTier.TIER_1

    def test_us_tier1(self):
        assert classify_jurisdiction("United States") == JurisdictionTier.TIER_1

    def test_uk_tier1(self):
        assert classify_jurisdiction("United Kingdom") == JurisdictionTier.TIER_1

    def test_germany_tier1(self):
        assert classify_jurisdiction("Germany") == JurisdictionTier.TIER_1

    def test_france_tier1(self):
        assert classify_jurisdiction("France") == JurisdictionTier.TIER_1

    def test_japan_tier1(self):
        assert classify_jurisdiction("Japan") == JurisdictionTier.TIER_1

    def test_singapore_tier1(self):
        assert classify_jurisdiction("Singapore") == JurisdictionTier.TIER_1

    def test_mexico_tier2(self):
        assert classify_jurisdiction("Mexico") == JurisdictionTier.TIER_2

    def test_brazil_tier2(self):
        assert classify_jurisdiction("Brazil") == JurisdictionTier.TIER_2

    def test_south_africa_tier2(self):
        assert classify_jurisdiction("South Africa") == JurisdictionTier.TIER_2

    def test_uae_tier2(self):
        assert classify_jurisdiction("United Arab Emirates") == JurisdictionTier.TIER_2

    def test_unknown_tier3(self):
        assert classify_jurisdiction("SomeCountry") == JurisdictionTier.TIER_3

    def test_none_unknown(self):
        assert classify_jurisdiction(None) == JurisdictionTier.UNKNOWN


class TestDataModels:
    def test_analysis_report_defaults(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="TEST", name="Test"))
        assert r.valuation is None
        assert r.market_intelligence is None
        assert r.financials == []
        assert r.fetched_at != ""

    def test_company_profile_defaults(self):
        p = CompanyProfile(ticker="X", name="X Corp")
        assert p.tier == CompanyTier.NANO
        assert p.stage == CompanyStage.STABILIZED
        assert p.primary_property_type == PropertyType.OTHER
        assert p.jurisdiction_tier == JurisdictionTier.UNKNOWN

    def test_solvency_metrics_defaults(self):
        s = SolvencyMetrics()
        assert s.cash_runway_years is None
        assert s.burn_as_pct_of_market_cap is None
        # REIT-specific fields default to None
        assert s.debt_to_gross_assets is None
        assert s.fixed_charge_coverage is None
        assert s.weighted_avg_debt_maturity is None
        assert s.pct_fixed_rate_debt is None

    def test_market_intelligence_defaults(self):
        mi = MarketIntelligence()
        assert mi.insider_transactions == []
        assert mi.risk_warnings == []
        assert mi.disclaimers == []

    def test_real_estate_quality_defaults(self):
        q = RealEstateQualityIndicators()
        # REIT-specific fields default to None
        assert q.portfolio_quality is None
        assert q.portfolio_diversification is None
        assert q.occupancy_assessment is None
        assert q.lease_duration_assessment is None
        assert q.tenant_concentration is None
        assert q.same_store_noi_trend is None
        assert q.cap_rate_assessment is None

    def test_financial_statement_reit_fields(self):
        fs = FinancialStatement(period="2025")
        assert fs.real_estate_assets is None
        assert fs.accumulated_depreciation is None
        assert fs.rental_income is None
        assert fs.property_operating_expenses is None
