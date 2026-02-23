"""Hard stop-loss and trailing stop-loss implementation."""

import numpy as np
import pandas as pd


def calculate_atr(prices: pd.DataFrame, period: int = 14) -> float:
    """Calculate Average True Range."""
    if len(prices) < period + 1:
        return np.nan
    high = prices["high"]
    low = prices["low"]
    close = prices["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.tail(period).mean()


def check_hard_stop_loss(current_price: float, entry_price: float,
                          atr: float, multiplier: float = 2.0) -> bool:
    """Check if hard stop-loss is triggered.

    Returns True if price dropped below entry - multiplier * ATR.
    """
    if np.isnan(atr):
        return False
    stop_level = entry_price - multiplier * atr
    return current_price <= stop_level


def check_trailing_stop(current_price: float, entry_price: float,
                         peak_price: float,
                         activation_gain: float = 0.10,
                         drawdown_trigger: float = 0.08) -> tuple[bool, bool]:
    """Check trailing stop status.

    Returns:
        (is_active, is_triggered): Whether trailing stop is active and if triggered.
    """
    is_active = peak_price >= entry_price * (1 + activation_gain)
    if not is_active:
        return False, False
    stop_level = peak_price * (1 - drawdown_trigger)
    is_triggered = current_price <= stop_level
    return is_active, is_triggered


class StopLossManager:
    """Manages stop-loss state for all positions."""

    def __init__(self, atr_period: int = 14, atr_multiplier: float = 2.0,
                 activation_gain: float = 0.10, drawdown_trigger: float = 0.08):
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.activation_gain = activation_gain
        self.drawdown_trigger = drawdown_trigger
        self.peak_prices: dict[str, float] = {}

    def update_peak(self, code: str, current_price: float):
        """Update peak price tracking."""
        if code not in self.peak_prices:
            self.peak_prices[code] = current_price
        else:
            self.peak_prices[code] = max(self.peak_prices[code], current_price)

    def check(self, code: str, current_price: float, entry_price: float,
              price_history: pd.DataFrame) -> dict:
        """Check all stop-loss conditions for a position."""
        self.update_peak(code, current_price)
        atr = calculate_atr(price_history, self.atr_period)

        hard_triggered = check_hard_stop_loss(
            current_price, entry_price, atr, self.atr_multiplier
        )
        trailing_active, trailing_triggered = check_trailing_stop(
            current_price, entry_price, self.peak_prices.get(code, current_price),
            self.activation_gain, self.drawdown_trigger
        )

        return {
            "hard_stop": hard_triggered,
            "trailing_active": trailing_active,
            "trailing_stop": trailing_triggered,
            "should_sell": hard_triggered or trailing_triggered,
        }

    def remove_position(self, code: str):
        """Clean up when position is closed."""
        self.peak_prices.pop(code, None)
