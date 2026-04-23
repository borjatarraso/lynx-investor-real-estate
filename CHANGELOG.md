# Changelog

## [4.0] - 2026-04-23

Part of **Lince Investor Suite v4.0** coordinated release.

### Added
- URL-safety enforcement for every RSS-sourced news URL and every
  `webbrowser.open(...)` site — powered by
  `lynx_investor_core.urlsafe`.
- Sector-specific ASCII art in easter-egg visuals (replaces the shared
  pickaxe motif that leaked into non-mining sectors).

### Changed
- Aligned every user-visible sector string with the package's real
  sector: titles, subtitles, app class names, splash taglines, news
  keywords, User-Agent headers, themes, export headers, and fortune
  quotes no longer carry template leftovers.
- Depends on `lynx-investor-core>=4.0`.

All notable changes to Lynx Real Estate Analysis are documented here.

## [3.0] - 2026-04-22

Part of **Lince Investor Suite v3.0** coordinated release.

### Added
- Uniform PageUp / PageDown navigation across every UI mode (GUI, TUI,
  interactive, console). Scrolling never goes above the current output
  in interactive and console mode; Shift+PageUp / Shift+PageDown remain
  reserved for the terminal emulator's own scrollback.
- Sector-mismatch warning now appends a `Suggestion: use
  'lynx-investor-<other>' instead.` line sourced from
  `lynx_investor_core.sector_registry`. The original warning text is
  preserved as-is.

### Changed
- TUI wires `lynx_investor_core.pager.PagingAppMixin` and
  `tui_paging_bindings()` into the main application.
- Graphical mode binds `<Prior>` / `<Next>` / `<Control-Home>` /
  `<Control-End>` via `bind_tk_paging()`.
- Interactive mode pages long output through `console_pager()` /
  `paged_print()`.
- Depends on `lynx-investor-core>=2.0`.

## 2.0 (2026-04-22)

- Initial Real Estate agent — cloned structure from Lynx Energy; metrics re-specialized for REITs (FFO, AFFO, NOI, cap rate, same-store NOI, occupancy, debt maturity, fixed-charge coverage).

## [2.0] - 2026-04-19

Major release — **Lince Investor Suite v2.0** unified release.

### Changed
- **Unified suite**: All Lince Investor projects now share consistent
  version numbering, logos, keybindings, CLI patterns, export styling,
  installation instructions, and documentation structure.
- **Export styling**: Monospace HTML (Consolas family), 90-char TXT width,
  unified with other suite projects.
- **Documentation**: Standardized installation section with dependency
  table matching other suite projects.

## [1.0] - 2026-04-19

### Release
- Bumped to v1.0 — first stable release, unified with Lince Investor suite

## [0.5] - 2026-04-19

### Fixed (30+ bugs from deep audit)

**Critical / High:**
- **Profitability table crash**: Pre-revenue companies (Pre-Development / Development) caused a Rich `MissingColumn` crash — table had 4 columns but the N/A row only passed 3 values
- **FCF yield only calculated for positive FCF**: Negative FCF (cash burn) was silently dropped, preventing scoring of cash-burning companies. Now negative yields are calculated and scored
- **Altman Z-Score explosion**: When `total_liabilities` was 0, the formula defaulted to dividing by 1, producing astronomical Z-scores. Now skips Z-Score when liabilities data is missing
- **Negative D/E rewarded as strength**: A negative debt-to-equity ratio (meaning negative equity/insolvency) was given +15 bonus points. Now only zero debt gets the bonus; negative D/E gets no reward
- **Conservative balance sheet false positive**: Companies with negative equity (D/E < 0) were listed as a "strength". Now requires `0 <= D/E < 0.2`
- **News RSS search used "mining stock"**: Google News queries returned irrelevant results for REITs. Changed to "REIT stock"
- **EDGAR User-Agent said "LynxMining"**: SEC EDGAR requests used wrong product identifier, risking request blocks

