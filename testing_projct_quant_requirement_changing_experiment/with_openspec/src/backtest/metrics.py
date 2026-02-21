"""Performance metrics: annualized return, Sharpe, max drawdown, etc."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.risk.drawdown import compute_max_drawdown


def compute_metrics(
    nav_series: pd.Series,
    trade_log: pd.DataFrame,
    initial_capital: float,
    config: dict,
) -> dict:
    """Compute comprehensive backtest performance metrics.

    Returns dict with:
        annual_return, annual_volatility, sharpe_ratio,
        max_drawdown, max_drawdown_duration,
        win_rate, profit_loss_ratio,
        total_trades, total_costs, annual_turnover,
        calmar_ratio, sortino_ratio
    """
    if nav_series.empty or len(nav_series) < 2:
        return _empty_metrics()

    bt_cfg = config.get("backtest", {})
    risk_free = bt_cfg.get("risk_free_rate", 0.02)

    nav = nav_series.values.astype(float)
    n_days = len(nav)
    n_years = n_days / 252

    # Returns
    daily_returns = np.diff(nav) / nav[:-1]

    # Annual return
    total_return = (nav[-1] / nav[0]) - 1
    annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0.0

    # Volatility
    annual_vol = np.std(daily_returns) * np.sqrt(252) if len(daily_returns) > 1 else 0.0

    # Sharpe ratio
    daily_rf = risk_free / 252
    excess_returns = daily_returns - daily_rf
    sharpe = (np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
              if np.std(excess_returns) > 0 else 0.0)

    # Max drawdown
    max_dd, max_dd_duration = compute_max_drawdown(nav.tolist())

    # Calmar ratio
    calmar = annual_return / max_dd if max_dd > 0 else 0.0

    # Sortino ratio (downside deviation)
    downside = daily_returns[daily_returns < daily_rf]
    downside_std = np.std(downside) * np.sqrt(252) if len(downside) > 1 else 0.0
    sortino = (annual_return - risk_free) / downside_std if downside_std > 0 else 0.0

    # Trade statistics
    total_trades = 0
    total_costs = 0.0
    wins = 0
    losses = 0
    win_pnl = 0.0
    loss_pnl = 0.0

    if not trade_log.empty and "cost" in trade_log.columns:
        total_trades = len(trade_log)
        total_costs = trade_log["cost"].sum()

        # Win/loss calculation from paired trades
        if "action" in trade_log.columns:
            buy_trades = trade_log[trade_log["action"].isin(["BUY"])]
            sell_trades = trade_log[trade_log["action"].isin(["SELL", "SELL_STOP"])]

            # Simple approximation: compare sell proceeds vs buy cost per symbol
            for sym in sell_trades["symbol"].unique():
                sym_buys = buy_trades[buy_trades["symbol"] == sym]
                sym_sells = sell_trades[sell_trades["symbol"] == sym]

                if sym_buys.empty:
                    continue

                avg_buy = (sym_buys["price"] * sym_buys["shares"]).sum() / sym_buys["shares"].sum()
                avg_sell = (sym_sells["price"] * sym_sells["shares"]).sum() / sym_sells["shares"].sum() if not sym_sells.empty else 0

                if avg_sell > avg_buy:
                    wins += 1
                    win_pnl += (avg_sell - avg_buy) * sym_sells["shares"].sum()
                elif avg_sell > 0:
                    losses += 1
                    loss_pnl += (avg_buy - avg_sell) * sym_sells["shares"].sum()

    total_round_trips = wins + losses
    win_rate = wins / total_round_trips if total_round_trips > 0 else 0.0
    profit_loss_ratio = (win_pnl / loss_pnl) if loss_pnl > 0 else 0.0

    # Turnover
    if not trade_log.empty and "price" in trade_log.columns and "shares" in trade_log.columns:
        total_traded = (trade_log["price"] * trade_log["shares"]).sum()
        annual_turnover = total_traded / initial_capital / n_years if n_years > 0 else 0.0
    else:
        annual_turnover = 0.0

    return {
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
        "max_drawdown_duration": max_dd_duration,
        "calmar_ratio": calmar,
        "sortino_ratio": sortino,
        "total_return": total_return,
        "win_rate": win_rate,
        "profit_loss_ratio": profit_loss_ratio,
        "total_trades": total_trades,
        "total_costs": total_costs,
        "annual_turnover": annual_turnover,
        "n_trading_days": n_days,
    }


def _empty_metrics() -> dict:
    return {
        "annual_return": 0.0,
        "annual_volatility": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "max_drawdown_duration": 0,
        "calmar_ratio": 0.0,
        "sortino_ratio": 0.0,
        "total_return": 0.0,
        "win_rate": 0.0,
        "profit_loss_ratio": 0.0,
        "total_trades": 0,
        "total_costs": 0.0,
        "annual_turnover": 0.0,
        "n_trading_days": 0,
    }
