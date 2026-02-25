import os
import pytest
import pandas as pd
from quant_bot.data.cache import DataCache


@pytest.fixture
def cache(tmp_path):
    return DataCache(cache_dir=str(tmp_path))


def test_save_and_load(cache):
    df = pd.DataFrame({"date": ["2024-01-02", "2024-01-03"], "close": [10.0, 11.0]})
    cache.save("test_stock", "daily", df)
    loaded = cache.load("test_stock", "daily")
    assert loaded is not None
    assert len(loaded) == 2
    assert loaded["close"].iloc[0] == 10.0


def test_load_missing(cache):
    result = cache.load("nonexistent", "daily")
    assert result is None


def test_is_cached(cache):
    df = pd.DataFrame({"a": [1]})
    assert not cache.is_cached("x", "daily")
    cache.save("x", "daily", df)
    assert cache.is_cached("x", "daily")
