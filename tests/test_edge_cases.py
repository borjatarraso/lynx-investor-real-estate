"""Edge case and input validation tests."""

import math
import pytest

from lynx_realestate.models import (
    AnalysisReport, CompanyProfile, CompanyStage, CompanyTier,
    ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics, GrowthMetrics,
    RealEstateQualityIndicators, ShareStructure, MarketIntelligence,
    FinancialStatement, InsiderTransaction,
)
from lynx_realestate.core.conclusion import generate_conclusion
from lynx_realestate.core.storage import _sanitize_ticker, set_mode, get_company_dir
from lynx_realestate.core.ticker import is_isin
from lynx_realestate.metrics.calculator import (
    calc_valuation, calc_profitability, calc_solvency, calc_growth,
    calc_share_structure, calc_real_estate_quality, calc_intrinsic_value,
)
from lynx_realestate.export import export_report, ExportFormat
from pathlib import Path
import tempfile


class TestSanitizeTicker:
    def test_normal_ticker(self):
        assert _sanitize_ticker("AAPL") == "AAPL"

    def test_dot_suffix(self):
        assert _sanitize_ticker("OCO.V") == "OCO.V"

    def test_path_traversal(self):
        assert ".." not in _sanitize_ticker("../../../etc")

    def test_special_chars_removed(self):
        result = _sanitize_ticker("<script>alert(1)</script>")
        assert "<" not in result
        assert ">" not in result

    def test_empty_string(self):
        assert _sanitize_ticker("") == "UNKNOWN"

    def test_only_dots(self):
        result = _sanitize_ticker("...")
        assert ".." not in result

    def test_spaces_stripped(self):
        assert _sanitize_ticker("  AAPL  ") == "AAPL"

    def test_lowercase_uppercased(self):
        assert _sanitize_ticker("aapl") == "AAPL"


class TestIsISIN:
    def test_valid_isin(self):
        assert is_isin("US0378331005") is True

    def test_ticker_not_isin(self):
        assert is_isin("AAPL") is False

    def test_empty_not_isin(self):
        assert is_isin("") is False

    def test_short_not_isin(self):
        assert is_isin("US") is False


class TestNanInfHandling:
    """Ensure NaN and Inf values don't crash any display or calculation."""

    def test_valuation_with_nan(self):
        v = calc_valuation(
            {"trailingPE": float("nan"), "marketCap": float("inf")},
            [], CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT,
        )
        assert v is not None

    def test_solvency_with_nan(self):
        stmts = [FinancialStatement(period="2025", operating_cash_flow=float("nan"),
                                     total_assets=float("inf"))]
        s = calc_solvency({"marketCap": 100}, stmts, CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert s is not None

    def test_profitability_with_nan(self):
        stmts = [FinancialStatement(
            period="2025", revenue=float("nan"),
            rental_income=float("nan"), property_operating_expenses=float("nan"),
        )]
        p = calc_profitability({}, stmts, CompanyTier.NANO, CompanyStage.STABILIZED)
        assert p is not None

    def test_conclusion_with_nan_metrics(self):
        r = AnalysisReport(
            profile=CompanyProfile(ticker="NAN", name="NaN Corp"),
            valuation=ValuationMetrics(pe_trailing=float("nan"), p_ffo=float("inf")),
            solvency=SolvencyMetrics(cash_runway_years=float("inf")),
            profitability=ProfitabilityMetrics(ffo=float("nan"), noi_margin=float("nan")),
        )
        c = generate_conclusion(r)
        assert c.verdict in ["Strong Buy", "Buy", "Hold", "Caution", "Avoid"]
        assert not math.isnan(c.overall_score)

    def test_export_with_nan(self):
        r = AnalysisReport(
            profile=CompanyProfile(ticker="NAN", name="NaN Corp"),
            valuation=ValuationMetrics(
                pe_trailing=float("nan"), pb_ratio=float("inf"),
                p_ffo=float("nan"), p_affo=float("inf"),
            ),
        )
        for fmt in [ExportFormat.TXT, ExportFormat.HTML]:
            with tempfile.NamedTemporaryFile(suffix=f".{fmt.value}", delete=False) as f:
                path = export_report(r, fmt, Path(f.name))
                content = path.read_text()
                assert len(content) > 0


class TestZeroDivision:
    def test_zero_shares(self):
        stmts = [
            FinancialStatement(period="2025", shares_outstanding=0, revenue=100),
            FinancialStatement(period="2024", shares_outstanding=0, revenue=50),
        ]
        g = calc_growth(stmts, CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert g is not None

    def test_zero_market_cap(self):
        v = calc_valuation({"marketCap": 0, "totalCash": 100}, [], CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert v.cash_to_market_cap is None or v.cash_to_market_cap == 0

    def test_zero_total_assets(self):
        stmts = [FinancialStatement(period="2025", total_assets=0, revenue=0)]
        s = calc_solvency({"marketCap": 100}, stmts, CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert s is not None

    def test_zero_rental_income(self):
        stmts = [FinancialStatement(
            period="2025", rental_income=0, property_operating_expenses=0,
            revenue=0,
        )]
        p = calc_profitability({}, stmts, CompanyTier.NANO, CompanyStage.STABILIZED)
        assert p is not None


class TestHTMLExportSecurity:
    def test_html_escaping(self):
        r = AnalysisReport(
            profile=CompanyProfile(
                ticker="XSS", name='<script>alert("xss")</script>',
                sector='Test & "Quotes"',
            ),
        )
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = export_report(r, ExportFormat.HTML, Path(f.name))
            content = path.read_text()
            assert "<script>" not in content
            assert "&lt;" in content or "alert" not in content

    def test_white_background(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="T", name="T"))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = export_report(r, ExportFormat.HTML, Path(f.name))
            content = path.read_text()
            assert "#fff" in content or "#ffffff" in content
            assert "word-wrap" in content


class TestEmptyReportDisplay:
    def test_empty_report_conclusion(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="MT", name="MT"))
        c = generate_conclusion(r)
        assert c.verdict != ""
        assert c.summary != ""

    def test_empty_market_intelligence(self):
        r = AnalysisReport(
            profile=CompanyProfile(ticker="MI", name="MI"),
            market_intelligence=MarketIntelligence(),
        )
        c = generate_conclusion(r)
        assert c is not None


class TestCalcEdgeCases:
    def test_growth_single_statement(self):
        g = calc_growth([FinancialStatement(period="2025")], CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert g.revenue_growth_yoy is None

    def test_share_structure_no_info(self):
        ss = calc_share_structure({}, [], GrowthMetrics(), CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert ss.share_structure_assessment is None

    def test_intrinsic_value_no_statements(self):
        iv = calc_intrinsic_value({}, [], GrowthMetrics(), SolvencyMetrics(),
                                  CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT)
        assert iv.primary_method is not None

    def test_real_estate_quality_empty(self):
        q = calc_real_estate_quality(
            ProfitabilityMetrics(), GrowthMetrics(), SolvencyMetrics(),
            ShareStructure(), [], {}, CompanyTier.NANO, CompanyStage.PRE_DEVELOPMENT,
        )
        assert q.quality_score is not None
