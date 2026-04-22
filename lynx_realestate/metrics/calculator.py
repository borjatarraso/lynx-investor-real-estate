"""Real-estate / REIT-specialized metrics calculation engine.

All calculations are both tier-aware AND stage-aware.
"""

from __future__ import annotations

import math
from typing import Optional

from datetime import datetime, timedelta

import yfinance as yf

from lynx_realestate.models import (
    PropertyType, CompanyStage, CompanyTier, EfficiencyMetrics, FinancialStatement,
    GrowthMetrics, InsiderTransaction, IntrinsicValue, MarketIntelligence,
    RealEstateQualityIndicators, ProfitabilityMetrics, ShareStructure,
    SolvencyMetrics, ValuationMetrics,
)


def _approx_ffo(stmt: FinancialStatement) -> Optional[float]:
    if stmt is None:
        return None
    ni = stmt.net_income
    if ni is None:
        return None
    da = None
    if stmt.ebitda is not None and stmt.operating_income is not None:
        da = stmt.ebitda - stmt.operating_income
    if da is None or da < 0:
        da = 0
    return ni + da


def _approx_affo(stmt: FinancialStatement) -> Optional[float]:
    ffo = _approx_ffo(stmt)
    if ffo is None:
        return None
    maint_capex = 0.0
    if stmt.capital_expenditure is not None:
        maint_capex = abs(stmt.capital_expenditure) * 0.5
    return ffo - maint_capex


def _approx_noi(stmt: FinancialStatement) -> Optional[float]:
    if stmt is None:
        return None
    if stmt.rental_income is not None and stmt.property_operating_expenses is not None:
        return stmt.rental_income - stmt.property_operating_expenses
    if stmt.operating_income is not None:
        da = 0.0
        if stmt.ebitda is not None and stmt.operating_income is not None:
            da = max(stmt.ebitda - stmt.operating_income, 0.0)
        return stmt.operating_income + da
    return None


