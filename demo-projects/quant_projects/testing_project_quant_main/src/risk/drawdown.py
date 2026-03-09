"""Portfolio drawdown monitoring with tiered response."""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DrawdownAlert:
    current_drawdown: float
    peak_nav: float
    current_nav: float
    tier: str  # "warning", "reduce", "liquidate"
    action: str  # Description of recommended action


def compute_drawdown(nav_series: list[float]) -> float:
    """Compute current drawdown from a NAV time series."""
    if not nav_series:
        return 0.0
    peak = nav_series[0]
    for nav in nav_series:
        if nav > peak:
            peak = nav
    current = nav_series[-1]
    if peak <= 0:
        return 0.0
    return (peak - current) / peak


def check_drawdown(
    nav_series: list[float],
    config: dict,
) -> DrawdownAlert | None:
    """Check portfolio drawdown against tiered thresholds.

    Tiers:
        < reduce threshold: No action
        >= reduce threshold (15%): Reduce position to 50%
        >= liquidate threshold (20%): Recommend full liquidation
    """
    risk_cfg = config.get("risk", {})
    reduce_threshold = risk_cfg.get("max_drawdown_reduce", 0.15)
    liquidate_threshold = risk_cfg.get("max_drawdown_liquidate", 0.20)

    if not nav_series or len(nav_series) < 2:
        return None

    dd = compute_drawdown(nav_series)
    peak = max(nav_series)
    current = nav_series[-1]

    if dd >= liquidate_threshold:
        return DrawdownAlert(
            current_drawdown=dd,
            peak_nav=peak,
            current_nav=current,
            tier="liquidate",
            action=f"Drawdown {dd:.1%} >= {liquidate_threshold:.0%}: RECOMMEND FULL LIQUIDATION",
        )
    elif dd >= reduce_threshold:
        return DrawdownAlert(
            current_drawdown=dd,
            peak_nav=peak,
            current_nav=current,
            tier="reduce",
            action=f"Drawdown {dd:.1%} >= {reduce_threshold:.0%}: REDUCE position to 50%",
        )

    return None


def compute_max_drawdown(nav_series: list[float]) -> tuple[float, int]:
    """Compute maximum drawdown and its duration in days.

    Returns:
        (max_drawdown, max_drawdown_duration)
    """
    if not nav_series or len(nav_series) < 2:
        return 0.0, 0

    peak = nav_series[0]
    max_dd = 0.0
    peak_idx = 0
    max_dd_duration = 0

    current_dd_start = 0

    for i, nav in enumerate(nav_series):
        if nav > peak:
            peak = nav
            peak_idx = i
            current_dd_start = i

        dd = (peak - nav) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
            max_dd_duration = i - current_dd_start

    return max_dd, max_dd_duration
