# Lynx Real Estate — REIT Fundamental Analysis

> Fundamental analysis specialized for REITs and real-estate operating companies.

Part of the **Lince Investor Suite**.

## Overview

Lynx Real Estate is a comprehensive fundamental analysis tool built specifically for REIT and real-estate investors. It evaluates publicly traded REITs and real-estate operating companies across all development stages — from pre-development and lease-up to stabilized portfolios and triple-net platforms — using real-estate-specific metrics, valuation methods, and risk assessments. The analysis is anchored on the cash-earnings measures that actually drive REIT total return: FFO, AFFO, NOI, cap rate, occupancy, same-store NOI growth, leverage and debt-maturity profile, and distribution coverage.

### Key Features

- **Stage-Aware Analysis**: Automatically classifies companies as Pre-Development, Development, Lease-Up, Stabilized, or Net Lease — and adapts all metrics and scoring accordingly
- **REIT-Specific Metrics**: P/FFO, P/AFFO, NOI margin, implied cap rate, occupancy rate, same-store NOI growth, AFFO payout ratio, debt-to-gross-assets, fixed-charge coverage, weighted-average debt maturity
- **4-Level Relevance System**: Marks each metric as Critical, Relevant, Contextual, or Irrelevant based on the company's stage and property type
- **Market Intelligence**: Insider transactions, institutional holders, analyst consensus, short interest analysis, price technicals with golden/death cross detection, benchmark-rate context (REITs are rate-sensitive)
- **REIT Screening Checklist**: Evaluates AFFO-covered distribution, leverage, occupancy, debt maturity profile, same-store NOI, insider ownership, and more
- **Jurisdiction Risk Classification**: Tier 1/2/3 based on property-market transparency and legal framework
- **Property Type Detection**: Automatic identification of primary property type (Residential, Office, Retail, Industrial, Hotel, Healthcare, Self-Storage, Data Center, Cell Tower, Net Lease, Diversified)
- **Multiple Interface Modes**: Console CLI, Interactive REPL, Textual TUI, Tkinter GUI
- **Export**: TXT, HTML, and PDF report generation
- **Sector & Industry Insights**: Deep context for each REIT sub-industry (Residential, Office, Retail, Industrial, Hotel, Healthcare, Specialty, Diversified, Services, Development)

### Target Companies

Designed for analyzing companies like:
- **Retail / Mall REITs**: Simon Property Group (SPG)
- **Net-Lease REITs**: Realty Income (O)
- **Industrial / Logistics REITs**: Prologis (PLD)
- **Data-Center REITs**: Equinix (EQIX)
- **Healthcare REITs**: Welltower (WELL)
- **Cell-Tower REITs**: American Tower (AMT)
- **Self-Storage REITs**: Public Storage (PSA)
- **Apartment REITs**: AvalonBay Communities (AVB)
- **Canadian REITs (TSX)**: RioCan (REI.UN), H&R (HR.UN)

## Installation

```bash
# Clone the repository
git clone https://github.com/borjatarraso/lynx-investor-real-estate.git
cd lynx-investor-real-estate

# Install in editable mode (creates the `lynx-realestate` command)
pip install -e .
```

### Dependencies

| Package        | Purpose                              |
|----------------|--------------------------------------|
| yfinance       | Financial data from Yahoo Finance    |
| requests       | HTTP calls (OpenFIGI, EDGAR, etc.)   |
| beautifulsoup4 | HTML parsing for SEC filings         |
| rich           | Terminal tables and formatting       |
| textual        | Full-screen TUI framework            |
| feedparser     | News RSS feed parsing                |
| pandas         | Data analysis                        |
| numpy          | Numerical computing                  |

All dependencies are installed automatically via `pip install -e .`.

## Usage

### Direct Execution
```bash
# Via the runner script
./lynx-investor-real-estate.py -p SPG

# Via Python
python3 lynx-investor-real-estate.py -p O

# Via pip-installed command
lynx-realestate -p PLD
```

### Execution Modes

| Flag | Mode | Description |
|------|------|-------------|
| `-p` | Production | Uses `data/` for persistent cache |
| `-t` | Testing | Uses `data_test/` (isolated, always fresh) |

### Interface Modes

| Flag | Interface | Description |
|------|-----------|-------------|
| (none) | Console | Progressive CLI output |
| `-i` | Interactive | REPL with commands |
| `-tui` | TUI | Textual terminal UI with themes |
| `-x` | GUI | Tkinter graphical interface |

