"""Unit tests for the storage module."""

import pytest
from lynx_realestate.core.storage import (
    set_mode, get_mode, is_testing, get_data_root,
    has_cache, drop_cache_all,
)


class TestStorageMode:
    def test_default_is_production(self):
        set_mode("production")
        assert get_mode() == "production"
        assert not is_testing()

    def test_switch_to_testing(self):
        set_mode("testing")
        assert get_mode() == "testing"
        assert is_testing()

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            set_mode("invalid")

    def test_data_root_exists(self):
        set_mode("testing")
        root = get_data_root()
        assert root.exists()
        set_mode("production")

    def test_has_cache_false_in_testing(self):
        set_mode("testing")
        assert not has_cache("NONEXISTENT_TICKER_12345")
        set_mode("production")
