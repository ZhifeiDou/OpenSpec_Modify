"""Position allocation with constraints."""

import pandas as pd


def allocate_positions(scores: pd.Series,
                        selected_stocks: list[str],
                        subsectors: dict[str, str],
                        single_max: float = 0.10,
                        sector_max: float = 0.25) -> dict[str, float]:
    """Allocate portfolio weights using score-proportional allocation.

    Args:
        scores: Composite scores for all stocks.
        selected_stocks: List of selected stock codes.
        subsectors: Mapping of stock code to subsector name.
        single_max: Maximum weight per stock (default 10%).
        sector_max: Maximum weight per sub-sector (default 25%).

    Returns:
        Dict of stock code to portfolio weight.
    """
    selected_scores = scores[selected_stocks]
    total = selected_scores.sum()
    if total == 0:
        weight = 1.0 / len(selected_stocks)
        return {code: weight for code in selected_stocks}

    # Initial score-proportional weights
    weights = {code: score / total for code, score in selected_scores.items()}

    # Apply single stock limit
    excess = 0.0
    uncapped = []
    for code in list(weights.keys()):
        if weights[code] > single_max:
            excess += weights[code] - single_max
            weights[code] = single_max
        else:
            uncapped.append(code)

    # Redistribute excess to uncapped stocks
    if uncapped and excess > 0:
        uncapped_total = sum(weights[c] for c in uncapped)
        if uncapped_total > 0:
            for code in uncapped:
                weights[code] += excess * (weights[code] / uncapped_total)

    # Apply sub-sector limit
    sector_weights: dict[str, float] = {}
    for code, w in weights.items():
        sector = subsectors.get(code, "other")
        sector_weights[sector] = sector_weights.get(sector, 0) + w

    for sector, total_w in sector_weights.items():
        if total_w > sector_max:
            scale = sector_max / total_w
            for code in weights:
                if subsectors.get(code, "other") == sector:
                    weights[code] *= scale

    # Renormalize to sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {c: w / total_weight for c, w in weights.items()}

    return weights