def calc_valuation(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> ValuationMetrics:
    v = ValuationMetrics()
    v.pe_trailing = info.get("trailingPE")
    v.pe_forward = info.get("forwardPE")
    v.pb_ratio = info.get("priceToBook")
    v.ps_ratio = info.get("priceToSalesTrailing12Months")
    v.peg_ratio = info.get("pegRatio")
    v.ev_ebitda = info.get("enterpriseToEbitda")
    v.ev_revenue = info.get("enterpriseToRevenue")
    v.dividend_yield = info.get("trailingAnnualDividendYield") or info.get("dividendYield")
    v.enterprise_value = info.get("enterpriseValue")
    v.market_cap = info.get("marketCap")

    if v.pe_trailing and v.pe_trailing > 0:
        v.earnings_yield = 1.0 / v.pe_trailing

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    if price and shares and statements:
        latest = statements[0]
        if latest.free_cash_flow and latest.free_cash_flow > 0:
            v.p_fcf = (price * shares) / latest.free_cash_flow

    if tier in (CompanyTier.MICRO, CompanyTier.NANO, CompanyTier.SMALL, CompanyTier.MID) and statements:
        latest = statements[0]
        if latest.total_equity and latest.total_assets and price and shares:
            tbv = latest.total_equity
            if shares > 0:
                tbv_per_share = tbv / shares
                if tbv_per_share > 0:
                    v.price_to_tangible_book = price / tbv_per_share
        if latest.current_assets and latest.total_liabilities and shares and shares > 0:
            ncav = latest.current_assets - latest.total_liabilities
            ncav_ps = ncav / shares
            if ncav_ps > 0 and price:
                v.price_to_ncav = price / ncav_ps

    total_cash = info.get("totalCash")
    if total_cash and v.market_cap and v.market_cap > 0:
        v.cash_to_market_cap = total_cash / v.market_cap

    # FCF Yield (FCF / Enterprise Value)
    if statements and v.enterprise_value and v.enterprise_value > 0:
        latest = statements[0]
        if latest.free_cash_flow is not None:
            v.fcf_yield = latest.free_cash_flow / v.enterprise_value

    # --- REIT-specific multiples ---
    if statements:
        latest = statements[0]
        ffo = _approx_ffo(latest)
        affo = _approx_affo(latest)
        noi = _approx_noi(latest)

        if ffo and ffo > 0 and v.market_cap and v.market_cap > 0:
            v.p_ffo = v.market_cap / ffo
            v.ffo_yield = ffo / v.market_cap
        elif v.pe_forward:
            v.p_ffo = v.pe_forward

        if affo and affo > 0 and v.market_cap and v.market_cap > 0:
            v.p_affo = v.market_cap / affo

        if noi and v.enterprise_value and v.enterprise_value > 0:
            v.implied_cap_rate = noi / v.enterprise_value

        if shares and shares > 0 and latest.total_equity is not None:
            equity = latest.total_equity
            debt_adj = 0.0
            if latest.accumulated_depreciation is not None:
                debt_adj = latest.accumulated_depreciation
            nav = equity + debt_adj
            if nav > 0:
                v.nav_per_share = nav / shares
                if price and v.nav_per_share > 0:
                    v.p_nav = price / v.nav_per_share

    return v


def calc_profitability(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> ProfitabilityMetrics:
    p = ProfitabilityMetrics()
    p.roe = info.get("returnOnEquity")
    p.roa = info.get("returnOnAssets")
    p.gross_margin = info.get("grossMargins")
    p.operating_margin = info.get("operatingMargins")
    p.net_margin = info.get("profitMargins")

    if statements:
        s = statements[0]
        if s.operating_income is not None and s.total_assets and s.total_cash is not None:
            nopat = s.operating_income * 0.75
            invested_capital = s.total_assets - (s.total_cash or 0)
            if invested_capital > 0:
                p.roic = nopat / invested_capital
        if s.free_cash_flow and s.revenue and s.revenue > 0:
            p.fcf_margin = s.free_cash_flow / s.revenue
        if s.ebitda and s.revenue and s.revenue > 0:
            p.ebitda_margin = s.ebitda / s.revenue

        if s.operating_cash_flow and s.total_assets and s.total_cash is not None:
            invested = s.total_assets - (s.total_cash or 0)
            if invested > 0:
                p.croci = s.operating_cash_flow / invested

        if s.operating_cash_flow and s.net_income and s.net_income > 0:
            p.ocf_to_net_income = s.operating_cash_flow / s.net_income

        # --- REIT-specific profitability ---
        noi = _approx_noi(s)
        if noi is not None:
            p.noi = noi
            if s.revenue and s.revenue > 0:
                p.noi_margin = noi / s.revenue

        ffo = _approx_ffo(s)
        if ffo is not None:
            p.ffo = ffo
            if s.revenue and s.revenue > 0:
                p.ffo_margin = ffo / s.revenue
            if s.shares_outstanding and s.shares_outstanding > 0:
                p.ffo_per_share = ffo / s.shares_outstanding

        affo = _approx_affo(s)
        if affo is not None:
            p.affo = affo
            if s.shares_outstanding and s.shares_outstanding > 0:
                p.affo_per_share = affo / s.shares_outstanding

        if len(statements) >= 2:
            prev = statements[1]
            if s.rental_income and prev.rental_income and prev.rental_income != 0:
                p.same_store_noi_growth = (s.rental_income - prev.rental_income) / abs(prev.rental_income)
            else:
                prev_noi = _approx_noi(prev)
                if noi is not None and prev_noi and prev_noi != 0:
                    p.same_store_noi_growth = (noi - prev_noi) / abs(prev_noi)

        p.occupancy_rate = info.get("occupancyRate")

        ev = info.get("enterpriseValue")
        if noi is not None and ev and ev > 0:
            p.implied_cap_rate = noi / ev

    return p


def calc_solvency(
    info: dict, statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> SolvencyMetrics:
    s = SolvencyMetrics()
    s.debt_to_equity = info.get("debtToEquity")
    if s.debt_to_equity:
        s.debt_to_equity /= 100
    s.current_ratio = info.get("currentRatio")
    s.quick_ratio = info.get("quickRatio")
    s.total_debt = info.get("totalDebt")
    s.total_cash = info.get("totalCash")

    if s.total_debt is not None and s.total_cash is not None:
        s.net_debt = s.total_debt - s.total_cash

    shares = info.get("sharesOutstanding")
    market_cap = info.get("marketCap")

    if statements:
        st = statements[0]

        if st.ebitda and st.ebitda > 0 and s.total_debt:
            s.debt_to_ebitda = s.total_debt / st.ebitda

        if st.operating_income:
            ie = abs(st.interest_expense) if st.interest_expense else None
            if ie is None and s.total_debt:
                ie = s.total_debt * 0.05
            if ie and ie > 0:
                s.interest_coverage = st.operating_income / ie
                s.fixed_charge_coverage = st.operating_income / ie

        if s.total_debt and st.total_assets and st.total_assets > 0:
            gross = st.total_assets
            if st.accumulated_depreciation is not None:
                gross = st.total_assets + st.accumulated_depreciation
            if gross > 0:
                s.debt_to_gross_assets = s.total_debt / gross

        if st.total_assets and st.total_assets > 0 and st.revenue and st.revenue > 0:
            ta = st.total_assets
            wc = 0
            if st.current_assets is not None and st.current_liabilities is not None:
                wc = st.current_assets - st.current_liabilities
            re = (st.total_equity or 0) * 0.5
            ebit = st.operating_income or 0
            mcap = info.get("marketCap", 0)
            tl = st.total_liabilities or 0
            if tl <= 0:
                s.altman_z_score = None
            else:
                rev = st.revenue or 0
                z = (1.2 * wc / ta + 1.4 * re / ta + 3.3 * ebit / ta +
                     0.6 * mcap / tl + 1.0 * rev / ta)
                s.altman_z_score = round(z, 2)

        if st.current_assets is not None and st.current_liabilities is not None:
            s.working_capital = st.current_assets - st.current_liabilities

        if s.total_cash and shares and shares > 0:
            s.cash_per_share = s.total_cash / shares

        if st.total_equity:
            s.tangible_book_value = st.total_equity

        if st.current_assets is not None and st.total_liabilities is not None:
            s.ncav = st.current_assets - st.total_liabilities
            if shares and shares > 0:
                s.ncav_per_share = s.ncav / shares

        if st.operating_cash_flow is not None:
            ocf = st.operating_cash_flow
            if ocf < 0:
                s.cash_burn_rate = ocf
                if s.total_cash and s.total_cash > 0:
                    s.cash_runway_years = s.total_cash / abs(ocf)
                s.quarterly_burn_rate = ocf / 4
            else:
                s.cash_burn_rate = 0

        if s.cash_burn_rate and s.cash_burn_rate < 0 and market_cap and market_cap > 0:
            s.burn_as_pct_of_market_cap = abs(s.cash_burn_rate) / market_cap

    if shares:
        if s.total_debt is not None and shares > 0:
            s.debt_per_share = s.total_debt / shares
        if s.net_debt is not None and shares > 0:
            s.net_debt_per_share = s.net_debt / shares

    if statements and s.total_debt and s.total_debt > 0:
        st = statements[0]
        if st.operating_cash_flow and st.operating_cash_flow > 0:
            ie = abs(st.interest_expense) if st.interest_expense else s.total_debt * 0.05
            s.debt_service_coverage = st.operating_cash_flow / ie if ie > 0 else None

    # Not available from yfinance
    s.weighted_avg_debt_maturity = None
    s.pct_fixed_rate_debt = None

    return s


def calc_growth(
    statements: list[FinancialStatement],
    tier: CompanyTier, stage: CompanyStage,
) -> GrowthMetrics:
    g = GrowthMetrics()
    if len(statements) < 2:
        return g
    stmts = statements

    if stmts[0].revenue and stmts[1].revenue and stmts[1].revenue != 0:
        g.revenue_growth_yoy = (stmts[0].revenue - stmts[1].revenue) / abs(stmts[1].revenue)

    if stmts[0].net_income and stmts[1].net_income and stmts[1].net_income != 0:
        g.earnings_growth_yoy = (stmts[0].net_income - stmts[1].net_income) / abs(stmts[1].net_income)

    if stmts[0].free_cash_flow and stmts[1].free_cash_flow and stmts[1].free_cash_flow != 0:
        g.fcf_growth_yoy = (stmts[0].free_cash_flow - stmts[1].free_cash_flow) / abs(stmts[1].free_cash_flow)

    if stmts[0].book_value_per_share and stmts[1].book_value_per_share and stmts[1].book_value_per_share != 0:
        g.book_value_growth_yoy = (stmts[0].book_value_per_share - stmts[1].book_value_per_share) / abs(stmts[1].book_value_per_share)

    if stmts[0].shares_outstanding and stmts[1].shares_outstanding and stmts[1].shares_outstanding > 0:
        g.shares_growth_yoy = (stmts[0].shares_outstanding - stmts[1].shares_outstanding) / stmts[1].shares_outstanding

    if len(stmts) >= 4 and stmts[0].shares_outstanding and stmts[3].shares_outstanding:
        g.shares_growth_3y_cagr = _cagr(stmts[3].shares_outstanding, stmts[0].shares_outstanding, 3)

    if len(stmts) >= 4:
        g.revenue_cagr_3y = _cagr(stmts[3].revenue, stmts[0].revenue, 3)
        g.earnings_cagr_3y = _cagr(stmts[3].net_income, stmts[0].net_income, 3)

    if len(stmts) >= 5:
        g.revenue_cagr_5y = _cagr(stmts[-1].revenue, stmts[0].revenue, len(stmts) - 1)
        g.earnings_cagr_5y = _cagr(stmts[-1].net_income, stmts[0].net_income, len(stmts) - 1)

    # --- REIT-specific growth ---
    ffo_curr = _approx_ffo(stmts[0])
    ffo_prev = _approx_ffo(stmts[1])
    if ffo_curr is not None and ffo_prev and ffo_prev != 0:
        g.ffo_growth_yoy = (ffo_curr - ffo_prev) / abs(ffo_prev)

    affo_curr = _approx_affo(stmts[0])
    affo_prev = _approx_affo(stmts[1])
    if affo_curr is not None and affo_prev and affo_prev != 0:
        g.affo_growth_yoy = (affo_curr - affo_prev) / abs(affo_prev)

    if len(stmts) >= 4:
        ffo_3y = _approx_ffo(stmts[3])
        if ffo_curr and ffo_3y:
            g.ffo_cagr_3y = _cagr(ffo_3y, ffo_curr, 3)

    if stmts[0].rental_income and stmts[1].rental_income and stmts[1].rental_income != 0:
        g.same_store_noi_growth_yoy = (stmts[0].rental_income - stmts[1].rental_income) / abs(stmts[1].rental_income)
    else:
        noi_c = _approx_noi(stmts[0])
        noi_p = _approx_noi(stmts[1])
        if noi_c is not None and noi_p and noi_p != 0:
            g.same_store_noi_growth_yoy = (noi_c - noi_p) / abs(noi_p)

    if (stmts[0].capital_expenditure is not None and
            stmts[1].capital_expenditure is not None and
            stmts[1].capital_expenditure != 0):
        curr_capex = abs(stmts[0].capital_expenditure)
        prev_capex = abs(stmts[1].capital_expenditure)
        if prev_capex > 0:
            growth_val = (curr_capex / prev_capex) - 1
            if growth_val > 0:
                g.acquisition_growth_yoy = growth_val

    if stmts[0].capital_expenditure is not None:
        capex = abs(stmts[0].capital_expenditure)

        if stmts[0].revenue and stmts[0].revenue > 0:
            g.capex_to_revenue = capex / stmts[0].revenue

        if stmts[0].operating_cash_flow and stmts[0].operating_cash_flow > 0:
            g.capex_to_ocf = capex / stmts[0].operating_cash_flow

        if stmts[0].ebitda and stmts[0].ebitda > 0:
            g.reinvestment_rate = capex / stmts[0].ebitda

    if stmts[0].dividends_paid and stmts[0].net_income and stmts[0].net_income > 0:
        g.dividend_payout_ratio = abs(stmts[0].dividends_paid) / stmts[0].net_income

    if stmts[0].dividends_paid and stmts[0].free_cash_flow and stmts[0].free_cash_flow > 0:
        g.dividend_coverage = stmts[0].free_cash_flow / abs(stmts[0].dividends_paid)

    if stmts[0].dividends_paid:
        div_paid = abs(stmts[0].dividends_paid)
        if ffo_curr and ffo_curr > 0:
            g.ffo_payout_ratio = div_paid / ffo_curr
        if affo_curr and affo_curr > 0:
            g.affo_payout_ratio = div_paid / affo_curr

    shares = stmts[0].shares_outstanding
    if shares and shares > 0:
        if stmts[0].free_cash_flow is not None:
            g.fcf_per_share = stmts[0].free_cash_flow / shares
        if stmts[0].operating_cash_flow is not None:
            g.ocf_per_share = stmts[0].operating_cash_flow / shares

    return g


def calc_efficiency(
    info: dict, statements: list[FinancialStatement], tier: CompanyTier,
) -> EfficiencyMetrics:
    e = EfficiencyMetrics()
    if not statements:
        return e
    s = statements[0]
    if s.revenue and s.total_assets and s.total_assets > 0:
        e.asset_turnover = s.revenue / s.total_assets

    if s.free_cash_flow is not None and s.ebitda and s.ebitda > 0:
        e.fcf_conversion = s.free_cash_flow / s.ebitda

    if s.capital_expenditure is not None and s.revenue and s.revenue > 0:
        e.capex_intensity = abs(s.capital_expenditure) / s.revenue

    if s.revenue and s.revenue > 0 and s.operating_income is not None:
        gross = s.gross_profit
        if gross is None and s.cost_of_revenue is not None:
            gross = s.revenue - s.cost_of_revenue
        if gross is not None:
            g_and_a = gross - s.operating_income
            if g_and_a >= 0:
                e.g_and_a_as_pct_of_revenue = g_and_a / s.revenue

    return e


def calc_share_structure(
    info: dict, statements: list[FinancialStatement],
    growth: GrowthMetrics, tier: CompanyTier, stage: CompanyStage,
) -> ShareStructure:
    ss = ShareStructure()
    ss.shares_outstanding = info.get("sharesOutstanding")
    ss.float_shares = info.get("floatShares")
    ss.insider_ownership_pct = info.get("heldPercentInsiders")
    ss.institutional_ownership_pct = info.get("heldPercentInstitutions")

    implied = info.get("impliedSharesOutstanding")
    if implied:
        ss.fully_diluted_shares = implied
    elif ss.shares_outstanding:
        ss.fully_diluted_shares = ss.shares_outstanding

    if ss.shares_outstanding and ss.fully_diluted_shares and ss.shares_outstanding > 0:
        ratio = ss.fully_diluted_shares / ss.shares_outstanding
        if growth:
            growth.dilution_ratio = ratio
            growth.fully_diluted_shares = ss.fully_diluted_shares

    if ss.fully_diluted_shares:
        fd = ss.fully_diluted_shares
        if fd < 80_000_000:
            ss.share_structure_assessment = "Very Tight (<80M shares)"
        elif fd < 150_000_000:
            ss.share_structure_assessment = "Tight (80-150M shares)"
        elif fd < 300_000_000:
            ss.share_structure_assessment = "Moderate (150-300M shares)"
        elif fd < 500_000_000:
            ss.share_structure_assessment = "Heavy (300-500M shares)"
        else:
            ss.share_structure_assessment = "Bloated (>500M shares)"

    return ss


def calc_real_estate_quality(
    profitability: ProfitabilityMetrics,
    growth: GrowthMetrics,
    solvency: SolvencyMetrics,
    share_structure: ShareStructure,
    statements: list[FinancialStatement],
    info: dict,
    tier: CompanyTier,
    stage: CompanyStage,
) -> RealEstateQualityIndicators:
    m = RealEstateQualityIndicators()
    score = 0.0
    max_score = 0.0

    # Insider Ownership / Management Quality (20 pts)
    max_score += 20
    insider_pct = share_structure.insider_ownership_pct if share_structure else None
    if insider_pct is not None:
        if insider_pct > 0.10:
            m.insider_alignment = "Strong insider alignment — >10% insider ownership"
            m.management_quality = "Strong insider alignment"
            score += 20
        elif insider_pct > 0.05:
            m.insider_alignment = "Moderate — 5-10% insider ownership"
            m.management_quality = "Moderate"
            score += 12
        elif insider_pct > 0.01:
            m.insider_alignment = "Low — 1-5% insider ownership"
            m.management_quality = "Low"
            score += 5
        else:
            m.insider_alignment = "Very low insider ownership (<1%)"
            m.management_quality = "Low"
            score += 2
        m.insider_ownership_pct = insider_pct
    else:
        m.insider_alignment = "Insider data unavailable"
        m.management_quality = "Unknown"
        score += 5

    # Financial Position (25 pts) — primarily debt/EBITDA driven
    max_score += 25
    d_e = solvency.debt_to_ebitda if solvency else None
    if d_e is not None:
        if d_e < 6:
            m.financial_position = "Healthy (debt/EBITDA <6x)"
            score += 25
        elif d_e < 8:
            m.financial_position = "Moderate leverage (debt/EBITDA 6-8x)"
            score += 14
        else:
            m.financial_position = "Stretched leverage (debt/EBITDA >8x)"
            score += 5
    elif solvency and solvency.cash_runway_years is not None:
        if solvency.cash_runway_years > 3:
            m.financial_position = "Strong — >3 years runway"
            score += 20
        elif solvency.cash_runway_years > 1.5:
            m.financial_position = "Adequate — 1.5-3 years runway"
            score += 12
        else:
            m.financial_position = "Tight runway"
            score += 5
    else:
        m.financial_position = "Insufficient data"
        score += 10

    # Dilution Risk (15 pts)
    max_score += 15
    dil = growth.shares_growth_yoy if growth else None
    if dil is not None:
        if dil < 0.03:
            m.dilution_risk = "Low dilution (<3%/yr)"
            score += 15
        elif dil < 0.10:
            m.dilution_risk = "Moderate dilution (3-10%/yr)"
            score += 8
        else:
            m.dilution_risk = "High dilution (>10%/yr)"
            score += 2
    else:
        m.dilution_risk = "Dilution data unavailable"
        score += 5

    if share_structure and share_structure.share_structure_assessment:
        m.share_structure_assessment = share_structure.share_structure_assessment

    # Portfolio Quality (15 pts) — NOI margin + occupancy
    max_score += 15
    noi_margin = profitability.noi_margin if profitability else None
    occ = profitability.occupancy_rate if profitability else None
    if noi_margin is not None and noi_margin > 0.60 and (occ is None or occ > 0.95):
        m.portfolio_quality = "Premium"
        score += 15
    elif noi_margin is not None and noi_margin > 0.40:
        m.portfolio_quality = "Mid-quality"
        score += 9
    elif noi_margin is not None:
        m.portfolio_quality = "Marginal"
        score += 3
    else:
        m.portfolio_quality = "Unknown"
        score += 6

    # Occupancy assessment (10 pts)
    max_score += 10
    if occ is not None:
        if occ > 0.95:
            m.occupancy_assessment = "High stabilized occupancy (>95%)"
            score += 10
        elif occ > 0.85:
            m.occupancy_assessment = "Healthy (85-95%)"
            score += 6
        else:
            m.occupancy_assessment = "Weak (<85%)"
            score += 2
    else:
        m.occupancy_assessment = "Occupancy data unavailable"
        score += 5

    # Cap rate assessment (5 pts)
    max_score += 5
    implied_cap = profitability.implied_cap_rate if profitability else None
    if implied_cap is not None:
        if implied_cap > 0.07:
            m.cap_rate_assessment = "Attractive implied cap rate (>7%)"
            score += 5
        elif implied_cap > 0.05:
            m.cap_rate_assessment = "Market implied cap rate (5-7%)"
            score += 3
        else:
            m.cap_rate_assessment = "Compressed implied cap rate (<5%)"
            score += 1
    else:
        m.cap_rate_assessment = "Cap rate unavailable"

    # Same-store NOI trend (5 pts)
    max_score += 5
    sso = growth.same_store_noi_growth_yoy if growth else None
    if sso is not None:
        if sso > 0.02:
            m.same_store_noi_trend = "Positive"
            score += 5
        elif sso > -0.02:
            m.same_store_noi_trend = "Flat"
            score += 3
        else:
            m.same_store_noi_trend = "Negative"
            score += 1
    else:
        m.same_store_noi_trend = "Unknown"
        score += 2

    # Asset Backing (5 pts)
    max_score += 5
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")
    if (solvency and solvency.tangible_book_value and solvency.tangible_book_value > 0
            and shares and shares > 0 and price):
        tbv_ps = solvency.tangible_book_value / shares
        if price < tbv_ps:
            m.asset_backing = "Below tangible book value"
            score += 5
        elif price < tbv_ps * 1.5:
            m.asset_backing = "Near tangible book value"
            score += 3
        else:
            m.asset_backing = "Above tangible book"
            score += 1
    else:
        m.asset_backing = "Insufficient asset data"

    # Revenue predictability by stage
    revenues = [s.revenue for s in statements if s.revenue and s.revenue > 0]
    if stage == CompanyStage.STABILIZED:
        m.revenue_predictability = "Stabilized portfolio — recurring rental income"
    elif stage == CompanyStage.NET_LEASE:
        m.revenue_predictability = "Net lease — long-duration predictable income"
    elif stage == CompanyStage.LEASE_UP:
        m.revenue_predictability = "Lease-up — revenue ramping"
    elif stage == CompanyStage.DEVELOPMENT:
        m.revenue_predictability = "Development — limited operating revenue"
    elif stage == CompanyStage.PRE_DEVELOPMENT:
        m.revenue_predictability = "Pre-development — no operating revenue"
    else:
        m.revenue_predictability = "Operating REIT" if revenues else "Pre-revenue"

    # Lease / tenant data not available via yfinance
    m.lease_duration_assessment = None
    m.tenant_concentration = None

    industry = info.get("industry") or ""
    if "diversified" in industry.lower():
        m.portfolio_diversification = "Diversified property portfolio"
    elif industry:
        m.portfolio_diversification = f"Focused REIT — {industry}"
    else:
        m.portfolio_diversification = "Unknown"

    if stage == CompanyStage.NET_LEASE:
        m.niche_position = "Net-lease niche"
    elif "data center" in industry.lower() or "tower" in industry.lower():
        m.niche_position = "Specialty REIT niche"
    else:
        m.niche_position = "Generalist REIT"

    m.catalyst_density = None
    m.near_term_catalysts = []

    m.roic_history = _calc_roic_history(statements)
    m.gross_margin_history = _calc_margin_history(statements)

    m.quality_score = round((score / max_score), 3) if max_score > 0 else 0
    pct = m.quality_score * 100 if m.quality_score else 0
    if pct >= 70:
        m.competitive_position = "Strong Position — High Quality"
    elif pct >= 50:
        m.competitive_position = "Viable Position — Moderate Quality"
    elif pct >= 30:
        m.competitive_position = "Speculative — Below Average Quality"
    else:
        m.competitive_position = "High Risk — Weak Fundamentals"

    return m


def calc_intrinsic_value(
    info: dict, statements: list[FinancialStatement],
    growth: GrowthMetrics, solvency: SolvencyMetrics,
    tier: CompanyTier, stage: CompanyStage,
    discount_rate: float = 0.10, terminal_growth: float = 0.03,
) -> IntrinsicValue:
    iv = IntrinsicValue()
    iv.current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    # Preliminary method selection by stage
    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE):
        iv.primary_method = "P/FFO Multiple"
        iv.secondary_method = "NAV per Share"
    elif stage == CompanyStage.LEASE_UP:
        iv.primary_method = "NAV per Share"
        iv.secondary_method = "P/FFO Multiple"
    elif stage == CompanyStage.DEVELOPMENT:
        iv.primary_method = "NAV per Share"
        iv.secondary_method = "Asset-Based (Tangible Book)"
    elif stage == CompanyStage.PRE_DEVELOPMENT:
        iv.primary_method = "Asset-Based (Tangible Book)"
        iv.secondary_method = "NAV per Share"
    else:
        iv.primary_method = "DCF"
        iv.secondary_method = "NAV per Share"

    if not statements:
        return iv
    latest = statements[0]

    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE, CompanyStage.LEASE_UP):
        if latest.free_cash_flow and latest.free_cash_flow > 0 and shares and shares > 0:
            fcf = latest.free_cash_flow
            growth_rate = min(growth.revenue_cagr_3y or 0.04, 0.15)
            growth_rate = max(growth_rate, 0.0)
            dr = discount_rate
            if tier == CompanyTier.SMALL:
                dr = 0.11
            elif tier in (CompanyTier.MICRO, CompanyTier.NANO):
                dr = 0.13
            if dr > terminal_growth:
                total_pv = 0.0
                projected_fcf = fcf
                for year in range(1, 11):
                    yr_growth = growth_rate - (growth_rate - terminal_growth) * (year / 10)
                    projected_fcf *= (1 + yr_growth)
                    total_pv += projected_fcf / ((1 + dr) ** year)
                terminal_fcf = projected_fcf * (1 + terminal_growth)
                terminal_value = terminal_fcf / (dr - terminal_growth)
                pv_terminal = terminal_value / ((1 + dr) ** 10)
                dcf = (total_pv + pv_terminal) / shares
                if not math.isnan(dcf) and not math.isinf(dcf) and dcf > 0:
                    iv.dcf_value = round(dcf, 2)

    eps = latest.eps or (latest.net_income / shares if latest.net_income and shares else None)
    bvps = latest.book_value_per_share or info.get("bookValue")
    if eps and eps > 0 and bvps and bvps > 0:
        iv.graham_number = round(math.sqrt(22.5 * eps * bvps), 2)

    if eps and eps > 0 and growth.earnings_cagr_3y and growth.earnings_cagr_3y > 0:
        eg = min(growth.earnings_cagr_3y * 100, 100)
        if eg > 0:
            result = eps * eg
            if not math.isnan(result) and not math.isinf(result):
                iv.lynch_fair_value = round(result, 2)

    if solvency.ncav_per_share is not None:
        iv.ncav_value = round(solvency.ncav_per_share, 4)

    if latest.total_equity and shares and shares > 0:
        iv.asset_based_value = round(latest.total_equity / shares, 4)

    # NAV per share (equity + accumulated depreciation addback)
    if latest.total_equity and shares and shares > 0:
        equity = latest.total_equity
        debt_adj = 0.0
        if latest.accumulated_depreciation is not None:
            debt_adj = latest.accumulated_depreciation
        nav = equity + debt_adj
        if nav > 0:
            iv.nav_per_share = round(nav / shares, 4)

    ffo = _approx_ffo(latest)
    affo = _approx_affo(latest)
    if ffo and shares and shares > 0:
        ffo_ps = ffo / shares
        if ffo_ps > 0:
            iv.ffo_multiple_value = round(ffo_ps * 15, 4)
    if affo and shares and shares > 0:
        affo_ps = affo / shares
        if affo_ps > 0:
            iv.affo_multiple_value = round(affo_ps * 18, 4)

    if iv.current_price and iv.current_price > 0:
        if iv.dcf_value:
            iv.margin_of_safety_dcf = round((iv.dcf_value - iv.current_price) / iv.dcf_value, 4)
        if iv.graham_number:
            iv.margin_of_safety_graham = round((iv.graham_number - iv.current_price) / iv.graham_number, 4)
        if iv.ncav_value and iv.ncav_value > 0:
            iv.margin_of_safety_ncav = round((iv.ncav_value - iv.current_price) / iv.ncav_value, 4)
        if iv.asset_based_value and iv.asset_based_value > 0:
            iv.margin_of_safety_asset = round((iv.asset_based_value - iv.current_price) / iv.asset_based_value, 4)
        if iv.nav_per_share and iv.nav_per_share > 0:
            iv.margin_of_safety_nav = round((iv.nav_per_share - iv.current_price) / iv.nav_per_share, 4)
        if iv.ffo_multiple_value and iv.ffo_multiple_value > 0:
            iv.margin_of_safety_ffo = round((iv.ffo_multiple_value - iv.current_price) / iv.ffo_multiple_value, 4)
        if iv.affo_multiple_value and iv.affo_multiple_value > 0:
            iv.margin_of_safety_affo = round((iv.affo_multiple_value - iv.current_price) / iv.affo_multiple_value, 4)

    # Prefer FFO multiple, else NAV, else DCF
    if iv.ffo_multiple_value:
        iv.primary_method = "P/FFO Multiple"
        iv.secondary_method = "NAV per Share" if iv.nav_per_share else "DCF"
    elif iv.nav_per_share:
        iv.primary_method = "NAV per Share"
        iv.secondary_method = "DCF" if iv.dcf_value else "Asset-Based (Tangible Book)"
    elif iv.dcf_value:
        iv.primary_method = "DCF"
        iv.secondary_method = "Asset-Based (Tangible Book)"

    return iv


def calc_market_intelligence(
    info: dict, ticker_obj, solvency: SolvencyMetrics,
    share_structure: ShareStructure, growth: GrowthMetrics,
    tier: CompanyTier, stage: CompanyStage,
) -> MarketIntelligence:
    """Aggregate market sentiment, insider activity, technicals, and risk warnings."""
    mi = MarketIntelligence()
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares_outstanding = info.get("sharesOutstanding")
    mi.price_current = price

    # Insider transactions
    try:
        insider_df = ticker_obj.insider_transactions
        if insider_df is not None and not insider_df.empty:
            top_rows = insider_df.head(10)
            for _, row in top_rows.iterrows():
                txn = InsiderTransaction(
                    insider=str(row.get("Insider", row.get("insider", ""))),
                    position=str(row.get("Position", row.get("position", ""))),
                    transaction_type=str(row.get("Transaction", row.get("transaction", ""))),
                    shares=row.get("Shares", row.get("shares")),
                    value=row.get("Value", row.get("value")),
                    date=str(row.get("Start Date", row.get("startDate", row.get("date", "")))),
                )
                mi.insider_transactions.append(txn)

            cutoff = datetime.now() - timedelta(days=90)
            net_shares = 0.0
            buy_count = 0
            sell_count = 0
            for _, row in insider_df.iterrows():
                date_val = row.get("Start Date", row.get("startDate", row.get("date")))
                try:
                    if hasattr(date_val, "to_pydatetime"):
                        txn_date = date_val.to_pydatetime()
                    elif isinstance(date_val, str) and date_val:
                        txn_date = datetime.strptime(date_val[:10], "%Y-%m-%d")
                    else:
                        continue
                    if txn_date.tzinfo is not None:
                        txn_date = txn_date.replace(tzinfo=None)
                    if txn_date < cutoff:
                        continue
                except (ValueError, TypeError):
                    continue

                txn_type = str(row.get("Transaction", row.get("transaction", ""))).lower()
                shares_val = row.get("Shares", row.get("shares", 0)) or 0

                if any(kw in txn_type for kw in ("acquisition", "exercise", "purchase", "buy")):
                    net_shares += abs(shares_val)
                    buy_count += 1
                elif any(kw in txn_type for kw in ("disposition", "sale", "sell")):
                    net_shares -= abs(shares_val)
                    sell_count += 1

            mi.net_insider_shares_3m = net_shares

            if net_shares > 0 and buy_count > 3:
                mi.insider_buy_signal = "Strong insider buying"
            elif net_shares < 0:
                mi.insider_buy_signal = "Insider selling"
            else:
                mi.insider_buy_signal = "Mixed/Neutral"
    except Exception:
        mi.insider_buy_signal = "Data unavailable"

    # Institutional holders
    try:
        inst_df = ticker_obj.institutional_holders
        if inst_df is not None and not inst_df.empty:
            holder_col = "Holder" if "Holder" in inst_df.columns else (
                "holder" if "holder" in inst_df.columns else None
            )
            if holder_col:
                mi.top_holders = inst_df[holder_col].head(5).tolist()
    except Exception:
        pass
    mi.institutions_count = info.get("institutionsCount")
    mi.institutions_pct = share_structure.institutional_ownership_pct if share_structure else None

    # Analyst consensus
    mi.target_high = info.get("targetHighPrice")
    mi.target_low = info.get("targetLowPrice")
    mi.target_mean = info.get("targetMeanPrice")
    mi.recommendation = info.get("recommendationKey")
    mi.analyst_count = info.get("numberOfAnalystOpinions")

    if mi.target_mean and price and price > 0:
        mi.target_upside_pct = (mi.target_mean - price) / price

    # Short interest
    mi.shares_short = info.get("sharesShort")
    mi.short_pct_of_float = info.get("shortPercentOfFloat")
    mi.short_ratio_days = info.get("shortRatio")

    short_pct = (mi.short_pct_of_float or 0) * 100
    short_ratio = mi.short_ratio_days or 0
    if short_pct > 15 and short_ratio > 5:
        mi.short_squeeze_risk = "High squeeze potential"
    elif short_pct > 8:
        mi.short_squeeze_risk = "Elevated short interest"
    else:
        mi.short_squeeze_risk = "Normal"

    # Price technicals
    mi.price_52w_high = info.get("fiftyTwoWeekHigh")
    mi.price_52w_low = info.get("fiftyTwoWeekLow")
    mi.sma_50 = info.get("fiftyDayAverage")
    mi.sma_200 = info.get("twoHundredDayAverage")
    mi.beta = info.get("beta")
    mi.avg_volume = info.get("averageVolume")
    mi.volume_10d_avg = info.get("averageDailyVolume10Day")

    if price and mi.price_52w_high and mi.price_52w_high > 0:
        mi.pct_from_52w_high = (price - mi.price_52w_high) / mi.price_52w_high
    if price and mi.price_52w_low and mi.price_52w_low > 0:
        mi.pct_from_52w_low = (price - mi.price_52w_low) / mi.price_52w_low
    if price and mi.price_52w_high and mi.price_52w_low is not None:
        range_span = mi.price_52w_high - mi.price_52w_low
        if range_span > 0:
            mi.price_52w_range_position = (price - mi.price_52w_low) / range_span

    if price and mi.sma_50:
        mi.above_sma_50 = price > mi.sma_50
    if price and mi.sma_200:
        mi.above_sma_200 = price > mi.sma_200
    if mi.sma_50 and mi.sma_200:
        mi.golden_cross = mi.sma_50 > mi.sma_200

    if mi.volume_10d_avg and mi.avg_volume and mi.avg_volume > 0:
        vol_ratio = mi.volume_10d_avg / mi.avg_volume
        if vol_ratio > 1.25:
            mi.volume_trend = "Increasing"
        elif vol_ratio < 0.75:
            mi.volume_trend = "Decreasing"
        else:
            mi.volume_trend = "Stable"

    # --- Rate / macro context (REITs are rate-sensitive) ---
    mi.benchmark_rate_name = "10-Year Treasury Yield"
    mi.benchmark_rate_value = None
    mi.rate_currency = "USD"
    mi.rate_52w_high = None
    mi.rate_52w_low = None
    mi.rate_52w_position = None
    mi.rate_ytd_change = None

    try:
        tnx = yf.Ticker("^TNX")
        ti = tnx.info or {}
        rate_val = ti.get("regularMarketPrice") or ti.get("previousClose")
        if rate_val:
            mi.benchmark_rate_value = rate_val / 100 if rate_val > 1 else rate_val
        hi = ti.get("fiftyTwoWeekHigh")
        lo = ti.get("fiftyTwoWeekLow")
        if hi:
            mi.rate_52w_high = hi / 100 if hi > 1 else hi
        if lo:
            mi.rate_52w_low = lo / 100 if lo > 1 else lo
        if (mi.benchmark_rate_value is not None and mi.rate_52w_high is not None
                and mi.rate_52w_low is not None):
            rng = mi.rate_52w_high - mi.rate_52w_low
            if rng > 0:
                mi.rate_52w_position = (mi.benchmark_rate_value - mi.rate_52w_low) / rng
    except Exception:
        pass

    # --- Sector ETF context: VNQ is the default REIT sector ETF ---
    mi.sector_etf_name = "Vanguard Real Estate ETF"
    mi.sector_etf_ticker = "VNQ"
    try:
        et = yf.Ticker("VNQ")
        ei = et.info or {}
        mi.sector_etf_price = ei.get("regularMarketPrice") or ei.get("previousClose")
        try:
            hist = et.history(period="3mo")
            if hist is not None and len(hist) > 1:
                mi.sector_etf_3m_perf = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1)
        except Exception:
            pass
    except Exception:
        pass

    mi.peer_etf_name = "iShares U.S. Real Estate ETF"
    mi.peer_etf_ticker = "IYR"
    try:
        et2 = yf.Ticker("IYR")
        ei2 = et2.info or {}
        mi.peer_etf_price = ei2.get("regularMarketPrice") or ei2.get("previousClose")
        try:
            hist2 = et2.history(period="3mo")
            if hist2 is not None and len(hist2) > 1:
                mi.peer_etf_3m_perf = (hist2["Close"].iloc[-1] / hist2["Close"].iloc[0] - 1)
        except Exception:
            pass
    except Exception:
        pass

    # Projected dilution (pre-operating REITs)
    pre_revenue_stages = (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT, CompanyStage.LEASE_UP)
    if stage in pre_revenue_stages:
        runway = solvency.cash_runway_years if solvency else None
        burn = solvency.cash_burn_rate if solvency else None
        if runway is not None and runway < 3 and burn is not None and burn < 0:
            if price and price > 0 and shares_outstanding and shares_outstanding > 0:
                new_shares = abs(burn) * 2 / price
                mi.projected_dilution_annual_pct = (new_shares / 2) / shares_outstanding
                mi.projected_shares_in_2y = shares_outstanding + new_shares

        if runway is not None:
            if runway < 1:
                mi.financing_warning = (
                    "Critical: cash runway under 1 year. "
                    "Imminent dilutive financing expected."
                )
            elif runway < 1.5:
                mi.financing_warning = (
                    "Warning: cash runway under 18 months. "
                    "Dilutive financing likely within next year."
                )
            elif runway < 3:
                mi.financing_warning = (
                    "Note: cash runway under 3 years. "
                    "Future financing probable; monitor cash position."
                )

    # Risk warnings
    warnings: list[str] = []

    if mi.beta and mi.beta > 2.0:
        warnings.append(
            f"High volatility (beta {mi.beta:.1f}) "
            "— price swings of 2-3x market moves"
        )

    if short_pct > 10:
        warnings.append(
            f"Elevated short interest ({short_pct:.1f}%) "
            "— negative sentiment or squeeze setup"
        )

    if not mi.analyst_count or mi.analyst_count == 0:
        warnings.append("No analyst coverage — higher information asymmetry")

    if mi.pct_from_52w_low is not None and mi.pct_from_52w_low < 0.20:
        warnings.append(
            "Trading near 52-week low — potential capitulation or value"
        )

    if mi.insider_buy_signal == "Insider selling":
        warnings.append("Recent insider selling detected")

    if solvency and solvency.cash_runway_years is not None and solvency.cash_runway_years < 1.5:
        warnings.append("Cash runway under 18 months — dilutive financing likely")

    if share_structure and share_structure.fully_diluted_shares:
        if share_structure.fully_diluted_shares > 500_000_000:
            warnings.append("Bloated share structure limits per-share upside")

    if stage in pre_revenue_stages and solvency and solvency.total_debt and solvency.total_debt > 0:
        warnings.append("Debt in pre-operating REIT — unusual leverage profile")

    mi.risk_warnings = warnings

    # Real-estate disclaimers
    disclaimers: list[str] = [
        "Real-estate investments are rate-sensitive; rising interest rates typically pressure REIT valuations.",
        "Cap-rate compression or expansion can swing NAV estimates materially.",
        "Occupancy, lease expiration schedules, and tenant credit drive long-term returns.",
    ]
    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT):
        disclaimers.append(
            "This company is pre-stabilization. Valuation is based on development "
            "plans rather than recurring rental cash flows."
        )
    if stage == CompanyStage.DEVELOPMENT:
        disclaimers.append(
            "Construction cost overruns of 10-30% above initial estimates "
            "are common in real-estate development projects."
        )
    disclaimers.extend([
        "Past performance and insider activity do not guarantee future results.",
        "This analysis is for informational purposes only and does not constitute investment advice.",
    ])
    mi.disclaimers = disclaimers

    return mi


def _calc_roic_history(statements: list[FinancialStatement]) -> list[Optional[float]]:
    vals = []
    for s in statements:
        if s.operating_income is not None and s.total_assets and s.total_cash is not None:
            nopat = s.operating_income * 0.75
            ic = s.total_assets - (s.total_cash or 0)
            if ic > 0:
                vals.append(nopat / ic)
    return vals


def _calc_margin_history(statements: list[FinancialStatement]) -> list[Optional[float]]:
    margins = []
    for s in statements:
        if s.gross_profit and s.revenue and s.revenue > 0:
            margins.append(s.gross_profit / s.revenue)
    return margins


def _cagr(start: Optional[float], end: Optional[float], years: int) -> Optional[float]:
    if not start or not end or start <= 0 or end <= 0 or years <= 0:
        return None
    try:
        result = (end / start) ** (1 / years) - 1
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except (ValueError, OverflowError, ZeroDivisionError):
        return None
