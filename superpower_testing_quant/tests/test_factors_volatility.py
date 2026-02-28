import pytest
import pandas as pd
import numpy as np
from quant_bot.factors.volatility import VolatilityFactor


def make_price_df(n=30):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    np.random.seed(42)
    prices = 10 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "close": prices,
        "high": prices + abs(np.random.randn(n) * 0.3),
        "low": prices - abs(np.random.randn(n) * 0.3),
    })


def test_hist_volatility():
    df = make_price_df(30)
    factor = VolatilityFactor(lookback=20)
    result = factor.calculate(df)
    assert "hist_volatility" in result.columns
    valid = result["hist_volatility"].dropna()
    assert len(valid) > 0
    assert (valid >= 0).all()


def test_atr():
    df = make_price_df(30)
    factor = VolatilityFactor(lookback=14)
    result = factor.calculate(df)
    assert "atr" in result.columns
    valid = result["atr"].dropna()
    assert len(valid) > 0
    assert (valid >= 0).all()
