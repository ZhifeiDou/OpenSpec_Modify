import pytest
import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor
from quant_bot.factors.momentum import MomentumFactor


def make_price_df(n=30):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    np.random.seed(42)
    prices = 10 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "close": prices,
        "high": prices + 0.5,
        "low": prices - 0.5,
    })


def test_base_factor_interface():
    with pytest.raises(TypeError):
        BaseFactor()


def test_return_n():
    df = make_price_df(30)
    factor = MomentumFactor(lookback=20)
    result = factor.calculate(df)
    assert "return_n" in result.columns
    assert len(result) == len(df)
    assert result["return_n"].iloc[:20].isna().all()
    assert not result["return_n"].iloc[20:].isna().any()


def test_rsi():
    df = make_price_df(30)
    factor = MomentumFactor(lookback=14)
    result = factor.calculate(df)
    assert "rsi" in result.columns
    valid_rsi = result["rsi"].dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
