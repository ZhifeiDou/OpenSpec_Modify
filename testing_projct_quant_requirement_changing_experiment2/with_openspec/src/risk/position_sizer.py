"""Volatility-based position sizing: max loss per stock = 2% of portfolio at 2x ATR stop distance."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.risk.stop_loss import _compute_atr

logger = logging.getLogger(__name__)


def compute_position_size(
    symbol: str,
    portfolio_value: float,
    config: dict,
    store: DataStore,
    date: str | None = None,
) -> dict:
    """Compute maximum position size based on volatility.

    The idea: at the hard stop-loss distance (2x ATR), the max loss
    should not exceed max_risk_per_stock (2%) of portfolio.

    Returns dict with:
        max_shares: int
        max_value: float
        max_weight: float
        atr: float
        stop_distance: float
    """
    risk_cfg = config.get("risk", {})
    max_risk_pct = risk_cfg.get("max_risk_per_stock", 0.02)
    atr_multiple = risk_cfg.get("hard_stop_atr_multiple", 2.0)

    df = store.read_stock_daily(symbol, end_date=date)
    if len(df) < 21:
        logger.warning("Insufficient data for position sizing: %s", symbol)
        return {
            "max_shares": 0,
            "max_value": 0.0,
            "max_weight": 0.0,
            "atr": 0.0,
            "stop_distance": 0.0,
        }

    current_price = df["close"].iloc[-1]
    atr = _compute_atr(df, period=14)
    stop_distance = atr_multiple * atr

    if stop_distance <= 0 or current_price <= 0:
        return {
            "max_shares": 0,
            "max_value": 0.0,
            "max_weight": 0.0,
            "atr": atr,
            "stop_distance": stop_distance,
        }

    # Max loss = portfolio_value * max_risk_pct
    # Max shares = max_loss / stop_distance
    max_loss = portfolio_value * max_risk_pct
    max_shares_float = max_loss / stop_distance

    # A-share: must buy in lots of 100
    max_shares = int(max_shares_float // 100) * 100
    max_value = max_shares * current_price
    max_weight = max_value / portfolio_value if portfolio_value > 0 else 0.0

    return {
        "max_shares": max_shares,
        "max_value": max_value,
        "max_weight": max_weight,
        "atr": atr,
        "stop_distance": stop_distance,
    }


def adjust_weights_by_volatility(
    target_weights: pd.Series,
    portfolio_value: float,
    config: dict,
    store: DataStore,
    date: str | None = None,
) -> pd.Series:
    """Adjust target weights so no single stock exceeds volatility-based position limit."""
    adjusted = target_weights.copy()

    for symbol in adjusted.index:
        sizing = compute_position_size(symbol, portfolio_value, config, store, date)
        max_weight = sizing["max_weight"]

        if max_weight > 0 and adjusted[symbol] > max_weight:
            logger.info(
                "Vol-sizing cap: %s weight %.2f%% → %.2f%%",
                symbol, adjusted[symbol] * 100, max_weight * 100,
            )
            adjusted[symbol] = max_weight

    # Renormalize to maintain position ratio
    original_sum = target_weights.sum()
    adjusted_sum = adjusted.sum()
    if adjusted_sum > 0 and original_sum > 0:
        adjusted = adjusted * (original_sum / adjusted_sum)

    return adjusted
