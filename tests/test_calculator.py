"""Unit tests for the metrics calculator."""

import pytest
from lynx_realestate.models import (
    CompanyStage, CompanyTier, FinancialStatement,
    GrowthMetrics, ProfitabilityMetrics, ShareStructure, SolvencyMetrics,
)
from lynx_realestate.metrics.calculator import (
    calc_valuation, calc_profitability, calc_solvency, calc_growth,
    calc_efficiency, calc_share_structure, calc_real_estate_quality,
    calc_intrinsic_value,
)


@pytest.fixture
def sample_info():
    return {
        "currentPrice": 50.0, "marketCap": 5_000_000_000,
        "sharesOutstanding": 100_000_000, "totalCash": 100_000_000,
        "totalDebt": 2_000_000_000, "priceToBook": 1.5,
        "trailingPE": 40.0, "enterpriseValue": 7_000_000_000,
        "enterpriseToEbitda": 18.0, "returnOnEquity": 0.06,
        "grossMargins": 0.70, "profitMargins": 0.16,
        "currentRatio": 1.2, "debtToEquity": 100.0,
        "heldPercentInsiders": 0.12,
        "heldPercentInstitutions": 0.80,
        "floatShares": 85_000_000,
        "occupancyRate": 0.96,
        "dividendYield": 0.05,
    }


@pytest.fixture
def sample_statements():
    # Two periods of a stabilized REIT. D&A = ebitda - operating_income = 100M.
    return [
        FinancialStatement(
            period="2025", revenue=500_000_000, net_income=80_000_000,
            operating_income=200_000_000, ebitda=300_000_000,
            total_assets=8_000_000_000, total_equity=3_500_000_000,
            total_cash=100_000_000, total_liabilities=4_500_000_000,
            total_debt=2_000_000_000, current_assets=250_000_000,
            current_liabilities=200_000_000, operating_cash_flow=180_000_000,
            free_cash_flow=100_000_000, capital_expenditure=-80_000_000,
            dividends_paid=-150_000_000, shares_outstanding=100_000_000,
            eps=0.80, book_value_per_share=35.0, interest_expense=60_000_000,
            rental_income=500_000_000, property_operating_expenses=200_000_000,
            accumulated_depreciation=1_000_000_000,
            real_estate_assets=6_500_000_000,
        ),
        FinancialStatement(
            period="2024", revenue=460_000_000, net_income=70_000_000,
            operating_income=180_000_000, ebitda=270_000_000,
            total_assets=7_500_000_000, total_equity=3_300_000_000,
            total_cash=90_000_000, total_liabilities=4_200_000_000,
            total_debt=1_900_000_000, operating_cash_flow=170_000_000,
            free_cash_flow=95_000_000, capital_expenditure=-75_000_000,
            dividends_paid=-140_000_000, shares_outstanding=98_000_000,
            rental_income=460_000_000, property_operating_expenses=190_000_000,
            accumulated_depreciation=900_000_000,
        ),
    ]


