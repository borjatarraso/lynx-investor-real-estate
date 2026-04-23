"""Lynx Real Estate — Fundamental analysis for REITs and real-estate operating companies."""

from pathlib import Path

# Suite-level constants come from lynx-investor-core (shared across every agent).
from lynx_investor_core import (
    LICENSE_NAME,
    LICENSE_TEXT,
    LICENSE_URL,
    SUITE_LABEL,
    SUITE_NAME,
    SUITE_VERSION,
    __author__,
    __author_email__,
    __license__,
    __year__,
)
from lynx_investor_core import storage as _core_storage

# Initialize the shared storage layer with this agent's project root so
# data/ and data_test/ live beside *this* package.
_core_storage.set_base_dir(Path(__file__).resolve().parent.parent)

# ---------------------------------------------------------------------------
# Agent-specific identity
# ---------------------------------------------------------------------------

__version__ = "5.2"  # lynx-investor-real-estate version (independent of core)

APP_NAME = "Lynx Real Estate Analysis"
APP_SHORT_NAME = "Real Estate Analysis"
APP_TAGLINE = "Real Estate Sector Analysis"
APP_SCOPE = "the real estate sector"
PROG_NAME = "lynx-realestate"
PACKAGE_NAME = "lynx_realestate"
USER_AGENT_PRODUCT = "LynxRealEstate"
NEWS_SECTOR_KEYWORD = "REIT stock"

TICKER_SUGGESTIONS = (
    "  - For US REITs, try: SPG, O, PLD, EQIX, AMT, VICI",
    "  - For specialty REITs, try: PSA (storage), WELL (healthcare), DLR (data centers)",
    "  - For TSX REITs, try: REI.UN, HR.UN, SRU.UN, NWH.UN",
    "  - You can also type the full company name: 'Simon Property Group'",
)

DESCRIPTION = (
    "Fundamental analysis specialized for REITs and real-estate operating "
    "companies. Evaluates property portfolios using REIT-specific metrics: "
    "FFO, AFFO, NOI, cap rate, occupancy, same-store NOI growth, P/FFO, "
    "payout ratio, debt-to-EBITDA, and more.\n\n"
    "Part of the Lince Investor Suite."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_logo_ascii() -> str:
    """Load the ASCII logo from img/logo_ascii.txt."""
    from lynx_investor_core.logo import load_logo_ascii
    return load_logo_ascii(Path(__file__).resolve().parent) or "  L Y N X   R E A L   E S T A T E   A N A L Y S I S\n"


def get_about_text() -> dict:
    """Return structured about information (uniform across agents)."""
    from lynx_investor_core.about import AgentMeta, build_about
    meta = AgentMeta(
        app_name=APP_NAME,
        short_name=APP_SHORT_NAME,
        tagline=APP_TAGLINE,
        package_name=PACKAGE_NAME,
        prog_name=PROG_NAME,
        version=__version__,
        description=DESCRIPTION,
        scope_description=APP_SCOPE,
    )
    about = build_about(meta, logo_ascii=get_logo_ascii())
    # Legacy key — some callers still reference about['logo'].
    about["logo"] = about["logo_ascii"]
    return about
