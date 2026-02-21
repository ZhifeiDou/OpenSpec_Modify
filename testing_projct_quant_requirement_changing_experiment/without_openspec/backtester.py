"""回测引擎 — 事件驱动逐日回测 + 绩效统计"""

import numpy as np
import pandas as pd

from config import BACKTEST, RISK, STRATEGY
from data_fetcher import get_stock_history, get_benchmark_history
from factor_engine import compute_all_factors
from strategy import select_portfolio


def run_backtest(stock_list, config=None):
    """运行回测。

    Parameters
    ----------
    stock_list : list[dict] — [{"code": ..., "name": ...}, ...]
    config : dict | None    — 覆盖 BACKTEST 配置

    Returns
    -------
    dict — {
        "equity_curve": [...],
        "benchmark_curve": [...],
        "trades": [...],
        "metrics": {...},
    }
    """
    cfg = {**BACKTEST, **(config or {})}
    start = cfg["start_date"]
    end = cfg["end_date"]
    capital = cfg["initial_capital"]
    commission = cfg["commission_rate"]
    stamp_tax = cfg["stamp_tax"]
    slippage = cfg["slippage"]
    max_positions = STRATEGY["max_positions"]

    # ── 预加载所有股票的历史数据 ──
    all_hist = {}
    for s in stock_list:
        code = s["code"]
        df = get_stock_history(code, start=start, end=end)
        if df is not None and len(df) > 0:
            df = df.sort_values("date").reset_index(drop=True)
            df.index = df["date"]
            all_hist[code] = df

    if not all_hist:
        return {"equity_curve": [], "benchmark_curve": [], "trades": [], "metrics": {}}

    # ── 构建交易日序列 ──
    all_dates = sorted(set().union(*(set(df.index) for df in all_hist.values())))
    # 过滤日期范围
    all_dates = [d for d in all_dates if start <= d <= end]

    if not all_dates:
        return {"equity_curve": [], "benchmark_curve": [], "trades": [], "metrics": {}}

    # ── 回测主循环 ──
    cash = capital
    positions = {}  # {code: {"shares": int, "cost": float}}
    equity_curve = []
    trades = []

    # 每20个交易日重新调仓
    rebalance_interval = 20
    days_since_rebalance = rebalance_interval  # 首日即调仓

    for i, date in enumerate(all_dates):
        # ── 计算当前组合市值 ──
        portfolio_value = cash
        for code, pos in list(positions.items()):
            if code in all_hist and date in all_hist[code].index:
                price = float(all_hist[code].loc[date, "close"])
                portfolio_value += pos["shares"] * price
            else:
                # 用最近的价格
                df = all_hist.get(code)
                if df is not None and len(df) > 0:
                    prior = df[df.index <= date]
                    if len(prior) > 0:
                        price = float(prior.iloc[-1]["close"])
                        portfolio_value += pos["shares"] * price

        equity_curve.append({"date": date, "equity": round(portfolio_value, 2)})

        # ── 止损检查 ──
        for code, pos in list(positions.items()):
            if code in all_hist and date in all_hist[code].index:
                price = float(all_hist[code].loc[date, "close"])
                pnl_pct = price / pos["cost"] - 1
                if pnl_pct < RISK["stop_loss"]:
                    # 触发止损，卖出
                    sell_price = price * (1 - slippage)
                    revenue = pos["shares"] * sell_price
                    fee = revenue * (commission + stamp_tax)
                    cash += revenue - fee
                    trades.append({
                        "date": date, "code": code, "action": "sell_stoploss",
                        "price": round(sell_price, 2), "shares": pos["shares"],
                        "fee": round(fee, 2),
                    })
                    del positions[code]

        # ── 调仓日 ──
        days_since_rebalance += 1
        if days_since_rebalance >= rebalance_interval:
            days_since_rebalance = 0

            # 计算截至当前日期的因子评分（使用最近的数据）
            # 为了回测效率，使用简化版：按最近收益率排序
            scored = []
            for s in stock_list:
                code = s["code"]
                if code not in all_hist:
                    continue
                df = all_hist[code]
                prior = df[df.index <= date]
                if len(prior) < 20:
                    continue
                close = prior["close"].astype(float)
                ret_20 = close.iloc[-1] / close.iloc[-20] - 1 if len(close) >= 20 else 0
                ret_5 = close.iloc[-1] / close.iloc[-5] - 1 if len(close) >= 5 else 0

                # 简易MACD
                ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
                ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
                macd = (ema12 - ema26) / (close.iloc[-1] + 1e-9)

                # 简易RSI
                delta = close.diff().dropna()
                if len(delta) >= 14:
                    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
                    rsi = 100 - 100 / (1 + gain / (loss + 1e-9))
                    rsi_score = (50 - rsi) / 50
                else:
                    rsi_score = 0

                score = ret_20 * 0.3 + ret_5 * 0.2 + macd * 0.3 + rsi_score * 0.2
                scored.append({"code": code, "name": s.get("name", code), "score": score})

            scored.sort(key=lambda x: x["score"], reverse=True)
            target_codes = [s["code"] for s in scored[:max_positions]]

            # ── 先卖出不在目标中的 ──
            for code in list(positions.keys()):
                if code not in target_codes:
                    if code in all_hist and date in all_hist[code].index:
                        price = float(all_hist[code].loc[date, "close"]) * (1 - slippage)
                        revenue = positions[code]["shares"] * price
                        fee = revenue * (commission + stamp_tax)
                        cash += revenue - fee
                        trades.append({
                            "date": date, "code": code, "action": "sell",
                            "price": round(price, 2),
                            "shares": positions[code]["shares"],
                            "fee": round(fee, 2),
                        })
                        del positions[code]

            # ── 买入目标中尚未持有的 ──
            buy_codes = [c for c in target_codes if c not in positions]
            if buy_codes:
                per_stock_cash = cash / (len(buy_codes) + len(positions)) if buy_codes else 0
                for code in buy_codes:
                    if code in all_hist and date in all_hist[code].index:
                        price = float(all_hist[code].loc[date, "close"]) * (1 + slippage)
                        shares = int(per_stock_cash / (price * 100)) * 100  # 整百股
                        if shares > 0:
                            cost = shares * price
                            fee = cost * commission
                            if cash >= cost + fee:
                                cash -= cost + fee
                                positions[code] = {"shares": shares, "cost": price}
                                trades.append({
                                    "date": date, "code": code, "action": "buy",
                                    "price": round(price, 2), "shares": shares,
                                    "fee": round(fee, 2),
                                })

    # ── 基准收益 ──
    bench = get_benchmark_history(start, end)
    benchmark_curve = []
    if bench is not None and len(bench) > 0:
        bench_start = float(bench.iloc[0]["close"])
        for _, row in bench.iterrows():
            benchmark_curve.append({
                "date": row["date"],
                "equity": round(capital * float(row["close"]) / bench_start, 2),
            })

    # ── 绩效指标 ──
    metrics = _calc_metrics(equity_curve, capital)

    return {
        "equity_curve": equity_curve,
        "benchmark_curve": benchmark_curve,
        "trades": trades,
        "metrics": metrics,
    }


