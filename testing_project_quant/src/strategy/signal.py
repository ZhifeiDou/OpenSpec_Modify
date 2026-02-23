"""Trade signal generation: compare target vs current holdings."""
from __future__ import annotations

import logging

import pandas as pd

from src.factors.base import compute_all_factors
from src.strategy.scorer import score_stocks, select_top_stocks
from src.strategy.allocator import allocate_weights
from src.data.storage import DataStore

logger = logging.getLogger(__name__)


def generate_signals(
    config: dict,
    date: str | None = None,
    current_holdings: dict[str, float] | None = None,
    position_ratio: float = 1.0,
    store: DataStore | None = None,
) -> list[dict]:
    """Generate trading signals by comparing target vs current portfolio.

    Args:
        config: Full settings dict.
        date: Target date for factor calculation.
        current_holdings: {symbol: weight} of current portfolio. None = empty.
        position_ratio: Timing-adjusted position ratio (0 to 1).
        store: DataStore instance.

    Returns:
        List of signal dicts with keys:
            symbol, name, action (BUY/ADD/REDUCE/SELL), current_weight, target_weight
    """
    if current_holdings is None:
        current_holdings = {}

    # Compute factors
    factor_matrix = compute_all_factors(config, date=date, store=store)
    if factor_matrix.empty:
        logger.warning("Empty factor matrix, no signals generated")
        return []

    # Score and select
    scores = score_stocks(factor_matrix, config)
    selected = select_top_stocks(scores, config, universe_size=len(factor_matrix))

    # Get subsector map for allocation
    subsector_map = _get_subsector_map(factor_matrix.index.tolist(), config, store)

    # Allocate weights
    target_weights = allocate_weights(
        selected, scores, config,
        subsector_map=subsector_map,
        position_ratio=position_ratio,
    )

    # Check if rebalance should be skipped
    strategy_cfg = config.get("strategy", {})
    skip_threshold = strategy_cfg.get("skip_rebalance_threshold", 0.02)

    if current_holdings and _should_skip_rebalance(
        current_holdings, target_weights, skip_threshold
    ):
        logger.info("Rebalance skipped: all weight changes < %.1f%%", skip_threshold * 100)
        return []

    # Generate signals
    signals = _compare_holdings(current_holdings, target_weights, config)
    return signals


def _get_subsector_map(
    symbols: list[str], config: dict, store: DataStore | None
) -> dict[str, str]:
    """Build {symbol: subsector} map."""
    if store is None:
        data_cfg = config.get("data", {})
        store = DataStore(data_cfg.get("db_path", "data/quant.db"))

    subsector_map = {}
    for symbol in symbols:
        df = store.read_table("universe_cache", where="symbol = ?", params=(symbol,))
        if not df.empty and "subsector" in df.columns:
            subsector_map[symbol] = df.iloc[0]["subsector"]
        else:
            subsector_map[symbol] = "other"
    return subsector_map


def _should_skip_rebalance(
    current: dict[str, float],
    target: pd.Series,
    threshold: float,
) -> bool:
    """Check if all weight changes are below threshold."""
    all_symbols = set(current.keys()) | set(target.index)
    for sym in all_symbols:
        curr_w = current.get(sym, 0.0)
        tgt_w = target.get(sym, 0.0)
        if abs(tgt_w - curr_w) >= threshold:
            return False
    return True


def _compare_holdings(
    current: dict[str, float],
    target: pd.Series,
    config: dict,
) -> list[dict]:
    """Compare current vs target to generate BUY/ADD/REDUCE/SELL signals."""
    signals = []

    all_symbols = set(current.keys()) | set(target.index)

    backtest_cfg = config.get("backtest", {})
    commission = backtest_cfg.get("commission", 0.0003)
    stamp_tax = backtest_cfg.get("stamp_tax", 0.0005)
    slippage = backtest_cfg.get("slippage", 0.0015)

    for sym in sorted(all_symbols):
        curr_w = current.get(sym, 0.0)
        tgt_w = target.get(sym, 0.0)
        diff = tgt_w - curr_w

        if abs(diff) < 0.001:
            continue  # Negligible change

        if curr_w == 0 and tgt_w > 0:
            action = "BUY"
            est_cost = tgt_w * (commission + slippage)
        elif curr_w > 0 and tgt_w == 0:
            action = "SELL"
            est_cost = curr_w * (commission + stamp_tax + slippage)
        elif diff > 0:
            action = "ADD"
            est_cost = diff * (commission + slippage)
        else:
            action = "REDUCE"
            est_cost = abs(diff) * (commission + stamp_tax + slippage)

        signals.append({
            "symbol": sym,
            "name": sym,  # Will be enriched with actual name if available
            "action": action,
            "current_weight": curr_w,
            "target_weight": tgt_w,
            "weight_change": diff,
            "estimated_cost_pct": est_cost,
        })

    return signals
