"""Multi-factor composite scoring: equal-weight and IC-weighted modes."""

import numpy as np
import pandas as pd


CATEGORY_FACTORS = {
    "commodity": ["metal_momentum", "futures_basis", "inventory_change"],
    "fundamental": ["pb_percentile", "gross_margin_trend", "roe_ttm", "ev_ebitda"],
    "technical": ["momentum", "mean_reversion", "turnover", "volatility"],
    "flow": ["financing_change", "northbound_flow"],
    "macro": ["pmi_direction", "usd_momentum", "m1_direction"],
}


def equal_weight_score(factor_df: pd.DataFrame,
                        category_weights: dict[str, float]) -> pd.Series:
    """Compute composite score using equal-weight within categories."""
    scores = pd.Series(0.0, index=factor_df.index)
    for category, weight in category_weights.items():
        cols = [c for c in CATEGORY_FACTORS.get(category, []) if c in factor_df.columns]
        if cols:
            cat_mean = factor_df[cols].mean(axis=1, skipna=True)
            scores += weight * cat_mean.fillna(0)
    return scores


def ic_weighted_score(factor_df: pd.DataFrame,
                       forward_returns: pd.Series,
                       ic_history: dict[str, list[float]],
                       category_weights: dict[str, float],
                       min_history: int = 12) -> pd.Series:
    """Compute composite score using IC-weighted factors.

    Falls back to equal-weight if IC history < min_history months.
    """
    # Check if we have enough IC history
    has_enough = all(
        len(ic_history.get(f, [])) >= min_history
        for factors in CATEGORY_FACTORS.values()
        for f in factors
        if f in factor_df.columns
    )

    if not has_enough:
        return equal_weight_score(factor_df, category_weights)

    scores = pd.Series(0.0, index=factor_df.index)
    for category, cat_weight in category_weights.items():
        cols = [c for c in CATEGORY_FACTORS.get(category, []) if c in factor_df.columns]
        if not cols:
            continue

        # Compute IC_IR for each factor
        ic_irs = {}
        for col in cols:
            hist = ic_history.get(col, [])
            if len(hist) > 0:
                ic_mean = np.mean(hist)
                ic_std = np.std(hist)
                ic_irs[col] = ic_mean / ic_std if ic_std > 0 else 0.0
            else:
                ic_irs[col] = 0.0

        # Normalize IC_IR weights within category
        total_ir = sum(abs(v) for v in ic_irs.values())
        if total_ir > 0:
            for col in cols:
                factor_weight = abs(ic_irs[col]) / total_ir
                scores += cat_weight * factor_weight * factor_df[col].fillna(0)
        else:
            cat_mean = factor_df[cols].mean(axis=1, skipna=True)
            scores += cat_weight * cat_mean.fillna(0)

    return scores
