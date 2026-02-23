"""Multi-factor scoring: equal-weight and IC-weighted modes."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def score_stocks(
    factor_matrix: pd.DataFrame,
    config: dict,
    ic_history: pd.DataFrame | None = None,
) -> pd.Series:
    """Score stocks based on standardized factor values.

    Args:
        factor_matrix: DataFrame (stocks x factors), already standardized.
        config: Full settings dict.
        ic_history: Optional DataFrame of historical IC values (dates x factors).
            Required for ic_weight mode.

    Returns:
        pd.Series of composite scores indexed by symbol.
    """
    if factor_matrix.empty:
        return pd.Series(dtype=float)

    factor_cfg = config.get("factors", {})
    mode = factor_cfg.get("scoring_mode", "equal_weight")
    category_weights = factor_cfg.get("weights", {})

    if mode == "ic_weight" and ic_history is not None:
        weights = _ic_weighted(factor_matrix, ic_history, category_weights, factor_cfg)
    else:
        if mode == "ic_weight":
            logger.warning("IC history not available, falling back to equal_weight")
        weights = _equal_weighted(factor_matrix, category_weights)

    # Compute composite score
    scores = (factor_matrix * weights).sum(axis=1)
    return scores


def _equal_weighted(
    factor_matrix: pd.DataFrame, category_weights: dict
) -> pd.Series:
    """Assign equal weight within each category, category weights from config."""
    from src.factors.base import get_registered_factors

    registry = get_registered_factors()
    weights = {}

    # Count factors per category
    category_counts: dict[str, int] = {}
    factor_categories: dict[str, str] = {}
    for name in factor_matrix.columns:
        if name in registry:
            cat = registry[name].category
        else:
            cat = "other"
        factor_categories[name] = cat
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Assign weights
    for name in factor_matrix.columns:
        cat = factor_categories[name]
        cat_weight = category_weights.get(cat, 0.0)
        count = category_counts.get(cat, 1)
        weights[name] = cat_weight / count

    weight_series = pd.Series(weights)
    # Normalize to sum to 1
    total = weight_series.sum()
    if total > 0:
        weight_series = weight_series / total
    return weight_series


def _ic_weighted(
    factor_matrix: pd.DataFrame,
    ic_history: pd.DataFrame,
    category_weights: dict,
    factor_cfg: dict,
) -> pd.Series:
    """IC-weighted scoring: use rolling rank IC to adjust factor weights.

    Falls back to equal weight for factors without enough IC history.
    """
    lookback = factor_cfg.get("ic_lookback_months", 12)

    # Use last `lookback` months of IC data
    if len(ic_history) < lookback:
        logger.warning(
            "IC history (%d months) < lookback (%d), using all available",
            len(ic_history), lookback,
        )
        recent_ic = ic_history
    else:
        recent_ic = ic_history.iloc[-lookback:]

    # Mean IC per factor
    mean_ic = recent_ic.mean()

    # Start with equal weights, then adjust by IC
    from src.factors.base import get_registered_factors
    registry = get_registered_factors()

    weights = {}
    for name in factor_matrix.columns:
        cat = registry.get(name, type("X", (), {"category": "other"})).category if name in registry else "other"
        cat_weight = category_weights.get(cat, 0.0)

        if name in mean_ic.index and not np.isnan(mean_ic[name]):
            # Use IC magnitude as weight modifier (clip negative IC to 0)
            ic_val = max(mean_ic[name], 0.0)
            weights[name] = cat_weight * ic_val
        else:
            # Fallback: equal share of category weight
            weights[name] = cat_weight * 0.03  # Default IC assumption

    weight_series = pd.Series(weights)
    total = weight_series.sum()
    if total > 0:
        weight_series = weight_series / total
    return weight_series


def select_top_stocks(
    scores: pd.Series, config: dict, universe_size: int | None = None
) -> list[str]:
    """Select top N stocks by score.

    N = min(max_stocks, floor(universe_size * top_ratio))
    """
    if scores.empty:
        return []

    strategy_cfg = config.get("strategy", {})
    max_stocks = strategy_cfg.get("max_stocks", 10)
    top_ratio = strategy_cfg.get("top_ratio", 0.2)

    if universe_size is None:
        universe_size = len(scores)

    n = min(max_stocks, int(universe_size * top_ratio))
    n = max(n, 1)  # At least 1

    # Drop NaN scores, sort descending
    valid = scores.dropna().sort_values(ascending=False)
    return valid.head(n).index.tolist()
