"""Stop-loss logic: hard stop (ATR-based) and trailing stop."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.data.storage import DataStore

logger = logging.getLogger(__name__)


@dataclass
class StopLossAlert:
    symbol: str
    trigger_type: str  # "hard_stop" or "trailing_stop"
    entry_price: float
    current_price: float
    stop_price: float
    loss_pct: float
    can_sell_today: bool  # False if T+1 constraint blocks it


def check_hard_stop(
    holdings: dict,
    store: DataStore,
    config: dict,
    date: str,
) -> list[StopLossAlert]:
    """Check hard stop-loss: trigger when loss > N x ATR.

    Args:
        holdings: {symbol: {"entry_price": float, "buy_date": str, "shares": int}}
        store: DataStore instance.
        config: Settings dict.
        date: Current date string.

    Returns:
        List of StopLossAlert for stocks that hit hard stop.
    """
    risk_cfg = config.get("risk", {})
    atr_multiple = risk_cfg.get("hard_stop_atr_multiple", 2.0)

    alerts = []
    for symbol, holding in holdings.items():
        entry_price = holding["entry_price"]
        buy_date = holding.get("buy_date", "")

        # T+1: can only sell if bought before today
        can_sell = buy_date < date

        # Get current price and ATR
        df = store.read_stock_daily(symbol, end_date=date)
        if len(df) < 21:
            continue

        current_price = df["close"].iloc[-1]
        atr = _compute_atr(df, period=14)

        stop_price = entry_price - atr_multiple * atr
        loss_pct = (current_price - entry_price) / entry_price

        if current_price <= stop_price:
            alerts.append(StopLossAlert(
                symbol=symbol,
                trigger_type="hard_stop",
                entry_price=entry_price,
                current_price=current_price,
                stop_price=stop_price,
                loss_pct=loss_pct,
                can_sell_today=can_sell,
            ))
            logger.warning(
                "Hard stop triggered: %s, loss=%.2f%%, ATR stop=%.2f",
                symbol, loss_pct * 100, stop_price,
            )

    return alerts


def check_trailing_stop(
    holdings: dict,
    store: DataStore,
    config: dict,
    date: str,
) -> list[StopLossAlert]:
    """Check trailing stop-loss: activate at +10% gain, trigger at 8% drop from peak.

    Args:
        holdings: {symbol: {"entry_price": float, "buy_date": str, "peak_price": float}}
        store: DataStore instance.
        config: Settings dict.
        date: Current date string.

    Returns:
        List of StopLossAlert for stocks that hit trailing stop.
    """
    risk_cfg = config.get("risk", {})
    activation_pct = risk_cfg.get("trailing_stop_activation", 0.10)
    drop_pct = risk_cfg.get("trailing_stop_drop", 0.08)

    alerts = []
    for symbol, holding in holdings.items():
        entry_price = holding["entry_price"]
        buy_date = holding.get("buy_date", "")
        peak_price = holding.get("peak_price", entry_price)

        can_sell = buy_date < date

        df = store.read_stock_daily(symbol, end_date=date)
        if df.empty:
            continue

        current_price = df["close"].iloc[-1]

        # Update peak price
        if current_price > peak_price:
            peak_price = current_price
            holding["peak_price"] = peak_price

        # Check if trailing stop is activated (gained > activation_pct from entry)
        gain_from_entry = (peak_price - entry_price) / entry_price
        if gain_from_entry < activation_pct:
            continue

        # Check if dropped from peak
        drop_from_peak = (peak_price - current_price) / peak_price
        if drop_from_peak >= drop_pct:
            loss_pct = (current_price - entry_price) / entry_price
            stop_price = peak_price * (1 - drop_pct)
            alerts.append(StopLossAlert(
                symbol=symbol,
                trigger_type="trailing_stop",
                entry_price=entry_price,
                current_price=current_price,
                stop_price=stop_price,
                loss_pct=loss_pct,
                can_sell_today=can_sell,
            ))
            logger.warning(
                "Trailing stop triggered: %s, peak=%.2f, current=%.2f, drop=%.2f%%",
                symbol, peak_price, current_price, drop_from_peak * 100,
            )

    return alerts


def _compute_atr(df: pd.DataFrame, period: int = 14) -> float:
    """Compute Average True Range."""
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values

    tr = np.maximum(
        high[1:] - low[1:],
        np.maximum(
            np.abs(high[1:] - close[:-1]),
            np.abs(low[1:] - close[:-1]),
        ),
    )
    if len(tr) < period:
        return np.mean(tr) if len(tr) > 0 else 0.0
    return np.mean(tr[-period:])
