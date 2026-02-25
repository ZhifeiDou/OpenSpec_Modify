import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor


class MomentumFactor(BaseFactor):
    """Momentum factors: N-day return, RSI, price position."""

    def __init__(self, lookback=20):
        self.lookback = lookback

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        close = result["close"]

        # N-day return
        result["return_n"] = close.pct_change(self.lookback)

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.lookback, min_periods=self.lookback).mean()
        avg_loss = loss.rolling(window=self.lookback, min_periods=self.lookback).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        result["rsi"] = 100 - (100 / (1 + rs))

        # Price position: where current price sits in N-day range [0, 1]
        rolling_high = result["high"].rolling(window=self.lookback, min_periods=self.lookback).max()
        rolling_low = result["low"].rolling(window=self.lookback, min_periods=self.lookback).min()
        denom = rolling_high - rolling_low
        result["price_position"] = (close - rolling_low) / denom.replace(0, np.nan)

        return result