**Medium:**
- **OCF/Net Income ratio distorted**: `abs()` on denominator made loss-making companies appear to have high earnings quality. Now only calculated when net income > 0
- **Burn rate required 2 financial statements**: Companies with only 1 year of data couldn't get burn rate calculated. Removed artificial requirement
- **Projected dilution was 2-year rate labeled as annual**: `projected_dilution_annual_pct` stored total 2-year dilution, not annual. Now divides by 2
- **P/Tangible Book not computed for Mid Cap**: The tier gate excluded MID tier despite relevance system marking it as RELEVANT. Added MID to computation scope
- **Ticker error message suggested irrelevant tickers**: old examples replaced with REIT tickers (SPG, O, PLD, EQIX, WELL)
- **9 GUI metric keys empty**: Solvency, growth, and share structure rows bypassed relevance filtering. All keys populated
- **GUI share structure info buttons disabled**: `metric_key=""` hardcoded; changed to pass actual key
- **GUI thread safety**: tkinter BooleanVars read from background thread; now read on main thread before spawning worker
- **GUI macOS mouse wheel**: `e.delta // 120` produced 0 on macOS; now platform-detected
- **Duplicate except clause in interactive mode**: Unreachable `except Exception` dead code removed

**Low (truthiness bugs — 0.0 treated as "no data"):**
- `cash_runway_years = 0.0` showed "N/A" instead of "0.0 years" (hid critical data)
- `cash_per_share = 0.0` showed "N/A" instead of "$0.00"
- `insider_ownership_pct = 0.0` showed "N/A" instead of "0.00%"
- `institutional_ownership_pct = 0.0` showed "N/A"
- `pct_from_52w_high = 0.0` showed empty string
- `institutions_pct = 0.0` hid the percentage display
- `current_price = 0.0` showed "N/A" in intrinsic value table
- All fixed to use `is not None` checks

### Changed
- Version bumped to 0.5 (pre-release)
- Total: 173 tests passing

## [0.4] - 2026-04-19

### Added
- **Impact column** in all metric tables showing relevance level with color coding:
  - Critical (blinking red), Important (orange), Relevant (yellow), Informational (green), Irrelevant (grey/hidden)
- **IMPORTANT relevance level** between CRITICAL and RELEVANT for key metrics (P/FFO, D/Gross Assets, ROE, EV/Revenue, share dilution) — displayed with `>` prefix and orange Impact tag
- **Severity markers** updated to final format across all 53 assessment functions:
  - `***CRITICAL***` — bold red uppercase
  - `*WARNING*` — orange text
  - `[WATCH]` — yellow text in brackets
  - `[OK]` — green text in brackets
  - `[STRONG]` — grey/silver text in brackets
- **12 new unit tests**: 7 for new REIT metrics (FCF yield, CROCI, OCF/NI, debt/share, capex/revenue, FCF/share, dividend coverage), 5 for IMPORTANT relevance level
- Updated Robot Framework tests for IMPORTANT level and new metrics
- Updated API documentation with all new fields and Impact column behavior

### Fixed
- **Financial statements table** truncation — increased Period column width and enabled table expansion
- **Insider transactions table** — dates trimmed to YYYY-MM-DD, columns use ratio-based widths to prevent truncation
- **Header legend** updated to show `>` = important marker alongside `*` = critical

### Changed
- All 4 UI modes (Console, TUI, GUI, Interactive) handle the IMPORTANT relevance level
- Version bumped to 0.4
- Total: 173 tests passing, 53 metric explanations

## [0.3] - 2026-04-19

### Added
- **15 new REIT-specific metrics** across all analysis sections:
  - **Valuation**: P/FFO, P/AFFO, Implied Cap Rate, FFO Yield — the primary valuation anchors for REITs
  - **Profitability**: CROCI (Cash Return on Capital Invested), OCF/Net Income ratio (earnings quality check), NOI margin, same-store NOI growth
  - **Solvency**: Debt-to-Gross-Assets, Weighted-Average Debt Maturity, % Fixed-Rate Debt, Fixed-Charge Coverage
  - **Growth & Capital Discipline**: Capex/Revenue, Capex/OCF, Reinvestment Rate (Capex/EBITDA), AFFO Payout Ratio, FFO Payout Ratio, Dividend Coverage (FCF/Dividends), Shareholder Yield, FCF Per Share, OCF Per Share
  - **Efficiency**: FCF Conversion (FCF/EBITDA), Capex Intensity (Capex/Revenue), G&A as % of Revenue
