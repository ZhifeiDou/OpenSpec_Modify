"""Fundamental factors: PB percentile, gross margin trend, ROE_TTM, EV/EBITDA."""

import numpy as np
import pandas as pd


def pb_percentile(current_pb: float, pb_history: pd.Series) -> float:
    """Calculate PB percentile rank over rolling history.
    Lower percentile = cheaper = better score.
    """
    if pd.isna(current_pb) or len(pb_history) < 252:  # ~1 year minimum
        return np.nan
    rank = (pb_history < current_pb).sum() / len(pb_history)
    return 1.0 - rank  # invert: lower PB = higher score


def gross_margin_trend(margins: pd.Series, window: int = 4) -> float:
    """Calculate gross margin trend (slope of recent quarters)."""
    if len(margins) < window:
        return np.nan
    recent = margins.tail(window).values
    x = np.arange(window)
    if np.std(recent) == 0:
        return 0.0
    slope = np.polyfit(x, recent, 1)[0]
    return slope


def roe_ttm_factor(roe: float) -> float:
    """ROE TTM as a factor value."""
    if pd.isna(roe):
        return np.nan
    return roe


def ev_ebitda_factor(ev_ebitda: float) -> float:
    """EV/EBITDA factor — lower is better."""
    if pd.isna(ev_ebitda) or ev_ebitda <= 0:
        return np.nan
    return 1.0 / ev_ebitda  # invert: lower EV/EBITDA = higher score


def compute_fundamental_factors(fundamental_data: dict,
                                 pb_history: pd.Series = None) -> dict:
    """Compute all fundamental factors for a stock."""
    pb = fundamental_data.get("pb", None)
    roe = fundamental_data.get("roe_ttm", None)
    gm = fundamental_data.get("gross_margin", None)
    ev = fundamental_data.get("ev_ebitda", None)

    pb_pct = np.nan
    if pb is not None and pb_history is not None:
        pb_pct = pb_percentile(pb, pb_history)

    return {
        "pb_percentile": pb_pct,
        "gross_margin_trend": np.nan,  # requires quarterly data
        "roe_ttm": roe_ttm_factor(roe) if roe else np.nan,
        "ev_ebitda": ev_ebitda_factor(ev) if ev else np.nan,
    }
