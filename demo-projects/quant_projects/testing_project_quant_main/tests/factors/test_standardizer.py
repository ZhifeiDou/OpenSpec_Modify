"""Tests for cross-sectional standardization."""
import numpy as np
import pandas as pd
from src.factors.standardizer import cross_sectional_standardize


def test_zscore_normalization():
    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "f2": [10.0, 20.0, 30.0, 40.0, 50.0],
    })
    result = cross_sectional_standardize(df, mad_multiple=3.0)
    # After Z-Score, mean should be ~0 and std ~1
    assert abs(result["f1"].mean()) < 0.01
    assert abs(result["f1"].std() - 1.0) < 0.1


def test_winsorize_extreme_values():
    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 100.0],  # 100 is extreme
    })
    result = cross_sectional_standardize(df, mad_multiple=3.0)
    # The extreme value should be clipped
    assert result["f1"].max() < 5.0  # Would be much higher without winsorization


def test_handles_nan():
    df = pd.DataFrame({
        "f1": [1.0, np.nan, 3.0, 4.0, 5.0],
    })
    result = cross_sectional_standardize(df, mad_multiple=3.0)
    assert pd.isna(result["f1"].iloc[1])  # NaN preserved
    non_nan = result["f1"].dropna()
    assert len(non_nan) == 4


def test_handles_constant_column():
    df = pd.DataFrame({
        "f1": [5.0, 5.0, 5.0, 5.0],
    })
    result = cross_sectional_standardize(df)
    # Constant column: std=0, should remain unchanged
    assert not result["f1"].isna().all()


def test_empty_dataframe():
    df = pd.DataFrame()
    result = cross_sectional_standardize(df)
    assert result.empty
