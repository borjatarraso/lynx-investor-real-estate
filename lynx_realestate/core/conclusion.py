"""REIT-focused report synthesis engine."""

from __future__ import annotations

import math

from lynx_realestate.models import AnalysisConclusion, AnalysisReport, CompanyStage, CompanyTier, JurisdictionTier


def _safe(val, default: float = 0.0) -> float:
    if val is None or isinstance(val, bool):
        return default
    try:
        f = float(val)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


_WEIGHTS = {
    (CompanyStage.PRE_DEVELOPMENT, CompanyTier.MEGA): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.PRE_DEVELOPMENT, CompanyTier.LARGE): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.PRE_DEVELOPMENT, CompanyTier.MID): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.PRE_DEVELOPMENT, CompanyTier.SMALL): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.PRE_DEVELOPMENT, CompanyTier.MICRO): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.PRE_DEVELOPMENT, CompanyTier.NANO): (0.10, 0.05, 0.35, 0.15, 0.35),
    (CompanyStage.DEVELOPMENT, CompanyTier.MEGA): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.DEVELOPMENT, CompanyTier.LARGE): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.DEVELOPMENT, CompanyTier.MID): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.DEVELOPMENT, CompanyTier.SMALL): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.DEVELOPMENT, CompanyTier.MICRO): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.DEVELOPMENT, CompanyTier.NANO): (0.10, 0.10, 0.30, 0.20, 0.30),
    (CompanyStage.LEASE_UP, CompanyTier.MEGA): (0.15, 0.15, 0.25, 0.25, 0.20),
    (CompanyStage.LEASE_UP, CompanyTier.LARGE): (0.15, 0.15, 0.25, 0.25, 0.20),
    (CompanyStage.LEASE_UP, CompanyTier.MID): (0.15, 0.15, 0.25, 0.25, 0.20),
    (CompanyStage.LEASE_UP, CompanyTier.SMALL): (0.15, 0.15, 0.25, 0.25, 0.20),
    (CompanyStage.LEASE_UP, CompanyTier.MICRO): (0.15, 0.15, 0.25, 0.25, 0.20),
    (CompanyStage.LEASE_UP, CompanyTier.NANO): (0.15, 0.15, 0.25, 0.25, 0.20),
    (CompanyStage.STABILIZED, CompanyTier.MEGA): (0.25, 0.25, 0.15, 0.15, 0.20),
    (CompanyStage.STABILIZED, CompanyTier.LARGE): (0.25, 0.25, 0.15, 0.15, 0.20),
    (CompanyStage.STABILIZED, CompanyTier.MID): (0.25, 0.25, 0.15, 0.15, 0.20),
    (CompanyStage.STABILIZED, CompanyTier.SMALL): (0.20, 0.20, 0.25, 0.15, 0.20),
    (CompanyStage.STABILIZED, CompanyTier.MICRO): (0.20, 0.20, 0.25, 0.15, 0.20),
    (CompanyStage.STABILIZED, CompanyTier.NANO): (0.20, 0.20, 0.25, 0.15, 0.20),
    (CompanyStage.NET_LEASE, CompanyTier.MEGA): (0.25, 0.20, 0.25, 0.10, 0.20),
    (CompanyStage.NET_LEASE, CompanyTier.LARGE): (0.25, 0.20, 0.25, 0.10, 0.20),
    (CompanyStage.NET_LEASE, CompanyTier.MID): (0.25, 0.20, 0.25, 0.10, 0.20),
    (CompanyStage.NET_LEASE, CompanyTier.SMALL): (0.25, 0.20, 0.25, 0.10, 0.20),
    (CompanyStage.NET_LEASE, CompanyTier.MICRO): (0.25, 0.20, 0.25, 0.10, 0.20),
    (CompanyStage.NET_LEASE, CompanyTier.NANO): (0.25, 0.20, 0.25, 0.10, 0.20),
}
_DEFAULT_WEIGHTS = (0.20, 0.20, 0.25, 0.15, 0.20)


