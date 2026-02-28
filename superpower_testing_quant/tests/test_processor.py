import pytest
import pandas as pd
import numpy as np
from quant_bot.data.processor import DataProcessor


@pytest.fixture
def processor():
    return DataProcessor()


def test_clean_daily_data(processor):
    df = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "open": [10.0, np.nan, 12.0, 13.0],
        "close": [10.5, 11.0, 12.5, 13.5],
        "high": [11.0, 11.5, 13.0, 14.0],
        "low": [9.5, 10.5, 12.0, 13.0],
        "volume": [1000, 0, 1500, 2000],
    })
    cleaned = processor.clean_daily_data(df)
    assert len(cleaned) == 3
    assert not cleaned["open"].isna().any()


def test_merge_stock_data(processor):
    daily = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03"],
        "close": [10.0, 11.0],
    })
    valuation = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03"],
        "pe_ttm": [15.0, 16.0],
        "pb": [2.0, 2.1],
    })
    merged = processor.merge_stock_data(daily, valuation)
    assert "close" in merged.columns
    assert "pe_ttm" in merged.columns
    assert len(merged) == 2
