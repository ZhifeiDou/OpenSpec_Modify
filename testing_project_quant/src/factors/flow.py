"""Fund flow factors: margin balance change, northbound capital net buy."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.factors.base import BaseFactor, register_factor


@register_factor
class MarginBalanceChange5dFactor(BaseFactor):
    name = "margin_balance_change_5d"
    category = "flow"

    def compute(self, universe, date, store, config):
        """5-day margin balance change rate."""
        results = {}
        for symbol in universe:
            df = store.read_table(
                "fund_flow",
                where="symbol = ? AND date <= ?",
                params=(symbol, date),
            )
            if df.empty or "margin_balance" not in df.columns:
                results[symbol] = 0.0  # Neutral if no data (not on margin list)
                continue

            mb = pd.to_numeric(df["margin_balance"], errors="coerce").dropna()
            if len(mb) < 6 or mb.iloc[-6] == 0:
                results[symbol] = 0.0
            else:
                results[symbol] = (mb.iloc[-1] - mb.iloc[-6]) / mb.iloc[-6]

        return pd.Series(results)


@register_factor
class NorthboundNetBuy10dFactor(BaseFactor):
    name = "northbound_net_buy_10d"
    category = "flow"

    def compute(self, universe, date, store, config):
        """10-day cumulative northbound capital net buy amount."""
        results = {}
        for symbol in universe:
            df = store.read_table(
                "fund_flow",
                where="symbol = ? AND date <= ?",
                params=(symbol, date),
            )
            if df.empty or "northbound_net_buy" not in df.columns:
                results[symbol] = 0.0
                continue

            nb = pd.to_numeric(df["northbound_net_buy"], errors="coerce").dropna()
            if len(nb) < 10:
                results[symbol] = nb.sum() if len(nb) > 0 else 0.0
            else:
                results[symbol] = nb.iloc[-10:].sum()

        return pd.Series(results)
