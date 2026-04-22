"""Tests for export functionality."""

import pytest
import tempfile
from pathlib import Path

from lynx_realestate.models import (
    AnalysisReport, CompanyProfile, CompanyTier, CompanyStage,
    ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics, GrowthMetrics,
    RealEstateQualityIndicators, ShareStructure, MarketIntelligence,
)
from lynx_realestate.export import export_report, ExportFormat


@pytest.fixture
def sample_report():
    p = CompanyProfile(
        ticker="TEST", name="Test Real Estate Corp",
        sector="Real Estate", industry="REIT—Residential",
        country="United States", market_cap=5_000_000_000,
    )
    p.tier = CompanyTier.LARGE
    p.stage = CompanyStage.STABILIZED
    r = AnalysisReport(
        profile=p,
        valuation=ValuationMetrics(
            pb_ratio=1.2, cash_to_market_cap=0.05, ev_ebitda=18.0,
            p_ffo=15.0, p_affo=18.0, p_nav=0.95,
            implied_cap_rate=0.06, ffo_yield=0.067, dividend_yield=0.045,
        ),
        profitability=ProfitabilityMetrics(
            noi=300_000_000, noi_margin=0.60,
            ffo=180_000_000, ffo_per_share=1.80, ffo_margin=0.36,
            affo=140_000_000, affo_per_share=1.40,
            occupancy_rate=0.96, same_store_noi_growth=0.03,
        ),
        solvency=SolvencyMetrics(
            debt_to_equity=1.0, debt_to_gross_assets=0.45,
            fixed_charge_coverage=3.0, weighted_avg_debt_maturity=6.5,
            total_cash=100_000_000, current_ratio=1.2,
        ),
        growth=GrowthMetrics(
            ffo_growth_yoy=0.06, affo_growth_yoy=0.05,
            same_store_noi_growth_yoy=0.03,
            affo_payout_ratio=0.80, ffo_payout_ratio=0.70,
            shares_growth_yoy=0.02,
        ),
        real_estate_quality=RealEstateQualityIndicators(
            quality_score=0.72,
            competitive_position="Strong Position — High Quality",
            portfolio_quality="Premium",
            occupancy_assessment="High stabilized occupancy (>95%)",
        ),
        share_structure=ShareStructure(
            shares_outstanding=100_000_000, insider_ownership_pct=0.12,
        ),
    )
    return r


class TestExportFormat:
    def test_accepts_enum(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(sample_report, ExportFormat.TXT, Path(f.name))
            assert p.exists()
            assert p.stat().st_size > 0

    def test_accepts_string(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(sample_report, "txt", Path(f.name))
            assert p.exists()

    def test_accepts_enum_constructed_from_string(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            p = export_report(sample_report, ExportFormat("html"), Path(f.name))
            assert p.exists()

    def test_invalid_format_raises(self, sample_report):
        with pytest.raises(ValueError):
            export_report(sample_report, "xyz")


class TestTxtExport:
    def test_contains_company_name(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(sample_report, "txt", Path(f.name))
            content = p.read_text()
            assert "Test Real Estate Corp" in content

    def test_contains_stage(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            assert "Stabilized" in content

    def test_no_truncation(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            assert len(content) > 500

    def test_contains_conclusion(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            assert "CONCLUSION" in content.upper()

    def test_contains_reit_terms(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            # Should contain at least some REIT-specific labels
            assert any(
                term in content for term in ["FFO", "AFFO", "NOI", "Occupancy", "Cap Rate", "cap rate"]
            )

    def test_no_energy_terms(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            content = export_report(sample_report, "txt", Path(f.name)).read_text()
            # Must not contain energy-sector specific labels
            assert "BOE" not in content
            assert "Netback" not in content
            assert "netback" not in content.lower() or "net back" not in content.lower()


class TestHtmlExport:
    def test_white_background(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "#fff" in content or "#ffffff" in content

    def test_word_wrap(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "word-wrap" in content or "overflow-wrap" in content

    def test_print_media(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "@media print" in content

    def test_xss_prevention(self):
        r = AnalysisReport(profile=CompanyProfile(
            ticker="XSS", name='<script>alert("xss")</script>'))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(r, "html", Path(f.name)).read_text()
            assert "<script>" not in content

    def test_contains_footer(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "Lince Investor Suite" in content

    def test_valid_html(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert content.startswith("<!DOCTYPE html>")
            assert "</html>" in content

    def test_contains_reit_terms(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert any(
                term in content for term in ["P/FFO", "FFO", "AFFO", "NOI", "Occupancy", "Real Estate"]
            )

    def test_no_energy_terms(self, sample_report):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            content = export_report(sample_report, "html", Path(f.name)).read_text()
            assert "BOE" not in content
            assert "Netback" not in content


class TestExportWithEmptyReport:
    def test_txt_empty(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="MT", name="MT"))
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            p = export_report(r, "txt", Path(f.name))
            assert p.exists()

    def test_html_empty(self):
        r = AnalysisReport(profile=CompanyProfile(ticker="MT", name="MT"))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            p = export_report(r, "html", Path(f.name))
            assert p.exists()
