"""Technical factors: momentum, reversal, turnover ratio, realized volatility."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.factors.base import BaseFactor, register_factor


@register_factor
class Momentum60dFactor(BaseFactor):
    name = "momentum_60d_skip5"
    category = "technical"

    def compute(self, universe, date, store, config):
        """60-day momentum skipping last 5 days to avoid short-term reversal."""
        results = {}
        for symbol in universe:
            df = store.read_stock_daily(symbol, end_date=date)
            if len(df) < 66:
                results[symbol] = np.nan
                continue

            close = df["close"].values
            # Skip last 5 days: use close[-6] / close[-66] - 1
            results[symbol] = close[-6] / close[-66] - 1

        return pd.Series(results)


@register_factor
class Reversal5dFactor(BaseFactor):
    name = "reversal_5d"
    category = "technical"

    def compute(self, universe, date, store, config):
        """5-day reversal: negative of 5-day return (mean reversion signal)."""
        results = {}
        for symbol in universe:
            df = store.read_stock_daily(symbol, end_date=date)
            if len(df) < 6:
                results[symbol] = np.nan
                continue

            close = df["close"].values
            ret_5d = close[-1] / close[-6] - 1
            results[symbol] = -ret_5d  # Negate: recent losers get higher score

        return pd.Series(results)


@register_factor
class TurnoverRatio20dFactor(BaseFactor):
    name = "turnover_ratio_20d"
    category = "technical"

    def compute(self, universe, date, store, config):
        """Abnormal turnover: today's turnover / 20-day average turnover."""
        results = {}
        for symbol in universe:
            df = store.read_stock_daily(symbol, end_date=date)
            if len(df) < 21:
                results[symbol] = np.nan
                continue

            vol = df["volume"].values
            avg_20 = vol[-21:-1].mean()
            if avg_20 == 0:
                results[symbol] = np.nan
            else:
                results[symbol] = vol[-1] / avg_20

        return pd.Series(results)


@register_factor
class RealizedVolatility20dFactor(BaseFactor):
    name = "realized_vol_20d"
    category = "technical"

    def compute(self, universe, date, store, config):
        """20-day realized volatility (annualized std of daily returns).
        Lower volatility is preferred, so we negate the value.
        """
        results = {}
        for symbol in universe:
            df = store.read_stock_daily(symbol, end_date=date)
            if len(df) < 21:
                results[symbol] = np.nan
                continue

            close = df["close"].values[-21:]
            returns = np.diff(close) / close[:-1]
            vol = returns.std() * np.sqrt(252)
            results[symbol] = -vol  # Negate: lower volatility gets higher score

        return pd.Series(results)