def generate_conclusion(report: AnalysisReport) -> AnalysisConclusion:
    c = AnalysisConclusion()
    tier, stage = report.profile.tier, report.profile.stage

    val_score = _score_valuation(report)
    prof_score = _score_profitability(report)
    solv_score = _score_solvency(report)
    grow_score = _score_growth(report)
    quality_score = _safe(report.real_estate_quality.quality_score) if report.real_estate_quality else 0

    c.category_scores = {"valuation": round(val_score, 1), "profitability": round(prof_score, 1),
                         "solvency": round(solv_score, 1), "growth": round(grow_score, 1),
                         "real_estate_quality": round(quality_score, 1)}

    w = _WEIGHTS.get((stage, tier), _DEFAULT_WEIGHTS)
    c.overall_score = round(val_score * w[0] + prof_score * w[1] + solv_score * w[2] + grow_score * w[3] + quality_score * w[4], 1)
    c.verdict = _verdict(c.overall_score)
    c.category_summaries = _build_summaries(report)
    c.strengths = _find_strengths(report)
    c.risks = _find_risks(report)
    c.summary = _build_narrative(report, c)
    c.tier_note = _tier_note(tier)
    c.stage_note = _stage_note(stage)
    c.screening_checklist = _reit_screening(report)
    return c


def _verdict(score: float) -> str:
    if score >= 75: return "Strong Buy"
    if score >= 60: return "Buy"
    if score >= 45: return "Hold"
    if score >= 30: return "Caution"
    return "Avoid"


def _score_valuation(r: AnalysisReport) -> float:
    v = r.valuation
    if v is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    # For stabilized / net lease REITs, P/FFO and P/AFFO drive valuation
    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE):
        p_ffo = _safe(v.p_ffo, None)
        if p_ffo is not None:
            if p_ffo < 10: score += 20
            elif p_ffo < 14: score += 10
            elif p_ffo < 18: score += 3
            elif p_ffo >= 25: score -= 10
        p_affo = _safe(v.p_affo, None)
        if p_affo is not None:
            if p_affo < 12: score += 15
            elif p_affo < 18: score += 7
            elif p_affo >= 28: score -= 10
        cap_rate = _safe(v.implied_cap_rate, None)
        if cap_rate is not None:
            if cap_rate > 0.08: score += 12
            elif cap_rate > 0.06: score += 6
            elif cap_rate < 0.04: score -= 8
        ffo_y = _safe(v.ffo_yield, None)
        if ffo_y is not None:
            if ffo_y > 0.10: score += 10
            elif ffo_y > 0.07: score += 5
            elif ffo_y < 0.04: score -= 5
        div_y = _safe(v.dividend_yield, None)
        if div_y is not None:
            if div_y > 0.06: score += 8
            elif div_y > 0.04: score += 4
    else:
        # Pre-revenue stages lean on NAV / cash / tangible book
        p_nav = _safe(v.p_nav, None)
        if p_nav is not None:
            if p_nav < 0.8: score += 20
            elif p_nav < 1.0: score += 10
            elif p_nav > 1.3: score -= 10
        pb = _safe(v.pb_ratio, None)
        if pb is not None:
            if pb < 1: score += 15
            elif pb < 1.5: score += 7
            elif pb >= 3: score -= 10
        ctm = _safe(v.cash_to_market_cap, None)
        if ctm is not None:
            if ctm > 0.50: score += 15
            elif ctm > 0.30: score += 8
            elif ctm > 0.15: score += 3
    return max(0, min(100, score))