### Examples

```bash
# Analyze a mall REIT
lynx-realestate -p SPG

# Analyze a net-lease REIT
lynx-realestate -p O

# Force fresh data download
lynx-realestate -p PLD --refresh

# Search by company name
lynx-realestate -p "Prologis"

# Interactive mode
lynx-realestate -p -i

# Export HTML report
lynx-realestate -p EQIX --export html

# Explain a REIT metric
lynx-realestate --explain p_ffo

# Skip filings and news for faster analysis
lynx-realestate -t WELL --no-reports --no-news
```

## Analysis Sections

1. **Company Profile** — Tier, stage, property type, jurisdiction classification
2. **Sector & Industry Insights** — REIT-specific context and benchmarks (by property type)
3. **Valuation Metrics** — P/FFO, P/AFFO, P/NAV, implied cap rate, dividend yield, EV/EBITDA
4. **Profitability Metrics** — NOI, NOI margin, FFO, AFFO, ROIC, same-store NOI growth, occupancy
5. **Solvency & Leverage** — Debt-to-gross-assets, Debt/EBITDA, fixed-charge coverage, weighted-avg debt maturity, % fixed-rate debt
6. **Growth & Dilution** — Revenue/FFO/AFFO growth, distribution growth, share dilution tracking
7. **Share Structure** — Outstanding/diluted shares, OP units, insider/institutional ownership
8. **Real Estate Quality** — Portfolio quality, diversification, occupancy, lease duration (WALT), tenant concentration, distribution safety
9. **Intrinsic Value** — P/FFO multiple, P/AFFO multiple, NAV/share, DCF (method selection by stage)
10. **Market Intelligence** — Analysts, short interest, technicals, insider trades, benchmark-rate context, risk warnings
11. **Financial Statements** — 5-year annual summary (revenue, NOI, FFO, AFFO, debt, real-estate assets)
12. **SEC/SEDAR Filings** — Downloadable regulatory filings
13. **News** — Yahoo Finance + Google News RSS
14. **Assessment Conclusion** — Weighted score, verdict, strengths/risks, screening checklist
15. **Real-Estate Disclaimers** — Stage-specific risk disclosures (rate risk, refinancing, occupancy, distribution sustainability)

## Relevance System

Each metric is classified by importance for the company's stage and property type:

| Level | Display | Meaning |
|-------|---------|---------|
| **Critical** | `*` bold cyan star | Must-check for this stage |
| **Relevant** | Normal | Important context |
| **Contextual** | Dimmed | Informational only |
| **Irrelevant** | Hidden | Not meaningful for this stage |

Example: For a Stabilized REIT, AFFO payout ratio and implied cap rate are **Critical** while GAAP P/E is **Contextual**.

## Scoring Methodology

The overall score (0-100) is a weighted average of 5 categories, with weights adapted by both company tier AND development stage:

| Stage | Valuation | Profitability | Solvency | Growth | Real Estate Quality |
|-------|-----------|---------------|----------|--------|---------------------|
| Pre-Development | 5% | 5% | 40% | 15% | 35% |
| Development | 10% | 5% | 35% | 15% | 35% |
| Lease-Up | 15% | 15% | 30% | 15% | 25% |
| Stabilized | 25% | 25% | 15% | 15% | 20% |
| Net Lease | 25% | 20% | 20% | 15% | 20% |

Verdicts: Strong Buy (>=75), Buy (>=60), Hold (>=45), Caution (>=30), Avoid (<30).

## Project Structure

```
lynx-investor-real-estate/
├── lynx-investor-real-estate.py       # Runner script
├── pyproject.toml                     # Build configuration
├── requirements.txt                   # Dependencies
├── img/                               # Logo images
├── data/                              # Production cache
├── data_test/                         # Testing cache
├── docs/                              # Documentation
│   └── API.md                         # API reference
├── robot/                             # Robot Framework tests
│   ├── cli_tests.robot
│   ├── api_tests.robot
│   └── export_tests.robot
├── tests/                             # Unit tests
└── lynx_realestate/                   # Main package
```

## Testing

```bash
# Unit tests
pytest tests/ -v

# Robot Framework acceptance tests
robot robot/
```

## License

BSD 3-Clause License. See LICENSE in source.

## Author

**Borja Tarraso** — borja.tarraso@member.fsf.org
