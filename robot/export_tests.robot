*** Settings ***
Documentation    Export workflow tests for lynx-realestate (uses Python API to avoid network timeouts)
Library          Process

*** Variables ***
${PYTHON}        python3

*** Keywords ***
When I Run Python Code "${code}"
    ${result}=    Run Process    ${PYTHON}    -c    ${code}    timeout=30s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

Then The Exit Code Should Be ${expected}
    Should Be Equal As Integers    ${RC}    ${expected}

Then The Output Should Contain "${text}"
    Should Contain    ${OUTPUT}    ${text}

*** Test Cases ***
Export TXT From Minimal Report
    [Documentation]    GIVEN a report WHEN I export as TXT THEN a readable file is created
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics; from lynx_realestate.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='SPG', name='Simon Property Group', sector='Real Estate', industry='REIT\u2014Retail', country='United States', market_cap=50000000000); p.tier = CompanyTier.LARGE; p.stage = CompanyStage.STABILIZED; r = AnalysisReport(profile=p, valuation=ValuationMetrics(p_ffo=12.0, p_affo=15.0, implied_cap_rate=0.065, dividend_yield=0.05), profitability=ProfitabilityMetrics(noi=2500000000, noi_margin=0.72, ffo=4200000000, affo=3600000000, occupancy_rate=0.945, same_store_noi_growth=0.035), solvency=SolvencyMetrics(debt_to_gross_assets=0.42, fixed_charge_coverage=3.1, weighted_avg_debt_maturity=7.2)); f = tempfile.NamedTemporaryFile(suffix='.txt', delete=False); path = export_report(r, ExportFormat.TXT, Path(f.name)); content = path.read_text(); assert 'Simon Property Group' in content; assert 'Stabilized' in content; assert len(content) > 500; print('OK', len(content), 'bytes')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export HTML From Minimal Report
    [Documentation]    GIVEN a report WHEN I export as HTML THEN a styled file with white background
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics; from lynx_realestate.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='O', name='Realty Income Corp', sector='Real Estate', industry='REIT\u2014Retail', country='United States', market_cap=40000000000); p.tier = CompanyTier.LARGE; p.stage = CompanyStage.NET_LEASE; r = AnalysisReport(profile=p, valuation=ValuationMetrics(p_ffo=14.0, p_affo=16.5, implied_cap_rate=0.058), profitability=ProfitabilityMetrics(noi=1800000000, occupancy_rate=0.988, ffo=2400000000), solvency=SolvencyMetrics(debt_to_gross_assets=0.38, weighted_avg_debt_maturity=6.5)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); content = path.read_text(); assert '#fff' in content or '#ffffff' in content, 'Missing white background'; assert 'word-wrap' in content, 'Missing word-wrap'; assert 'Realty Income Corp' in content; assert len(content) > 1000; print('OK', len(content), 'bytes')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

HTML Has No Text Truncation
    [Documentation]    GIVEN an HTML export WHEN I check table cells THEN word-wrap is enabled
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, ValuationMetrics; from lynx_realestate.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='T', name='T Corp'); p.tier = CompanyTier.MICRO; p.stage = CompanyStage.STABILIZED; r = AnalysisReport(profile=p, valuation=ValuationMetrics(p_ffo=10.0)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); c = path.read_text(); assert 'overflow-wrap' in c and 'break-word' in c; assert 'table-layout' in c and 'fixed' in c; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

HTML Has Professional White Background
    [Documentation]    GIVEN an HTML export WHEN I check styling THEN it uses white background
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile; from lynx_realestate.export import export_report, ExportFormat; from pathlib import Path; import tempfile; r = AnalysisReport(profile=CompanyProfile(ticker='T', name='T')); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); c = path.read_text(); assert '#fff' in c or '#ffffff' in c, 'No white bg'; assert 'color: #1a1a2e' in c or 'color:#1a1a2e' in c, 'No dark text'; assert '@media print' in c, 'No print styles'; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export TXT With Real Estate Quality Field
    [Documentation]    GIVEN a report with real_estate_quality WHEN I export as TXT THEN quality data is included
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, CompanyTier, CompanyStage, RealEstateQualityIndicators; from lynx_realestate.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='PLD', name='Prologis Inc', sector='Real Estate', industry='REIT\u2014Industrial', country='United States', market_cap=100000000000); p.tier = CompanyTier.MEGA; p.stage = CompanyStage.STABILIZED; rq = RealEstateQualityIndicators(quality_score=88.0, portfolio_quality='High', occupancy_assessment='Strong 97%+ occupancy', lease_duration_assessment='WALT 6.5 years', tenant_concentration='Diversified'); r = AnalysisReport(profile=p, real_estate_quality=rq); f = tempfile.NamedTemporaryFile(suffix='.txt', delete=False); path = export_report(r, ExportFormat.TXT, Path(f.name)); content = path.read_text(); assert 'Prologis' in content; assert 'Quality' in content or 'quality' in content; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"

Export HTML With REIT Metric Fields
    [Documentation]    GIVEN a report with REIT metrics WHEN I export as HTML THEN new fields are included
    When I Run Python Code "from lynx_realestate.models import AnalysisReport, CompanyProfile, ValuationMetrics, ProfitabilityMetrics, SolvencyMetrics; from lynx_realestate.export import export_report, ExportFormat; from pathlib import Path; import tempfile; p = CompanyProfile(ticker='EQIX', name='Equinix Inc'); r = AnalysisReport(profile=p, valuation=ValuationMetrics(pb_ratio=1.2, p_ffo=24.0, p_affo=28.0, implied_cap_rate=0.045, fcf_yield=0.03), profitability=ProfitabilityMetrics(noi=3200000000, noi_margin=0.51, ffo=2900000000, affo=2500000000, occupancy_rate=0.955, croci=0.09), solvency=SolvencyMetrics(debt_to_gross_assets=0.45, fixed_charge_coverage=3.4, weighted_avg_debt_maturity=7.8, pct_fixed_rate_debt=0.92)); f = tempfile.NamedTemporaryFile(suffix='.html', delete=False); path = export_report(r, ExportFormat.HTML, Path(f.name)); content = path.read_text(); assert 'Equinix Inc' in content; assert len(content) > 1000; print('OK')"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "OK"
