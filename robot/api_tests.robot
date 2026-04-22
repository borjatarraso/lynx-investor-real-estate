*** Settings ***
Documentation    Python API tests for lynx-realestate
Library          Process

*** Variables ***
${PYTHON}        python3

*** Keywords ***
When I Run Python Code "${code}"
    ${result}=    Run Process    ${PYTHON}    -c    ${code}    timeout=120s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

Then The Exit Code Should Be ${expected}
    Should Be Equal As Integers    ${RC}    ${expected}

Then The Output Should Contain "${text}"
    Should Contain    ${OUTPUT}    ${text}

*** Test Cases ***
Import All Models
    [Documentation]    GIVEN the package WHEN I import models THEN all classes are available
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, CompanyStage, CompanyTier, PropertyType, JurisdictionTier, Relevance, MarketIntelligence, InsiderTransaction; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Import All Calculators
    [Documentation]    GIVEN the package WHEN I import calculators THEN all functions exist
    When I Run Python Code "from lynx_realestate.metrics.calculator import calc_valuation, calc_profitability, calc_solvency, calc_growth, calc_efficiency, calc_share_structure, calc_real_estate_quality, calc_intrinsic_value, calc_market_intelligence; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Classify Company Tier Mega Cap
    [Documentation]    GIVEN a large market cap WHEN I classify THEN it returns Mega Cap
    When I Run Python Code "from lynx_realestate.models import classify_tier; print(classify_tier(500_000_000_000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Mega Cap"

Classify Company Tier Micro Cap
    [Documentation]    GIVEN a small market cap WHEN I classify THEN it returns Micro Cap
    When I Run Python Code "from lynx_realestate.models import classify_tier; print(classify_tier(100_000_000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Micro Cap"

Classify Company Tier None
    [Documentation]    GIVEN None market cap WHEN I classify THEN it returns Nano Cap
    When I Run Python Code "from lynx_realestate.models import classify_tier; print(classify_tier(None).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Nano Cap"

Classify Real Estate Stage Stabilized
    [Documentation]    GIVEN a description with stabilized portfolio WHEN I classify THEN Stabilized
    When I Run Python Code "from lynx_realestate.models import classify_stage; print(classify_stage('stabilized portfolio with 95% occupancy and rental income', 500000000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Stabilized"

Classify Real Estate Stage Net Lease
    [Documentation]    GIVEN a triple-net description WHEN I classify THEN Net Lease
    When I Run Python Code "from lynx_realestate.models import classify_stage; print(classify_stage('triple net single-tenant net lease portfolio', 500000000).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Net Lease"

Classify Real Estate Stage Development
    [Documentation]    GIVEN a development-pipeline description WHEN I classify THEN Development
    When I Run Python Code "from lynx_realestate.models import classify_stage; print(classify_stage('construction in progress development pipeline', 0).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Development"

Classify Real Estate Stage Pre-Development
    [Documentation]    GIVEN land-banking description WHEN I classify THEN Pre-Development
    When I Run Python Code "from lynx_realestate.models import classify_stage; print(classify_stage('land banking site selection feasibility study', 0).value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Pre-Development"

Classify Property Type Residential
    [Documentation]    GIVEN residential text WHEN I classify THEN Residential detected
    When I Run Python Code "from lynx_realestate.models import classify_property_type; print(classify_property_type('apartment multifamily residential rental housing', 'REIT').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Residential"

Classify Property Type Industrial
    [Documentation]    GIVEN industrial text WHEN I classify THEN Industrial detected
    When I Run Python Code "from lynx_realestate.models import classify_property_type; print(classify_property_type('industrial logistics warehouse distribution center', 'REIT Industrial').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Industrial"

Classify Property Type Data Center
    [Documentation]    GIVEN data center text WHEN I classify THEN Data Center detected
    When I Run Python Code "from lynx_realestate.models import classify_property_type; print(classify_property_type('data center hyperscale colocation interconnection', 'REIT Specialty').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Data Center"

Classify Jurisdiction Tier 1
    [Documentation]    GIVEN United States WHEN I classify THEN Tier 1
    When I Run Python Code "from lynx_realestate.models import classify_jurisdiction; print(classify_jurisdiction('United States').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Tier 1"

Classify Jurisdiction Tier 2
    [Documentation]    GIVEN Mexico WHEN I classify THEN Tier 2
    When I Run Python Code "from lynx_realestate.models import classify_jurisdiction; print(classify_jurisdiction('Mexico').value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Tier 2"

