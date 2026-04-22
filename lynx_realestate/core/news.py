"""News fetching for real estate companies (shim over :mod:`lynx_investor_core.news`)."""

from __future__ import annotations

from typing import Optional

from lynx_investor_core import news as _core_news
from lynx_investor_core.models import NewsArticle  # noqa: F401 (re-exported)

from lynx_realestate import NEWS_SECTOR_KEYWORD, USER_AGENT_PRODUCT

_UA = f"Mozilla/5.0 (compatible; {USER_AGENT_PRODUCT}/0.1)"


def fetch_news_yfinance(ticker: str) -> list[NewsArticle]:
    return _core_news.fetch_news_yfinance(ticker)


def fetch_news_rss(company_name: str, ticker: str) -> list[NewsArticle]:
    return _core_news.fetch_news_rss(
        company_name, ticker, sector_keyword=NEWS_SECTOR_KEYWORD,
    )


def fetch_all_news(ticker: str, company_name: Optional[str] = None) -> list[NewsArticle]:
    return _core_news.fetch_all_news(
        ticker, company_name, sector_keyword=NEWS_SECTOR_KEYWORD,
    )


def download_article(ticker: str, article: NewsArticle) -> Optional[str]:
    return _core_news.download_article(ticker, article, user_agent=_UA)
