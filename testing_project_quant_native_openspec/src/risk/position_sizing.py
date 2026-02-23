"""Position sizing based on max loss constraint."""

import numpy as np


def calculate_position_size(portfolio_value: float,
                             max_loss_pct: float,
                             atr: float,
                             atr_multiplier: float = 2.0,
                             stock_price: float = 1.0) -> int:
    """Calculate maximum shares based on max loss per stock.

    max_loss = portfolio_value * max_loss_pct
    risk_per_share = atr_multiplier * atr
    max_shares = max_loss / risk_per_share

    Args:
        portfolio_value: Total portfolio value.
        max_loss_pct: Maximum loss per stock as fraction of portfolio (default 2%).
        atr: Average True Range of the stock.
        atr_multiplier: ATR multiplier for stop-loss (default 2.0).
        stock_price: Current stock price for lot size calculation.

    Returns:
        Maximum number of shares (rounded down to lot of 100 for A-share).
    """
    if np.isnan(atr) or atr <= 0:
        return 0

    max_loss = portfolio_value * max_loss_pct
    risk_per_share = atr_multiplier * atr
    max_shares = int(max_loss / risk_per_share)

    # A-share: must buy in lots of 100
    max_shares = (max_shares // 100) * 100
    return max(0, max_shares)
