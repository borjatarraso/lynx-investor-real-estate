"""Entry-point registration for the Lince Investor Suite plugin system.

Exposed via ``pyproject.toml`` under the ``lynx_investor_suite.agents``
entry-point group. See :mod:`lynx_investor_core.plugins` for the
discovery contract.
"""

from __future__ import annotations

from lynx_investor_core.plugins import SectorAgent

from lynx_realestate import APP_TAGLINE, PROG_NAME, __version__


def register() -> SectorAgent:
    """Return this agent's descriptor for the plugin registry."""
    return SectorAgent(
        name="lynx-investor-real-estate",
        short_name="realestate",
        sector="Real Estate",
        tagline=APP_TAGLINE,
        prog_name=PROG_NAME,
        version=__version__,
        package_module="lynx_realestate",
        entry_point_module="lynx_realestate.__main__",
        entry_point_function="main",
        icon="\U0001f3e2",  # office building
    )
