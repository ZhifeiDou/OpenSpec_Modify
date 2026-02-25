import pandas as pd
import numpy as np
from quant_bot.factors.base import BaseFactor


class VolatilityFactor(BaseFactor):
    """Volatility factors: historical volatility, ATR. Lower volatility scores higher."""

    def __init__(self, lookback=20):
        self.lookback = lookback

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        close = result["close"]

        log_ret = np.log(close / close.shift(1))
        result["hist_volatility"] = log_ret.rolling(window=self.lookback, min_periods=self.lookback).std() * np.sqrt(252)

        high = result["high"]
        low = result["low"]
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        result["atr"] = tr.rolling(window=self.lookback, min_periods=self.lookback).mean()

        return result