- **Severity markers** on ALL metric assessments — color-coded with distinct formatting:
  - `***CRITICAL***` — urgent red flag, bold red uppercase text
  - `*WARNING*` — significant concern, orange text
  - `[WATCH]` — needs monitoring, yellow text
  - `[OK]` — normal range, green text
  - `[STRONG]` — excellent signal, grey/silver text
- **Impact column** added to all metric tables showing relevance level:
  - Critical — blinking red text
  - Important — orange text
  - Relevant — yellow text
  - Informational — green text
  - Irrelevant — grey text (hidden metrics)
- **New IMPORTANT relevance level** added between CRITICAL and RELEVANT for metrics that are truly important but not quite critical (P/FFO for stabilized REITs, D/EBITDA ratio, EV/Revenue, ROE, share dilution)
- **15 new assessment functions** with severity-graded thresholds tailored to REIT sector benchmarks
- **2 new screening checklist criteria** for stabilized REITs:
  - Capital Discipline (Capex <80% of OCF)
  - Distribution Covered by AFFO
- **15 new metric explanations** in the --explain system with REIT-specific context
- **Stage-aware relevance overrides** for all 15 new metrics (e.g., P/FFO is *CRITICAL* for Stabilized, *IRRELEVANT* for Pre-Development)
- **Scoring integration**: P/FFO, CROCI, Fixed-Charge Coverage, Capex/OCF, and AFFO Payout now contribute to the composite scoring across valuation, profitability, solvency, and growth categories
- Total explained metrics: 53 (up from 38)

### Changed
- All existing assessment functions (38 total) updated with severity markers between asterisks
- Version bumped to 0.3

## [0.2] - 2026-04-19

### Fixed
- **(CRITICAL) Sector validation too loose**: Generic words like "property", "lease", "building" in company descriptions caused non-real-estate companies to pass the sector gate. Regex patterns now require real-estate-specific phrases ("real estate", "REIT", "rental income", "shopping center", "medical office") instead of bare generic words
- **(CRITICAL) Diversified REITs misclassified as Net Lease**: The keyword "lease" matched "leaseback" and "leasing" in descriptions of diversified operators. Removed bare "lease" from net-lease detection; now requires exact "triple-net" or "net lease" via word-boundary regex
- **(HIGH) Pre-revenue stage check in exports used wrong enum value**: Exports checked for "Pre-Dev" but the actual enum value is "Pre-Development", causing pre-revenue profitability messages to not appear in TXT/HTML exports
- **(HIGH) Short % of Float double-scaled in exports**: `short_pct_of_float` was stored as percentage (5.0) instead of ratio (0.05), then exports called `_fmt_pct()` which multiplied by 100 again, displaying 500% instead of 5%. Now stored as ratio consistently with all other percentage fields
- **(MEDIUM) Extreme dilution penalty unreachable**: `elif dil > 0.20` was checked after `elif dil > 0.10`, making the -25 point penalty for >20% dilution unreachable. Reversed the order so extreme dilution gets the full penalty
- **(MEDIUM) Revenue-generating REITs with no stage keywords had no default**: Companies with $10M+ revenue but no specific stabilized/net-lease keywords in their description fell through to the general keyword loop. Now defaults to Stabilized when revenue threshold is met
- **(LOW) 52-week low display showed `+-X.X%`**: Hardcoded `+` prefix before percentage caused double sign when price was below 52-week low. Now uses `:+.1f` format specifier
- **(LOW) Jurisdiction substring matching false positives**: "india" in description matched "Indiana" (US state), classifying US companies as Tier 2. Now uses word-boundary regex for description matching; country field still uses substring (reliable)
- **(LOW) Orphaned screening labels in display**: 4 screening checklist labels (`positive_fcf`, `book_value_growing`, `reasonable_valuation`, `institutional_interest`) were defined but never produced by the scoring engine. Removed dead labels

### Changed
- **TUI theme renamed**: "mining-dark" / "mining-light" → "realestate-dark" / "realestate-light"
- **GUI icon updated**: Icon for quality section changed to building silhouette
- Version bumped to 0.2

