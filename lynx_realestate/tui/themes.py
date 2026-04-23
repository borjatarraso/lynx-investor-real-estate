"""Custom Textual themes for the lynx-realestate TUI application.

Ships a small set of sector-flavored "house" themes plus the full
Suite-wide gallery (Catppuccin, Dracula, Tokyo Night, Nord, Gruvbox,
Kanagawa, Matrix, Synthwave '84, and more) — see
:mod:`lynx_investor_core.themes` for the full list.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from textual.theme import Theme

from lynx_investor_core.themes import (
    SUITE_THEMES,
    SUITE_THEME_NAMES,
    register_suite_themes,
)

if TYPE_CHECKING:
    from textual.app import App


# Sector-flavored "house" themes (kept from prior versions).

LYNX_DARK = Theme(
    name="realestate-dark",
    primary="#89b4fa",
    secondary="#a6adc8",
    accent="#f9e2af",
    warning="#fab387",
    error="#f38ba8",
    success="#a6e3a1",
    foreground="#cdd6f4",
    background="#1e1e2e",
    surface="#313244",
    panel="#45475a",
    dark=True,
)

LYNX_LIGHT = Theme(
    name="realestate-light",
    primary="#1e66f5",
    secondary="#6c6f85",
    accent="#df8e1d",
    warning="#fe640b",
    error="#d20f39",
    success="#40a02b",
    foreground="#4c4f69",
    background="#eff1f5",
    surface="#e6e9ef",
    panel="#ccd0da",
    dark=False,
)

HOUSE_THEMES: List[Theme] = [LYNX_DARK, LYNX_LIGHT]

CUSTOM_THEMES: List[Theme] = HOUSE_THEMES + SUITE_THEMES

THEME_NAMES: List[str] = (
    ["realestate-dark", "realestate-light"] + SUITE_THEME_NAMES + ["textual-dark", "textual-light"]
)


def register_all_themes(app: "App") -> None:
    """Register every house + Suite theme on *app*."""
    for theme in HOUSE_THEMES:
        app.register_theme(theme)
    register_suite_themes(app)
