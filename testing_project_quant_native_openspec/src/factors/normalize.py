"""Cross-sectional z-score normalization and winsorization."""

import numpy as np
import pandas as pd


def zscore_normalize(series: pd.Series) -> pd.Series:
    """Z-score normalize a series (mean=0, std=1)."""
    mean = series.mean()
    std = series.std()
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    return (series - mean) / std


def winsorize(series: pd.Series, n_std: float = 3.0) -> pd.Series:
    """Clip values at ±n standard deviations."""
    return series.clip(lower=-n_std, upper=n_std)


def normalize_factors(factor_df: pd.DataFrame) -> pd.DataFrame:
    """Apply z-score normalization and winsorization to all factor columns.

    Args:
        factor_df: DataFrame with stocks as rows, factors as columns.

    Returns:
        Normalized and winsorized factor DataFrame.
    """
    result = factor_df.copy()
    for col in result.columns:
        valid = result[col].dropna()
        if len(valid) < 2:
            continue
        result[col] = zscore_normalize(result[col])
        result[col] = winsorize(result[col])
    return result