def _score_profitability(r: AnalysisReport) -> float:
    if r.profile.stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT):
        return 50.0
    p = r.profitability
    if p is None:
        return 50.0
    score = 50.0
    # Occupancy rate — core REIT operating metric
    occ = _safe(p.occupancy_rate, None)
    if occ is not None:
        if occ > 0.95: score += 15
        elif occ > 0.90: score += 8
        elif occ > 0.85: score += 2
        elif occ < 0.80: score -= 12
    # NOI margin
    noi_m = _safe(p.noi_margin, None)
    if noi_m is not None:
        if noi_m > 0.65: score += 12
        elif noi_m > 0.55: score += 6
        elif noi_m < 0.40: score -= 8
    # FFO margin
    ffo_m = _safe(p.ffo_margin, None)
    if ffo_m is not None:
        if ffo_m > 0.40: score += 10
        elif ffo_m > 0.25: score += 5
        elif ffo_m < 0.10: score -= 8
    # Same-store NOI growth signals portfolio health
    ss_noi = _safe(p.same_store_noi_growth, None)
    if ss_noi is not None:
        if ss_noi > 0.04: score += 10
        elif ss_noi > 0.02: score += 5
        elif ss_noi < 0: score -= 10
    roe = _safe(p.roe, None)
    if roe is not None:
        if roe > 0.12: score += 8
        elif roe > 0.06: score += 3
        elif roe < 0: score -= 10
    return max(0, min(100, score))


def _score_solvency(r: AnalysisReport) -> float:
    s = r.solvency
    if s is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    de = _safe(s.debt_to_equity, None)
    if de is not None:
        if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT):
            if de == 0: score += 15
            elif de < 0.3: score += 10
            elif de > 1.0: score -= 20
        else:
            if de < 0.8: score += 10
            elif de < 1.5: score += 3
            elif de > 3.0: score -= 15
    # Debt to gross assets — REIT leverage standard
    dga = _safe(s.debt_to_gross_assets, None)
    if dga is not None:
        if dga < 0.35: score += 10
        elif dga < 0.50: score += 5
        elif dga > 0.65: score -= 12
    # Fixed-charge coverage — critical for REIT debt service
    fcc = _safe(s.fixed_charge_coverage, None)
    if fcc is not None:
        if fcc > 3.5: score += 10
        elif fcc > 2.5: score += 5
        elif fcc < 1.5: score -= 12
    # Weighted average debt maturity (years)
    wadm = _safe(s.weighted_avg_debt_maturity, None)
    if wadm is not None:
        if wadm > 7: score += 6
        elif wadm > 5: score += 3
        elif wadm < 3: score -= 6
    # Fixed rate debt share — protects from rate shocks
    fxd = _safe(s.pct_fixed_rate_debt, None)
    if fxd is not None:
        if fxd > 0.85: score += 5
        elif fxd < 0.50: score -= 5
    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT, CompanyStage.LEASE_UP):
        burn = _safe(s.cash_burn_rate, None)
        if burn is not None and burn < 0:
            runway = _safe(s.cash_runway_years, None)
            if runway is not None:
                if runway > 3: score += 5
                elif runway < 1: score -= 25
                elif runway < 1.5: score -= 15
                elif runway < 2: score -= 5
        bpct = _safe(s.burn_as_pct_of_market_cap, None)
        if bpct is not None and bpct > 0.08:
            score -= 10
    dsc = _safe(s.debt_service_coverage, None)
    if dsc is not None:
        if dsc > 3: score += 5
        elif dsc < 1.2: score -= 10
    return max(0, min(100, score))


