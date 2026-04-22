*** Settings ***
Documentation    CLI integration tests for lynx-realestate
Library          Process
Library          OperatingSystem

*** Variables ***
${PYTHON}        python3
${MODULE}        lynx_realestate

*** Keywords ***
Run App
    [Arguments]    @{args}
    ${result}=    Run Process    ${PYTHON}    -m    ${MODULE}    @{args}    timeout=120s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

Given The Application Is Available
    Run App    --version
    Should Contain    ${OUTPUT}    lynx-realestate

When I Run The Help Command
    Run App    -p    --help

When I Run About
    Run App    --about

When I Run Version
    Run App    --version

When I Explain Metric "${metric}"
    Run App    --explain    ${metric}

When I List All Metrics
    Run App    --explain

When I Explain Section "${section}"
    Run App    --explain-section    ${section}

When I Explain Conclusion "${category}"
    Run App    --explain-conclusion    ${category}

When I Run Python Code "${code}"
    ${result}=    Run Process    ${PYTHON}    -c    ${code}    timeout=30s
    Set Test Variable    ${OUTPUT}    ${result.stdout}${result.stderr}
    Set Test Variable    ${RC}    ${result.rc}

When I Search For "${query}"
    Run App    -p    -s    ${query}

When I List Cache In Testing Mode
    Run App    -t    --list-cache

When I Drop All Cache In Testing Mode
    Run App    -t    --drop-cache    ALL

Then The Exit Code Should Be ${expected}
    Should Be Equal As Integers    ${RC}    ${expected}

Then The Output Should Contain "${text}"
    Should Contain    ${OUTPUT}    ${text}

*** Test Cases ***
Show Help
    [Documentation]    GIVEN the app is available WHEN I run help THEN it shows usage
    Given The Application Is Available
    When I Run The Help Command
    Then The Exit Code Should Be 0
    Then The Output Should Contain "lynx-realestate"
    Then The Output Should Contain "production-mode"
    Then The Output Should Contain "testing-mode"
    Then The Output Should Contain "--gui"
    Then The Output Should Contain "--export"

Show Version
    [Documentation]    GIVEN the app WHEN I run version THEN it shows version info
    Given The Application Is Available
    When I Run Version
    Then The Exit Code Should Be 0
    Then The Output Should Contain "lynx-realestate"
    Then The Output Should Contain "3.0"
    Then The Output Should Contain "Lince Investor Suite"

Show About
    [Documentation]    GIVEN the app WHEN I run about THEN it shows author and license
    Given The Application Is Available
    When I Run About
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Lynx Real Estate Analysis"
    Then The Output Should Contain "Borja Tarraso"
    Then The Output Should Contain "BSD-3-Clause"

Explain A Valuation Metric
    [Documentation]    GIVEN the app WHEN I explain p_ffo THEN it shows details
    Given The Application Is Available
    When I Explain Metric "p_ffo"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "FFO"

Explain A REIT-Specific Metric
    [Documentation]    GIVEN the app WHEN I explain occupancy_rate THEN it shows occupancy info
    Given The Application Is Available
    When I Explain Metric "occupancy_rate"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Occupancy"

List All Available Metrics
    [Documentation]    GIVEN the app WHEN I list metrics THEN it shows the full table including REIT metrics
    Given The Application Is Available
    When I List All Metrics
    Then The Exit Code Should Be 0
    Then The Output Should Contain "p_ffo"
    Then The Output Should Contain "ffo"
    Then The Output Should Contain "affo"
    Then The Output Should Contain "noi"
    Then The Output Should Contain "occupancy_rate"
    Then The Output Should Contain "implied_cap_rate"
    Then The Output Should Contain "quality_score"

Explain A Section
    [Documentation]    GIVEN the app WHEN I explain a section THEN it shows section description
    Given The Application Is Available
    When I Explain Section "real_estate_quality"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Real Estate Quality"

Explain Conclusion Methodology
    [Documentation]    GIVEN the app WHEN I explain conclusion THEN it shows scoring method
    Given The Application Is Available
    When I Explain Conclusion "overall"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "real-estate quality"

Search For A Company
    [Documentation]    GIVEN the app WHEN I search for a company THEN results are shown
    Given The Application Is Available
    When I Search For "REIT"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Search Results"

Drop All Test Cache
    [Documentation]    GIVEN the app WHEN I drop all test cache THEN it confirms
    Given The Application Is Available
    When I Drop All Cache In Testing Mode
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Removed"

Invalid Ticker Shows Error
    [Documentation]    GIVEN the app WHEN I analyze a nonsense ticker THEN it shows an error
    Given The Application Is Available
    Run App    -t    ZZZZZZZZZZZZZ999    --no-reports    --no-news
    Then The Exit Code Should Be 1
    Then The Output Should Contain "Error"

No Identifier Shows Help
    [Documentation]    GIVEN the app WHEN I provide no identifier THEN it shows help
    Given The Application Is Available
    Run App    -p
    Then The Exit Code Should Be 1

Explain REIT Metric FFO
    [Documentation]    GIVEN the app WHEN I explain ffo THEN it shows details
    Given The Application Is Available
    When I Explain Metric "ffo"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "FFO"

Explain REIT Metric AFFO
    [Documentation]    GIVEN the app WHEN I explain affo THEN it shows details
    Given The Application Is Available
    When I Explain Metric "affo"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "AFFO"

Explain REIT Metric NOI
    [Documentation]    GIVEN the app WHEN I explain noi THEN it shows details
    Given The Application Is Available
    When I Explain Metric "noi"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "NOI"

Explain REIT Metric Implied Cap Rate
    [Documentation]    GIVEN the app WHEN I explain implied_cap_rate THEN it shows details
    Given The Application Is Available
    When I Explain Metric "implied_cap_rate"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Cap Rate"

Explain REIT Metric FCF Yield Still Available
    [Documentation]    GIVEN the app WHEN I explain fcf_yield THEN it shows details
    Given The Application Is Available
    When I Explain Metric "fcf_yield"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "FCF"

Explain REIT Metric CROCI Still Available
    [Documentation]    GIVEN the app WHEN I explain croci THEN it shows details
    Given The Application Is Available
    When I Explain Metric "croci"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "CROCI"

Explain Capex To Revenue
    [Documentation]    GIVEN the app WHEN I explain capex_to_revenue THEN it shows details
    Given The Application Is Available
    When I Explain Metric "capex_to_revenue"
    Then The Exit Code Should Be 0
    Then The Output Should Contain "Capex"
