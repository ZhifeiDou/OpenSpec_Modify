"""Position allocation: score-proportional weights with constraints."""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def allocate_weights(
    selected_symbols: list[str],
    scores: pd.Series,
    config: dict,
    subsector_map: dict[str, str] | None = None,
    position_ratio: float = 1.0,
) -> pd.Series:
    """Allocate portfolio weights to selected stocks.

    Score-proportional allocation with single-stock and sub-sector caps.

    Args:
        selected_symbols: Symbols selected for the portfolio.
        scores: Full score series (all universe stocks).
        config: Settings dict.
        subsector_map: {symbol: subsector} mapping for sub-sector cap enforcement.
        position_ratio: Timing-adjusted position ratio (0.0 to 1.0).

    Returns:
        pd.Series of target weights indexed by symbol.
    """
    if not selected_symbols:
        return pd.Series(dtype=float)

    strategy_cfg = config.get("strategy", {})
    max_single = strategy_cfg.get("max_single_weight", 0.10)
    max_subsector = strategy_cfg.get("max_subsector_weight", 0.25)

    # Get scores for selected stocks
    sel_scores = scores.loc[selected_symbols].copy()
    sel_scores = sel_scores.clip(lower=0)  # Ensure non-negative

    # Score-proportional weights
    total_score = sel_scores.sum()
    if total_score <= 0:
        # Equal weight fallback
        weights = pd.Series(1.0 / len(selected_symbols), index=selected_symbols)
    else:
        weights = sel_scores / total_score

    # Apply single-stock cap iteratively
    weights = _apply_single_cap(weights, max_single)

    # Apply sub-sector cap
    if subsector_map:
        weights = _apply_subsector_cap(weights, subsector_map, max_subsector)

    # Apply position ratio from timing
    weights = weights * position_ratio

    return weights


def _apply_single_cap(weights: pd.Series, cap: float, max_iter: int = 10) -> pd.Series:
    """Iteratively clip weights at cap and redistribute excess."""
    for _ in range(max_iter):
        excess_mask = weights > cap
        if not excess_mask.any():
            break

        excess = (weights[excess_mask] - cap).sum()
        weights[excess_mask] = cap

        # Redistribute excess proportionally to uncapped stocks
        uncapped = weights[~excess_mask]
        if uncapped.sum() > 0:
            weights[~excess_mask] = uncapped + excess * (uncapped / uncapped.sum())
        else:
            break

    # Final normalization
    total = weights.sum()
    if total > 0:
        weights = weights / total
    return weights


def _apply_subsector_cap(
    weights: pd.Series,
    subsector_map: dict[str, str],
    cap: float,
    max_iter: int = 10,
) -> pd.Series:
    """Iteratively enforce sub-sector weight cap."""
    for _ in range(max_iter):
        # Calculate sub-sector weights
        subsector_weights: dict[str, float] = {}
        for sym, w in weights.items():
            ss = subsector_map.get(sym, "other")
            subsector_weights[ss] = subsector_weights.get(ss, 0.0) + w

        # Find sub-sectors over cap
        over = {ss: sw for ss, sw in subsector_weights.items() if sw > cap}
        if not over:
            break

        for ss, ss_weight in over.items():
            # Stocks in this sub-sector
            ss_stocks = [s for s in weights.index if subsector_map.get(s, "other") == ss]
            scale = cap / ss_weight
            excess = 0.0
            for s in ss_stocks:
                old_w = weights[s]
                new_w = old_w * scale
                excess += old_w - new_w
                weights[s] = new_w

            # Redistribute excess to other sub-sectors
            other_stocks = [s for s in weights.index if subsector_map.get(s, "other") != ss]
            other_total = weights[other_stocks].sum()
            if other_total > 0:
                for s in other_stocks:
                    weights[s] += excess * (weights[s] / other_total)

    # Final normalization
    total = weights.sum()
    if total > 0:
        weights = weights / total
    return weights