def _score_growth(r: AnalysisReport) -> float:
    g = r.growth
    if g is None:
        return 50.0
    score = 50.0
    stage = r.profile.stage
    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT, CompanyStage.LEASE_UP):
        dil = _safe(g.shares_growth_yoy, None)
        if dil is not None:
            if dil < 0.01: score += 15
            elif dil < 0.05: score += 5
            elif dil > 0.20: score -= 25
            elif dil > 0.10: score -= 15
        bv = _safe(g.book_value_growth_yoy, None)
        if bv is not None:
            if bv > 0.10: score += 10
            elif bv > 0: score += 5
            elif bv < -0.10: score -= 10
        return max(0, min(100, score))
    # FFO growth — primary REIT growth metric
    ffo_g = _safe(g.ffo_growth_yoy, None)
    if ffo_g is not None:
        if ffo_g > 0.08: score += 15
        elif ffo_g > 0.04: score += 7
        elif ffo_g < -0.02: score -= 12
    affo_g = _safe(g.affo_growth_yoy, None)
    if affo_g is not None:
        if affo_g > 0.06: score += 10
        elif affo_g > 0.03: score += 5
        elif affo_g < 0: score -= 8
    ss = _safe(g.same_store_noi_growth_yoy, None)
    if ss is not None:
        if ss > 0.04: score += 10
        elif ss > 0.02: score += 5
        elif ss < 0: score -= 10
    # AFFO payout ratio — distribution sustainability
    af_pay = _safe(g.affo_payout_ratio, None)
    if af_pay is not None:
        if 0.60 <= af_pay <= 0.85: score += 10
        elif af_pay > 1.0: score -= 15
        elif af_pay < 0.50: score += 3
    # Distribution growth (5y)
    dist_g = _safe(g.distribution_growth_5y, None)
    if dist_g is not None:
        if dist_g > 0.05: score += 8
        elif dist_g > 0.02: score += 4
        elif dist_g < 0: score -= 8
    dil = _safe(g.shares_growth_yoy, None)
    if dil is not None:
        if dil < -0.02: score += 5
        elif dil > 0.10: score -= 10
    return max(0, min(100, score))


def _reit_screening(r: AnalysisReport) -> dict:
    checks = {}
    s, g, ss, v, p = r.solvency, r.growth, r.share_structure, r.valuation, r.profitability
    stage = r.profile.stage

    runway = _safe(s.cash_runway_years, None) if s else None
    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT, CompanyStage.LEASE_UP):
        if runway is not None:
            checks["cash_runway_18m"] = runway > 1.5
        elif s and _safe(s.cash_burn_rate, None) is not None and s.cash_burn_rate >= 0:
            checks["cash_runway_18m"] = True
        else:
            checks["cash_runway_18m"] = None
    else:
        checks["cash_runway_18m"] = None

    dil = _safe(g.shares_growth_yoy, None) if g else None
    checks["low_dilution"] = dil < 0.05 if dil is not None else None

    insider = _safe(ss.insider_ownership_pct, None) if ss else None
    checks["insider_ownership"] = insider > 0.05 if insider is not None else None

    fd = _safe(ss.fully_diluted_shares, None) if ss else None
    checks["tight_share_structure"] = fd < 200_000_000 if fd is not None else None

    de = _safe(s.debt_to_equity, None) if s else None
    if de is not None:
        checks["no_excessive_debt"] = de < 0.5 if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT) else de < 2.0
    else:
        checks["no_excessive_debt"] = None

    # REIT-specific: debt to gross assets <= 60% is a common threshold
    dga = _safe(s.debt_to_gross_assets, None) if s else None
    checks["debt_to_gross_assets_ok"] = dga < 0.60 if dga is not None else None

    fcc = _safe(s.fixed_charge_coverage, None) if s else None
    checks["fixed_charge_coverage_ok"] = fcc > 2.0 if fcc is not None else None

    wc = _safe(s.working_capital, None) if s else None
    checks["positive_working_capital"] = wc > 0 if wc is not None else None
    checks["management_track_record"] = None

    jt = r.profile.jurisdiction_tier
    checks["tier_1_2_jurisdiction"] = jt in (JurisdictionTier.TIER_1, JurisdictionTier.TIER_2) if jt != JurisdictionTier.UNKNOWN else None

    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT):
        ctm = _safe(r.valuation.cash_to_market_cap, None) if r.valuation else None
        checks["cash_backing"] = ctm > 0.30 if ctm is not None else None
    else:
        checks["cash_backing"] = None

    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE, CompanyStage.LEASE_UP):
        checks["has_rental_income"] = any(fs.revenue and fs.revenue > 0 for fs in r.financials)
    else:
        checks["has_rental_income"] = None

    # REIT distribution sustainability
    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE) and g:
        af_pay = _safe(g.affo_payout_ratio, None)
        checks["distribution_covered_by_affo"] = af_pay < 1.0 if af_pay is not None else None
        ffo_pay = _safe(g.ffo_payout_ratio, None)
        checks["distribution_covered_by_ffo"] = ffo_pay < 0.95 if ffo_pay is not None else None
    else:
        checks["distribution_covered_by_affo"] = None
        checks["distribution_covered_by_ffo"] = None

    # Occupancy screen for operating REITs
    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE) and p:
        occ = _safe(p.occupancy_rate, None)
        checks["high_occupancy"] = occ > 0.90 if occ is not None else None
    else:
        checks["high_occupancy"] = None

    # Cap rate vs valuation sanity check
    if stage in (CompanyStage.STABILIZED, CompanyStage.NET_LEASE) and v:
        cap = _safe(v.implied_cap_rate, None)
        checks["reasonable_cap_rate"] = cap > 0.05 if cap is not None else None
    else:
        checks["reasonable_cap_rate"] = None

    return checks


