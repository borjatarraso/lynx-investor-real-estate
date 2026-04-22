# Lynx Real Estate Analysis -- API Reference

Public Python API for the `lynx_realestate` package (v2.0).

## Package Structure

```
lynx_realestate/
├── __init__.py          # Version, about text
├── __main__.py          # Entry point
├── cli.py               # CLI argument parser
├── display.py           # Rich console display
├── interactive.py       # Interactive REPL mode
├── easter.py            # Hidden features
├── models.py            # Data models
├── core/
│   ├── analyzer.py      # Analysis orchestrator (includes sector gate)
│   ├── conclusion.py    # Verdict synthesis
│   ├── fetcher.py       # yfinance data fetching
│   ├── news.py          # News aggregation
│   ├── reports.py       # SEC/SEDAR filing fetching
│   ├── storage.py       # Cache management
│   └── ticker.py        # Ticker resolution
├── metrics/
│   ├── calculator.py    # Metric calculations
│   ├── relevance.py     # Metric relevance by stage/tier
│   ├── explanations.py  # Metric educational content
│   └── sector_insights.py # REIT / real-estate industry insights
├── export/
│   ├── __init__.py      # Export dispatcher
│   ├── txt_export.py    # Plain text export
│   ├── html_export.py   # HTML export
│   └── pdf_export.py    # PDF export
├── gui/
│   └── app.py           # Tkinter GUI
└── tui/
    ├── app.py           # Textual TUI
    └── themes.py        # TUI color themes
```

---

## Core API

### Analysis (`lynx_realestate.core.analyzer`)

#### `run_full_analysis`

```python
def run_full_analysis(
    identifier: str,
    download_reports: bool = True,
    download_news: bool = True,
    max_filings: int = 10,
    verbose: bool = False,
    refresh: bool = False,
) -> AnalysisReport
```

Run a complete fundamental analysis for a REIT or real-estate operating company.
This is a convenience wrapper around `run_progressive_analysis` with
`on_progress=None`.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `identifier` | `str` | required | Ticker symbol (`SPG`), ISIN, or company name (`Simon Property Group`). |
| `download_reports` | `bool` | `True` | Fetch SEC/SEDAR filings. |
| `download_news` | `bool` | `True` | Fetch recent news articles. |
| `max_filings` | `int` | `10` | Maximum number of filings to download locally. |
| `verbose` | `bool` | `False` | Enable verbose console output. |
| `refresh` | `bool` | `False` | Force re-fetch from network even if cached data exists. |

**Returns:** `AnalysisReport` -- fully populated report dataclass.

