"""Backward-compat shim — delegates to :mod:`lynx_investor_core.storage`.

All storage logic lives in the shared core package; this module re-exports it
so existing imports keep working. The base directory is configured at package
import time by ``lynx_realestate.__init__``.
"""

from __future__ import annotations

from lynx_investor_core.storage import (  # noqa: F401
    _sanitize_ticker,
    drop_cache_all,
    drop_cache_ticker,
    get_base_dir,
    get_cache_age_hours,
    get_company_dir,
    get_data_root,
    get_financials_dir,
    get_mode,
    get_news_dir,
    get_reports_dir,
    has_cache,
    is_testing,
    list_cached_tickers,
    list_saved_analyses,
    load_cached_report,
    load_json,
    save_analysis_report,
    save_binary,
    save_json,
    save_text,
    set_base_dir,
    set_mode,
)
