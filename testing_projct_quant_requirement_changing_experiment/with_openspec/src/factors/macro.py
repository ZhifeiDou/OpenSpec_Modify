"""Macro factors: PMI direction, USD index momentum, M1 growth direction."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.factors.base import BaseFactor, register_factor


@register_factor
class PMIDirectionFactor(BaseFactor):
    name = "pmi_direction"
    category = "macro"

    def compute(self, universe, date, store, config):
        """PMI month-over-month direction: +1 if rising, -1 if falling."""
        df = store.read_table("macro", where="indicator = 'pmi'")
        if df.empty or len(df) < 2:
            return pd.Series(np.nan, index=universe)

        values = pd.to_numeric(df["value"], errors="coerce").dropna()
        if len(values) < 2:
            return pd.Series(np.nan, index=universe)

        direction = 1.0 if values.iloc[-1] > values.iloc[-2] else -1.0
        # Macro factors are uniform across all stocks
        return pd.Series(direction, index=universe)


@register_factor
class USDIndexMomentumFactor(BaseFactor):
    name = "usd_index_mom_20d"
    category = "macro"

    def compute(self, universe, date, store, config):
        """USD index 20-day momentum. Negative momentum is bullish for metals."""
        df = store.read_table("macro", where="indicator = 'usd_index'")
        if df.empty or len(df) < 21:
            return pd.Series(np.nan, index=universe)

        values = pd.to_numeric(df["value"], errors="coerce").dropna()
        if len(values) < 21:
            return pd.Series(np.nan, index=universe)

        # Negate: USD weakness is bullish for metals
        mom = -(values.iloc[-1] / values.iloc[-21] - 1)
        return pd.Series(mom, index=universe)


@register_factor
class M1GrowthDirectionFactor(BaseFactor):
    name = "m1_yoy_direction"
    category = "macro"

    def compute(self, universe, date, store, config):
        """M1 year-over-year growth direction: +1 if accelerating, -1 if decelerating."""
        df = store.read_table("macro", where="indicator = 'm1'")
        if df.empty or len(df) < 2:
            return pd.Series(np.nan, index=universe)

        values = pd.to_numeric(df["value"], errors="coerce").dropna()
        if len(values) < 2:
            return pd.Series(np.nan, index=universe)

        direction = 1.0 if values.iloc[-1] > values.iloc[-2] else -1.0
        return pd.Series(direction, index=universe)