def _calc_metrics(equity_curve, initial_capital):
    """计算绩效指标"""
    if not equity_curve:
        return {}

    equities = [e["equity"] for e in equity_curve]
    total_return = equities[-1] / initial_capital - 1

    # 年化收益
    n_days = len(equities)
    annual_return = (1 + total_return) ** (252 / max(n_days, 1)) - 1

    # 最大回撤
    peak = equities[0]
    max_dd = 0
    for eq in equities:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak
        if dd > max_dd:
            max_dd = dd

    # 日收益率序列
    daily_returns = []
    for i in range(1, len(equities)):
        daily_returns.append(equities[i] / equities[i - 1] - 1)

    # 夏普比率 (无风险利率 3%)
    if daily_returns:
        avg_r = np.mean(daily_returns)
        std_r = np.std(daily_returns)
        sharpe = (avg_r - 0.03 / 252) / (std_r + 1e-9) * np.sqrt(252)
    else:
        sharpe = 0

    # 胜率
    wins = sum(1 for r in daily_returns if r > 0)
    win_rate = wins / len(daily_returns) if daily_returns else 0

    # 盈亏比
    avg_win = np.mean([r for r in daily_returns if r > 0]) if wins > 0 else 0
    losses = [r for r in daily_returns if r < 0]
    avg_loss = abs(np.mean(losses)) if losses else 1e-9
    profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0

    return {
        "total_return": round(total_return * 100, 2),
        "annual_return": round(annual_return * 100, 2),
        "max_drawdown": round(max_dd * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "win_rate": round(win_rate * 100, 2),
        "profit_loss_ratio": round(profit_loss_ratio, 2),
        "total_trades": 0,  # updated by caller
    }
