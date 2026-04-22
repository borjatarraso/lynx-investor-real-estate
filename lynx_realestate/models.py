"""Data models for Lynx Real Estate — REIT-focused fundamental analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Company tier classification (market cap based)
# ---------------------------------------------------------------------------

class CompanyTier(str, Enum):
    MEGA = "Mega Cap"
    LARGE = "Large Cap"
    MID = "Mid Cap"
    SMALL = "Small Cap"
    MICRO = "Micro Cap"
    NANO = "Nano Cap"


def classify_tier(market_cap: Optional[float]) -> CompanyTier:
    if market_cap is None or market_cap <= 0:
        return CompanyTier.NANO
    if market_cap >= 200_000_000_000:
        return CompanyTier.MEGA
    if market_cap >= 10_000_000_000:
        return CompanyTier.LARGE
    if market_cap >= 2_000_000_000:
        return CompanyTier.MID
    if market_cap >= 300_000_000:
        return CompanyTier.SMALL
    if market_cap >= 50_000_000:
        return CompanyTier.MICRO
    return CompanyTier.NANO


# ---------------------------------------------------------------------------
# Real estate company stage classification
# ---------------------------------------------------------------------------

class CompanyStage(str, Enum):
    PRE_DEVELOPMENT = "Pre-Development"
    DEVELOPMENT = "Development"
    LEASE_UP = "Lease-Up"
    STABILIZED = "Stabilized"
    NET_LEASE = "Net Lease / Triple-Net"


class PropertyType(str, Enum):
    RESIDENTIAL = "Residential / Apartment"
    OFFICE = "Office"
    RETAIL = "Retail"
    INDUSTRIAL = "Industrial / Logistics"
    HOTEL = "Hotel / Hospitality"
    HEALTHCARE = "Healthcare"
    SELF_STORAGE = "Self-Storage"
    DATA_CENTER = "Data Center"
    INFRASTRUCTURE = "Infrastructure / Cell Tower"
    DIVERSIFIED = "Diversified"
    NET_LEASE = "Net Lease"
    OTHER = "Other"


class JurisdictionTier(str, Enum):
    TIER_1 = "Tier 1 — Low Risk"
    TIER_2 = "Tier 2 — Moderate Risk"
    TIER_3 = "Tier 3 — High Risk"
    UNKNOWN = "Unknown"


class Relevance(str, Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    RELEVANT = "relevant"
    CONTEXTUAL = "contextual"
    IRRELEVANT = "irrelevant"


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

@dataclass
class CompanyProfile:
    ticker: str
    name: str
    isin: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    tier: CompanyTier = CompanyTier.NANO
    stage: CompanyStage = CompanyStage.STABILIZED
    primary_property_type: PropertyType = PropertyType.OTHER
    jurisdiction_tier: JurisdictionTier = JurisdictionTier.UNKNOWN
    jurisdiction_country: Optional[str] = None


@dataclass
class ValuationMetrics:
    pe_trailing: Optional[float] = None
    pe_forward: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    p_fcf: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    peg_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    earnings_yield: Optional[float] = None
    enterprise_value: Optional[float] = None
    market_cap: Optional[float] = None
    price_to_tangible_book: Optional[float] = None
    price_to_ncav: Optional[float] = None
    # REIT-specific valuation
    p_ffo: Optional[float] = None
    p_affo: Optional[float] = None
    p_nav: Optional[float] = None
    implied_cap_rate: Optional[float] = None
    cash_to_market_cap: Optional[float] = None
    nav_per_share: Optional[float] = None
    fcf_yield: Optional[float] = None
    ffo_yield: Optional[float] = None


@dataclass
class ProfitabilityMetrics:
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    # REIT-specific profitability
    noi: Optional[float] = None                  # Net Operating Income
    noi_margin: Optional[float] = None           # NOI / revenue
    ffo: Optional[float] = None                  # Funds From Operations
    ffo_per_share: Optional[float] = None
    affo: Optional[float] = None                 # Adjusted FFO
    affo_per_share: Optional[float] = None
    ffo_margin: Optional[float] = None
    same_store_noi_growth: Optional[float] = None
    occupancy_rate: Optional[float] = None
    implied_cap_rate: Optional[float] = None
    croci: Optional[float] = None
    ocf_to_net_income: Optional[float] = None


@dataclass
class SolvencyMetrics:
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    debt_to_gross_assets: Optional[float] = None    # REIT leverage metric
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    fixed_charge_coverage: Optional[float] = None   # REIT debt service
    altman_z_score: Optional[float] = None
    net_debt: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    cash_burn_rate: Optional[float] = None
    cash_runway_years: Optional[float] = None
    working_capital: Optional[float] = None
    cash_per_share: Optional[float] = None
    tangible_book_value: Optional[float] = None
    ncav: Optional[float] = None
    ncav_per_share: Optional[float] = None
    quarterly_burn_rate: Optional[float] = None
    burn_as_pct_of_market_cap: Optional[float] = None
    debt_per_share: Optional[float] = None
    net_debt_per_share: Optional[float] = None
    debt_service_coverage: Optional[float] = None
    weighted_avg_debt_maturity: Optional[float] = None  # years
    pct_fixed_rate_debt: Optional[float] = None


@dataclass
class GrowthMetrics:
    revenue_growth_yoy: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None
    earnings_cagr_3y: Optional[float] = None
    earnings_cagr_5y: Optional[float] = None
    fcf_growth_yoy: Optional[float] = None
    ffo_growth_yoy: Optional[float] = None
    ffo_cagr_3y: Optional[float] = None
    affo_growth_yoy: Optional[float] = None
    book_value_growth_yoy: Optional[float] = None
    dividend_growth_5y: Optional[float] = None
    distribution_growth_5y: Optional[float] = None
    shares_growth_yoy: Optional[float] = None
    shares_growth_3y_cagr: Optional[float] = None
    fully_diluted_shares: Optional[float] = None
    dilution_ratio: Optional[float] = None
    same_store_noi_growth_yoy: Optional[float] = None
    acquisition_growth_yoy: Optional[float] = None
    capex_to_revenue: Optional[float] = None
    capex_to_ocf: Optional[float] = None
    reinvestment_rate: Optional[float] = None
    dividend_payout_ratio: Optional[float] = None
    affo_payout_ratio: Optional[float] = None    # REIT-critical
    ffo_payout_ratio: Optional[float] = None
    dividend_coverage: Optional[float] = None
    shareholder_yield: Optional[float] = None
    fcf_per_share: Optional[float] = None
    ocf_per_share: Optional[float] = None


@dataclass
class EfficiencyMetrics:
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    days_sales_outstanding: Optional[float] = None
    days_inventory: Optional[float] = None
    cash_conversion_cycle: Optional[float] = None
    fcf_conversion: Optional[float] = None
    capex_intensity: Optional[float] = None
    g_and_a_as_pct_of_revenue: Optional[float] = None  # Real estate G&A overhead


@dataclass
class RealEstateQualityIndicators:
    quality_score: Optional[float] = None
    management_quality: Optional[str] = None
    insider_ownership_pct: Optional[float] = None
    management_track_record: Optional[str] = None
    jurisdiction_assessment: Optional[str] = None
    jurisdiction_score: Optional[float] = None
    # REIT-specific quality signals
    portfolio_quality: Optional[str] = None
    portfolio_diversification: Optional[str] = None
    occupancy_assessment: Optional[str] = None
    lease_duration_assessment: Optional[str] = None   # WALT (weighted avg lease term)
    tenant_concentration: Optional[str] = None
    same_store_noi_trend: Optional[str] = None
    cap_rate_assessment: Optional[str] = None
    financial_position: Optional[str] = None
    dilution_risk: Optional[str] = None
    share_structure_assessment: Optional[str] = None
    catalyst_density: Optional[str] = None
    near_term_catalysts: list[str] = field(default_factory=list)
    strategic_backing: Optional[str] = None
    competitive_position: Optional[str] = None
    asset_backing: Optional[str] = None
    niche_position: Optional[str] = None
    insider_alignment: Optional[str] = None
    revenue_predictability: Optional[str] = None
    roic_history: list[Optional[float]] = field(default_factory=list)
    gross_margin_history: list[Optional[float]] = field(default_factory=list)


@dataclass
class IntrinsicValue:
    dcf_value: Optional[float] = None
    graham_number: Optional[float] = None
    lynch_fair_value: Optional[float] = None
    ncav_value: Optional[float] = None
    asset_based_value: Optional[float] = None
    nav_per_share: Optional[float] = None
    ffo_multiple_value: Optional[float] = None     # P/FFO based fair value
    affo_multiple_value: Optional[float] = None    # P/AFFO based fair value
    current_price: Optional[float] = None
    margin_of_safety_dcf: Optional[float] = None
    margin_of_safety_graham: Optional[float] = None
    margin_of_safety_ncav: Optional[float] = None
    margin_of_safety_asset: Optional[float] = None
    margin_of_safety_nav: Optional[float] = None
    margin_of_safety_ffo: Optional[float] = None
    margin_of_safety_affo: Optional[float] = None
    primary_method: Optional[str] = None
    secondary_method: Optional[str] = None


@dataclass
class ShareStructure:
    shares_outstanding: Optional[float] = None
    fully_diluted_shares: Optional[float] = None
    warrants_outstanding: Optional[float] = None
    options_outstanding: Optional[float] = None
    insider_ownership_pct: Optional[float] = None
    institutional_ownership_pct: Optional[float] = None
    float_shares: Optional[float] = None
    share_structure_assessment: Optional[str] = None
    warrant_overhang_risk: Optional[str] = None


@dataclass
class InsiderTransaction:
    """A single insider buy/sell transaction."""
    insider: str = ""
    position: str = ""
    transaction_type: str = ""
    shares: Optional[float] = None
    value: Optional[float] = None
    date: str = ""


@dataclass
class MarketIntelligence:
    """Market sentiment, insider activity, institutional holdings, and technicals.

    Real-estate investors watch dividend/distribution sustainability,
    interest-rate sensitivity, and property-market signals closely; this
    section aggregates those inputs with the generic sentiment feeds.
    """
    # Insider activity
    insider_transactions: list[InsiderTransaction] = field(default_factory=list)
    net_insider_shares_3m: Optional[float] = None
    insider_buy_signal: Optional[str] = None

    # Institutional holders
    top_holders: list[str] = field(default_factory=list)
    institutions_count: Optional[int] = None
    institutions_pct: Optional[float] = None

    # Analyst consensus
    analyst_count: Optional[int] = None
    recommendation: Optional[str] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    target_mean: Optional[float] = None
    target_upside_pct: Optional[float] = None

    # Short interest
    shares_short: Optional[float] = None
    short_pct_of_float: Optional[float] = None
    short_ratio_days: Optional[float] = None
    short_squeeze_risk: Optional[str] = None

    # Price technicals
    price_current: Optional[float] = None
    price_52w_high: Optional[float] = None
    price_52w_low: Optional[float] = None
    pct_from_52w_high: Optional[float] = None
    pct_from_52w_low: Optional[float] = None
    price_52w_range_position: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    above_sma_50: Optional[bool] = None
    above_sma_200: Optional[bool] = None
    golden_cross: Optional[bool] = None
    beta: Optional[float] = None
    avg_volume: Optional[float] = None
    volume_10d_avg: Optional[float] = None
    volume_trend: Optional[str] = None

    # Projected dilution (REITs are frequent secondary-offering issuers)
    projected_dilution_annual_pct: Optional[float] = None
    projected_shares_in_2y: Optional[float] = None
    financing_warning: Optional[str] = None

    # Rate / macro context (REITs are rate-sensitive)
    benchmark_rate_name: Optional[str] = None
    benchmark_rate_value: Optional[float] = None
    rate_currency: str = "USD"
    rate_52w_high: Optional[float] = None
    rate_52w_low: Optional[float] = None
    rate_52w_position: Optional[float] = None
    rate_ytd_change: Optional[float] = None

    # Sector ETF context
    sector_etf_name: Optional[str] = None
    sector_etf_ticker: Optional[str] = None
    sector_etf_price: Optional[float] = None
    sector_etf_3m_perf: Optional[float] = None
    peer_etf_name: Optional[str] = None
    peer_etf_ticker: Optional[str] = None
    peer_etf_price: Optional[float] = None
    peer_etf_3m_perf: Optional[float] = None

    # Risk warnings
    risk_warnings: list[str] = field(default_factory=list)

    # Real-estate-specific disclaimers
    disclaimers: list[str] = field(default_factory=list)


@dataclass
class FinancialStatement:
    period: str
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None
    interest_expense: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None
    free_cash_flow: Optional[float] = None
    dividends_paid: Optional[float] = None
    shares_outstanding: Optional[float] = None
    eps: Optional[float] = None
    book_value_per_share: Optional[float] = None
    # REIT-specific line items
    real_estate_assets: Optional[float] = None
    accumulated_depreciation: Optional[float] = None
    rental_income: Optional[float] = None
    property_operating_expenses: Optional[float] = None


@dataclass
class AnalysisConclusion:
    overall_score: float = 0.0
    verdict: str = ""
    summary: str = ""
    category_scores: dict = field(default_factory=dict)
    category_summaries: dict = field(default_factory=dict)
    strengths: list = field(default_factory=list)
    risks: list = field(default_factory=list)
    tier_note: str = ""
    stage_note: str = ""
    screening_checklist: dict = field(default_factory=dict)


@dataclass
class MetricExplanation:
    key: str
    full_name: str
    description: str
    why_used: str
    formula: str
    category: str


@dataclass
class Filing:
    form_type: str
    filing_date: str
    period: str
    url: str
    description: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class NewsArticle:
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class AnalysisReport:
    profile: CompanyProfile
    valuation: Optional[ValuationMetrics] = None
    profitability: Optional[ProfitabilityMetrics] = None
    solvency: Optional[SolvencyMetrics] = None
    growth: Optional[GrowthMetrics] = None
    efficiency: Optional[EfficiencyMetrics] = None
    real_estate_quality: Optional[RealEstateQualityIndicators] = None
    intrinsic_value: Optional[IntrinsicValue] = None
    share_structure: Optional[ShareStructure] = None
    market_intelligence: Optional[MarketIntelligence] = None
    financials: list[FinancialStatement] = field(default_factory=list)
    filings: list[Filing] = field(default_factory=list)
    news: list[NewsArticle] = field(default_factory=list)
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Stage classification helpers
# ---------------------------------------------------------------------------

_STAGE_KEYWORDS = {
    CompanyStage.NET_LEASE: [
        "triple net", "net lease", "net-lease", "single-tenant net",
        "ground lease", "sale-leaseback", "long-term lease",
    ],
    CompanyStage.STABILIZED: [
        "stabilized portfolio", "stabilized occupancy", "operating reit",
        "rental income", "same-store noi", "occupancy rate",
        "portfolio occupancy", "fully leased", "operating portfolio",
        "diversified real estate", "income-producing",
    ],
    CompanyStage.LEASE_UP: [
        "lease-up", "leasing phase", "recently completed",
        "initial lease", "stabilization period", "newly delivered",
        "pre-leasing", "initial occupancy",
    ],
    CompanyStage.DEVELOPMENT: [
        "under construction", "development pipeline", "construction in progress",
        "ground-up development", "redevelopment", "entitlements",
        "predevelopment", "project delivery", "construction phase",
    ],
    CompanyStage.PRE_DEVELOPMENT: [
        "land banking", "land assembly", "acquisition pipeline",
        "site identification", "pre-development", "planning phase",
        "feasibility study", "site selection",
    ],
}

_PROPERTY_TYPE_KEYWORDS = {
    PropertyType.RESIDENTIAL: [
        "apartment", "multifamily", "residential", "rental housing",
        "single-family rental", "student housing", "senior living",
    ],
    PropertyType.OFFICE: [
        "office", "office tower", "class a office", "workplace",
        "commercial office",
    ],
    PropertyType.RETAIL: [
        "retail", "shopping center", "mall", "outlet", "strip mall",
        "power center", "grocery-anchored", "mixed-use retail",
    ],
    PropertyType.INDUSTRIAL: [
        "industrial", "logistics", "warehouse", "distribution center",
        "fulfillment", "last-mile", "light industrial", "cold storage",
    ],
    PropertyType.HOTEL: [
        "hotel", "hospitality", "lodging", "resort", "extended stay",
        "rooms revpar", "lodging reit",
    ],
    PropertyType.HEALTHCARE: [
        "healthcare", "medical office", "mob", "skilled nursing",
        "senior housing", "life science", "lab space", "hospital",
    ],
    PropertyType.SELF_STORAGE: [
        "self-storage", "storage facility", "self storage",
    ],
    PropertyType.DATA_CENTER: [
        "data center", "datacenter", "hyperscale", "colocation",
        "interconnection",
    ],
    PropertyType.INFRASTRUCTURE: [
        "cell tower", "tower reit", "communications infrastructure",
        "fiber", "macro tower", "small cell",
    ],
    PropertyType.NET_LEASE: [
        "triple net", "net lease", "net-lease", "single-tenant net",
    ],
    PropertyType.DIVERSIFIED: [
        "diversified real estate", "diversified portfolio",
        "mixed portfolio", "multi-asset reit",
    ],
}

_TIER_1_JURISDICTIONS = {
    "united states", "canada", "australia", "new zealand",
    "united kingdom", "ireland", "germany", "france", "netherlands",
    "belgium", "switzerland", "sweden", "norway", "denmark", "finland",
    "japan", "singapore", "hong kong",
}

_TIER_2_JURISDICTIONS = {
    "spain", "italy", "portugal", "poland", "czech republic",
    "hungary", "greece", "mexico", "chile", "brazil", "uruguay",
    "south korea", "taiwan", "malaysia", "thailand", "south africa",
    "united arab emirates", "israel",
}


def classify_stage(description: Optional[str], revenue: Optional[float],
                   info: Optional[dict] = None) -> CompanyStage:
    if description is None:
        description = ""
    desc_lower = description.lower()

    if revenue is not None and revenue > 10_000_000:
        import re as _re
        for pattern in [r"\btriple.?net\b", r"\bnet.?lease\b"]:
            if _re.search(pattern, desc_lower):
                return CompanyStage.NET_LEASE
        for kw in _STAGE_KEYWORDS[CompanyStage.STABILIZED]:
            if kw.lower() in desc_lower:
                return CompanyStage.STABILIZED
        # Revenue-generating REIT defaults to Stabilized
        return CompanyStage.STABILIZED

    for stage in [CompanyStage.LEASE_UP,
                  CompanyStage.DEVELOPMENT, CompanyStage.PRE_DEVELOPMENT]:
        for kw in _STAGE_KEYWORDS[stage]:
            if kw.lower() in desc_lower:
                return stage

    # Check STABILIZED keywords last in the fallback (no revenue threshold met)
    for kw in _STAGE_KEYWORDS[CompanyStage.STABILIZED]:
        if kw.lower() in desc_lower:
            return CompanyStage.STABILIZED

    if info:
        industry = (info.get("industry") or "").lower()
        if "reit" in industry or "real estate" in industry:
            return CompanyStage.DEVELOPMENT

    return CompanyStage.PRE_DEVELOPMENT


def classify_property_type(description: Optional[str],
                           industry: Optional[str] = None) -> PropertyType:
    import re
    text = ((description or "") + " " + (industry or "")).lower()
    scores: dict[PropertyType, int] = {}
    for prop_type, keywords in _PROPERTY_TYPE_KEYWORDS.items():
        count = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if len(kw_lower) <= 3:
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', text):
                    count += 1
            else:
                if kw_lower in text:
                    count += 1
        if count > 0:
            scores[prop_type] = count
    if scores:
        return max(scores, key=scores.get)
    return PropertyType.OTHER


def classify_jurisdiction(country: Optional[str],
                          description: Optional[str] = None) -> JurisdictionTier:
    import re as _re
    if not country:
        return JurisdictionTier.UNKNOWN
    c_lower = country.lower().strip()
    for j in _TIER_1_JURISDICTIONS:
        if j in c_lower:
            return JurisdictionTier.TIER_1
    for j in _TIER_2_JURISDICTIONS:
        if j in c_lower:
            return JurisdictionTier.TIER_2
    if description:
        desc_lower = description.lower()
        for j in _TIER_1_JURISDICTIONS:
            if _re.search(r'\b' + _re.escape(j) + r'\b', desc_lower):
                return JurisdictionTier.TIER_1
        for j in _TIER_2_JURISDICTIONS:
            if _re.search(r'\b' + _re.escape(j) + r'\b', desc_lower):
                return JurisdictionTier.TIER_2
    return JurisdictionTier.TIER_3
