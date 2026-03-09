"""Tests for data quality validators."""
import pandas as pd
import numpy as np
from src.data.validators import validate_stock_daily, validate_futures_daily


def test_validate_stock_daily_clean_data():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-02", periods=5, freq="B"),
        "open": [10.0, 10.1, 10.2, 10.3, 10.4],
        "high": [10.5, 10.6, 10.7, 10.8, 10.9],
        "low": [9.5, 9.6, 9.7, 9.8, 9.9],
        "close": [10.2, 10.3, 10.4, 10.5, 10.6],
        "volume": [1000, 2000, 3000, 4000, 5000],
        "amount": [10000, 20000, 30000, 40000, 50000],
    })
    result = validate_stock_daily(df)
    assert result.passed
    assert len(result.warnings) == 0
    assert len(result.clean_df) == 5


def test_validate_stock_daily_removes_negative_prices():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-02", periods=3, freq="B"),
        "open": [10.0, -1.0, 10.2],
        "high": [10.5, 10.6, 10.7],
        "low": [9.5, 9.6, 9.7],
        "close": [10.2, 10.3, 10.4],
        "volume": [1000, 2000, 3000],
        "amount": [10000, 20000, 30000],
    })
    result = validate_stock_daily(df)
    assert len(result.clean_df) == 2
    assert result.dropped_rows >= 1
    assert any("non-positive" in w for w in result.warnings)


def test_validate_stock_daily_removes_duplicates():
    dates = pd.to_datetime(["2024-01-02", "2024-01-02", "2024-01-03"])
    df = pd.DataFrame({
        "date": dates,
        "open": [10.0, 10.0, 10.1],
        "high": [10.5, 10.5, 10.6],
        "low": [9.5, 9.5, 9.6],
        "close": [10.2, 10.2, 10.3],
        "volume": [1000, 1000, 2000],
        "amount": [10000, 10000, 20000],
    })
    result = validate_stock_daily(df)
    assert len(result.clean_df) == 2


def test_validate_empty_dataframe():
    result = validate_stock_daily(pd.DataFrame())
    assert result.passed
    assert result.clean_df.empty


def test_validate_futures_daily():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-02", periods=3, freq="B"),
        "open": [70000, 70100, 70200],
        "high": [70500, 70600, 70700],
        "low": [69500, 69600, 69700],
        "close": [70200, 70300, 70400],
        "volume": [100000, 200000, 300000],
    })
    result = validate_futures_daily(df)
    assert result.passed
    assert len(result.clean_df) == 3
