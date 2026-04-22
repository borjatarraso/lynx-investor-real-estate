"""Ticker / ISIN / name resolution (shim over :mod:`lynx_investor_core.ticker`)."""

from __future__ import annotations

from lynx_investor_core.ticker import (  # noqa: F401 — re-exported
    EXCHANGE_SUFFIXES,
    SearchResult,
    console,
    display_search_results,
    is_isin,
    search_companies,
    validate_ticker,
)
from lynx_investor_core import ticker as _core_ticker

from lynx_realestate import TICKER_SUGGESTIONS


def resolve_identifier(identifier: str) -> tuple[str, str | None]:
    return _core_ticker.resolve_identifier(identifier, suggestions=TICKER_SUGGESTIONS)
