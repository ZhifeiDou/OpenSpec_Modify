"""Metal price crash alerts and daily risk check aggregation."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.universe.classifier import SUBSECTOR_METAL_MAP

logger = logging.getLogger(__name__)


@dataclass
class MetalCrashAlert:
    metal: str
    daily_return: float
    affected_symbols: list[str]


def check_metal_crash(
    store: DataStore,
    config: dict,
    date: str | None = None,
    holdings: dict | None = None,
) -> list[MetalCrashAlert]:
    """Check if any metal futures dropped more than threshold in a single day.

    Args:
        store: DataStore instance.
        config: Settings dict.
        date: Current date.
        holdings: {symbol: {"subsector": str, ...}} current holdings.

    Returns:
        List of MetalCrashAlert for metals that crashed.
    """
    risk_cfg = config.get("risk", {})
    threshold = risk_cfg.get("metal_crash_threshold", 0.03)

    alerts = []
    for metal_code in set(SUBSECTOR_METAL_MAP.values()):
        if metal_code is None:
            continue

        df = store.read_futures_daily(metal_code, end_date=date)
        if len(df) < 2:
            continue

        close = df["close"].values
        daily_ret = (close[-1] / close[-2]) - 1

        if daily_ret < -threshold:
            # Find affected holdings
            affected = []
            if holdings:
                for sym, info in holdings.items():
                    ss = info.get("subsector", "other")
                    if SUBSECTOR_METAL_MAP.get(ss) == metal_code:
                        affected.append(sym)

            alerts.append(MetalCrashAlert(
                metal=metal_code,
                daily_return=daily_ret,
                affected_symbols=affected,
            ))
            logger.warning(
                "Metal crash alert: %s dropped %.2f%%, affected: %s",
                metal_code, daily_ret * 100, affected,
            )

    return alerts


def run_daily_risk_check(
    config: dict,
    holdings: dict | None = None,
    nav_history: list[float] | None = None,
    store: DataStore | None = None,
    date: str | None = None,
) -> dict:
    """Run comprehensive daily risk check.

    Returns dict with:
        drawdown: float
        drawdown_alert: DrawdownAlert | None
        stop_loss_alerts: list[StopLossAlert]
        trailing_stop_alerts: list[StopLossAlert]
        metal_crash_alerts: list[MetalCrashAlert]
    """
    from src.risk.stop_loss import check_hard_stop, check_trailing_stop
    from src.risk.drawdown import check_drawdown, compute_drawdown

    if store is None:
        data_cfg = config.get("data", {})
        store = DataStore(data_cfg.get("db_path", "data/quant.db"))

    if date is None:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

    if holdings is None:
        holdings = {}
    if nav_history is None:
        nav_history = []

    # Drawdown check
    dd = compute_drawdown(nav_history) if nav_history else 0.0
    dd_alert = check_drawdown(nav_history, config) if nav_history else None

    # Stop-loss checks
    hard_stops = check_hard_stop(holdings, store, config, date) if holdings else []
    trailing_stops = check_trailing_stop(holdings, store, config, date) if holdings else []

    # Metal crash check
    metal_crashes = check_metal_crash(store, config, date, holdings)

    return {
        "drawdown": dd,
        "drawdown_alert": dd_alert,
        "stop_loss_alerts": hard_stops,
        "trailing_stop_alerts": trailing_stops,
        "metal_crash_alerts": metal_crashes,
    }
