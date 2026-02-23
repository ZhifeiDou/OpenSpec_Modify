"""策略信号生成 — 基于多因子综合评分产生买卖信号"""

import pandas as pd

from config import STRATEGY


def generate_signals(scores_df, current_positions=None):
    """基于因子综合评分生成交易信号。

    Parameters
    ----------
    scores_df : pd.DataFrame — 包含 code, name, composite_score, rank
    current_positions : list[str] | None — 当前持仓股票代码列表

    Returns
    -------
    list[dict] — 每个元素: {"code", "name", "signal", "score", "reason"}
        signal: "buy" | "sell" | "hold"
    """
    if scores_df is None or scores_df.empty:
        return []

    if current_positions is None:
        current_positions = []

    buy_thresh = STRATEGY["buy_threshold"]
    sell_thresh = STRATEGY["sell_threshold"]
    max_pos = STRATEGY["max_positions"]

    signals = []

    for _, row in scores_df.iterrows():
        code = row["code"]
        name = row.get("name", code)
        score = row["composite_score"]
        rank = row.get("rank", 0)

        if code in current_positions:
            # 已持仓股票
            if score < sell_thresh:
                signals.append({
                    "code": code, "name": name, "signal": "sell",
                    "score": round(score, 4),
                    "reason": f"综合评分 {score:.4f} 低于卖出阈值 {sell_thresh}",
                })
            else:
                signals.append({
                    "code": code, "name": name, "signal": "hold",
                    "score": round(score, 4),
                    "reason": f"继续持有，评分 {score:.4f}",
                })
        else:
            # 未持仓股票
            if score > buy_thresh and len([s for s in signals if s["signal"] == "buy"]) < max_pos:
                signals.append({
                    "code": code, "name": name, "signal": "buy",
                    "score": round(score, 4),
                    "reason": f"综合评分 {score:.4f} 超过买入阈值 {buy_thresh}，排名第{rank}",
                })

    return signals


def select_portfolio(scores_df, max_positions=None):
    """从评分表中选出前N只股票构成组合。

    Returns
    -------
    list[dict] — [{"code", "name", "score", "weight"}, ...]
    """
    if max_positions is None:
        max_positions = STRATEGY["max_positions"]

    if scores_df is None or scores_df.empty:
        return []

    top = scores_df.head(max_positions)
    weight = 1.0 / len(top)

    portfolio = []
    for _, row in top.iterrows():
        portfolio.append({
            "code": row["code"],
            "name": row.get("name", row["code"]),
            "score": round(row["composite_score"], 4),
            "weight": round(weight, 4),
        })

    return portfolio
