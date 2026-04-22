"""HTML export — full analysis report with Catppuccin Mocha theme."""

from __future__ import annotations

import math
from html import escape as esc
from pathlib import Path
from typing import Optional

from lynx_realestate.models import AnalysisReport, CompanyStage


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _safe(val, default=None):
    if val is None or isinstance(val, bool):
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def _fmt_num(val, decimals: int = 1, suffix: str = "") -> str:
    v = _safe(val)
    if v is None:
        return "N/A"
    abs_v = abs(v)
    if abs_v >= 1e9:
        return f"{v / 1e9:,.{decimals}f}B{suffix}"
    if abs_v >= 1e6:
        return f"{v / 1e6:,.{decimals}f}M{suffix}"
    if abs_v >= 1e3:
        return f"{v / 1e3:,.{decimals}f}K{suffix}"
    return f"{v:,.{decimals}f}{suffix}"


def _fmt_pct(val, decimals: int = 1) -> str:
    v = _safe(val)
    if v is None:
        return "N/A"
    return f"{v * 100:,.{decimals}f}%"


def _fmt_money(val, decimals: int = 2, currency: str = "$") -> str:
    v = _safe(val)
    if v is None:
        return "N/A"
    abs_v = abs(v)
    sign = "-" if v < 0 else ""
    if abs_v >= 1e9:
        return f"{sign}{currency}{abs_v / 1e9:,.{decimals}f}B"
    if abs_v >= 1e6:
        return f"{sign}{currency}{abs_v / 1e6:,.{decimals}f}M"
    if abs_v >= 1e3:
        return f"{sign}{currency}{abs_v / 1e3:,.{decimals}f}K"
    return f"{sign}{currency}{abs_v:,.{decimals}f}"


def _fmt_ratio(val, decimals: int = 2) -> str:
    v = _safe(val)
    if v is None:
        return "N/A"
    return f"{v:,.{decimals}f}"


def _fmt_bool(val) -> str:
    if val is None:
        return "N/A"
    return "Yes" if val else "No"