class TestCalcValuation:
    def test_basic_valuation(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert v.pe_trailing == 40.0
        assert v.pb_ratio == 1.5
        assert v.market_cap == 5_000_000_000

    def test_cash_to_market_cap(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert v.cash_to_market_cap == pytest.approx(0.02, abs=0.01)

    def test_p_ffo_populated(self, sample_info, sample_statements):
        """P/FFO = market_cap / (net_income + depreciation) for a stabilized REIT."""
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert v.p_ffo is not None
        # FFO ~= 80M + 100M = 180M => P/FFO ~= 5e9 / 180e6 ~= 27.8
        assert 20 < v.p_ffo < 35

    def test_p_affo_populated(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert v.p_affo is not None
        assert v.p_affo > 0

    def test_ffo_yield_populated(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert v.ffo_yield is not None
        # FFO yield in a sensible range
        assert 0.01 < v.ffo_yield < 0.20

    def test_implied_cap_rate(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # NOI / EV: (500M - 200M) / 7B = ~0.043
        assert v.implied_cap_rate is not None
        assert 0.01 < v.implied_cap_rate < 0.15

    def test_p_nav_populated(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert v.p_nav is not None
        assert v.p_nav > 0
        assert v.nav_per_share is not None

    def test_empty_info(self):
        v = calc_valuation({}, [], CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert v.pe_trailing is None
        assert v.cash_to_market_cap is None
        assert v.p_ffo is None


class TestCalcProfitability:
    def test_noi_computed(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # NOI = rental_income - property_operating_expenses = 500M - 200M = 300M
        assert p.noi == pytest.approx(300_000_000, rel=0.01)

    def test_noi_margin(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert p.noi_margin is not None
        assert 0.3 < p.noi_margin < 0.9

    def test_ffo_computed(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # FFO ~= net_income + D&A = 80M + 100M = 180M
        assert p.ffo is not None
        assert p.ffo == pytest.approx(180_000_000, rel=0.05)

    def test_affo_computed(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # AFFO ~= FFO - 0.5*|capex| = 180M - 40M = 140M
        assert p.affo is not None
        assert p.affo < p.ffo  # must be lower than FFO
        assert p.affo == pytest.approx(140_000_000, rel=0.15)

    def test_ffo_per_share_and_affo_per_share(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert p.ffo_per_share is not None
        assert p.affo_per_share is not None
        assert p.ffo_per_share > p.affo_per_share

    def test_ffo_margin(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert p.ffo_margin is not None
        assert 0 < p.ffo_margin < 1

    def test_occupancy_from_info(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert p.occupancy_rate == 0.96

    def test_same_store_noi_growth(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # rental_income went from 460M -> 500M => ~8.7%
        assert p.same_store_noi_growth is not None
        assert p.same_store_noi_growth > 0

    def test_implied_cap_rate(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert p.implied_cap_rate is not None
        assert p.implied_cap_rate > 0


class TestCalcSolvency:
    def test_debt_to_gross_assets(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # gross = total_assets + accumulated_depreciation = 8B + 1B = 9B
        # debt/gross = 2B / 9B = ~0.22
        assert s.debt_to_gross_assets is not None
        assert 0.15 < s.debt_to_gross_assets < 0.30

    def test_fixed_charge_coverage(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # op_income / interest_expense = 200M / 60M = ~3.3
        assert s.fixed_charge_coverage is not None
        assert s.fixed_charge_coverage > 0

    def test_debt_to_ebitda(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # debt/ebitda = 2B / 300M = ~6.7
        assert s.debt_to_ebitda is not None
        assert 4 < s.debt_to_ebitda < 10

    def test_cash_positive_stabilized(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # Positive operating cash flow => no burn
        assert s.cash_burn_rate == 0

    def test_ncav_calculated(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # NCAV = current_assets - total_liabilities = 250M - 4.5B = negative
        assert s.ncav is not None
        assert s.ncav == 250_000_000 - 4_500_000_000


class TestCalcGrowth:
    def test_revenue_growth(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.revenue_growth_yoy is not None
        # 500M / 460M - 1 ~= 0.087
        assert g.revenue_growth_yoy == pytest.approx(0.087, abs=0.01)

    def test_ffo_growth_yoy(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.ffo_growth_yoy is not None
        # FFO current: 80+100=180M; prev: 70+90=160M => ~12.5%
        assert g.ffo_growth_yoy > 0

    def test_affo_growth_yoy(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.affo_growth_yoy is not None

    def test_same_store_noi_growth_yoy(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.same_store_noi_growth_yoy is not None
        assert g.same_store_noi_growth_yoy > 0

    def test_affo_payout_ratio(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.affo_payout_ratio is not None
        # distributions 150M vs AFFO ~140M => >1.0
        assert g.affo_payout_ratio > 0

    def test_ffo_payout_ratio(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.ffo_payout_ratio is not None
        assert g.ffo_payout_ratio > 0
        # FFO payout should be lower than AFFO payout
        if g.affo_payout_ratio:
            assert g.ffo_payout_ratio <= g.affo_payout_ratio

    def test_share_dilution(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert g.shares_growth_yoy is not None
        # 100M vs 98M ~ 2% dilution
        assert g.shares_growth_yoy > 0

    def test_empty_statements(self):
        g = calc_growth([], CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert g.revenue_growth_yoy is None

    def test_single_statement(self):
        g = calc_growth([FinancialStatement(period="2025")], CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert g.revenue_growth_yoy is None


class TestCalcShareStructure:
    def test_share_assessment(self, sample_info, sample_statements):
        g = GrowthMetrics()
        ss = calc_share_structure(sample_info, sample_statements, g, CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert ss.shares_outstanding == 100_000_000
        assert ss.insider_ownership_pct == 0.12
        assert ss.share_structure_assessment is not None
        assert "Tight" in ss.share_structure_assessment

    def test_bloated_structure(self):
        info = {"sharesOutstanding": 600_000_000, "impliedSharesOutstanding": 700_000_000}
        ss = calc_share_structure(info, [], GrowthMetrics(), CompanyTier.MICRO, CompanyStage.DEVELOPMENT)
        assert "Bloated" in ss.share_structure_assessment


class TestCalcRealEstateQuality:
    def test_quality_score_range(self, sample_info, sample_statements):
        g = GrowthMetrics(shares_growth_yoy=0.02, same_store_noi_growth_yoy=0.04)
        s = SolvencyMetrics(debt_to_ebitda=6.0, tangible_book_value=3_500_000_000)
        ss = ShareStructure(insider_ownership_pct=0.12, share_structure_assessment="Tight (80-150M shares)")
        p = ProfitabilityMetrics(
            noi=300_000_000, noi_margin=0.60, occupancy_rate=0.96,
            implied_cap_rate=0.055,
        )
        m = calc_real_estate_quality(p, g, s, ss, sample_statements, sample_info,
                                     CompanyTier.LARGE, CompanyStage.STABILIZED)
        assert m.quality_score is not None
        assert 0 <= m.quality_score <= 100
        assert m.competitive_position is not None
        # REIT-specific fields should be populated
        assert m.portfolio_quality is not None
        assert m.occupancy_assessment is not None
        assert m.same_store_noi_trend is not None
        assert m.cap_rate_assessment is not None

    def test_empty_inputs(self):
        m = calc_real_estate_quality(
            ProfitabilityMetrics(), GrowthMetrics(), SolvencyMetrics(),
            ShareStructure(), [], {}, CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT,
        )
        assert m.quality_score is not None

    def test_occupancy_assessment_high(self, sample_info, sample_statements):
        p = ProfitabilityMetrics(noi_margin=0.65, occupancy_rate=0.97)
        m = calc_real_estate_quality(
            p, GrowthMetrics(), SolvencyMetrics(), ShareStructure(),
            sample_statements, sample_info, CompanyTier.LARGE, CompanyStage.STABILIZED,
        )
        assert m.occupancy_assessment is not None
        assert "High" in m.occupancy_assessment or ">95" in m.occupancy_assessment


class TestCalcIntrinsicValue:
    def test_method_selection_stabilized(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.STABILIZED,
        )
        primary = iv.primary_method or ""
        assert any(k in primary for k in ["FFO", "NAV", "DCF"])

    def test_method_selection_net_lease(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.NET_LEASE,
        )
        primary = iv.primary_method or ""
        assert any(k in primary for k in ["FFO", "NAV", "DCF"])

    def test_method_selection_pre_development(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT,
        )
        assert iv.primary_method is not None

    def test_ffo_multiple_value_populated(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.STABILIZED,
        )
        assert iv.ffo_multiple_value is not None
        assert iv.ffo_multiple_value > 0

    def test_affo_multiple_value_populated(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.STABILIZED,
        )
        assert iv.affo_multiple_value is not None
        assert iv.affo_multiple_value > 0

    def test_nav_per_share_populated(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.STABILIZED,
        )
        assert iv.nav_per_share is not None
        assert iv.nav_per_share > 0

    def test_margin_of_safety_ffo(self, sample_info, sample_statements):
        iv = calc_intrinsic_value(
            sample_info, sample_statements, GrowthMetrics(),
            SolvencyMetrics(), CompanyTier.LARGE, CompanyStage.STABILIZED,
        )
        # margin_of_safety_ffo should be set if we have ffo_multiple_value and current_price
        if iv.ffo_multiple_value and iv.current_price:
            assert iv.margin_of_safety_ffo is not None


class TestGenericMetrics:
    """Smoke tests for metrics shared with non-REIT agents."""

    def test_fcf_yield_calculated(self, sample_info, sample_statements):
        v = calc_valuation(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        if v.fcf_yield is not None:
            assert -1 < v.fcf_yield < 1

    def test_croci_calculated(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        if p.croci is not None:
            assert isinstance(p.croci, float)

    def test_ocf_to_net_income(self, sample_info, sample_statements):
        p = calc_profitability(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        if p.ocf_to_net_income is not None:
            assert isinstance(p.ocf_to_net_income, float)

    def test_debt_per_share(self, sample_info, sample_statements):
        s = calc_solvency(sample_info, sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        if s.debt_per_share is not None:
            assert s.debt_per_share >= 0

    def test_capex_to_revenue(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        if g.capex_to_revenue is not None:
            assert 0 <= g.capex_to_revenue <= 2

    def test_fcf_per_share(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        if g.fcf_per_share is not None:
            assert isinstance(g.fcf_per_share, float)

    def test_dividend_coverage(self, sample_statements):
        g = calc_growth(sample_statements, CompanyTier.LARGE, CompanyStage.STABILIZED)
        # dividend_coverage may be None if no dividends paid
        assert g.dividend_coverage is None or g.dividend_coverage > 0
