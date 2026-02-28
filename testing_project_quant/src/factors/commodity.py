"""Commodity factors: metal price momentum, futures basis, inventory change, gold and silver cross-metal ratios."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.universe.classifier import SUBSECTOR_METAL_MAP
from src.factors.base import BaseFactor, register_factor

logger = logging.getLogger(__name__)


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


@register_factor
class GoldSilverRatioFactor(BaseFactor):
    name = "gold_silver_ratio"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """Gold-silver ratio deviation from rolling mean. Only applies to gold-subsector stocks."""
        gcm_cfg = config.get("factors", {}).get("gold_cross_metal", {})
        lookback = gcm_cfg.get("gsr_lookback", 60)

        au_df = store.read_futures_daily("au", end_date=date)
        ag_df = store.read_futures_daily("ag", end_date=date)

        value = np.nan
        if len(au_df) >= lookback + 1 and len(ag_df) >= lookback + 1:
            au_close = au_df["close"].values[-(lookback + 1):]
            ag_close = ag_df["close"].values[-(lookback + 1):]
            # Align lengths
            n = min(len(au_close), len(ag_close))
            au_close = au_close[-n:]
            ag_close = ag_close[-n:]
            # Compute ratio series
            with np.errstate(divide="ignore", invalid="ignore"):
                ratios = au_close / ag_close
            ratios = ratios[np.isfinite(ratios)]
            if len(ratios) >= lookback + 1:
                rolling_mean = ratios[:-1].mean()
                current_ratio = ratios[-1]
                if rolling_mean > 0:
                    value = (current_ratio - rolling_mean) / rolling_mean
        else:
            logger.warning(
                "Insufficient futures data for gold-silver ratio (au: %d, ag: %d, need: %d)",
                len(au_df), len(ag_df), lookback + 1,
            )

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = value if metal == "au" else np.nan

        return pd.Series(results)


@register_factor
class GoldCopperRatioFactor(BaseFactor):
    name = "gold_copper_ratio"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """Gold-copper ratio rate-of-change. Only applies to gold-subsector stocks."""
        gcm_cfg = config.get("factors", {}).get("gold_cross_metal", {})
        lookback = gcm_cfg.get("gcr_lookback", 20)

        au_df = store.read_futures_daily("au", end_date=date)
        cu_df = store.read_futures_daily("cu", end_date=date)

        value = np.nan
        if len(au_df) >= lookback + 1 and len(cu_df) >= lookback + 1:
            au_close = au_df["close"].values
            cu_close = cu_df["close"].values
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio_today = au_close[-1] / cu_close[-1]
                ratio_past = au_close[-(lookback + 1)] / cu_close[-(lookback + 1)]
            if np.isfinite(ratio_today) and np.isfinite(ratio_past) and ratio_past > 0:
                value = (ratio_today - ratio_past) / ratio_past
        else:
            logger.warning(
                "Insufficient futures data for gold-copper ratio (au: %d, cu: %d, need: %d)",
                len(au_df), len(cu_df), lookback + 1,
            )

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = value if metal == "au" else np.nan

        return pd.Series(results)


@register_factor
class SilverGoldRatioFactor(BaseFactor):
    name = "silver_gold_ratio"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """Silver-gold ratio deviation from rolling mean. Only applies to silver-subsector stocks."""
        scm_cfg = config.get("factors", {}).get("silver_cross_metal", {})
        lookback = scm_cfg.get("sgr_lookback", 60)

        ag_df = store.read_futures_daily("ag", end_date=date)
        au_df = store.read_futures_daily("au", end_date=date)

        value = np.nan
        if len(ag_df) >= lookback + 1 and len(au_df) >= lookback + 1:
            ag_close = ag_df["close"].values[-(lookback + 1):]
            au_close = au_df["close"].values[-(lookback + 1):]
            # Align lengths
            n = min(len(ag_close), len(au_close))
            ag_close = ag_close[-n:]
            au_close = au_close[-n:]
            # Compute ratio series
            with np.errstate(divide="ignore", invalid="ignore"):
                ratios = ag_close / au_close
            ratios = ratios[np.isfinite(ratios)]
            if len(ratios) >= lookback + 1:
                rolling_mean = ratios[:-1].mean()
                current_ratio = ratios[-1]
                if rolling_mean > 0:
                    value = (current_ratio - rolling_mean) / rolling_mean
        else:
            logger.warning(
                "Insufficient futures data for silver-gold ratio (ag: %d, au: %d, need: %d)",
                len(ag_df), len(au_df), lookback + 1,
            )

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = value if metal == "ag" else np.nan

        return pd.Series(results)


@register_factor
class SilverCopperRatioFactor(BaseFactor):
    name = "silver_copper_ratio"
    category = "commodity"

    def compute(self, universe, date, store, config):
        """Silver-copper ratio rate-of-change. Only applies to silver-subsector stocks."""
        scm_cfg = config.get("factors", {}).get("silver_cross_metal", {})
        lookback = scm_cfg.get("scr_lookback", 20)

        ag_df = store.read_futures_daily("ag", end_date=date)
        cu_df = store.read_futures_daily("cu", end_date=date)

        value = np.nan
        if len(ag_df) >= lookback + 1 and len(cu_df) >= lookback + 1:
            ag_close = ag_df["close"].values
            cu_close = cu_df["close"].values
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio_today = ag_close[-1] / cu_close[-1]
                ratio_past = ag_close[-(lookback + 1)] / cu_close[-(lookback + 1)]
            if np.isfinite(ratio_today) and np.isfinite(ratio_past) and ratio_past > 0:
                value = (ratio_today - ratio_past) / ratio_past
        else:
            logger.warning(
                "Insufficient futures data for silver-copper ratio (ag: %d, cu: %d, need: %d)",
                len(ag_df), len(cu_df), lookback + 1,
            )

        results = {}
        for symbol in universe:
            metal = _get_stock_metal(symbol, config, store)
            results[symbol] = value if metal == "ag" else np.nan

        return pd.Series(results)
