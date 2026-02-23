"""Macro factors: PMI direction, USD index momentum, M1 growth direction."""

import numpy as np
import pandas as pd


def pmi_direction(pmi_series: pd.Series) -> float:
    """PMI direction: +1 if > 50 (expansion), -1 if < 50 (contraction)."""
    if len(pmi_series) == 0:
        return np.nan
    latest = pmi_series.iloc[-1]
    if pd.isna(latest):
        return np.nan
    return 1.0 if latest > 50 else -1.0


def usd_index_momentum(usd_series: pd.Series, window: int = 20) -> float:
    """USD index momentum: N-day return (negative = good for commodities)."""
    if len(usd_series) < window:
        return np.nan
    recent = usd_series.iloc[-1]
    past = usd_series.iloc[-window]
    if past == 0:
        return np.nan
    return -((recent - past) / past)  # negative USD momentum is positive for metals


def m1_growth_direction(m1_series: pd.Series) -> float:
    """M1 growth direction: +1 if positive, -1 if negative."""
    if len(m1_series) == 0:
        return np.nan
    latest = m1_series.iloc[-1]
    if pd.isna(latest):
        return np.nan
    return 1.0 if latest > 0 else -1.0


def compute_macro_factors(pmi_data: pd.DataFrame,
                           usd_data: pd.DataFrame,
                           m1_data: pd.DataFrame) -> dict:
    """Compute all macro factors."""
    pmi = np.nan
    if not pmi_data.empty and "pmi" in pmi_data.columns:
        pmi = pmi_direction(pmi_data["pmi"])

    usd = np.nan
    if not usd_data.empty and "usd_index" in usd_data.columns:
        usd = usd_index_momentum(usd_data["usd_index"])

    m1 = np.nan
    if not m1_data.empty and "m1_growth" in m1_data.columns:
        m1 = m1_growth_direction(m1_data["m1_growth"])

    return {
        "pmi_direction": pmi,
        "usd_momentum": usd,
        "m1_direction": m1,
    }