def _build_summaries(r: AnalysisReport) -> dict[str, str]:
    summaries: dict[str, str] = {}
    stage = r.profile.stage
    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT):
        ctm = _safe(r.valuation.cash_to_market_cap, None) if r.valuation else None
        summaries["valuation"] = f"Cash backing: {ctm*100:.0f}% of market cap" if ctm else "Limited valuation data (pre-operating REIT)"
    else:
        p_ffo = _safe(r.valuation.p_ffo, None) if r.valuation else None
        p_affo = _safe(r.valuation.p_affo, None) if r.valuation else None
        if p_ffo:
            summaries["valuation"] = f"P/FFO of {p_ffo:.1f}" + (f", P/AFFO {p_affo:.1f}" if p_affo else "")
        else:
            pe = _safe(r.valuation.pe_trailing, None) if r.valuation else None
            summaries["valuation"] = f"P/E of {pe:.1f}" if pe else "Limited valuation data"
    if stage in (CompanyStage.PRE_DEVELOPMENT, CompanyStage.DEVELOPMENT):
        summaries["profitability"] = "Pre-operating — no rental income yet"
    else:
        occ = _safe(r.profitability.occupancy_rate, None) if r.profitability else None
        noi_m = _safe(r.profitability.noi_margin, None) if r.profitability else None
        if occ is not None:
            summaries["profitability"] = f"Occupancy: {occ*100:.1f}%" + (f", NOI margin {noi_m*100:.0f}%" if noi_m else "")
        elif noi_m is not None:
            summaries["profitability"] = f"NOI margin: {noi_m*100:.1f}%"
        else:
            summaries["profitability"] = "Limited data"
    if r.solvency:
        dga = _safe(r.solvency.debt_to_gross_assets, None)
        fcc = _safe(r.solvency.fixed_charge_coverage, None)
        runway = _safe(r.solvency.cash_runway_years, None)
        if dga is not None:
            summaries["solvency"] = f"Debt/Gross Assets: {dga*100:.0f}%" + (f", FCC {fcc:.1f}x" if fcc else "")
        elif runway is not None:
            summaries["solvency"] = f"Cash runway: {runway:.1f} years"
        elif _safe(r.solvency.cash_burn_rate, None) is not None and r.solvency.cash_burn_rate >= 0:
            summaries["solvency"] = "Cash flow positive"
        else:
            summaries["solvency"] = "Limited solvency data"
    else:
        summaries["solvency"] = "Limited solvency data"
    if r.growth:
        ffo_g = _safe(r.growth.ffo_growth_yoy, None)
        ssn = _safe(r.growth.same_store_noi_growth_yoy, None)
        if ffo_g is not None:
            summaries["growth"] = f"FFO growth YoY: {ffo_g*100:.1f}%" + (f", SSNOI {ssn*100:.1f}%" if ssn else "")
        elif ssn is not None:
            summaries["growth"] = f"Same-store NOI growth: {ssn*100:.1f}%"
        else:
            dil = _safe(r.growth.shares_growth_yoy, None)
            summaries["growth"] = f"Share dilution: {dil*100:.1f}%/yr" if dil is not None else "Limited growth data"
    else:
        summaries["growth"] = "Limited growth data"
    summaries["real_estate_quality"] = (r.real_estate_quality.competitive_position or "N/A") if r.real_estate_quality else "N/A"
    return summaries


