"""Financial data fetching (shim over :mod:`lynx_investor_core.fetcher`)."""

from __future__ import annotations

from lynx_investor_core import fetcher as _core_fetcher
from lynx_realestate.models import CompanyProfile, FinancialStatement


def fetch_info(ticker: str) -> dict:
    return _core_fetcher.fetch_info(ticker)


def fetch_company_profile(ticker: str, info: dict | None = None) -> CompanyProfile:
    return _core_fetcher.fetch_company_profile(ticker, CompanyProfile, info=info)


def fetch_financial_statements(ticker: str) -> list[FinancialStatement]:
    return _core_fetcher.fetch_financial_statements(ticker, FinancialStatement)
