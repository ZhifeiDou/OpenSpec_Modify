import pytest
import pandas as pd
import numpy as np
from quant_bot.factors.value import ValueFactor


def test_value_factor():
    df = pd.DataFrame({
        "date": ["2024-01-02", "2024-01-03", "2024-01-04"],
        "close": [10, 11, 12],
        "pe_ttm": [15.0, 20.0, 10.0],
        "pb": [2.0, 3.0, 1.5],
        "dividend_yield_ttm": [2.5, 1.0, 3.0],
    })
    factor = ValueFactor()
    result = factor.calculate(df)
    assert "ep_ratio" in result.columns
    assert "bp_ratio" in result.columns
    assert "div_yield" in result.columns
    assert result["ep_ratio"].iloc[2] > result["ep_ratio"].iloc[1]


def test_value_factor_handles_zero_pe():
    df = pd.DataFrame({
        "date": ["2024-01-02"],
        "close": [10],
        "pe_ttm": [0.0],
        "pb": [2.0],
        "dividend_yield_ttm": [1.0],
    })
    factor = ValueFactor()
    result = factor.calculate(df)
    assert not np.isinf(result["ep_ratio"].iloc[0])
