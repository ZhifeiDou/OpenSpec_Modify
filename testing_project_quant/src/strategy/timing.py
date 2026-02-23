"""Commodity momentum market timing: adjust position ratio based on metal trends."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.data.storage import DataStore

logger = logging.getLogger(__name__)


def compute_timing_signal(
    config: dict,
    date: str | None = None,
    store: DataStore | None = None,
) -> dict:
    """Compute market timing signal based on SHFE copper/aluminum momentum.

    Returns dict with:
        position_ratio: float (1.0 / 0.6 / 0.3 / 0.2)
        gold_hedge: bool (whether to shift toward gold sub-sector)
        details: dict with momentum values
    """
    timing_cfg = config.get("timing", {})

    # Check for manual override
    override = timing_cfg.get("override_ratio")
    if override is not None:
        return {
            "position_ratio": float(override),
            "gold_hedge": False,
            "details": {"override": True},
        }

    if not timing_cfg.get("enabled", True):
        return {"position_ratio": 1.0, "gold_hedge": False, "details": {"disabled": True}}

    if store is None:
        data_cfg = config.get("data", {})
        store = DataStore(data_cfg.get("db_path", "data/quant.db"))

    # Compute copper and aluminum momentum
    cu_mom_20 = _metal_momentum(store, "cu", 20, date)
    cu_mom_60 = _metal_momentum(store, "cu", 60, date)
    al_mom_20 = _metal_momentum(store, "al", 20, date)
    al_mom_60 = _metal_momentum(store, "al", 60, date)

    # Average momentum across copper and aluminum
    mom_20_vals = [m for m in [cu_mom_20, al_mom_20] if not np.isnan(m)]
    mom_60_vals = [m for m in [cu_mom_60, al_mom_60] if not np.isnan(m)]

    avg_mom_20 = np.mean(mom_20_vals) if mom_20_vals else np.nan
    avg_mom_60 = np.mean(mom_60_vals) if mom_60_vals else np.nan

    # Determine position ratio based on momentum signals
    position_ratio = _determine_position_ratio(avg_mom_20, avg_mom_60)

    # Check gold hedge signal
    gold_hedge = _check_gold_hedge(store, config, avg_mom_20, date)

    details = {
        "cu_mom_20d": cu_mom_20,
        "cu_mom_60d": cu_mom_60,
        "al_mom_20d": al_mom_20,
        "al_mom_60d": al_mom_60,
        "avg_mom_20d": avg_mom_20,
        "avg_mom_60d": avg_mom_60,
    }

    logger.info(
        "Timing signal: position_ratio=%.1f, gold_hedge=%s, mom_20=%.3f, mom_60=%.3f",
        position_ratio,
        gold_hedge,
        avg_mom_20 if not np.isnan(avg_mom_20) else 0,
        avg_mom_60 if not np.isnan(avg_mom_60) else 0,
    )

    return {
        "position_ratio": position_ratio,
        "gold_hedge": gold_hedge,
        "details": details,
    }


def _metal_momentum(store: DataStore, metal: str, days: int, date: str | None) -> float:
    """Calculate metal price momentum over N days."""
    df = store.read_futures_daily(metal, end_date=date)
    if len(df) < days + 1:
        return np.nan
    close = df["close"].values
    return close[-1] / close[-(days + 1)] - 1


def _determine_position_ratio(mom_20: float, mom_60: float) -> float:
    """Determine position ratio from momentum signals.

    Rules:
        Both positive → 1.0 (full position)
        20d positive, 60d negative → 0.6 (early recovery)
        20d negative, 60d positive → 0.3 (weakening trend)
        Both negative → 0.2 (defensive)
        Insufficient data → 0.6 (cautious default)
    """
    if np.isnan(mom_20) or np.isnan(mom_60):
        return 0.6  # Cautious default

    if mom_20 > 0 and mom_60 > 0:
        return 1.0
    elif mom_20 > 0 and mom_60 <= 0:
        return 0.6
    elif mom_20 <= 0 and mom_60 > 0:
        return 0.3
    else:
        return 0.2


def _check_gold_hedge(
    store: DataStore, config: dict, industrial_mom: float, date: str | None
) -> bool:
    """Check if gold hedging should be activated.

    Trigger: industrial metals momentum negative AND gold momentum > threshold.
    """
    threshold = config.get("timing", {}).get("gold_hedge_threshold", 0.05)

    if np.isnan(industrial_mom) or industrial_mom >= 0:
        return False

    # Check gold momentum
    gold_mom = _metal_momentum(store, "au", 20, date)
    if np.isnan(gold_mom):
        return False

    return gold_mom > threshold