def _find_strengths(r: AnalysisReport) -> list[str]:
    strengths = []
    if r.solvency:
        dga = _safe(r.solvency.debt_to_gross_assets, None)
        if dga is not None and dga < 0.35:
            strengths.append(f"Conservative leverage (Debt/GA {dga*100:.0f}%)")
        fcc = _safe(r.solvency.fixed_charge_coverage, None)
        if fcc is not None and fcc > 3.0:
            strengths.append(f"Strong debt coverage (FCC {fcc:.1f}x)")
        wadm = _safe(r.solvency.weighted_avg_debt_maturity, None)
        if wadm is not None and wadm > 7:
            strengths.append(f"Long debt maturity ({wadm:.1f}y)")
        runway = _safe(r.solvency.cash_runway_years, None)
        if runway and runway > 3:
            strengths.append(f"Strong cash position ({runway:.1f} years runway)")
    if r.profitability:
        occ = _safe(r.profitability.occupancy_rate, None)
        if occ is not None and occ > 0.95:
            strengths.append(f"High occupancy ({occ*100:.1f}%)")
        noi_m = _safe(r.profitability.noi_margin, None)
        if noi_m is not None and noi_m > 0.65:
            strengths.append(f"Strong NOI margin ({noi_m*100:.0f}%)")
    if r.valuation:
        cap = _safe(r.valuation.implied_cap_rate, None)
        if cap is not None and cap > 0.07:
            strengths.append(f"Attractive implied cap rate ({cap*100:.1f}%)")
        p_affo = _safe(r.valuation.p_affo, None)
        if p_affo is not None and p_affo < 14:
            strengths.append(f"Low P/AFFO ({p_affo:.1f})")
        p_nav = _safe(r.valuation.p_nav, None)
        if p_nav is not None and p_nav < 0.9:
            strengths.append(f"Trading below NAV (P/NAV {p_nav:.2f})")
    if r.growth:
        ffo_g = _safe(r.growth.ffo_growth_yoy, None)
        if ffo_g is not None and ffo_g > 0.08:
            strengths.append(f"FFO growth {ffo_g*100:.1f}% YoY")
        dist_g = _safe(r.growth.distribution_growth_5y, None)
        if dist_g is not None and dist_g > 0.05:
            strengths.append(f"Consistent distribution growth ({dist_g*100:.1f}%/yr)")
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil < 0.02:
            strengths.append("Minimal share dilution")
    if r.share_structure:
        if r.share_structure.share_structure_assessment and "Tight" in r.share_structure.share_structure_assessment:
            strengths.append("Tight share structure")
        insider = _safe(r.share_structure.insider_ownership_pct, None)
        if insider and insider > 0.10:
            strengths.append(f"Strong insider ownership ({insider*100:.0f}%)")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_1:
        strengths.append("Tier 1 real estate jurisdiction")
    return strengths[:6]