**Raises:** `SectorMismatchError` if the resolved company is not a REIT or
real-estate operating company (see [Sector Validation](#sector-validation)).

**Example:**

```python
from lynx_realestate.core.analyzer import run_full_analysis

report = run_full_analysis("SPG")
print(report.profile.name)       # "Simon Property Group, Inc."
print(report.profile.tier.value) # "Large Cap"
print(report.profitability.ffo)
```

---

#### `run_progressive_analysis`

```python
def run_progressive_analysis(
    identifier: str,
    download_reports: bool = True,
    download_news: bool = True,
    max_filings: int = 10,
    verbose: bool = False,
    refresh: bool = False,
    on_progress: Optional[Callable[[str, AnalysisReport], None]] = None,
) -> AnalysisReport
```

Same as `run_full_analysis`, but accepts a progress callback that is invoked
after each analysis stage completes.  Used by the TUI and GUI interfaces to
update the display incrementally.

**Callback stages** (passed as the first `str` argument):

`"profile"` | `"financials"` | `"valuation"` | `"profitability"` |
`"solvency"` | `"growth"` | `"share_structure"` | `"real_estate_quality"` |
`"intrinsic_value"` | `"market_intelligence"` | `"filings"` | `"news"` |
`"conclusion"` | `"complete"`

**Example:**

```python
from lynx_realestate.core.analyzer import run_progressive_analysis

def on_progress(stage: str, report):
    print(f"Stage complete: {stage}")

report = run_progressive_analysis("O", on_progress=on_progress)
```

---

### Sector Validation

Lynx Real Estate is scope-restricted to REITs and real-estate operating
companies.  Before running analysis, the resolved `CompanyProfile` is passed
through a sector validator.  Companies outside scope raise
`SectorMismatchError` with a human-readable message.

**Allowed sectors:** `"Real Estate"` (including `"Real Estate—REITs"`).

**Allowed industries (subset):**
`REIT—Residential`, `REIT—Office`, `REIT—Retail`, `REIT—Industrial`,
`REIT—Hotel & Motel`, `REIT—Healthcare Facilities`, `REIT—Specialty`,
`REIT—Diversified`, `REIT—Mortgage`, `Real Estate Services`,
`Real Estate—Development`, `Real Estate—Diversified`,
`Real Estate Operating Companies`.

Description-based fallback patterns also admit companies whose yfinance
classification is missing or generic but whose business description contains
clear REIT / real-estate signals (`reit`, `real estate`, `rental income`,
`same-store noi`, `ffo`, `affo`, `cap rate`, etc.).

```python
from lynx_investor_core.sector_gate import SectorMismatchError

try:
    report = run_full_analysis("AAPL")
except SectorMismatchError as e:
    print(e)  # Apple is not a REIT / real-estate operator -> rejected
```

---

### Conclusion (`lynx_realestate.core.conclusion`)

#### `generate_conclusion`

```python
def generate_conclusion(report: AnalysisReport) -> AnalysisConclusion
```

Synthesize a scored verdict from a completed `AnalysisReport`.

Scoring weights are determined by the company's `(stage, tier)` combination.
For example, solvency and real-estate quality are weighted much more heavily
for pre-development REITs than for stabilized large-cap REITs.

**Returns:** `AnalysisConclusion` with:

- `overall_score` -- 0-100 composite score.
- `verdict` -- one of `"Strong Buy"`, `"Buy"`, `"Hold"`, `"Caution"`, `"Avoid"`.
- `summary` -- one-paragraph narrative.
- `category_scores` -- dict with scores for `valuation`, `profitability`, `solvency`, `growth`, `real_estate_quality`.
- `category_summaries` -- dict with human-readable summary per category.
- `strengths` / `risks` -- lists of up to 6 key points each.
- `tier_note` / `stage_note` -- explanations of why certain metrics matter for this company.
- `screening_checklist` -- dict of boolean pass/fail/None checks (e.g. `affo_covers_distribution`, `low_leverage`, `strong_occupancy`, `capital_discipline`, `insider_ownership`).

**Example:**

```python
from lynx_realestate.core.conclusion import generate_conclusion

conclusion = generate_conclusion(report)
print(conclusion.verdict)          # "Hold"
print(conclusion.overall_score)    # 62.3
print(conclusion.strengths)        # ["Stable 94% occupancy", "Strong AFFO coverage 1.3x", ...]
print(conclusion.screening_checklist)
```

---

## Data Models (`lynx_realestate.models`)

All models are Python `dataclasses`.  Every numeric field defaults to `None`
(meaning "not available") unless otherwise noted.

### Enums

| Enum | Values |
|---|---|
| `CompanyTier` | `MEGA`, `LARGE`, `MID`, `SMALL`, `MICRO`, `NANO` |
| `CompanyStage` | `PRE_DEVELOPMENT`, `DEVELOPMENT`, `LEASE_UP`, `STABILIZED`, `NET_LEASE` |
| `PropertyType` | `RESIDENTIAL`, `OFFICE`, `RETAIL`, `INDUSTRIAL`, `HOTEL`, `HEALTHCARE`, `SELF_STORAGE`, `DATA_CENTER`, `INFRASTRUCTURE`, `DIVERSIFIED`, `NET_LEASE`, `OTHER` |
| `JurisdictionTier` | `TIER_1` (Low Risk), `TIER_2` (Moderate Risk), `TIER_3` (High Risk), `UNKNOWN` |
| `Relevance` | `CRITICAL`, `IMPORTANT`, `RELEVANT`, `CONTEXTUAL`, `IRRELEVANT` |

### Core Dataclasses

#### `CompanyProfile`

Company identity and classification.

| Field | Type | Description |
|---|---|---|
| `ticker` | `str` | Resolved ticker symbol. |
| `name` | `str` | Company name. |
| `isin` | `Optional[str]` | ISIN code if resolved. |
| `sector` | `Optional[str]` | Sector (e.g. `"Real Estate"`). |
| `industry` | `Optional[str]` | Industry (e.g. `"REIT—Retail"`). |
| `country` | `Optional[str]` | Country of domicile. |
| `exchange` | `Optional[str]` | Primary exchange. |
| `currency` | `Optional[str]` | Reporting currency. |
| `market_cap` | `Optional[float]` | Market capitalization. |
| `description` | `Optional[str]` | Company description from filings. |
| `website` | `Optional[str]` | Corporate website. |
| `employees` | `Optional[int]` | Number of employees. |
| `tier` | `CompanyTier` | Market-cap tier (default `NANO`). |
| `stage` | `CompanyStage` | Real-estate development stage (default `STABILIZED`). |
| `primary_property_type` | `PropertyType` | Primary property type (default `OTHER`). |
| `jurisdiction_tier` | `JurisdictionTier` | Jurisdiction risk tier (default `UNKNOWN`). |
| `jurisdiction_country` | `Optional[str]` | Country used for jurisdiction classification. |

#### `ValuationMetrics`

Traditional and REIT-specific valuation ratios.

Key fields: `pe_trailing`, `pe_forward`, `pb_ratio`, `ps_ratio`, `p_fcf`,
`ev_ebitda`, `ev_revenue`, `peg_ratio`, `dividend_yield`, `earnings_yield`,
`enterprise_value`, `market_cap`, `price_to_tangible_book`, `price_to_ncav`,
`p_ffo`, `p_affo`, `p_nav`, `implied_cap_rate`, `cash_to_market_cap`,
`nav_per_share`, `fcf_yield`, `ffo_yield`.

The REIT-specific fields (`p_ffo`, `p_affo`, `p_nav`, `implied_cap_rate`,
`ffo_yield`) replace the traditional earnings multiples as the primary
valuation anchors for REITs.

#### `ProfitabilityMetrics`

Margins and returns, plus REIT-specific operating metrics.

Key fields: `roe`, `roa`, `roic`, `gross_margin`, `operating_margin`,
`net_margin`, `fcf_margin`, `ebitda_margin`, `noi`, `noi_margin`, `ffo`,
`ffo_per_share`, `affo`, `affo_per_share`, `ffo_margin`,
`same_store_noi_growth`, `occupancy_rate`, `implied_cap_rate`, `croci`,
`ocf_to_net_income`.

NOI (Net Operating Income), FFO (Funds From Operations), AFFO (Adjusted FFO),
same-store NOI growth and occupancy are the cash-earnings and operating
indicators that drive REIT total return.

#### `SolvencyMetrics`

Balance sheet health and REIT-specific leverage metrics.

Key fields: `debt_to_equity`, `debt_to_ebitda`, `debt_to_gross_assets`,
`current_ratio`, `quick_ratio`, `interest_coverage`, `fixed_charge_coverage`,
`altman_z_score`, `net_debt`, `total_debt`, `total_cash`, `cash_burn_rate`,
`cash_runway_years`, `working_capital`, `cash_per_share`,
`tangible_book_value`, `ncav`, `ncav_per_share`, `quarterly_burn_rate`,
`burn_as_pct_of_market_cap`, `debt_per_share`, `net_debt_per_share`,
`debt_service_coverage`, `weighted_avg_debt_maturity`, `pct_fixed_rate_debt`.

The REIT-specific additions (`debt_to_gross_assets`, `fixed_charge_coverage`,
`weighted_avg_debt_maturity`, `pct_fixed_rate_debt`) capture leverage and
refinancing risk that drive REIT credit quality.

#### `GrowthMetrics`

Revenue, FFO / AFFO, and dilution growth rates.

Key fields: `revenue_growth_yoy`, `revenue_cagr_3y`, `revenue_cagr_5y`,
`earnings_growth_yoy`, `earnings_cagr_3y`, `earnings_cagr_5y`,
`fcf_growth_yoy`, `ffo_growth_yoy`, `ffo_cagr_3y`, `affo_growth_yoy`,
`book_value_growth_yoy`, `dividend_growth_5y`, `distribution_growth_5y`,
`shares_growth_yoy`, `shares_growth_3y_cagr`, `fully_diluted_shares`,
`dilution_ratio`, `same_store_noi_growth_yoy`, `acquisition_growth_yoy`,
`capex_to_revenue`, `capex_to_ocf`, `reinvestment_rate`,
`dividend_payout_ratio`, `affo_payout_ratio`, `ffo_payout_ratio`,
`dividend_coverage`, `shareholder_yield`, `fcf_per_share`, `ocf_per_share`.

#### `EfficiencyMetrics`

Operational efficiency ratios.

Key fields: `asset_turnover`, `inventory_turnover`, `receivables_turnover`,
`days_sales_outstanding`, `days_inventory`, `cash_conversion_cycle`,
`fcf_conversion`, `capex_intensity`, `g_and_a_as_pct_of_revenue`.

#### `RealEstateQualityIndicators`

Composite quality score and qualitative assessments for REIT portfolio,
operations, and balance sheet.

Key fields: `quality_score` (0-100), `management_quality`,
`insider_ownership_pct`, `management_track_record`,
`jurisdiction_assessment`, `jurisdiction_score`, `portfolio_quality`,
`portfolio_diversification`, `occupancy_assessment`,
`lease_duration_assessment` (WALT), `tenant_concentration`,
`same_store_noi_trend`, `cap_rate_assessment`, `financial_position`,
`dilution_risk`, `share_structure_assessment`, `catalyst_density`,
`near_term_catalysts` (list), `strategic_backing`,
`competitive_position`, `asset_backing`, `niche_position`,
`insider_alignment`, `revenue_predictability`,
`roic_history` (list), `gross_margin_history` (list).

#### `IntrinsicValue`

Intrinsic value estimates using multiple methods.

Key fields: `dcf_value`, `graham_number`, `lynch_fair_value`, `ncav_value`,
`asset_based_value`, `nav_per_share`, `ffo_multiple_value`,
`affo_multiple_value`, `current_price`, `margin_of_safety_dcf`,
`margin_of_safety_graham`, `margin_of_safety_ncav`,
`margin_of_safety_asset`, `margin_of_safety_nav`, `margin_of_safety_ffo`,
`margin_of_safety_affo`, `primary_method`, `secondary_method`.

The `primary_method` and `secondary_method` fields indicate which valuation
approach is most appropriate for the company's stage (e.g. `"p_ffo_multiple"`
for stabilized REITs, `"nav"` for development-stage, `"asset_based"` for
pre-development).

#### `ShareStructure`

Share count, dilution, and ownership breakdown.

Key fields: `shares_outstanding`, `fully_diluted_shares`,
`warrants_outstanding`, `options_outstanding`, `insider_ownership_pct`,
`institutional_ownership_pct`, `float_shares`,
`share_structure_assessment`, `warrant_overhang_risk`.

Note: `fully_diluted_shares` for REITs should include operating partnership
(OP) units when available, as these are convertible into common shares.

#### `InsiderTransaction`

A single insider buy/sell transaction.

Fields: `insider`, `position`, `transaction_type`, `shares`, `value`, `date`.

#### `MarketIntelligence`

Market sentiment, insider activity, institutional holdings, technicals,
rate / macro context, and sector ETF context.

Groups of fields:
- **Insider activity:** `insider_transactions` (list of `InsiderTransaction`),
  `net_insider_shares_3m`, `insider_buy_signal`.
- **Institutional holders:** `top_holders`, `institutions_count`, `institutions_pct`.
- **Analyst consensus:** `analyst_count`, `recommendation`, `target_high`,
  `target_low`, `target_mean`, `target_upside_pct`.
- **Short interest:** `shares_short`, `short_pct_of_float`, `short_ratio_days`,
  `short_squeeze_risk`.
- **Price technicals:** `price_current`, `price_52w_high`, `price_52w_low`,
  `pct_from_52w_high`, `pct_from_52w_low`, `price_52w_range_position`,
  `sma_50`, `sma_200`, `above_sma_50`, `above_sma_200`, `golden_cross`,
  `beta`, `avg_volume`, `volume_10d_avg`, `volume_trend`.
- **Projected dilution:** `projected_dilution_annual_pct`,
  `projected_shares_in_2y`, `financing_warning`.
- **Rate / macro context (REITs are rate-sensitive):** `benchmark_rate_name`,
  `benchmark_rate_value`, `rate_currency`, `rate_52w_high`, `rate_52w_low`,
  `rate_52w_position`, `rate_ytd_change`.
- **Sector ETF context:** `sector_etf_name`, `sector_etf_ticker`,
  `sector_etf_price`, `sector_etf_3m_perf`, `peer_etf_name`,
  `peer_etf_ticker`, `peer_etf_price`, `peer_etf_3m_perf`.
- **Risk warnings:** `risk_warnings` (list), `disclaimers` (list).

#### `FinancialStatement`

One annual fiscal period.

Fields: `period`, `revenue`, `cost_of_revenue`, `gross_profit`,
`operating_income`, `net_income`, `ebitda`, `interest_expense`,
`total_assets`, `total_liabilities`, `total_equity`, `total_debt`,
`total_cash`, `current_assets`, `current_liabilities`,
`operating_cash_flow`, `capital_expenditure`, `free_cash_flow`,
`dividends_paid`, `shares_outstanding`, `eps`, `book_value_per_share`,
`real_estate_assets`, `accumulated_depreciation`, `rental_income`,
`property_operating_expenses`.

The REIT-specific additions (`real_estate_assets`, `accumulated_depreciation`,
`rental_income`, `property_operating_expenses`) are used to compute NOI,
debt-to-gross-assets, and NAV.

#### `AnalysisConclusion`

Scored verdict produced by `generate_conclusion`.

Fields: `overall_score`, `verdict`, `summary`, `category_scores`,
`category_summaries`, `strengths`, `risks`, `tier_note`, `stage_note`,
`screening_checklist`.

#### `Filing`

An SEC/SEDAR filing reference.

Fields: `form_type`, `filing_date`, `period`, `url`, `description`,
`local_path`.

#### `NewsArticle`

A news article reference.

Fields: `title`, `url`, `published`, `source`, `summary`, `local_path`.

#### `AnalysisReport`

The main container returned by analysis functions.

| Field | Type | Description |
|---|---|---|
| `profile` | `CompanyProfile` | Always populated. |
| `valuation` | `Optional[ValuationMetrics]` | Valuation ratios. |
| `profitability` | `Optional[ProfitabilityMetrics]` | Margin, NOI, FFO, AFFO metrics. |
| `solvency` | `Optional[SolvencyMetrics]` | Balance sheet health and leverage. |
| `growth` | `Optional[GrowthMetrics]` | Growth rates and dilution. |
| `efficiency` | `Optional[EfficiencyMetrics]` | Operational efficiency. |
| `real_estate_quality` | `Optional[RealEstateQualityIndicators]` | Composite portfolio quality score. |
| `intrinsic_value` | `Optional[IntrinsicValue]` | Intrinsic value estimates. |
| `share_structure` | `Optional[ShareStructure]` | Share count and ownership. |
| `market_intelligence` | `Optional[MarketIntelligence]` | Sentiment, technicals, rate context. |
| `financials` | `list[FinancialStatement]` | Annual financial statements. |
| `filings` | `list[Filing]` | SEC/SEDAR filings. |
| `news` | `list[NewsArticle]` | Recent news articles. |
| `fetched_at` | `str` | ISO timestamp of when data was fetched. |

---

## Classification Helpers (`lynx_realestate.models`)

#### `classify_tier`

```python
def classify_tier(market_cap: Optional[float]) -> CompanyTier
```

Classify by market capitalization:

| Threshold | Tier |
|---|---|
| >= $200B | Mega Cap |
| >= $10B | Large Cap |
| >= $2B | Mid Cap |
| >= $300M | Small Cap |
| >= $50M | Micro Cap |
| < $50M or None | Nano Cap |

#### `classify_stage`

```python
def classify_stage(
    description: Optional[str],
    revenue: Optional[float],
    info: Optional[dict] = None,
) -> CompanyStage
```

Classify the real-estate company development stage by keyword matching
against the company description.  Companies with revenue > $10M and
net-lease keywords are classified as `NET_LEASE`; other revenue-generating
companies default to `STABILIZED`.  Falls back to industry-based heuristics
from `info` if no keywords match.

#### `classify_property_type`

```python
def classify_property_type(
    description: Optional[str],
    industry: Optional[str] = None,
) -> PropertyType
```

Identify primary property type from description and industry text using
keyword frequency scoring.  Uses word-boundary matching for short keywords
to avoid false positives.

#### `classify_jurisdiction`

```python
def classify_jurisdiction(
    country: Optional[str],
    description: Optional[str] = None,
) -> JurisdictionTier
```

Classify jurisdiction risk for real-estate markets:

- **Tier 1 (Low Risk):** United States, Canada, Australia, New Zealand, United Kingdom, Ireland, Germany, France, Netherlands, Belgium, Switzerland, Sweden, Norway, Denmark, Finland, Japan, Singapore, Hong Kong.
- **Tier 2 (Moderate Risk):** Spain, Italy, Portugal, Poland, Czech Republic, Hungary, Greece, Mexico, Chile, Brazil, Uruguay, South Korea, Taiwan, Malaysia, Thailand, South Africa, UAE, Israel.
- **Tier 3 (High Risk):** Everything else.

---

## Metrics Calculator (`lynx_realestate.metrics.calculator`)

All `calc_*` functions accept `info` (yfinance info dict), `statements`
(list of `FinancialStatement`), and tier/stage classification.  They return
the corresponding metrics dataclass with all fields computed from available
data.

| Function | Returns | Description |
|---|---|---|
| `calc_valuation(info, statements, tier, stage)` | `ValuationMetrics` | P/E, P/B, EV/EBITDA, P/FCF, cash-to-market-cap, tangible book, NCAV. REIT-specific: P/FFO, P/AFFO, P/NAV, implied cap rate, FFO yield. |
| `calc_profitability(info, statements, tier, stage)` | `ProfitabilityMetrics` | ROE, ROA, ROIC, gross/operating/net/FCF/EBITDA margins. REIT-specific: NOI, NOI margin, FFO, AFFO, same-store NOI growth, occupancy rate. |
| `calc_solvency(info, statements, tier, stage)` | `SolvencyMetrics` | D/E, Debt/EBITDA, current/quick ratios, Altman Z, cash runway, working capital. REIT-specific: debt-to-gross-assets, fixed-charge coverage, weighted-avg debt maturity, % fixed-rate debt. |
| `calc_growth(statements, tier, stage)` | `GrowthMetrics` | Revenue/earnings YoY and CAGR (3y, 5y). FFO / AFFO growth. Share dilution YoY and 3y CAGR. Distribution growth. AFFO payout. |
| `calc_efficiency(info, statements, tier)` | `EfficiencyMetrics` | Asset turnover, FCF conversion, G&A as % of revenue. |
| `calc_share_structure(info, statements, growth, tier, stage)` | `ShareStructure` | Outstanding/fully-diluted shares (incl. OP units), insider/institutional ownership %, structure assessment. |
| `calc_real_estate_quality(profitability, growth, solvency, share_structure, statements, info, tier, stage)` | `RealEstateQualityIndicators` | Composite quality score (0-100) based on portfolio quality, occupancy, lease duration (WALT), tenant concentration, leverage, distribution coverage, and insider alignment. |
| `calc_intrinsic_value(info, statements, growth, solvency, tier, stage, discount_rate=0.10, terminal_growth=0.03)` | `IntrinsicValue` | DCF, Graham number, Lynch fair value, NCAV, asset-based value, NAV/share, P/FFO-multiple fair value, P/AFFO-multiple fair value. Method selection is stage-aware. |
| `calc_market_intelligence(info, ticker_obj, solvency, share_structure, growth, tier, stage)` | `MarketIntelligence` | Insider transactions, institutional holders, analyst consensus, short interest, price technicals, rate context, projected dilution, risk warnings. |

---

## Relevance System (`lynx_realestate.metrics.relevance`)

#### `get_relevance`

```python
def get_relevance(
    metric_key: str,
    tier: CompanyTier,
    category: str = "valuation",
    stage: CompanyStage = CompanyStage.STABILIZED,
) -> Relevance
```

Look up the relevance level of a metric given the company's tier and stage.

**Stage overrides take precedence** over tier-based lookups, because
development stage is the primary analytical axis for REITs and real-estate
operating companies.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `metric_key` | `str` | Metric field name (e.g. `"p_ffo"`, `"occupancy_rate"`). |
| `tier` | `CompanyTier` | Company size tier. |
| `category` | `str` | One of `"valuation"`, `"profitability"`, `"solvency"`, `"growth"`, `"real_estate_quality"`, `"share_structure"`. |
| `stage` | `CompanyStage` | Real-estate development stage. |

**Returns:** `Relevance` enum value.

### Relevance Levels

| Level | Meaning | Visual Treatment |
|---|---|---|
| `CRITICAL` | Must-check metric for this stage/tier. | `***CRITICAL***` marker (red). |
| `IMPORTANT` | High-priority metric, between critical and relevant. | Bold display with emphasis. |
| `RELEVANT` | Standard metric, displayed normally. | Normal display. |
| `CONTEXTUAL` | Informational only, not a primary decision driver. | Dimmed. |
| `IRRELEVANT` | Not meaningful for this stage/tier. | Hidden or struck-through. |

### Severity Markers

Console display uses the following severity markers with color coding:

| Marker | Color | Meaning |
|---|---|---|
| `***CRITICAL***` | Red | Critical issue requiring immediate attention. |
| `*WARNING*` | Orange | Warning condition. |
| `[WATCH]` | Yellow | Metric to monitor. |
| `[OK]` | Green | Metric within acceptable range. |
| `[STRONG]` | Grey | Strong/healthy metric. |

### Impact Column

Metric tables in console display include an **Impact** column that shows
how each metric affects the overall analysis score. This provides
transparency into the scoring methodology and helps users understand
which metrics are driving the verdict.

**Stage-driven examples:**

- `occupancy_rate` is `CRITICAL` for Stabilized, Lease-Up, Net Lease; `CONTEXTUAL` for Pre-Development and Development.
- `p_ffo` is `CRITICAL` for Stabilized and Net Lease; `IRRELEVANT` for Pre-Development and Development.
- `affo_payout_ratio` is `CRITICAL` for Stabilized and Net Lease; `CONTEXTUAL` for Lease-Up; `IRRELEVANT` for Pre-Development.
- `cash_runway_years` is `CRITICAL` for Pre-Development and Development; `CONTEXTUAL` for Stabilized; `IRRELEVANT` for Net Lease.
- `weighted_avg_debt_maturity` is `IMPORTANT` for Stabilized and Net Lease; `RELEVANT` for Lease-Up.

---

## Storage (`lynx_realestate.core.storage`)

Two isolated data directories: `data/` (production) and `data_test/` (testing).

#### `set_mode`

```python
def set_mode(mode: str) -> None
```

Set the storage mode.  `mode` must be `"production"` or `"testing"`.

In testing mode, cache reads are disabled (always returns `None`/`False`)
to ensure fresh data.

#### `has_cache`

```python
def has_cache(ticker: str) -> bool
```

Returns `True` if a cached `analysis_latest.json` exists for this ticker.
Always returns `False` in testing mode.

#### `load_cached_report`

```python
def load_cached_report(ticker: str) -> Optional[dict]
```

Load the latest cached analysis as a raw dict, or `None` if unavailable.

#### `save_analysis_report`

```python
def save_analysis_report(ticker: str, report_dict: dict) -> Path
```

Save an analysis report dict.  Creates both a timestamped file
(`analysis_YYYYMMDD_HHMMSS.json`) and an `analysis_latest.json` symlink.
Returns the path to the timestamped file.

#### `list_cached_tickers`

```python
def list_cached_tickers() -> list[dict]
```

List all cached tickers with metadata.  Each dict contains:
`ticker`, `path`, `name`, `tier`, `stage`, `fetched_at`, `age_hours`,
`files` (count), `size_mb`.

#### `drop_cache_ticker`

```python
def drop_cache_ticker(ticker: str) -> bool
```

Delete all cached data for a ticker.  Returns `True` if data existed.

#### `drop_cache_all`

```python
def drop_cache_all() -> int
```

Delete all cached data.  Returns the number of ticker directories removed.

---

## Ticker Resolution (`lynx_realestate.core.ticker`)

#### `resolve_identifier`

```python
def resolve_identifier(identifier: str) -> tuple[str, str | None]
```

Resolve a user-provided identifier to a `(ticker, isin)` tuple.

Accepts:
- **Ticker symbols:** `SPG`, `O`, `PLD`, `REI.UN`
- **ISIN codes:** 12-character format
- **Company names:** `"Simon Property Group"`, `"Prologis"`

Resolution strategy:
1. ISIN -- search via yfinance, return best equity match.
2. Company name (contains spaces or > 12 chars) -- search.
3. Direct ticker probe -- check if the symbol has price data.
4. Suffix scan -- try common exchange suffixes (`.UN`, `.TO`, `.L`, `.DE`, etc.).
5. Broadened search -- append "REIT" or "real estate" to query.

Raises `ValueError` if no match is found.

#### `search_companies`

```python
def search_companies(query: str, max_results: int = 10) -> list[SearchResult]
```

Search for companies by name or ticker via yfinance.

Returns a list of `SearchResult` dataclasses:

```python
@dataclass
class SearchResult:
    symbol: str
    name: str
    exchange: str
    quote_type: str
    score: float = 0.0
```

---

## Export (`lynx_realestate.export`)

#### `export_report`

```python
def export_report(
    report: AnalysisReport,
    fmt: ExportFormat,
    output_path: Optional[Path] = None,
) -> Path
```

Export an analysis report to the specified format.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `report` | `AnalysisReport` | The completed analysis report. |
| `fmt` | `ExportFormat` | `ExportFormat.TXT`, `ExportFormat.HTML`, or `ExportFormat.PDF`. |
| `output_path` | `Optional[Path]` | Output file path.  Defaults to `data/<TICKER>/report_<timestamp>.<ext>`. |

**Returns:** `Path` to the written file.

```python
from lynx_realestate.export import ExportFormat
```

---

## Sector Insights (`lynx_realestate.metrics.sector_insights`)

#### `get_sector_insight`

```python
def get_sector_insight(sector: str | None) -> SectorInsight | None
```

Get sector-level analysis guidance.  Returns `None` if the sector is not
recognized.

```python
@dataclass
class SectorInsight:
    sector: str
    overview: str
    critical_metrics: list[str]
    key_risks: list[str]
    what_to_watch: list[str]
    typical_valuation: str
```

Available sectors: `"Real Estate"` (with aliases `"Real-Estate"`, `"REITs"`,
`"REIT"`, `"Real Estate—REIT"`).

#### `get_industry_insight`

```python
def get_industry_insight(industry: str | None) -> IndustryInsight | None
```

Get industry-level analysis guidance.  Returns `None` if the industry is
not recognized.

```python
@dataclass
class IndustryInsight:
    industry: str
    sector: str
    overview: str
    critical_metrics: list[str]
    key_risks: list[str]
    what_to_watch: list[str]
    typical_valuation: str
```

Available industries: `"REIT—Residential"`, `"REIT—Office"`,
`"REIT—Retail"`, `"REIT—Industrial"`, `"REIT—Hotel & Motel"`,
`"REIT—Healthcare Facilities"`, `"REIT—Specialty"`,
`"REIT—Diversified"`, `"Real Estate Services"`,
`"Real Estate—Development"`.

---

## REIT-Specific Metric Reference

Brief interpretation of the REIT-specific metrics used throughout the
analysis:

- **FFO (Funds From Operations)** — net income + real-estate depreciation
  − gains on sale of property. NAREIT-defined, the standard REIT earnings
  measure.  Adds back the non-cash depreciation that distorts GAAP earnings
  for property-heavy businesses.
- **AFFO (Adjusted FFO)** — FFO − recurring maintenance capex −
  straight-line rent adjustments. The best single measure of distributable
  cash; the correct denominator for REIT distribution-coverage analysis.
- **NOI (Net Operating Income)** — rental revenue − property operating
  expenses.  The clean property-level cash profit, unburdened by corporate
  overhead, financing, or depreciation.
- **Implied Cap Rate** — NOI / Enterprise Value.  The cap rate implied by
  the current market price; compare to private-market transaction cap rates
  to judge whether the REIT is trading cheap or rich relative to the
  underlying property values.
- **Occupancy Rate** — leased area / total leasable area. Leading
  indicator of NOI trajectory.  95%+ is strong for apartments and
  industrial; 85-90% is healthy for office; net-lease REITs target 99%+.
- **Same-Store NOI Growth** — NOI growth from properties owned in both
  periods.  The cleanest organic growth signal; strips out acquisitions,
  dispositions, and developments.
- **AFFO Payout Ratio** — distributions / AFFO.  Must stay below 1.0x for
  the distribution to be self-funded.  80-90% is typical for growth-oriented
  REITs; >95% leaves little cushion.
- **Debt-to-Gross-Assets** — total debt / gross (undepreciated) real estate
  assets.  The REIT-specific leverage ratio; 40-50% is typical, >60% is
  aggressive.
- **Fixed-Charge Coverage** — EBITDA / (interest + preferred dividends +
  ground rent).  Stricter than interest coverage.  Bond covenants typically
  require >1.5x.
- **Weighted-Average Debt Maturity** — average years until debt comes due,
  weighted by balance.  Longer is better (less refinancing risk); quality
  REITs ladder maturities at 6-8+ years.
- **% Fixed-Rate Debt** — share of total debt at fixed rates.  Protects
  the REIT from rate spikes; 80%+ is conservative, <60% exposes
  distributions to rate risk.

---

## Usage Examples

### 1. Basic Analysis

```python
from lynx_realestate.core.analyzer import run_full_analysis
from lynx_realestate.core.conclusion import generate_conclusion

report = run_full_analysis("SPG")

print(f"{report.profile.name} ({report.profile.ticker})")
print(f"Tier: {report.profile.tier.value}")
print(f"Stage: {report.profile.stage.value}")
print(f"Property type: {report.profile.primary_property_type.value}")
print(f"Jurisdiction: {report.profile.jurisdiction_tier.value}")

conclusion = generate_conclusion(report)
print(f"Score: {conclusion.overall_score}/100 -- {conclusion.verdict}")
```

### 2. Progressive Analysis with Callback

```python
from lynx_realestate.core.analyzer import run_progressive_analysis

def progress_handler(stage: str, report):
    if stage == "profile":
        print(f"Analyzing: {report.profile.name}")
    elif stage == "profitability":
        occ = report.profitability.occupancy_rate
        if occ is not None:
            print(f"Occupancy: {occ:.1%}")
    elif stage == "real_estate_quality":
        score = report.real_estate_quality.quality_score
        if score is not None:
            print(f"Quality score: {score:.0f}/100")
    elif stage == "complete":
        print("Analysis complete.")

report = run_progressive_analysis("O", on_progress=progress_handler)
```

### 3. Accessing Specific Metrics

```python
report = run_full_analysis("PLD")

# Valuation -- the primary REIT anchors
if report.valuation:
    print(f"P/FFO: {report.valuation.p_ffo:.1f}")
    print(f"P/AFFO: {report.valuation.p_affo:.1f}")
    print(f"Implied cap rate: {report.valuation.implied_cap_rate:.2%}")
    print(f"Dividend yield: {report.valuation.dividend_yield:.2%}")

# Profitability -- operating fundamentals
if report.profitability:
    print(f"NOI margin: {report.profitability.noi_margin:.1%}")
    print(f"Occupancy: {report.profitability.occupancy_rate:.1%}")
    print(f"Same-store NOI growth: {report.profitability.same_store_noi_growth:.2%}")

# Solvency -- leverage and refinancing
if report.solvency:
    print(f"Debt / Gross Assets: {report.solvency.debt_to_gross_assets:.1%}")
    print(f"Fixed-charge coverage: {report.solvency.fixed_charge_coverage:.2f}x")
    print(f"Weighted-avg debt maturity: {report.solvency.weighted_avg_debt_maturity:.1f} yrs")

# Growth -- distribution sustainability
if report.growth:
    print(f"AFFO payout: {report.growth.affo_payout_ratio:.1%}")
    print(f"Distribution growth 5y: {report.growth.distribution_growth_5y:.2%}")

# Market intelligence
if report.market_intelligence:
    mi = report.market_intelligence
    print(f"Insider signal: {mi.insider_buy_signal}")
    print(f"Analyst target upside: {mi.target_upside_pct:.1%}")
    print(f"Benchmark rate ({mi.benchmark_rate_name}): {mi.benchmark_rate_value}")
```

### 4. Checking Metric Relevance

```python
from lynx_realestate.metrics.relevance import get_relevance
from lynx_realestate.models import CompanyTier, CompanyStage, Relevance

# For a large-cap stabilized REIT, which metrics matter?
tier = CompanyTier.LARGE
stage = CompanyStage.STABILIZED

# P/FFO is CRITICAL for stabilized REITs
rel = get_relevance("p_ffo", tier, "valuation", stage)
assert rel == Relevance.CRITICAL

# Occupancy is CRITICAL for stabilized REITs
rel = get_relevance("occupancy_rate", tier, "profitability", stage)
assert rel == Relevance.CRITICAL

# Cash runway is IRRELEVANT for stabilized REITs (they generate cash)
rel = get_relevance("cash_runway_years", tier, "solvency", stage)
assert rel in (Relevance.IRRELEVANT, Relevance.CONTEXTUAL)
```

### 5. Exporting Reports

```python
from pathlib import Path
from lynx_realestate.core.analyzer import run_full_analysis
from lynx_realestate.export import ExportFormat, export_report

report = run_full_analysis("EQIX")

# Export as HTML (default path: data/EQIX/report_<timestamp>.html)
html_path = export_report(report, ExportFormat.HTML)
print(f"HTML report: {html_path}")

# Export as plain text to a custom path
txt_path = export_report(report, ExportFormat.TXT, Path("./eqix_report.txt"))
print(f"Text report: {txt_path}")

# Export as PDF
pdf_path = export_report(report, ExportFormat.PDF)
print(f"PDF report: {pdf_path}")
```
