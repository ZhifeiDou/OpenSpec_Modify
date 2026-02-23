"""Stock selection: top N% by composite score."""

import pandas as pd


def select_top_stocks(scores: pd.Series,
                       top_percent: float = 0.20,
                       max_stocks: int = 10) -> list[str]:
    """Select top stocks by composite score.

    Args:
        scores: Series with stock codes as index, composite scores as values.
        top_percent: Top percentage to select (default 20%).
        max_stocks: Maximum number of stocks (default 10).

    Returns:
        List of selected stock codes.
    """
    valid_scores = scores.dropna().sort_values(ascending=False)
    n_top = max(1, int(len(valid_scores) * top_percent))
    n_select = min(n_top, max_stocks)
    return valid_scores.head(n_select).index.tolist()
