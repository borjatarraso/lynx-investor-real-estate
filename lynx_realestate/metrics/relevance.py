"""Metric relevance by company tier AND REIT lifecycle stage."""

from __future__ import annotations

from lynx_realestate.models import CompanyStage, CompanyTier, Relevance

C = Relevance.CRITICAL
M = Relevance.IMPORTANT
R = Relevance.RELEVANT
X = Relevance.CONTEXTUAL
I = Relevance.IRRELEVANT


def get_relevance(
    metric_key: str,
    tier: CompanyTier,
    category: str = "valuation",
    stage: CompanyStage = CompanyStage.STABILIZED,
) -> Relevance:
    stage_override = _STAGE_OVERRIDES.get(metric_key, {}).get(stage)
    if stage_override is not None:
        return stage_override

    table = {
        "valuation": VALUATION_RELEVANCE,
        "profitability": PROFITABILITY_RELEVANCE,
        "solvency": SOLVENCY_RELEVANCE,
        "growth": GROWTH_RELEVANCE,
        "real_estate_quality": REAL_ESTATE_QUALITY_RELEVANCE,
        "share_structure": SHARE_STRUCTURE_RELEVANCE,
    }.get(category, {})
    entry = table.get(metric_key, {})
    return entry.get(tier, Relevance.RELEVANT)


# ======================================================================
# Stage-based overrides (take precedence over tier-based lookups)
# ======================================================================

_STAGE_OVERRIDES: dict[str, dict[CompanyStage, Relevance]] = {
    # VALUATION
    "pe_trailing": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "pe_forward": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: R},
    "p_fcf": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ev_ebitda": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ev_revenue": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "peg_ratio": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "dividend_yield": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "earnings_yield": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "cash_to_market_cap": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "pb_ratio": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "price_to_tangible_book": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "price_to_ncav": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: I},
    "ps_ratio": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "fcf_yield": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ffo_yield": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "p_ffo": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: I, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "p_affo": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "p_nav": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "implied_cap_rate": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "nav_per_share": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    # PROFITABILITY
    "roe": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "roa": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "roic": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "gross_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "operating_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "net_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "fcf_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ebitda_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "noi": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "noi_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "ffo": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "ffo_per_share": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "affo": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "affo_per_share": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "ffo_margin": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "same_store_noi_growth": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: I, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: X},
    "occupancy_rate": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: M},
    "croci": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ocf_to_net_income": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    # SOLVENCY
    "cash_burn_rate": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: I},
    "cash_runway_years": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: I, CompanyStage.NET_LEASE: I},
    "burn_as_pct_of_market_cap": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: I, CompanyStage.NET_LEASE: I},
    "working_capital": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "cash_per_share": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "ncav_per_share": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: I, CompanyStage.NET_LEASE: I},
    "current_ratio": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "quick_ratio": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "debt_to_equity": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "debt_to_ebitda": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: M},
    "debt_to_gross_assets": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: M, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: C},
    "interest_coverage": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "fixed_charge_coverage": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "weighted_avg_debt_maturity": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: C},
    "pct_fixed_rate_debt": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "altman_z_score": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "debt_per_share": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "debt_service_coverage": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "net_debt": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    # GROWTH
    "shares_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "shares_growth_3y_cagr": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "dilution_ratio": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "revenue_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "revenue_cagr_3y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "revenue_cagr_5y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "earnings_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "earnings_cagr_3y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "earnings_cagr_5y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "book_value_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
    "fcf_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ffo_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: I, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: R},
    "affo_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: R},
    "ffo_cagr_3y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: R},
    "same_store_noi_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: I},
    "acquisition_growth_yoy": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "capex_to_revenue": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: I},
    "capex_to_ocf": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "reinvestment_rate": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "dividend_payout_ratio": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "ffo_payout_ratio": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: M},
    "affo_payout_ratio": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "distribution_growth_5y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: C},
    "dividend_growth_5y": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "dividend_coverage": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: C},
    "shareholder_yield": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "fcf_per_share": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: X, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "ocf_per_share": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    # REAL ESTATE QUALITY
    "quality_score": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "insider_alignment": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "insider_ownership_pct": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "financial_position": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "dilution_risk": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "asset_backing": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: M, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "portfolio_quality": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: M, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "portfolio_diversification": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: M},
    "occupancy_assessment": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: C, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: M},
    "lease_duration_assessment": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: C},
    "tenant_concentration": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: M, CompanyStage.NET_LEASE: C},
    "same_store_noi_trend": {CompanyStage.PRE_DEVELOPMENT: I, CompanyStage.DEVELOPMENT: I, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: X},
    "cap_rate_assessment": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    "catalyst_density": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: M, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "revenue_predictability": {CompanyStage.PRE_DEVELOPMENT: X, CompanyStage.DEVELOPMENT: X, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: C, CompanyStage.NET_LEASE: C},
    # SHARE STRUCTURE
    "shares_outstanding": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "fully_diluted_shares": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: M, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: X},
    "institutional_ownership_pct": {CompanyStage.PRE_DEVELOPMENT: R, CompanyStage.DEVELOPMENT: R, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: R, CompanyStage.NET_LEASE: R},
    "share_structure_assessment": {CompanyStage.PRE_DEVELOPMENT: C, CompanyStage.DEVELOPMENT: C, CompanyStage.LEASE_UP: R, CompanyStage.STABILIZED: X, CompanyStage.NET_LEASE: X},
}


