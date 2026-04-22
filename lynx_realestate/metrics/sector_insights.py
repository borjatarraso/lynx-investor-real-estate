"""Real Estate-focused sector and industry insights."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SectorInsight:
    sector: str; overview: str; critical_metrics: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list); what_to_watch: list[str] = field(default_factory=list)
    typical_valuation: str = ""

@dataclass
class IndustryInsight:
    industry: str; sector: str; overview: str; critical_metrics: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list); what_to_watch: list[str] = field(default_factory=list)
    typical_valuation: str = ""

_SECTORS: dict[str, SectorInsight] = {}
_INDUSTRIES: dict[str, IndustryInsight] = {}

def _add_sector(sector, overview, cm, kr, wtw, tv):
    _SECTORS[sector.lower()] = SectorInsight(sector=sector, overview=overview, critical_metrics=cm, key_risks=kr, what_to_watch=wtw, typical_valuation=tv)

def _add_industry(industry, sector, overview, cm, kr, wtw, tv):
    _INDUSTRIES[industry.lower()] = IndustryInsight(industry=industry, sector=sector, overview=overview, critical_metrics=cm, key_risks=kr, what_to_watch=wtw, typical_valuation=tv)


_REIT_SECTOR_NAME = "REIT\u2014Real Estate"

_add_sector(_REIT_SECTOR_NAME,
    "Real-estate operating companies and REITs generate rental income from property portfolios. REITs distribute 90%+ of taxable income as dividends, making payout sustainability and occupancy-driven cash flow the central thesis. Interest-rate sensitivity, asset quality, and cap rate trends dominate valuation.",
    ["FFO / AFFO growth", "NOI growth", "Occupancy", "Debt/EBITDA", "AFFO payout ratio", "Implied cap rate vs market cap rate", "Distribution coverage"],
    ["Interest rate increases compressing valuations", "Tenant credit deterioration", "Oversupply in key markets", "Refinancing risk at higher rates", "Secular demand shifts (remote work, e-commerce)", "Cap rate expansion reducing NAV"],
    ["10-year Treasury yield and spread vs cap rates", "Same-store NOI growth trends", "Re-leasing spreads and lease expirations", "Debt maturities and refinancing costs", "Transaction market cap rate benchmarks", "Dividend coverage and AFFO payout"],
    "P/FFO 12\u201322 for quality REITs; P/AFFO 15\u201328; implied cap rate 4\u20138% by sub-sector and geography.")

for _alias in ["Real Estate", "Real-Estate", "REITs", "REIT", "Real Estate\u2014REIT"]:
    _SECTORS[_alias.lower()] = _SECTORS[_REIT_SECTOR_NAME.lower()]


_add_industry("REIT\u2014Residential", _REIT_SECTOR_NAME,
    "Residential REITs own multifamily apartments, single-family rentals, and student housing. Performance is driven by occupancy, rent growth, and demographic trends in target markets. Sunbelt migration, wage growth, and housing affordability shape demand. Capital recycling and same-store NOI growth are core KPIs.",
    ["Occupancy (95%+ target)", "Rent growth (same-store)", "Same-store NOI growth", "AFFO payout ratio", "Debt/EBITDA", "Implied cap rate"],
    ["New supply in target markets", "Rent regulation / rent control", "Interest rate sensitivity", "Home ownership affordability shifts", "Local employment weakness"],
    ["Multifamily permits and completions by MSA", "Blended lease trade-outs (new + renewal)", "Job growth in top markets", "Cap rate trends in transaction market", "Single-family build-to-rent pipeline"],
    "P/FFO 15\u201322 for quality residential REITs. Implied cap rate 4.5\u20136%. AFFO payout 65\u201380%.")
for _alias in ["REIT - Residential", "Residential REITs", "Apartment REITs", "REIT-Residential"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Residential".lower()]


_add_industry("REIT\u2014Office", _REIT_SECTOR_NAME,
    "Office REITs own CBD and suburban office towers leased to corporate tenants. The sector faces structural headwinds from hybrid work reducing demand, elevated sublease space, and flight-to-quality dynamics favoring trophy assets. Lease expiration walls and re-leasing spreads are decisive. Balance sheet strength determines survival through the cycle.",
    ["Occupancy", "Lease expirations (next 1\u20133 years)", "Re-leasing spreads", "WALT (weighted avg lease term)", "NOI margin", "Debt/EBITDA"],
    ["Remote/hybrid work reducing demand", "Tenant bankruptcies and move-outs", "Refinancing risk in rising rate environment", "Obsolescence of Class B/C stock", "Capex intensity of tenant improvements"],
    ["National office vacancy and sublease availability", "Return-to-office mandates", "Corporate downsizing announcements", "Transaction cap rates (if any trades clear)", "Loan maturities and workout activity"],
    "P/FFO 10\u201315 given secular headwinds. Implied cap rates 7\u20139%+. Discount to NAV common. Dividend cuts possible for stressed names.")
for _alias in ["REIT - Office", "Office REITs", "REIT-Office"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Office".lower()]


_add_industry("REIT\u2014Retail", _REIT_SECTOR_NAME,
    "Retail REITs own shopping centers, regional malls, and grocery-anchored strip centers. Grocery-anchored and open-air centers have proven more resilient than enclosed malls. Tenant credit, foot traffic, and re-leasing spreads drive performance. Omnichannel retail is reshaping tenant mix toward experiential and necessity-based uses.",
    ["Occupancy", "Traffic / foot traffic trends", "Re-leasing spreads", "Tenant concentration (top-10 exposure)", "Same-store NOI growth", "AFFO payout"],
    ["E-commerce displacing in-store sales", "Major tenant bankruptcies (anchors, big-box)", "Co-tenancy clauses triggering rent reductions", "Capex for redevelopment", "Suburban vs urban demand shifts"],
    ["Retail bankruptcies and store closures", "Grocer sales-per-square-foot trends", "Leasing momentum and spreads", "Redevelopment/mixed-use densification pipelines", "Consumer spending and wage growth"],
    "P/FFO 10\u201316. Grocery-anchored at upper end, mall REITs at discount. Implied cap rate 6\u20138%.")
for _alias in ["REIT - Retail", "Retail REITs", "REIT-Retail"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Retail".lower()]


_add_industry("REIT\u2014Industrial", _REIT_SECTOR_NAME,
    "Industrial REITs own warehouses, logistics facilities, and last-mile distribution assets. E-commerce penetration and supply-chain reshoring have driven double-digit rent growth and occupancy above 96%. Proximity to population centers commands premium rents. Development pipelines and land banks are key growth drivers.",
    ["Occupancy (96%+ typical)", "Rent growth (often double-digit recent years)", "Same-store NOI growth", "Development yield-on-cost", "Cash re-leasing spreads", "Debt/EBITDA"],
    ["New supply oversaturating secondary markets", "E-commerce growth deceleration", "Tenant concentration (Amazon, 3PLs)", "Construction cost inflation for development", "Interest rate impact on cap rates"],
    ["National industrial absorption and deliveries", "E-commerce sales growth", "Port and logistics volumes", "Market rent mark-to-market upside", "Development starts and yields"],
    "P/FFO 18\u201328 premium to broader REIT sector. Implied cap rate 4\u20135.5%. AFFO payout 60\u201375%.")
for _alias in ["REIT - Industrial", "Industrial REITs", "REIT-Industrial"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Industrial".lower()]


_add_industry("REIT\u2014Hotel & Motel", _REIT_SECTOR_NAME,
    "Hotel and resort REITs own hospitality assets with daily-priced rooms, producing volatile revenue tied to business and leisure travel cycles. RevPAR (revenue per available room) is the headline KPI. Operating leverage is high: small RevPAR moves drive large GOP margin swings. Capex-intensive with brand/PIP requirements.",
    ["RevPAR", "Occupancy", "ADR (average daily rate)", "GOP margin (gross operating profit)", "EBITDA margin", "Net debt/EBITDA"],
    ["Recession sharply reducing travel", "New supply in key markets", "Labor cost inflation", "Brand PIP (property improvement plan) capex", "Event-driven disruptions (pandemics, geopolitics)"],
    ["US and global RevPAR trends by chain scale", "Corporate travel recovery", "Group booking pace", "International inbound travel", "STR industry data"],
    "EV/EBITDA 10\u201314. P/FFO less reliable due to earnings volatility. NAV approach common. Dividend variable through cycle.")
for _alias in ["REIT - Hotel & Motel", "REIT\u2014Hotel & Resort", "REIT - Hotel & Resort", "Hotel & Resort REITs", "Hospitality REITs", "Lodging REITs"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Hotel & Motel".lower()]


_add_industry("REIT\u2014Healthcare Facilities", _REIT_SECTOR_NAME,
    "Healthcare REITs own medical office buildings, senior housing, skilled nursing, hospitals, and life science labs. Cash flow stability depends on operator/tenant credit and lease coverage. Demographic tailwinds from aging populations support long-term demand. Life science is a high-growth sub-segment tied to biotech R&D spending.",
    ["Occupancy", "Operator/tenant credit quality", "Lease coverage (EBITDARM/rent)", "Same-store NOI growth", "AFFO payout", "Debt/EBITDA"],
    ["Operator financial distress (skilled nursing)", "Medicare/Medicaid reimbursement changes", "Senior housing labor cost pressure", "Life science tenant funding cycle", "New supply in senior housing"],
    ["Senior housing occupancy recovery and rate growth", "Biotech funding environment (life science demand)", "Operator coverage ratios", "Government reimbursement policy", "Medical office leasing trends"],
    "P/FFO 14\u201320. Implied cap rate 5\u20137%. Life science and MOB at premium, skilled nursing at discount.")
for _alias in ["REIT - Healthcare Facilities", "REIT\u2014Healthcare", "REIT - Healthcare", "Healthcare REITs", "Health Care REITs"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Healthcare Facilities".lower()]


_add_industry("REIT\u2014Specialty", _REIT_SECTOR_NAME,
    "Specialty REITs cover self-storage, data centers, cell towers, and net-lease single-tenant properties. Each sub-type has distinct drivers: storage on occupancy and rate optimization, data centers on power/leasable capacity, towers on tenant colocation, net-lease on long-duration contractual income. Premium valuations reflect visibility and secular growth.",
    ["Occupancy (self-storage)", "Leased power capacity / MW (data centers)", "Tenants per tower (colocation)", "WALT and rent escalators (net-lease)", "Same-store NOI growth", "AFFO payout"],
    ["New supply in self-storage sub-markets", "Hyperscaler concentration risk (data centers)", "Carrier consolidation (towers)", "Interest rate sensitivity (net-lease)", "Power availability constraints for data centers"],
    ["Self-storage street rate trends and move-in volumes", "Data center power pipeline and pre-leasing", "5G and edge deployment (towers)", "Net-lease cap rate spreads to Treasuries", "AI-driven data center demand"],
    "P/FFO 15\u201330 with premium for data centers and towers. Self-storage 18\u201325. Net-lease 12\u201316. Implied cap rate 4\u20137%.")
for _alias in ["REIT - Specialty", "Specialty REITs", "REIT-Specialty"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Specialty".lower()]


_add_industry("REIT\u2014Diversified", _REIT_SECTOR_NAME,
    "Diversified property REITs own multiple property types across geographies. Mortgage REITs (mREITs) instead own portfolios of residential or commercial mortgage securities, earning a spread between asset yields and financing costs. mREITs are leveraged and interest-rate sensitive; book value per share is the core valuation anchor.",
    ["Book value per share (mREITs)", "Net interest spread / portfolio yield", "Leverage (debt-to-equity)", "BV discount / premium", "Dividend coverage by core earnings", "Hedge ratio"],
    ["Rate volatility causing BV declines (mREITs)", "Mortgage spread widening", "Prepayment speed changes (agency mREITs)", "Credit losses (non-agency/CRE mREITs)", "Dividend cuts"],
    ["Agency MBS spreads vs Treasuries", "Yield curve shape and Fed policy", "Prepayment speeds", "Book value updates vs peers", "Hedging strategy and leverage trends"],
    "mREITs P/BV 0.8\u20131.2 with high dividend yields (10\u201315%). Diversified property REITs P/FFO 10\u201316.")
for _alias in ["REIT - Diversified", "Diversified REITs", "REIT\u2014Mortgage", "REIT - Mortgage", "Mortgage REITs", "mREITs"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["REIT\u2014Diversified".lower()]


_add_industry("Real Estate Services", _REIT_SECTOR_NAME,
    "Real estate services companies include brokerages, property managers, title insurers, and proptech platforms. Revenue is transaction-driven (brokerage) or recurring (property management, title). Unlike REITs, these are operating companies valued on P/E and EBITDA, not FFO. Sensitive to housing volumes and mortgage activity.",
    ["Transaction volume (home sales, commercial deals)", "Agent count and productivity", "Commission rate / take rate", "EBITDA margin", "Recurring revenue mix", "Free cash flow conversion"],
    ["Housing transaction slowdown", "Commission compression (NAR settlement)", "Agent attrition to competitors", "Mortgage rate sensitivity", "Tech disruption of traditional brokerage"],
    ["Existing home sales and median price", "Mortgage application activity", "Commission rate trends post-NAR settlement", "Agent recruitment and retention", "Commercial transaction volumes"],
    "P/E 12\u201320 depending on growth and cyclicality. EV/EBITDA 8\u201315. Recurring-revenue models at premium.")
for _alias in ["Real Estate - Services", "Real-Estate Services", "Real Estate\u2014Services"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["Real Estate Services".lower()]


_add_industry("Real Estate\u2014Development", _REIT_SECTOR_NAME,
    "Real estate developers acquire land, entitle, build, and sell or lease finished properties. Cash flows are lumpy and project-based. Homebuilders fall here in some taxonomies. Balance sheet leverage, land bank duration, and gross margin trends drive returns. Sensitive to interest rates, construction costs, and absorption.",
    ["Gross margin on sales", "Land bank years of supply", "Net debt/equity", "Absorption rate (units/community/month)", "Backlog value", "Return on invested capital"],
    ["Interest rates impacting buyer affordability", "Construction cost inflation", "Land impairments in downturns", "Municipal entitlement delays", "Inventory build in slow markets"],
    ["New home sales and builder sentiment (NAHB)", "Mortgage rate trends", "Cancellation rates", "Lumber and input costs", "Land acquisition spending discipline"],
    "P/E 6\u201312 at cycle peak, higher at trough. P/B 1.0\u20132.0. ROE 15\u201325% in favorable cycles.")
for _alias in ["Real Estate - Development", "Real-Estate Development", "Real Estate Development"]:
    _INDUSTRIES[_alias.lower()] = _INDUSTRIES["Real Estate\u2014Development".lower()]


def get_sector_insight(sector: str | None) -> SectorInsight | None:
    return _SECTORS.get(sector.lower()) if sector else None

def get_industry_insight(industry: str | None) -> IndustryInsight | None:
    return _INDUSTRIES.get(industry.lower()) if industry else None

def list_sectors() -> list[str]:
    return sorted({s.sector for s in _SECTORS.values()})

def list_industries() -> list[str]:
    return sorted({i.industry for i in _INDUSTRIES.values()})