Relevance Enum Includes IMPORTANT
    [Documentation]    GIVEN Relevance enum WHEN I access IMPORTANT THEN it exists between CRITICAL and RELEVANT
    When I Run Python Code "from lynx_realestate.models import Relevance; vals = [r.value for r in Relevance]; assert 'important' in vals; idx_c = vals.index('critical'); idx_i = vals.index('important'); idx_r = vals.index('relevant'); assert idx_c < idx_i < idx_r; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Relevance Stabilized P FFO Is Decision Grade
    [Documentation]    GIVEN stabilized REIT WHEN I check P/FFO THEN critical / important / relevant
    When I Run Python Code "from lynx_realestate.metrics.relevance import get_relevance; from lynx_realestate.models import CompanyTier, CompanyStage, Relevance; r = get_relevance('p_ffo', CompanyTier.LARGE, 'valuation', CompanyStage.STABILIZED); assert r in (Relevance.CRITICAL, Relevance.IMPORTANT, Relevance.RELEVANT); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Relevance Stabilized Occupancy Rate Is Decision Grade
    [Documentation]    GIVEN stabilized REIT WHEN I check occupancy_rate THEN critical / important / relevant
    When I Run Python Code "from lynx_realestate.metrics.relevance import get_relevance; from lynx_realestate.models import CompanyTier, CompanyStage, Relevance; r = get_relevance('occupancy_rate', CompanyTier.LARGE, 'profitability', CompanyStage.STABILIZED); assert r in (Relevance.CRITICAL, Relevance.IMPORTANT, Relevance.RELEVANT); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Relevance Pre-Development Cash Runway Critical Or Important
    [Documentation]    GIVEN pre-development WHEN I check cash runway THEN critical or important
    When I Run Python Code "from lynx_realestate.metrics.relevance import get_relevance; from lynx_realestate.models import CompanyTier, CompanyStage, Relevance; r = get_relevance('cash_runway_years', CompanyTier.MICRO, 'solvency', CompanyStage.PRE_DEVELOPMENT); assert r in (Relevance.CRITICAL, Relevance.IMPORTANT); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Get Metric Explanation P FFO
    [Documentation]    GIVEN metric key p_ffo WHEN I get explanation THEN details returned
    When I Run Python Code "from lynx_realestate.metrics.explanations import get_explanation; e = get_explanation('p_ffo'); print(e.full_name)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Funds From Operations"

Get Unknown Metric Returns None
    [Documentation]    GIVEN bad key WHEN I get explanation THEN None
    When I Run Python Code "from lynx_realestate.metrics.explanations import get_explanation; print(get_explanation('nonexistent'))"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "None"

Get Sector Insight Real Estate
    [Documentation]    GIVEN Real Estate WHEN I get insight THEN data returned
    When I Run Python Code "from lynx_realestate.metrics.sector_insights import get_sector_insight; s = get_sector_insight('Real Estate'); print('OK' if s else 'FAIL')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Get Industry Insight REIT Residential
    [Documentation]    GIVEN REIT-Residential WHEN I get insight THEN data returned
    When I Run Python Code "from lynx_realestate.metrics.sector_insights import get_industry_insight; i = get_industry_insight('REIT\u2014Residential'); print('OK' if i else 'FAIL')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Storage Mode Switching
    [Documentation]    GIVEN storage WHEN I switch modes THEN it works
    When I Run Python Code "from lynx_realestate.core.storage import set_mode, get_mode, is_testing; set_mode('testing'); assert is_testing(); set_mode('production'); assert not is_testing(); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Storage Invalid Mode Raises Error
    [Documentation]    GIVEN storage WHEN I set invalid mode THEN error
    When I Run Python Code "from lynx_realestate.core.storage import set_mode; set_mode('invalid')"
    Then The Exit Code Should Be 1
    Then The Output Should Contain "ValueError"

Export Formats Available
    [Documentation]    GIVEN export module WHEN I check formats THEN all exist
    When I Run Python Code "from lynx_realestate.export import ExportFormat; print(ExportFormat.TXT.value, ExportFormat.HTML.value, ExportFormat.PDF.value)"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "txt html pdf"

About Text Has All Fields
    [Documentation]    GIVEN package WHEN I get about THEN all fields present
    When I Run Python Code "from lynx_realestate import get_about_text; a = get_about_text(); assert all(k in a for k in ['name','suite','version','author','license','description']); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Conclusion Generation
    [Documentation]    GIVEN minimal report WHEN I generate conclusion THEN a verdict is produced
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile; from lynx_realestate.core.conclusion import generate_conclusion; r = AnalysisReport(profile=CompanyProfile(ticker='TEST', name='Test')); c = generate_conclusion(r); assert c.verdict in ['Strong Buy','Buy','Hold','Caution','Avoid']; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

REIT Metrics In Explanations
    [Documentation]    GIVEN explanations WHEN I list THEN REIT metrics present
    When I Run Python Code "from lynx_realestate.metrics.explanations import list_metrics; keys = [m.key for m in list_metrics()]; assert 'p_ffo' in keys; assert 'quality_score' in keys; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

