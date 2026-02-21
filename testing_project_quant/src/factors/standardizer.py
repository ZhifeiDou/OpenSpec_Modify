"""Cross-sectional factor standardization: MAD winsorization + Z-Score."""
from __future__ import annotations

import numpy as np
import pandas as pd


def cross_sectional_standardize(
    factor_matrix: pd.DataFrame, mad_multiple: float = 3.0
) -> pd.DataFrame:
    """Standardize factor values cross-sectionally.

    Steps per column:
    1. Winsorize at mad_multiple * MAD from median
    2. Z-Score normalize (subtract mean, divide by std)
    """
    result = factor_matrix.copy()

    for col in result.columns:
        series = result[col].dropna()
        if len(series) < 3:
            continue

        # Step 1: MAD winsorization
        median = series.median()
        mad = np.median(np.abs(series - median))
        if mad == 0:
            mad = series.std()
        if mad == 0:
            continue

        upper = median + mad_multiple * mad
        lower = median - mad_multiple * mad
        result[col] = result[col].clip(lower=lower, upper=upper)

        # Step 2: Z-Score
        mean = result[col].mean()
        std = result[col].std()
        if std > 0:
            result[col] = (result[col] - mean) / std

    return result