# ======================================================================
# Tier-based relevance tables (fallback when no stage override exists)
# ======================================================================

VALUATION_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "pe_trailing":           {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "pb_ratio":              {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "ps_ratio":              {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "p_fcf":                 {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "p_ffo":                 {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "p_affo":                {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "p_nav":                 {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: M, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "implied_cap_rate":      {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "ffo_yield":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "ev_ebitda":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "cash_to_market_cap":    {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "price_to_tangible_book":{CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "price_to_ncav":         {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

PROFITABILITY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "roe":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "roic":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
    "noi":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "noi_margin":       {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "ffo":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "affo":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "occupancy_rate":   {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: M},
    "gross_margin":     {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "fcf_margin":       {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: R, CompanyTier.SMALL: R, CompanyTier.MICRO: X, CompanyTier.NANO: I},
}

SOLVENCY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "debt_to_equity":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "debt_to_gross_assets":        {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: M, CompanyTier.NANO: R},
    "debt_to_ebitda":              {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "fixed_charge_coverage":       {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: R},
    "weighted_avg_debt_maturity":  {CompanyTier.MEGA: M, CompanyTier.LARGE: M, CompanyTier.MID: M, CompanyTier.SMALL: R, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "pct_fixed_rate_debt":         {CompanyTier.MEGA: M, CompanyTier.LARGE: M, CompanyTier.MID: M, CompanyTier.SMALL: R, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "current_ratio":               {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "cash_burn_rate":              {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "cash_runway_years":           {CompanyTier.MEGA: I, CompanyTier.LARGE: I, CompanyTier.MID: X, CompanyTier.SMALL: R, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}

GROWTH_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "shares_growth_yoy":          {CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "revenue_growth_yoy":         {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "ffo_growth_yoy":             {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "affo_growth_yoy":            {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "same_store_noi_growth_yoy":  {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "distribution_growth_5y":     {CompanyTier.MEGA: M, CompanyTier.LARGE: M, CompanyTier.MID: M, CompanyTier.SMALL: M, CompanyTier.MICRO: R, CompanyTier.NANO: X},
    "ffo_payout_ratio":           {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: M, CompanyTier.NANO: R},
    "affo_payout_ratio":          {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: M, CompanyTier.NANO: R},
}

REAL_ESTATE_QUALITY_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "quality_score":               {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "insider_alignment":           {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "portfolio_quality":           {CompanyTier.MEGA: C, CompanyTier.LARGE: C, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: M, CompanyTier.NANO: M},
    "portfolio_diversification":   {CompanyTier.MEGA: M, CompanyTier.LARGE: M, CompanyTier.MID: M, CompanyTier.SMALL: R, CompanyTier.MICRO: R, CompanyTier.NANO: R},
    "tenant_concentration":        {CompanyTier.MEGA: M, CompanyTier.LARGE: M, CompanyTier.MID: C, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "lease_duration_assessment":   {CompanyTier.MEGA: M, CompanyTier.LARGE: M, CompanyTier.MID: M, CompanyTier.SMALL: M, CompanyTier.MICRO: M, CompanyTier.NANO: R},
}

SHARE_STRUCTURE_RELEVANCE: dict[str, dict[CompanyTier, Relevance]] = {
    "shares_outstanding":       {CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "fully_diluted_shares":     {CompanyTier.MEGA: X, CompanyTier.LARGE: X, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
    "insider_ownership_pct":    {CompanyTier.MEGA: R, CompanyTier.LARGE: R, CompanyTier.MID: R, CompanyTier.SMALL: C, CompanyTier.MICRO: C, CompanyTier.NANO: C},
}