def _ga(obj, key, default=""):
    """Get attribute from dataclass or dict (handles deserialized data)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _tr(label: str, value: str) -> str:
    """Table row with label and value."""
    return f"<tr><td>{esc(label)}</td><td>{esc(value)}</td></tr>"


def _metric_rows(fields: list[tuple[str, str]]) -> str:
    """Generate table rows, skipping N/A values."""
    rows = []
    for label, val in fields:
        if val != "N/A":
            rows.append(_tr(label, val))
    return "\n".join(rows)


def _metric_table(fields: list[tuple[str, str]]) -> str:
    body = _metric_rows(fields)
    if not body:
        return '<p class="meta">No data available.</p>'
    return f"<table>\n<tr><th>Metric</th><th>Value</th></tr>\n{body}\n</table>"


# ---------------------------------------------------------------------------
# CSS — Catppuccin Mocha
# ---------------------------------------------------------------------------

CSS = """
@page { margin: 20mm; }
@media print {
  body { padding: 0; font-size: 9pt; }
  .card { break-inside: avoid; box-shadow: none; border: 1px solid #ddd; }
  .no-print { display: none; }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Consolas', 'Monaco', 'Menlo', 'Noto Sans Mono', monospace;
  max-width: 1100px; margin: 0 auto; padding: 24px 40px;
  background: #fff; color: #1a1a2e; line-height: 1.55;
  font-size: 14px;
}
h1 {
  color: #2c5282; font-size: 1.75em; font-weight: 700;
  margin-bottom: 2px; letter-spacing: -0.02em;
  border-bottom: 2px solid #cbd5e0; padding-bottom: 8px;
}
h2 {
  color: #2c5282; font-size: 1.05em; font-weight: 600;
  margin: 0 0 10px 0; padding-bottom: 5px;
  border-bottom: 1px solid #cbd5e0;
  text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.88em;
}
.subtitle {
  color: #5a6378; font-size: 0.92em; margin-bottom: 18px;
  font-style: italic;
}
.card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 6px;
  padding: 16px 20px; margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
table {
  width: 100%; border-collapse: collapse; margin-bottom: 6px;
  table-layout: fixed;
}
th, td {
  padding: 6px 10px; text-align: left;
  border-bottom: 1px solid #e5e7eb;
  word-wrap: break-word; overflow-wrap: break-word;
  font-size: 0.92em; vertical-align: top;
}
th {
  background: #f3f4f6; color: #374151; font-weight: 600;
  font-size: 0.82em; text-transform: uppercase; letter-spacing: 0.04em;
}
tr:nth-child(even) { background: #f9fafb; }
td:first-child { font-weight: 500; color: #374151; }
td:nth-child(2) { color: #111827; font-variant-numeric: tabular-nums; }
.verdict-card {
  text-align: center; padding: 18px; border-radius: 6px; margin: 16px 0;
  font-family: Georgia, serif; font-size: 1.35em; font-weight: 700;
  letter-spacing: 0.02em;
}
.verdict-strong-buy { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.verdict-buy { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.verdict-hold { background: #fffbeb; color: #78350f; border: 1px solid #fde68a; }
.verdict-caution { background: #fff7ed; color: #7c2d12; border: 1px solid #fed7aa; }
.verdict-avoid { background: #fef2f2; color: #7f1d1d; border: 1px solid #fecaca; }
.score-bg {
  background: #e5e7eb; width: 100px; display: inline-block; height: 10px;
  border-radius: 5px; position: relative; vertical-align: middle;
  overflow: hidden;
}
.score-fill {
  height: 10px; border-radius: 5px; position: absolute; left: 0; top: 0;
}
.s { color: #065f46; } .r { color: #7f1d1d; }
.pass { color: #065f46; font-weight: 600; }
.fail { color: #991b1b; font-weight: 600; }
.na { color: #9ca3af; }
.meta { color: #6b7280; font-size: 0.85em; }
.warn {
  color: #7f1d1d; background: #fef2f2; padding: 8px 14px;
  border-radius: 4px; border-left: 3px solid #dc2626;
  margin: 5px 0; font-size: 0.9em;
}
.disclaimer {
  color: #6b7280; font-size: 0.8em; font-style: italic;
  padding: 5px 14px; border-left: 2px solid #d1d5db; margin: 3px 0;
}
.cols { display: flex; gap: 16px; flex-wrap: wrap; }
.cols > div { flex: 1; min-width: 220px; }
ul { margin: 4px 0; padding-left: 18px; }
li { margin: 2px 0; font-size: 0.92em; }
a { color: #1a2744; text-decoration: underline; }
.footer {
  margin-top: 24px; padding-top: 12px; border-top: 1px solid #d1d5db;
  text-align: center; color: #9ca3af; font-size: 0.78em;
}
"""


# ---------------------------------------------------------------------------
# Main export
# ---------------------------------------------------------------------------

def export_html(report: AnalysisReport, output_path: Path) -> Path:
    from lynx_realestate.core.conclusion import generate_conclusion

    p = report.profile
    c = generate_conclusion(report)
    verdict_class = c.verdict.lower().replace(" ", "-")

    parts: list[str] = []

    # --- Document head ---
    parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lynx Report — {esc(p.name)} ({esc(p.ticker)})</title>
<style>{CSS}</style>
</head>
<body>
""")

    # --- Header ---
    def _ev(val):
        """Extract enum .value or return str."""
        return val.value if hasattr(val, "value") else str(val) if val else "N/A"

    parts.append(f"""<h1>{esc(p.name)} ({esc(p.ticker)})</h1>
<p class="meta">
Tier: {esc(_ev(p.tier))} &nbsp;|&nbsp;
Stage: {esc(_ev(p.stage))} &nbsp;|&nbsp;
Property Type: {esc(_ev(p.primary_property_type))} &nbsp;|&nbsp;
Jurisdiction: {esc(_ev(p.jurisdiction_tier))}
{(' &nbsp;|&nbsp; Jurisdiction Country: ' + esc(p.jurisdiction_country)) if p.jurisdiction_country else ''}
</p>
""")

    # --- Verdict Card ---
    parts.append(f"""<div class="verdict-card verdict-{verdict_class}">
{esc(c.verdict)} &mdash; {c.overall_score:.0f}/100
</div>
<div class="card"><p>{esc(c.summary)}</p></div>
""")

    # --- Company Profile ---
    parts.append('<div class="card"><h2>Company Profile</h2>')
    profile_fields = [
        ("Sector", p.sector or "N/A"),
        ("Industry", p.industry or "N/A"),
        ("Country", p.country or "N/A"),
        ("Exchange", p.exchange or "N/A"),
        ("Currency", p.currency or "N/A"),
        ("Market Cap", _fmt_money(p.market_cap)),
        ("Employees", f"{p.employees:,}" if p.employees else "N/A"),
        ("ISIN", p.isin or "N/A"),
    ]
    if p.website:
        profile_fields.append(("Website", p.website))
    parts.append(_metric_table(profile_fields))
    parts.append("</div>")

    # --- Valuation Metrics ---
    if report.valuation:
        v = report.valuation
        parts.append('<div class="card"><h2>Valuation Metrics</h2>')
        parts.append(_metric_table([
            ("P/E (Trailing)", _fmt_ratio(v.pe_trailing)),
            ("P/E (Forward)", _fmt_ratio(v.pe_forward)),
            ("P/B Ratio", _fmt_ratio(v.pb_ratio)),
            ("P/S Ratio", _fmt_ratio(v.ps_ratio)),
            ("P/FCF", _fmt_ratio(v.p_fcf)),
            ("EV/EBITDA", _fmt_ratio(v.ev_ebitda)),
            ("EV/Revenue", _fmt_ratio(v.ev_revenue)),
            ("PEG Ratio", _fmt_ratio(v.peg_ratio)),
            ("Dividend Yield", _fmt_pct(v.dividend_yield)),
            ("Earnings Yield", _fmt_pct(v.earnings_yield)),
            ("Enterprise Value", _fmt_money(v.enterprise_value)),
            ("Market Cap", _fmt_money(v.market_cap)),
            ("P/Tangible Book", _fmt_ratio(v.price_to_tangible_book)),
            ("P/NCAV", _fmt_ratio(v.price_to_ncav)),
            ("P/FFO", _fmt_ratio(v.p_ffo)),
            ("P/AFFO", _fmt_ratio(v.p_affo)),
            ("FFO Yield", _fmt_pct(v.ffo_yield)),
            ("Implied Cap Rate", _fmt_pct(v.implied_cap_rate)),
            ("P/NAV", _fmt_ratio(v.p_nav)),
            ("Cash/Market Cap", _fmt_pct(v.cash_to_market_cap)),
            ("NAV/Share", _fmt_money(v.nav_per_share)),
        ]))
        parts.append("</div>")

    # --- Profitability Metrics ---
    parts.append('<div class="card"><h2>Profitability Metrics</h2>')
    _pre_revenue = _ev(p.stage) in ("Pre-Development", "Development")
    if _pre_revenue:
        parts.append('<p class="meta">N/A for pre-revenue company at this stage.</p>')
    elif report.profitability:
        pr = report.profitability
        parts.append(_metric_table([
            ("ROE", _fmt_pct(pr.roe)),
            ("ROA", _fmt_pct(pr.roa)),
            ("ROIC", _fmt_pct(pr.roic)),
            ("Gross Margin", _fmt_pct(pr.gross_margin)),
            ("Operating Margin", _fmt_pct(pr.operating_margin)),
            ("Net Margin", _fmt_pct(pr.net_margin)),
            ("FCF Margin", _fmt_pct(pr.fcf_margin)),
            ("EBITDA Margin", _fmt_pct(pr.ebitda_margin)),
            ("NOI", _fmt_money(pr.noi)),
            ("NOI Margin", _fmt_pct(pr.noi_margin)),
            ("FFO", _fmt_money(pr.ffo)),
            ("FFO/Share", _fmt_money(pr.ffo_per_share)),
            ("AFFO", _fmt_money(pr.affo)),
            ("AFFO/Share", _fmt_money(pr.affo_per_share)),
            ("FFO Margin", _fmt_pct(pr.ffo_margin)),
            ("Same-Store NOI Growth", _fmt_pct(pr.same_store_noi_growth)),
            ("Occupancy Rate", _fmt_pct(pr.occupancy_rate)),
        ]))
    else:
        parts.append('<p class="meta">No profitability data available.</p>')
    parts.append("</div>")

    # --- Solvency & Survival ---
    if report.solvency:
        s = report.solvency
        parts.append('<div class="card"><h2>Solvency &amp; Survival</h2>')
        parts.append(_metric_table([
            ("Total Cash", _fmt_money(s.total_cash)),
            ("Total Debt", _fmt_money(s.total_debt)),
            ("Net Debt", _fmt_money(s.net_debt)),
            ("Cash/Share", _fmt_money(s.cash_per_share)),
            ("Cash Burn Rate (annual)", _fmt_money(s.cash_burn_rate)),
            ("Quarterly Burn Rate", _fmt_money(s.quarterly_burn_rate)),
            ("Cash Runway", f"{s.cash_runway_years:.1f} years" if _safe(s.cash_runway_years) is not None else "N/A"),
            ("Burn % of Mkt Cap", _fmt_pct(s.burn_as_pct_of_market_cap)),
            ("Debt/Equity", _fmt_ratio(s.debt_to_equity)),
            ("Debt/EBITDA", _fmt_ratio(s.debt_to_ebitda)),
            ("Debt / Gross Assets", _fmt_pct(s.debt_to_gross_assets)),
            ("Current Ratio", _fmt_ratio(s.current_ratio)),
            ("Quick Ratio", _fmt_ratio(s.quick_ratio)),
            ("Interest Coverage", _fmt_ratio(s.interest_coverage)),
            ("Fixed Charge Coverage", _fmt_ratio(s.fixed_charge_coverage)),
            ("Weighted Avg Debt Maturity (yrs)", f"{s.weighted_avg_debt_maturity:,.1f}" if _safe(s.weighted_avg_debt_maturity) is not None else "N/A"),
            ("% Fixed Rate Debt", _fmt_pct(s.pct_fixed_rate_debt)),
            ("Working Capital", _fmt_money(s.working_capital)),
            ("Altman Z-Score", _fmt_ratio(s.altman_z_score)),
            ("Tangible Book Value", _fmt_money(s.tangible_book_value)),
            ("NCAV", _fmt_money(s.ncav)),
            ("NCAV/Share", _fmt_money(s.ncav_per_share)),
        ]))
        parts.append("</div>")

    # --- Growth & Dilution ---
    if report.growth:
        g = report.growth
        parts.append('<div class="card"><h2>Growth &amp; Dilution</h2>')
        parts.append(_metric_table([
            ("Revenue Growth (YoY)", _fmt_pct(g.revenue_growth_yoy)),
            ("Revenue CAGR 3Y", _fmt_pct(g.revenue_cagr_3y)),
            ("Revenue CAGR 5Y", _fmt_pct(g.revenue_cagr_5y)),
            ("Earnings Growth (YoY)", _fmt_pct(g.earnings_growth_yoy)),
            ("Earnings CAGR 3Y", _fmt_pct(g.earnings_cagr_3y)),
            ("Earnings CAGR 5Y", _fmt_pct(g.earnings_cagr_5y)),
            ("FCF Growth (YoY)", _fmt_pct(g.fcf_growth_yoy)),
            ("FFO Growth YoY", _fmt_pct(g.ffo_growth_yoy)),
            ("FFO CAGR 3Y", _fmt_pct(g.ffo_cagr_3y)),
            ("AFFO Growth YoY", _fmt_pct(g.affo_growth_yoy)),
            ("Book Value Growth (YoY)", _fmt_pct(g.book_value_growth_yoy)),
            ("Dividend Growth 5Y", _fmt_pct(g.dividend_growth_5y)),
            ("Distribution Growth 5Y", _fmt_pct(g.distribution_growth_5y)),
            ("Same-Store NOI Growth YoY", _fmt_pct(g.same_store_noi_growth_yoy)),
            ("Acquisition Growth YoY", _fmt_pct(g.acquisition_growth_yoy)),
            ("FFO Payout Ratio", _fmt_pct(g.ffo_payout_ratio)),
            ("AFFO Payout Ratio", _fmt_pct(g.affo_payout_ratio)),
            ("Share Dilution (YoY)", _fmt_pct(g.shares_growth_yoy)),
            ("Share Dilution CAGR 3Y", _fmt_pct(g.shares_growth_3y_cagr)),
            ("Fully Diluted Shares", _fmt_num(g.fully_diluted_shares, 0)),
            ("Dilution Ratio", _fmt_ratio(g.dilution_ratio)),
        ]))
        parts.append("</div>")

    # --- Share Structure ---
    if report.share_structure:
        ss = report.share_structure
        parts.append('<div class="card"><h2>Share Structure</h2>')
        parts.append(_metric_table([
            ("Shares Outstanding", _fmt_num(ss.shares_outstanding, 0)),
            ("Fully Diluted Shares", _fmt_num(ss.fully_diluted_shares, 0)),
            ("Warrants Outstanding", _fmt_num(ss.warrants_outstanding, 0)),
            ("Options Outstanding", _fmt_num(ss.options_outstanding, 0)),
            ("Float Shares", _fmt_num(ss.float_shares, 0)),
            ("Insider Ownership", _fmt_pct(ss.insider_ownership_pct)),
            ("Institutional Ownership", _fmt_pct(ss.institutional_ownership_pct)),
            ("Assessment", ss.share_structure_assessment or "N/A"),
            ("Warrant Overhang Risk", ss.warrant_overhang_risk or "N/A"),
        ]))
        parts.append("</div>")

    # --- Real Estate Quality Indicators ---
    if report.real_estate_quality:
        mq = report.real_estate_quality
        parts.append('<div class="card"><h2>Real Estate Quality Indicators</h2>')
        parts.append(_metric_table([
            ("Quality Score", f"{mq.quality_score:.0f}/100" if _safe(mq.quality_score) is not None else "N/A"),
            ("Competitive Position", mq.competitive_position or "N/A"),
            ("Management Quality", mq.management_quality or "N/A"),
            ("Management Track Record", mq.management_track_record or "N/A"),
            ("Insider Ownership", _fmt_pct(mq.insider_ownership_pct)),
            ("Insider Alignment", mq.insider_alignment or "N/A"),
            ("Jurisdiction Assessment", mq.jurisdiction_assessment or "N/A"),
            ("Jurisdiction Score", f"{mq.jurisdiction_score:.0f}" if _safe(mq.jurisdiction_score) is not None else "N/A"),
            ("Portfolio Quality", mq.portfolio_quality or "N/A"),
            ("Portfolio Diversification", mq.portfolio_diversification or "N/A"),
            ("Occupancy Assessment", mq.occupancy_assessment or "N/A"),
            ("Lease Duration (WALT)", mq.lease_duration_assessment or "N/A"),
            ("Tenant Concentration", mq.tenant_concentration or "N/A"),
            ("Same-Store NOI Trend", mq.same_store_noi_trend or "N/A"),
            ("Cap Rate Assessment", mq.cap_rate_assessment or "N/A"),
            ("Financial Position", mq.financial_position or "N/A"),
            ("Dilution Risk", mq.dilution_risk or "N/A"),
            ("Share Structure", mq.share_structure_assessment or "N/A"),
            ("Catalyst Density", mq.catalyst_density or "N/A"),
            ("Strategic Backing", mq.strategic_backing or "N/A"),
            ("Asset Backing", mq.asset_backing or "N/A"),
            ("Niche Position", mq.niche_position or "N/A"),
            ("Revenue Predictability", mq.revenue_predictability or "N/A"),
        ]))
        if mq.near_term_catalysts:
            parts.append("<p><strong>Near-term Catalysts:</strong></p><ul>")
            for cat in mq.near_term_catalysts:
                parts.append(f"<li>{esc(cat)}</li>")
            parts.append("</ul>")
        parts.append("</div>")

    # --- Intrinsic Value ---
    if report.intrinsic_value:
        iv = report.intrinsic_value
        parts.append('<div class="card"><h2>Intrinsic Value Estimates</h2>')
        parts.append(f'<p>Current Price: <strong>{esc(_fmt_money(iv.current_price))}</strong>'
                     f' &nbsp;|&nbsp; Primary: {esc(iv.primary_method or "N/A")}'
                     f' &nbsp;|&nbsp; Secondary: {esc(iv.secondary_method or "N/A")}</p>')

        def _iv_entry(name: str, val_field, mos_field) -> Optional[tuple[str, str]]:
            v = _safe(val_field)
            if v is None:
                return None
            mos = _safe(mos_field)
            mos_str = f" (MoS: {mos * 100:+.0f}%)" if mos is not None else ""
            return (name, f"{_fmt_money(val_field)}{mos_str}")

        iv_fields = [
            _iv_entry("DCF Value", iv.dcf_value, iv.margin_of_safety_dcf),
            _iv_entry("Graham Number", iv.graham_number, iv.margin_of_safety_graham),
            _iv_entry("Lynch Fair Value", iv.lynch_fair_value, None),
            _iv_entry("NCAV Value", iv.ncav_value, iv.margin_of_safety_ncav),
            _iv_entry("Asset-Based Value", iv.asset_based_value, iv.margin_of_safety_asset),
            _iv_entry("NAV/Share", iv.nav_per_share, iv.margin_of_safety_nav),
            _iv_entry("FFO Multiple Value", iv.ffo_multiple_value, iv.margin_of_safety_ffo),
            _iv_entry("AFFO Multiple Value", iv.affo_multiple_value, iv.margin_of_safety_affo),
        ]
        iv_fields_clean = [f for f in iv_fields if f is not None]
        if _safe(iv.margin_of_safety_ffo) is not None:
            iv_fields_clean.append(("Margin of Safety (FFO)", _fmt_pct(iv.margin_of_safety_ffo)))
        if _safe(iv.margin_of_safety_affo) is not None:
            iv_fields_clean.append(("Margin of Safety (AFFO)", _fmt_pct(iv.margin_of_safety_affo)))
        if iv_fields_clean:
            parts.append("<table><tr><th>Method</th><th>Value</th></tr>")
            for label, val in iv_fields_clean:
                parts.append(f"<tr><td>{esc(label)}</td><td>{esc(val)}</td></tr>")
            parts.append("</table>")
        else:
            parts.append('<p class="meta">No intrinsic value estimates available.</p>')
        parts.append("</div>")

    # --- Market Intelligence ---
    if report.market_intelligence:
        mi = report.market_intelligence
        parts.append('<div class="card"><h2>Market Intelligence</h2>')

        # Rate & Sector Context
        if mi.benchmark_rate_name or mi.sector_etf_name:
            parts.append("<h2>Rate &amp; Sector Context</h2>")
            ctx_fields = []
            if mi.benchmark_rate_name and mi.benchmark_rate_value is not None:
                ctx_fields.append(("Benchmark Rate", f"{mi.benchmark_rate_name} — {mi.benchmark_rate_value:,.2f}"))
                if mi.rate_52w_high is not None and mi.rate_52w_low is not None:
                    ctx_fields.append(("52W Range", f"{mi.rate_52w_low:,.2f} — {mi.rate_52w_high:,.2f}"))
                if mi.rate_ytd_change is not None:
                    ctx_fields.append(("YTD Change", _fmt_pct(mi.rate_ytd_change)))
            if mi.sector_etf_name:
                perf = f" ({mi.sector_etf_3m_perf*100:+.1f}% 3m)" if mi.sector_etf_3m_perf is not None else ""
                ctx_fields.append(("Sector ETF", f"{mi.sector_etf_name} — ${mi.sector_etf_price:,.2f}{perf}" if mi.sector_etf_price else mi.sector_etf_name))
            if mi.peer_etf_name:
                perf = f" ({mi.peer_etf_3m_perf*100:+.1f}% 3m)" if mi.peer_etf_3m_perf is not None else ""
                ctx_fields.append(("Peer ETF", f"{mi.peer_etf_name} — ${mi.peer_etf_price:,.2f}{perf}" if mi.peer_etf_price else mi.peer_etf_name))
            parts.append(_metric_table(ctx_fields))

        # Analyst Consensus
        parts.append("<h2>Analyst Consensus</h2>")
        parts.append(_metric_table([
            ("Recommendation", mi.recommendation or "N/A"),
            ("Analyst Count", str(mi.analyst_count) if mi.analyst_count is not None else "N/A"),
            ("Target High", _fmt_money(mi.target_high)),
            ("Target Low", _fmt_money(mi.target_low)),
            ("Target Mean", _fmt_money(mi.target_mean)),
            ("Target Upside", _fmt_pct(mi.target_upside_pct)),
        ]))

        # Short Interest
        parts.append("<h2>Short Interest</h2>")
        parts.append(_metric_table([
            ("Shares Short", _fmt_num(mi.shares_short, 0)),
            ("Short % of Float", _fmt_pct(mi.short_pct_of_float)),
            ("Days to Cover", _fmt_ratio(mi.short_ratio_days)),
            ("Short Squeeze Risk", mi.short_squeeze_risk or "N/A"),
        ]))

        # Price & Technicals
        parts.append("<h2>Price &amp; Technicals</h2>")
        parts.append(_metric_table([
            ("Current Price", _fmt_money(mi.price_current)),
            ("52W High", _fmt_money(mi.price_52w_high)),
            ("52W Low", _fmt_money(mi.price_52w_low)),
            ("% from 52W High", _fmt_pct(mi.pct_from_52w_high)),
            ("% from 52W Low", _fmt_pct(mi.pct_from_52w_low)),
            ("52W Range Position", _fmt_pct(mi.price_52w_range_position)),
            ("SMA 50", _fmt_money(mi.sma_50)),
            ("SMA 200", _fmt_money(mi.sma_200)),
            ("Above SMA 50", _fmt_bool(mi.above_sma_50)),
            ("Above SMA 200", _fmt_bool(mi.above_sma_200)),
            ("Golden Cross", _fmt_bool(mi.golden_cross)),
            ("Beta", _fmt_ratio(mi.beta)),
            ("Avg Volume", _fmt_num(mi.avg_volume, 0)),
            ("10D Avg Volume", _fmt_num(mi.volume_10d_avg, 0)),
            ("Volume Trend", mi.volume_trend or "N/A"),
        ]))

        # Insider Activity
        parts.append("<h2>Insider Activity</h2>")
        parts.append(_metric_table([
            ("Insider Buy Signal", mi.insider_buy_signal or "N/A"),
            ("Net Insider Shares (3M)", _fmt_num(mi.net_insider_shares_3m, 0)),
        ]))
        if mi.insider_transactions:
            parts.append("<table><tr><th>Date</th><th>Insider</th><th>Type</th><th>Shares</th><th>Value</th></tr>")
            for t in mi.insider_transactions[:8]:
                parts.append(
                    f"<tr><td>{esc(str(_ga(t, 'date', '')))}</td>"
                    f"<td>{esc(str(_ga(t, 'insider', '')))}</td>"
                    f"<td>{esc(str(_ga(t, 'transaction_type', '')))}</td>"
                    f"<td>{esc(_fmt_num(_ga(t, 'shares'), 0))}</td>"
                    f"<td>{esc(_fmt_money(_ga(t, 'value')))}</td></tr>"
                )
            parts.append("</table>")

        # Institutional Holdings
        if mi.institutions_count or mi.institutions_pct or mi.top_holders:
            parts.append("<h2>Institutional Holdings</h2>")
            parts.append(_metric_table([
                ("Institutions Count", str(mi.institutions_count) if mi.institutions_count is not None else "N/A"),
                ("Institutional %", _fmt_pct(mi.institutions_pct)),
            ]))
            if mi.top_holders:
                parts.append("<p><strong>Top Holders:</strong></p><ul>")
                for h in mi.top_holders[:5]:
                    parts.append(f"<li>{esc(h)}</li>")
                parts.append("</ul>")

        # Projected Dilution
        if mi.projected_dilution_annual_pct or mi.financing_warning:
            parts.append("<h2>Projected Dilution</h2>")
            parts.append(_metric_table([
                ("Annual Dilution Rate", _fmt_pct(mi.projected_dilution_annual_pct)),
                ("Projected Shares (2Y)", _fmt_num(mi.projected_shares_in_2y, 0)),
            ]))
            if mi.financing_warning:
                parts.append(f'<div class="warn">{esc(mi.financing_warning)}</div>')

        # Risk Warnings
        if mi.risk_warnings:
            parts.append("<h2>Risk Warnings</h2>")
            for w_msg in mi.risk_warnings:
                parts.append(f'<div class="warn">{esc(w_msg)}</div>')

        # Disclaimers
        if mi.disclaimers:
            parts.append("<h2>Disclaimers</h2>")
            for d in mi.disclaimers:
                parts.append(f'<div class="disclaimer">{esc(d)}</div>')

        parts.append("</div>")  # end market intelligence card

    # --- Conclusion ---
    parts.append('<div class="card"><h2>Conclusion</h2>')

    # Category scores with visual bars
    if c.category_scores:
        parts.append("<table><tr><th>Category</th><th>Score</th><th>Bar</th></tr>")
        for cat, score in c.category_scores.items():
            label = cat.replace("_", " ").title()
            pct = max(0, min(100, score))
            if pct >= 65:
                bar_color = "#059669"
            elif pct >= 45:
                bar_color = "#d97706"
            else:
                bar_color = "#dc2626"
            parts.append(
                f'<tr><td>{esc(label)}</td><td>{score:.1f}</td>'
                f'<td><span class="score-bg">'
                f'<span class="score-fill" style="width:{pct:.0f}%;background:{bar_color}"></span>'
                f'</span></td></tr>'
            )
        parts.append("</table>")

    # Strengths & Risks columns
    if c.strengths or c.risks:
        parts.append('<div class="cols">')
        if c.strengths:
            parts.append("<div><h2>Strengths</h2><ul>")
            for s_item in c.strengths:
                parts.append(f'<li class="s">{esc(s_item)}</li>')
            parts.append("</ul></div>")
        if c.risks:
            parts.append("<div><h2>Risks</h2><ul>")
            for r_item in c.risks:
                parts.append(f'<li class="r">{esc(r_item)}</li>')
            parts.append("</ul></div>")
        parts.append("</div>")

    # Screening Checklist
    if c.screening_checklist:
        parts.append("<h2>Real Estate Screening Checklist</h2>")
        parts.append("<table><tr><th>Check</th><th>Result</th></tr>")
        for check, result in c.screening_checklist.items():
            label = check.replace("_", " ").title()
            if result is True:
                cls, text = "pass", "PASS"
            elif result is False:
                cls, text = "fail", "FAIL"
            else:
                cls, text = "na", "N/A"
            parts.append(f'<tr><td>{esc(label)}</td><td class="{cls}">{text}</td></tr>')
        parts.append("</table>")

    # Stage & Tier Notes
    if c.tier_note:
        parts.append(f'<p class="meta"><strong>Tier:</strong> {esc(c.tier_note)}</p>')
    if c.stage_note:
        parts.append(f'<p class="meta"><strong>Stage:</strong> {esc(c.stage_note)}</p>')

    parts.append("</div>")  # end conclusion card

    # --- Footer ---
    parts.append(f"""
<div class="footer">
  Lynx Real Estate Analysis &mdash; Lince Investor Suite<br>
  Report generated: {esc(report.fetched_at)}<br>
  This report is for informational purposes only and does not constitute investment advice.
</div>
</body>
</html>""")

    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path
