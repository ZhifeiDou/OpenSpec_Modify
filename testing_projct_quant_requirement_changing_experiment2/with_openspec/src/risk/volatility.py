"""Volatility regime detection: compute volatility ratio and derive adaptive parameters."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.data.storage import DataStore

logger = logging.getLogger(__name__)


def compute_volatility_ratio(
    store: DataStore,
    date: str,
    short_window: int = 20,
    long_window: int = 120,
) -> float:
    """Compute the volatility ratio: recent vol / historical median vol.

    Uses aggregate stock_daily data (average daily returns across available stocks)
    to estimate market-level volatility.

    Args:
        store: DataStore instance.
        date: Current date string (YYYY-MM-DD).
        short_window: Days for recent volatility (default 20).
        long_window: Days for historical median (default 120).

    Returns:
        Volatility ratio. Returns 1.0 (normal) if insufficient data.
    """
    # Get a broad sample of daily close prices to represent the market
    with store._get_conn() as conn:
        rows = conn.execute(
            """SELECT date, AVG(close) as avg_close
               FROM stock_daily
               WHERE date <= ?
               ORDER BY date DESC
               LIMIT ?""",
            (date, long_window + 5),
        ).fetchall()

    if len(rows) < short_window:
        logger.warning(
            "Insufficient data for volatility ratio: %d days (need %d). Using default 1.0.",
            len(rows), short_window,
        )
        return 1.0

    # Compute daily returns (oldest to newest)
    closes = np.array([r[1] for r in reversed(rows)], dtype=float)
    returns = np.diff(closes) / closes[:-1]

    if len(returns) < short_window:
        return 1.0

    # Recent volatility (standard deviation of last short_window returns)
    vol_short = np.std(returns[-short_window:])

    # Historical median volatility: rolling short_window stdev over long_window period
    available = min(len(returns), long_window)
    if available < short_window:
        return 1.0

    rolling_vols = []
    for i in range(short_window, available + 1):
        window = returns[i - short_window:i]
        rolling_vols.append(np.std(window))

    vol_median = np.median(rolling_vols)

    if vol_median <= 0:
        return 1.0

    ratio = vol_short / vol_median
    logger.debug("Volatility ratio on %s: %.3f (short=%.5f, median=%.5f)", date, ratio, vol_short, vol_median)
    return ratio


def get_adaptive_atr_multiple(volatility_ratio: float, config: dict) -> float:
    """Map volatility ratio to ATR multiple for stop-loss.

    Args:
        volatility_ratio: Current volatility ratio.
        config: Settings dict.

    Returns:
        ATR multiple: 1.5 (low vol), 2.0 (normal), or 2.5 (high vol).
    """
    risk_cfg = config.get("risk", {})
    low_threshold = risk_cfg.get("volatility_low_threshold", 0.8)
    high_threshold = risk_cfg.get("volatility_high_threshold", 1.5)
    mult_low = risk_cfg.get("atr_multiple_low_vol", 1.5)
    mult_normal = risk_cfg.get("atr_multiple_normal_vol", 2.0)
    mult_high = risk_cfg.get("atr_multiple_high_vol", 2.5)

    if volatility_ratio < low_threshold:
        return mult_low
    elif volatility_ratio > high_threshold:
        return mult_high
    else:
        return mult_normal


def get_rebalance_regime(volatility_ratio: float, config: dict | None = None) -> str:
    """Map volatility ratio to rebalance frequency regime.

    Args:
        volatility_ratio: Current volatility ratio.
        config: Optional settings dict for custom thresholds.

    Returns:
        "monthly", "biweekly", or "weekly".
    """
    if config:
        risk_cfg = config.get("risk", {})
        biweekly_threshold = risk_cfg.get("volatility_biweekly_threshold", 1.5)
        weekly_threshold = risk_cfg.get("volatility_weekly_threshold", 2.0)
    else:
        biweekly_threshold = 1.5
        weekly_threshold = 2.0

    if volatility_ratio > weekly_threshold:
        return "weekly"
    elif volatility_ratio > biweekly_threshold:
        return "biweekly"
    else:
        return "monthly"