### Added
- **8 new tests** for sector validation (generic property blocked, generic lease blocked, standalone "building" blocked, real estate in desc allowed, REIT in desc allowed)
- **2 new tests** for stage classification (diversified REIT not classified as net lease, revenue defaults to stabilized)
- **1 new test** for dilution scoring (extreme dilution gets full penalty)
- Total: 161 tests, all passing

## [0.1] - 2026-04-19

### Added
- Initial release of Lynx Real Estate Analysis
- **Fundamental analysis engine** specialized for REITs and real-estate operating companies:
  - Residential / Apartment REITs, Office REITs, Retail REITs, Industrial / Logistics REITs
  - Hotel / Hospitality REITs, Healthcare REITs, Self-Storage REITs, Data-Center REITs
  - Cell-Tower / Infrastructure REITs, Net-Lease REITs, Diversified REITs
  - Real-estate operating companies and real-estate services firms
- **Stage-aware analysis** (Pre-Development / Development / Lease-Up / Stabilized / Net Lease)
- **REIT-specific metrics**:
  - P/FFO, P/AFFO, P/NAV, Implied Cap Rate for valuation
  - NOI, NOI margin, FFO, AFFO, same-store NOI growth, occupancy rate
  - Debt-to-Gross-Assets, Fixed-Charge Coverage, Weighted-Average Debt Maturity
  - AFFO Payout Ratio, distribution coverage, share dilution tracking
- **4-level relevance system** (Critical / Relevant / Contextual / Irrelevant)
  - Stage overrides take precedence over tier-based lookups
  - Drives visual highlighting across all interface modes
- **Real Estate Quality Score** (0-100 composite):
  - Portfolio quality and diversification (25 pts), Occupancy and lease duration (20 pts)
  - Financial position / leverage (20 pts), Distribution coverage (15 pts)
  - Insider alignment (10 pts), Tenant concentration / catalyst density (10 pts)
- **REIT screening checklist** evaluating key quality criteria (AFFO coverage, leverage, occupancy, maturity ladder)
- **Property type detection** (Residential, Office, Retail, Industrial, Hotel, Healthcare, Self-Storage, Data Center, Infrastructure / Cell Tower, Net Lease, Diversified)
- **Jurisdiction risk classification** for real-estate markets
  - Tier 1: United States, Canada, United Kingdom, Australia, Western Europe, Japan, Singapore
  - Tier 2: Spain, Italy, Poland, Mexico, Chile, Brazil, South Korea, South Africa, UAE, Israel
  - Tier 3: All others
- **Sector validation gate**: Analysis blocked for non-real-estate companies with prominent warning
- **4 interface modes**:
  - Console CLI with progressive output
  - Interactive REPL with command-driven analysis
  - Textual TUI with themes and navigation
  - Tkinter GUI with Catppuccin Mocha dark theme
- **Export formats**: TXT, HTML, PDF reports
- **Market Intelligence section**:
  - Benchmark-rate context (10-year Treasury / Bund / JGB — REITs are rate-sensitive)
  - Sector ETF tracking (VNQ, IYR, REZ, REM, XHB)
  - Analyst consensus, short interest, price technicals
  - Insider transaction tracking with buy/sell signals
  - Projected dilution analysis for equity-issuing REITs
  - Real-estate investment disclaimers (rate risk, refinancing, occupancy)
- **Intrinsic value estimates** adapted by stage:
  - Stabilized: P/FFO multiple / P/AFFO multiple
  - Net Lease: DCF / NAV per share
  - Development / Lease-Up: NAV-based with pipeline adjustments
  - Pre-Development: Asset-based / land value
- **Sector & industry insights** for 10 REIT sub-industries
- **Comprehensive test suite**: 153 unit tests + Robot Framework acceptance tests
- **Full documentation**: README, DEVELOPMENT guide, API reference
- **Data caching**: Production (persistent) and testing (always fresh) modes
- **SEC/SEDAR filing download** with rate limiting
- **News aggregation** from yfinance + Google News RSS
- **Easter eggs**: ASCII art, animations, fortune quotes
