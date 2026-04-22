"""SEC EDGAR filings (shim over :mod:`lynx_investor_core.reports`)."""

from __future__ import annotations

from typing import Optional

from lynx_investor_core import reports as _core_reports
from lynx_realestate import USER_AGENT_PRODUCT
from lynx_realestate.models import Filing


def fetch_sec_filings(ticker: str) -> list[Filing]:
    return _core_reports.fetch_sec_filings(
        ticker, Filing, user_agent_product=USER_AGENT_PRODUCT,
    )


def download_filing(ticker: str, filing: Filing, max_size_mb: int = 20) -> Optional[str]:
    return _core_reports.download_filing(
        ticker, filing,
        user_agent_product=USER_AGENT_PRODUCT,
        max_size_mb=max_size_mb,
    )


def download_top_filings(ticker: str, filings: list[Filing], max_count: int = 10) -> list[Filing]:
    return _core_reports.download_top_filings(
        ticker, filings,
        user_agent_product=USER_AGENT_PRODUCT,
        max_count=max_count,
    )
