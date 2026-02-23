"""回测引擎 — 事件驱动逐日回测 + 绩效统计
增加：波动率自适应止损、动态再平衡频率、熔断机制"""

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
    positions = {}  # {code: {"shares": int, "cost": float, "buy_date": str}}
    equity_curve = []
    trades = []

    # 动态再平衡相关变量
    rebalance_interval = 20
    days_since_rebalance = rebalance_interval  # 首日即调仓

    # 熔断相关变量
    circuit_breaker_active = False
    circuit_breaker_level = 0  # 0=正常, 1=一级, 2=二级
    circuit_breaker_recovery_count = 0
    prev_equity = capital

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

        # ── 计算波动率比值（用于自适应止损和动态再平衡） ──
        vol_ratio = _calc_volatility_ratio(all_hist, all_dates, i)

        # ── 熔断检查 ──
        if i > 0:
            daily_return = (portfolio_value - prev_equity) / prev_equity
            if circuit_breaker_active:
                # 检查恢复条件
                if portfolio_value > prev_equity:
                    circuit_breaker_recovery_count += 1
                else:
                    circuit_breaker_recovery_count = 0
                # 一级熔断需要3天恢复，二级需要5天
                recovery_needed = 3 if circuit_breaker_level == 1 else 5
                if circuit_breaker_recovery_count >= recovery_needed:
                    circuit_breaker_active = False
                    circuit_breaker_level = 0
                    circuit_breaker_recovery_count = 0
                # 检查是否从一级升级到二级
                if circuit_breaker_level == 1 and daily_return < RISK["circuit_breaker_l2"]:
                    circuit_breaker_level = 2
                    circuit_breaker_recovery_count = 0
                    # 清仓所有持仓
                    for code in list(positions.keys()):
                        if code in all_hist and date in all_hist[code].index:
                            price = float(all_hist[code].loc[date, "close"]) * (1 - slippage)
                            revenue = positions[code]["shares"] * price
                            fee = revenue * (commission + stamp_tax)
                            cash += revenue - fee
                            trades.append({
                                "date": date, "code": code, "action": "sell_circuit_breaker",
                                "price": round(price, 2), "shares": positions[code]["shares"],
                                "fee": round(fee, 2),
                            })
                            del positions[code]
            else:
                # 检查是否触发熔断
                if daily_return < RISK["circuit_breaker_l2"]:
                    # 二级熔断：全部清仓
                    circuit_breaker_active = True
                    circuit_breaker_level = 2
                    circuit_breaker_recovery_count = 0
                    for code in list(positions.keys()):
                        if code in all_hist and date in all_hist[code].index:
                            price = float(all_hist[code].loc[date, "close"]) * (1 - slippage)
                            revenue = positions[code]["shares"] * price
                            fee = revenue * (commission + stamp_tax)
                            cash += revenue - fee
                            trades.append({
                                "date": date, "code": code, "action": "sell_circuit_breaker",
                                "price": round(price, 2), "shares": positions[code]["shares"],
                                "fee": round(fee, 2),
                            })
                            del positions[code]
                elif daily_return < RISK["circuit_breaker_l1"]:
                    # 一级熔断：仓位减半
                    circuit_breaker_active = True
                    circuit_breaker_level = 1
                    circuit_breaker_recovery_count = 0
                    for code in list(positions.keys()):
                        if code in all_hist and date in all_hist[code].index:
                            shares_to_sell = positions[code]["shares"] // 2
                            if shares_to_sell > 0:
                                price = float(all_hist[code].loc[date, "close"]) * (1 - slippage)
                                revenue = shares_to_sell * price
                                fee = revenue * (commission + stamp_tax)
                                cash += revenue - fee
                                positions[code]["shares"] -= shares_to_sell
                                trades.append({
                                    "date": date, "code": code, "action": "sell_circuit_breaker",
                                    "price": round(price, 2), "shares": shares_to_sell,
                                    "fee": round(fee, 2),
                                })
                            if positions[code]["shares"] <= 0:
                                del positions[code]

        prev_equity = portfolio_value

        # ── 止损检查（波动率自适应） ──
        if not circuit_breaker_active:
            # 根据波动率比值确定止损线
            if vol_ratio < 0.8:
                stop_loss_pct = RISK.get("stop_loss_low_vol", -0.06)
            elif vol_ratio > 1.5:
                stop_loss_pct = RISK.get("stop_loss_high_vol", -0.10)
            else:
                stop_loss_pct = RISK["stop_loss"]

            for code, pos in list(positions.items()):
                if code in all_hist and date in all_hist[code].index:
                    price = float(all_hist[code].loc[date, "close"])
                    pnl_pct = price / pos["cost"] - 1
                    if pnl_pct < stop_loss_pct:
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

        # ── 动态再平衡频率 ──
        if vol_ratio > 2.0:
            current_rebalance_interval = 5  # 周度
        elif vol_ratio > 1.5:
            current_rebalance_interval = 10  # 双周
        else:
            current_rebalance_interval = 20  # 月度

        # ── 调仓日 ──
        days_since_rebalance += 1
        if not circuit_breaker_active and days_since_rebalance >= current_rebalance_interval:
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
                                positions[code] = {"shares": shares, "cost": price, "buy_date": date}
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


def _calc_volatility_ratio(all_hist, all_dates, current_idx):
    """计算波动率比值（简化版）"""
    if current_idx < 20:
        return 1.0  # 数据不足，返回正常

    # 用所有股票的平均收盘价作为代表
    recent_returns = []
    for j in range(max(0, current_idx - 20), current_idx):
        day_prices = []
        for code, df in all_hist.items():
            if all_dates[j] in df.index and all_dates[j + 1] in df.index:
                p1 = float(df.loc[all_dates[j], "close"])
                p2 = float(df.loc[all_dates[j + 1], "close"])
                if p1 > 0:
                    day_prices.append(p2 / p1 - 1)
        if day_prices:
            recent_returns.append(np.mean(day_prices))

    if len(recent_returns) < 10:
        return 1.0

    vol_short = np.std(recent_returns)

    # 长期波动率
    long_start = max(0, current_idx - 120)
    long_returns = []
    for j in range(long_start, current_idx):
        if j + 1 < len(all_dates):
            day_prices = []
            for code, df in all_hist.items():
                if all_dates[j] in df.index and all_dates[j + 1] in df.index:
                    p1 = float(df.loc[all_dates[j], "close"])
                    p2 = float(df.loc[all_dates[j + 1], "close"])
                    if p1 > 0:
                        day_prices.append(p2 / p1 - 1)
            if day_prices:
                long_returns.append(np.mean(day_prices))

    if len(long_returns) < 20:
        return 1.0

    # 计算滚动波动率的中位数
    rolling_vols = []
    for k in range(20, len(long_returns) + 1):
        window = long_returns[k - 20:k]
        rolling_vols.append(np.std(window))

    if not rolling_vols:
        return 1.0

    vol_median = np.median(rolling_vols)
    if vol_median <= 0:
        return 1.0

    return vol_short / vol_median


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
