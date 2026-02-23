"""Tests for data pipeline: caching and failover."""

import pytest
import pandas as pd
import os
from src.data.cache import DataCache


@pytest.fixture
def cache(tmp_path):
    db_path = str(tmp_path / "test_cache.db")
    c = DataCache(db_path=db_path)
    yield c
    c.close()


class TestDataCache:
    def test_save_and_retrieve_stock_prices(self, cache):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "open": [10.0, 10.5],
            "high": [10.5, 11.0],
            "low": [9.8, 10.2],
            "close": [10.3, 10.8],
            "volume": [1000, 1200],
            "amount": [10300, 12960],
        })
        cache.save_stock_prices("600000", df)
        result = cache.get_stock_prices("600000", "2024-01-01", "2024-01-02")
        assert len(result) == 2
        assert result.iloc[0]["close"] == 10.3

    def test_has_data_returns_true_when_cached(self, cache):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "open": [10.0, 10.5, 11.0],
            "high": [10.5, 11.0, 11.5],
            "low": [9.8, 10.2, 10.8],
            "close": [10.3, 10.8, 11.2],
            "volume": [1000, 1200, 1100],
            "amount": [10300, 12960, 12320],
        })
        cache.save_stock_prices("600000", df)
        assert cache.has_data("stock_prices", "code", "600000", "2024-01-01", "2024-01-03")

    def test_has_data_returns_false_when_not_cached(self, cache):
        assert not cache.has_data("stock_prices", "code", "600000", "2024-01-01", "2024-01-03")

    def test_get_latest_date(self, cache):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "open": [10.0, 10.5],
            "high": [10.5, 11.0],
            "low": [9.8, 10.2],
            "close": [10.3, 10.8],
            "volume": [1000, 1200],
            "amount": [10300, 12960],
        })
        cache.save_stock_prices("600000", df)
        assert cache.get_latest_date("stock_prices", "code", "600000") == "2024-01-02"

    def test_metal_futures_cache(self, cache):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "close": [8500.0, 8600.0],
        })
        cache.save_metal_futures("copper", df)
        result = cache.get_metal_futures("copper", "2024-01-01", "2024-01-02")
        assert len(result) == 2
