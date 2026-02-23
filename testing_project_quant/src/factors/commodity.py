"""Commodity factors: metal price momentum, futures basis, inventory change."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.universe.classifier import SUBSECTOR_METAL_MAP
from src.factors.base import BaseFactor, register_factor


def _get_stock_metal(symbol: str, config: dict, store: DataStore) -> str | None:
    """Look up the metal futures symbol for a stock based on its sub-sector."""
    # Try to find sub-sector from universe cache or default to copper
    universe_df = store.read_table(
        "universe_cache", where="symbol = ?", params=(symbol,)
    )
    if not universe_df.empty and "subsector" in universe_df.columns:
        subsector = universe_df.iloc[0]["subsector"]
        return SUBSECTOR_METAL_MAP.get(subsector, "cu")
    return "cu"  # Default to copper


@register_factor
class MetalPriceMomentum60dFactor(BaseFactor):
    name = "metal_price_mom_60d"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """60-day price momentum of the related SHFE metal futures."""
        # Pre-compute momentum for each metal
        metal_momentum = {}
        for metal_code in set(SUBSECTOR_METAL_MAP.values()):
            if metal_code is None:
                continue
            df = store.read_futures_daily(metal_code, end_date=date)
            if len(df) < 61:
                metal_momentum[metal_code] = np.nan
            else:
                close = df["close"].values
                metal_momentum[metal_code] = close[-1] / close[-61] - 1

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = metal_momentum.get(metal, np.nan) if metal else np.nan

        return pd.Series(results)


@register_factor
class FuturesBasisFactor(BaseFactor):
    name = "futures_basis"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """Futures basis: positive basis (backwardation) is bullish."""
        # Simplified: use last close vs 20-day average as proxy
        metal_basis = {}
        for metal_code in set(SUBSECTOR_METAL_MAP.values()):
            if metal_code is None:
                continue
            df = store.read_futures_daily(metal_code, end_date=date)
            if len(df) < 21:
                metal_basis[metal_code] = np.nan
            else:
                close = df["close"].values
                ma20 = close[-20:].mean()
                metal_basis[metal_code] = (close[-1] - ma20) / ma20 if ma20 > 0 else np.nan

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = metal_basis.get(metal, np.nan) if metal else np.nan

        return pd.Series(results)


@register_factor
class InventoryWeeklyChangeFactor(BaseFactor):
    name = "inventory_weekly_change"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """Weekly inventory change rate. Destocking (negative) is bullish."""
        metal_inv_change = {}
        for metal_code in set(SUBSECTOR_METAL_MAP.values()):
            if metal_code is None:
                continue
            df = store.read_table(
                "inventory", where="metal = ?", params=(metal_code,)
            )
            if df.empty or "inventory" not in df.columns or len(df) < 2:
                metal_inv_change[metal_code] = np.nan
                continue

            inv = pd.to_numeric(df["inventory"], errors="coerce").dropna()
            if len(inv) < 2 or inv.iloc[-2] == 0:
                metal_inv_change[metal_code] = np.nan
            else:
                change = (inv.iloc[-1] - inv.iloc[-2]) / inv.iloc[-2]
                metal_inv_change[metal_code] = -change  # Negate: destocking is positive

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = metal_inv_change.get(metal, np.nan) if metal else np.nan

        return pd.Series(results)
