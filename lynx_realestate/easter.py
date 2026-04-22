"""Easter-egg shim over :mod:`lynx_investor_core.easter`.

Binds real-estate-specific labels and fortune quotes so call sites stay unchanged.
Also re-exports the legacy constants (LYNX_ASCII, WOLF_ASCII, BULL_ASCII,
PICKAXE_ASCII, FORTUNE_QUOTES, ROCKET_ASCII) for callers that reference them
directly (e.g. the Textual TUI).
"""

from __future__ import annotations

from lynx_investor_core import easter as _core_easter
from lynx_investor_core.easter import (  # noqa: F401
    BULL_ASCII,
    GENERIC_FORTUNES,
    ROCKET_ASCII,
    WOLF_ASCII,
)

_REAL_ESTATE_FORTUNES = (
    '"Ninety percent of all millionaires become so through owning real estate." \u2014 Andrew Carnegie',
    '"Don\'t wait to buy real estate. Buy real estate and wait." \u2014 Will Rogers',
    '"Real estate cannot be lost or stolen, nor can it be carried away. Purchased with '
    'common sense, paid for in full, and managed with reasonable care, it is about the '
    'safest investment in the world." \u2014 Franklin D. Roosevelt',
)

FORTUNE_QUOTES = tuple(GENERIC_FORTUNES) + _REAL_ESTATE_FORTUNES

_EGG = _core_easter.AgentEasterEgg(
    label="Real Estate Analysis",
    sublabel="Real Estate Sector Research",
    banner_prog="lynx-realestate",
    extra_fortunes=_REAL_ESTATE_FORTUNES,
)

# Pre-rendered ASCII variants (legacy callers that import these directly).
LYNX_ASCII = _core_easter._lynx_ascii(_EGG.label)
PICKAXE_ASCII = _core_easter._pickaxe_ascii(_EGG.sublabel)


def rich_matrix(console, duration: float = 3.0) -> None:
    _core_easter.rich_matrix(console, duration=duration)


def rich_fortune(console) -> None:
    _core_easter.rich_fortune(console, _EGG)


def rich_rocket(console) -> None:
    _core_easter.rich_rocket(console)


def rich_lynx(console) -> None:
    _core_easter.rich_lynx(console, _EGG)


def tk_fireworks(root) -> None:
    _core_easter.tk_fireworks(root, _EGG)


def tk_rainbow_title(root, count: int = 20) -> None:
    _core_easter.tk_rainbow_title(root, _EGG, count=count)