REIT Valuation Metrics FFO And AFFO Exist
    [Documentation]    GIVEN ValuationMetrics WHEN I check p_ffo and p_affo THEN they exist
    When I Run Python Code "from lynx_realestate.models import ValuationMetrics; v = ValuationMetrics(); assert hasattr(v, 'p_ffo'); assert hasattr(v, 'p_affo'); assert hasattr(v, 'implied_cap_rate'); assert hasattr(v, 'ffo_yield'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

REIT Profitability Metrics NOI FFO AFFO Occupancy Exist
    [Documentation]    GIVEN ProfitabilityMetrics WHEN I check REIT fields THEN they exist
    When I Run Python Code "from lynx_realestate.models import ProfitabilityMetrics; p = ProfitabilityMetrics(); assert hasattr(p, 'noi'); assert hasattr(p, 'noi_margin'); assert hasattr(p, 'ffo'); assert hasattr(p, 'affo'); assert hasattr(p, 'ffo_per_share'); assert hasattr(p, 'affo_per_share'); assert hasattr(p, 'same_store_noi_growth'); assert hasattr(p, 'occupancy_rate'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

REIT Solvency Fields Exist
    [Documentation]    GIVEN SolvencyMetrics WHEN I check REIT leverage fields THEN they exist
    When I Run Python Code "from lynx_realestate.models import SolvencyMetrics; s = SolvencyMetrics(); assert hasattr(s, 'debt_to_gross_assets'); assert hasattr(s, 'fixed_charge_coverage'); assert hasattr(s, 'weighted_avg_debt_maturity'); assert hasattr(s, 'pct_fixed_rate_debt'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

REIT Growth Fields Exist
    [Documentation]    GIVEN GrowthMetrics WHEN I check REIT fields THEN they exist
    When I Run Python Code "from lynx_realestate.models import GrowthMetrics; g = GrowthMetrics(); assert hasattr(g, 'ffo_growth_yoy'); assert hasattr(g, 'affo_growth_yoy'); assert hasattr(g, 'distribution_growth_5y'); assert hasattr(g, 'affo_payout_ratio'); assert hasattr(g, 'ffo_payout_ratio'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

General FCF Yield And CROCI Still Present
    [Documentation]    GIVEN generic quality metrics WHEN I check fcf_yield and croci THEN they still exist
    When I Run Python Code "from lynx_realestate.models import ValuationMetrics, ProfitabilityMetrics; v = ValuationMetrics(); p = ProfitabilityMetrics(); assert hasattr(v, 'fcf_yield'); assert hasattr(p, 'croci'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Financial Statement Has REIT Specific Fields
    [Documentation]    GIVEN FinancialStatement WHEN I check REIT-specific line items THEN they exist
    When I Run Python Code "from lynx_realestate.models import FinancialStatement; s = FinancialStatement(period='2024'); assert hasattr(s, 'real_estate_assets'); assert hasattr(s, 'accumulated_depreciation'); assert hasattr(s, 'rental_income'); assert hasattr(s, 'property_operating_expenses'); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

CompanyStage Has REIT Stages
    [Documentation]    GIVEN CompanyStage WHEN I enumerate THEN real-estate stages are present
    When I Run Python Code "from lynx_realestate.models import CompanyStage; vals = {s.name for s in CompanyStage}; assert vals == {'PRE_DEVELOPMENT','DEVELOPMENT','LEASE_UP','STABILIZED','NET_LEASE'}; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

PropertyType Replaces Commodity
    [Documentation]    GIVEN PropertyType WHEN I check values THEN key property types are present
    When I Run Python Code "from lynx_realestate.models import PropertyType; names = {p.name for p in PropertyType}; required = {'RESIDENTIAL','OFFICE','RETAIL','INDUSTRIAL','HOTEL','HEALTHCARE','SELF_STORAGE','DATA_CENTER','INFRASTRUCTURE','NET_LEASE','DIVERSIFIED','OTHER'}; assert required.issubset(names); print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

AnalysisReport Uses Real Estate Quality Field
    [Documentation]    GIVEN AnalysisReport WHEN I set real_estate_quality THEN it accepts RealEstateQualityIndicators
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, RealEstateQualityIndicators; rq = RealEstateQualityIndicators(quality_score=75.0); r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T'), real_estate_quality=rq); assert r.real_estate_quality.quality_score == 75.0; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Profile Uses Primary Property Type
    [Documentation]    GIVEN CompanyProfile WHEN I set primary_property_type THEN it accepts PropertyType
    When I Run Python Code "from lynx_realestate.models import CompanyProfile, PropertyType; p = CompanyProfile(ticker='T', name='T', primary_property_type=PropertyType.INDUSTRIAL); assert p.primary_property_type == PropertyType.INDUSTRIAL; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"