def _find_risks(r: AnalysisReport) -> list[str]:
    risks = []
    if r.solvency:
        dga = _safe(r.solvency.debt_to_gross_assets, None)
        if dga is not None and dga > 0.60:
            risks.append(f"Elevated leverage (Debt/GA {dga*100:.0f}%)")
        fcc = _safe(r.solvency.fixed_charge_coverage, None)
        if fcc is not None and fcc < 1.8:
            risks.append(f"Thin debt coverage (FCC {fcc:.1f}x)")
        runway = _safe(r.solvency.cash_runway_years, None)
        if runway is not None and runway < 1.5:
            risks.append(f"Limited cash runway ({runway:.1f} years)")
        bpct = _safe(r.solvency.burn_as_pct_of_market_cap, None)
        if bpct and bpct > 0.08:
            risks.append(f"High burn rate ({bpct*100:.0f}% of market cap/yr)")
    if r.profitability:
        occ = _safe(r.profitability.occupancy_rate, None)
        if occ is not None and occ < 0.85:
            risks.append(f"Low occupancy ({occ*100:.1f}%)")
    if r.growth:
        af_pay = _safe(r.growth.affo_payout_ratio, None)
        if af_pay is not None and af_pay > 1.0:
            risks.append(f"Distribution exceeds AFFO (payout {af_pay*100:.0f}%)")
        ssn = _safe(r.growth.same_store_noi_growth_yoy, None)
        if ssn is not None and ssn < -0.02:
            risks.append(f"Negative same-store NOI growth ({ssn*100:.1f}%)")
        dil = _safe(r.growth.shares_growth_yoy, None)
        if dil is not None and dil > 0.10:
            risks.append(f"Heavy share dilution ({dil*100:.1f}%/yr)")
    if r.share_structure and r.share_structure.share_structure_assessment and "Bloated" in r.share_structure.share_structure_assessment:
        risks.append("Bloated share structure (>500M shares)")
    if r.profile.jurisdiction_tier == JurisdictionTier.TIER_3:
        risks.append("Tier 3 jurisdiction — high geopolitical risk")
    if r.profile.stage == CompanyStage.PRE_DEVELOPMENT:
        risks.append("Pre-development stage — no rental income yet, binary execution risk")
    if r.profile.stage == CompanyStage.DEVELOPMENT:
        risks.append("Under construction — delivery and cost-overrun risk")
    return risks[:6]


def _build_narrative(r: AnalysisReport, c: AnalysisConclusion) -> str:
    parts = [f"{r.profile.name} ({r.profile.tier.value}, {r.profile.stage.value}) scores {c.overall_score:.0f}/100 — '{c.verdict}'."]
    if c.strengths:
        parts.append(f"Strengths: {c.strengths[0].lower()}" + (f" and {c.strengths[1].lower()}" if len(c.strengths) > 1 else "") + ".")
    if c.risks:
        parts.append(f"Risks: {c.risks[0].lower()}" + (f" and {c.risks[1].lower()}" if len(c.risks) > 1 else "") + ".")
    return " ".join(parts)


def _tier_note(tier: CompanyTier) -> str:
    return {
        CompanyTier.MEGA: "Full traditional REIT analysis. P/FFO, P/AFFO and implied cap rate primary.",
        CompanyTier.LARGE: "Full REIT analysis. All metrics reliable; dividend track record matters.",
        CompanyTier.MID: "Blended REIT analysis. Portfolio quality and leverage weighted heavily.",
        CompanyTier.SMALL: "Balance sheet critical. Debt maturity ladder and payout sustainability key.",
        CompanyTier.MICRO: "Survival and dilution metrics dominate. Leverage and distribution coverage critical.",
        CompanyTier.NANO: "Speculative. NAV-based valuation only. High execution and liquidity risk.",
    }.get(tier, "")


def _stage_note(stage: CompanyStage) -> str:
    return {
        CompanyStage.PRE_DEVELOPMENT: "Pre-Development: land banking / entitlement phase. Cash backing, insider ownership and catalyst density are primary. No rental income yet — binary execution risk.",
        CompanyStage.DEVELOPMENT: "Development: under construction. Debt service, capex discipline and dilution control are key. Cost overruns (20-40%) common. NAV and cash runway critical.",
        CompanyStage.LEASE_UP: "Lease-Up: property filling up. Occupancy trajectory and same-store NOI growth emerge. Leverage and interest coverage begin to matter as NOI ramps.",
        CompanyStage.STABILIZED: "Stabilized Operating REIT: P/FFO, P/AFFO, implied cap rate, occupancy and same-store NOI are primary. Dividend sustainability via AFFO payout ratio is central.",
        CompanyStage.NET_LEASE: "Net Lease / Triple-Net: long-duration, contractual rental income. Distribution growth, fixed-charge coverage, debt maturity ladder and tenant quality dominate.",
    }.get(stage, "")
