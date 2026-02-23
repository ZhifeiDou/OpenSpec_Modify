"""Performance metrics calculation."""

import numpy as np
import pandas as pd


def total_return(nav_series: pd.Series) -> float:
    """Total return from start to end."""
    if len(nav_series) < 2:
        return 0.0
    return (nav_series.iloc[-1] / nav_series.iloc[0]) - 1


def annualized_return(nav_series: pd.Series, trading_days: int = 252) -> float:
    """Annualized return."""
    if len(nav_series) < 2:
        return 0.0
    total = total_return(nav_series)
    n_days = len(nav_series)
    return (1 + total) ** (trading_days / n_days) - 1


def max_drawdown(nav_series: pd.Series) -> float:
    """Maximum drawdown."""
    if len(nav_series) < 2:
        return 0.0
    peak = nav_series.expanding().max()
    drawdown = (nav_series - peak) / peak
    return abs(drawdown.min())


def sharpe_ratio(nav_series: pd.Series, risk_free_rate: float = 0.03,
                  trading_days: int = 252) -> float:
    """Sharpe ratio."""
    if len(nav_series) < 2:
        return 0.0
    returns = nav_series.pct_change().dropna()
    daily_rf = risk_free_rate / trading_days
    excess = returns - daily_rf
    if excess.std() == 0:
        return 0.0
    return (excess.mean() / excess.std()) * np.sqrt(trading_days)


def calmar_ratio(nav_series: pd.Series, trading_days: int = 252) -> float:
    """Calmar ratio: annualized return / max drawdown."""
    ann_ret = annualized_return(nav_series, trading_days)
    mdd = max_drawdown(nav_series)
    if mdd == 0:
        return 0.0
    return ann_ret / mdd


def win_rate(trade_log: list[dict]) -> float:
    """Win rate from trade log."""
    sells = [t for t in trade_log if t["direction"] == "sell"]
    if not sells:
        return 0.0
    # Simplified: compare sell price vs buy price for same stock
    wins = sum(1 for t in sells if t.get("amount", 0) > 0)
    return wins / len(sells)


def profit_loss_ratio(trade_log: list[dict]) -> float:
    """Average profit / average loss ratio."""
    profits = []
    losses = []
    for t in trade_log:
        if t["direction"] == "sell":
            pnl = t.get("amount", 0)
            if pnl > 0:
                profits.append(pnl)
            elif pnl < 0:
                losses.append(abs(pnl))

    avg_profit = np.mean(profits) if profits else 0
    avg_loss = np.mean(losses) if losses else 1
    if avg_loss == 0:
        return float("inf") if avg_profit > 0 else 0.0
    return avg_profit / avg_loss


def calculate_all_metrics(nav_history: list[dict],
                           trade_log: list[dict]) -> dict:
    """Calculate all performance metrics."""
    nav_series = pd.Series([h["nav"] for h in nav_history])
    return {
        "total_return": total_return(nav_series),
        "annualized_return": annualized_return(nav_series),
        "max_drawdown": max_drawdown(nav_series),
        "sharpe_ratio": sharpe_ratio(nav_series),
        "calmar_ratio": calmar_ratio(nav_series),
        "win_rate": win_rate(trade_log),
        "profit_loss_ratio": profit_loss_ratio(trade_log),
    }
