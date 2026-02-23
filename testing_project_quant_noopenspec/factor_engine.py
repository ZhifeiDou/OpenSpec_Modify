"""多因子计算引擎 — 5大类因子计算 + Z-Score标准化 + 加权综合评分"""

import numpy as np
import pandas as pd

from config import FACTOR_WEIGHTS, SUB_FACTOR_WEIGHTS
from data_fetcher import get_stock_history, get_financial_data, get_money_flow


# ════════════════════════════════════════════
# 动量因子
# ════════════════════════════════════════════

def calc_momentum_factors(df):
    """计算动量因子：5/20/60日收益率、成交量变化率"""
    if df is None or len(df) < 60:
        return {}
    close = df["close"].astype(float)
    volume = df["volume"].astype(float)

    ret_5d = (close.iloc[-1] / close.iloc[-6] - 1) if len(close) > 5 else 0
    ret_20d = (close.iloc[-1] / close.iloc[-21] - 1) if len(close) > 20 else 0
    ret_60d = (close.iloc[-1] / close.iloc[-61] - 1) if len(close) > 60 else 0

    vol_recent = volume.iloc[-5:].mean()
    vol_prev = volume.iloc[-25:-5].mean()
    volume_change = (vol_recent / vol_prev - 1) if vol_prev > 0 else 0

    return {
        "ret_5d": ret_5d,
        "ret_20d": ret_20d,
        "ret_60d": ret_60d,
        "volume_change": volume_change,
    }


# ════════════════════════════════════════════
# 技术因子
# ════════════════════════════════════════════

def _ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def calc_technical_factors(df):
    """计算技术因子：MACD, RSI, 布林带, 均线排列, KDJ"""
    if df is None or len(df) < 60:
        return {}
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    # MACD
    ema12 = _ema(close, 12)
    ema26 = _ema(close, 26)
    dif = ema12 - ema26
    dea = _ema(dif, 9)
    macd_val = dif.iloc[-1] - dea.iloc[-1]  # 柱状图
    # 归一化到 [-1, 1]
    macd_score = np.clip(macd_val / (close.iloc[-1] * 0.02 + 1e-9), -1, 1)

    # RSI (14日)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain.iloc[-1] / (loss.iloc[-1] + 1e-9)
    rsi = 100 - 100 / (1 + rs)
    # RSI转为得分：50附近中性，>70偏高（超买，看空），<30偏低（超卖，看多）
    rsi_score = (50 - rsi) / 50  # 超卖为正分，超买为负分

    # 布林带位置
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = ma20 + 2 * std20
    lower = ma20 - 2 * std20
    boll_pos = (close.iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1] + 1e-9)
    boll_score = 1 - 2 * boll_pos  # 靠近下轨得正分

    # 均线多空排列 MA5 > MA10 > MA20 > MA60
    ma5 = close.rolling(5).mean().iloc[-1]
    ma10 = close.rolling(10).mean().iloc[-1]
    ma20_val = ma20.iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1]
    alignment = 0
    if ma5 > ma10:
        alignment += 0.25
    if ma10 > ma20_val:
        alignment += 0.25
    if ma20_val > ma60:
        alignment += 0.25
    if ma5 > ma60:
        alignment += 0.25
    ma_score = alignment * 2 - 1  # 映射到 [-1, 1]

    # KDJ
    low_min = low.rolling(9).min()
    high_max = high.rolling(9).max()
    rsv = (close - low_min) / (high_max - low_min + 1e-9) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d
    # J值>80超买，<20超卖
    kdj_score = (50 - j.iloc[-1]) / 50
    kdj_score = np.clip(kdj_score, -1, 1)

    return {
        "macd": float(macd_score),
        "rsi": float(np.clip(rsi_score, -1, 1)),
        "boll_position": float(np.clip(boll_score, -1, 1)),
        "ma_alignment": float(ma_score),
        "kdj": float(kdj_score),
    }


# ════════════════════════════════════════════
# 价值因子
# ════════════════════════════════════════════

def calc_value_factors(financial, all_financials):
    """计算价值因子：PE/PB百分位、股息率"""
    if not financial:
        return {}

    pe = financial.get("pe")
    pb = financial.get("pb")
    div_yield = financial.get("dividend_yield") or 0

    # 在全板块中计算百分位
    all_pe = [f.get("pe") for f in all_financials if f.get("pe") is not None and f.get("pe") > 0]
    all_pb = [f.get("pb") for f in all_financials if f.get("pb") is not None and f.get("pb") > 0]

    pe_pct = 0.5
    if pe and pe > 0 and all_pe:
        pe_pct = sum(1 for x in all_pe if x < pe) / len(all_pe)

    pb_pct = 0.5
    if pb and pb > 0 and all_pb:
        pb_pct = sum(1 for x in all_pb if x < pb) / len(all_pb)

    # PE越低越好 → 百分位低得正分
    pe_score = 1 - 2 * pe_pct
    pb_score = 1 - 2 * pb_pct
    div_score = np.clip(div_yield / 5.0, -1, 1) if div_yield else 0

    return {
        "pe_percentile": float(pe_score),
        "pb_percentile": float(pb_score),
        "dividend_yield": float(div_score),
    }


# ════════════════════════════════════════════
# 质量因子
# ════════════════════════════════════════════

def calc_quality_factors(financial):
    """计算质量因子：ROE、营收增长、净利润增长"""
    if not financial:
        return {}
    roe = financial.get("roe") or 0
    rev_g = financial.get("revenue_growth") or 0
    prof_g = financial.get("profit_growth") or 0

    return {
        "roe": float(np.clip(roe / 30, -1, 1)),         # ROE 30%满分
        "revenue_growth": float(np.clip(rev_g / 50, -1, 1)),
        "profit_growth": float(np.clip(prof_g / 50, -1, 1)),
    }


# ════════════════════════════════════════════
# 资金流向因子
# ════════════════════════════════════════════

def calc_money_flow_factors(flow_df, hist_df):
    """计算资金流向因子"""
    result = {"main_net_inflow": 0.0, "north_inflow": 0.0}

    if flow_df is not None and len(flow_df) > 0:
        inflow = flow_df["main_net_inflow"].astype(float)
        avg_inflow = inflow.mean()
        # 以日均成交额标准化
        if hist_df is not None and "amount" in hist_df.columns and len(hist_df) > 0:
            avg_amount = hist_df["amount"].astype(float).iloc[-20:].mean()
            if avg_amount > 0:
                result["main_net_inflow"] = float(np.clip(avg_inflow / avg_amount, -1, 1))

    return result


# ════════════════════════════════════════════
# 综合评分
# ════════════════════════════════════════════

def zscore_normalize(series):
    """Z-Score标准化"""
    mean = series.mean()
    std = series.std()
    if std == 0 or pd.isna(std):
        return series * 0
    return (series - mean) / std


def compute_all_factors(stock_list, start="20240101", end=None, weights=None):
    """计算全部股票的所有因子，返回综合评分DataFrame。

    Parameters
    ----------
    stock_list : list[dict]  — [{"code": "601899", "name": "紫金矿业"}, ...]
    start, end : str         — 日期范围
    weights    : dict | None — 覆盖 FACTOR_WEIGHTS

    Returns
    -------
    pd.DataFrame — columns: code, name, 各因子得分, composite_score, rank
    """
    if weights is None:
        weights = FACTOR_WEIGHTS

    records = []
    all_financials = []

    # 第一遍：获取财务数据（用于价值因子的全板块百分位计算）
    fin_map = {}
    for s in stock_list:
        code = s["code"]
        fin = get_financial_data(code)
        fin_map[code] = fin
        all_financials.append(fin)

    # 第二遍：计算所有因子
    for s in stock_list:
        code = s["code"]
        name = s.get("name", code)
        hist = get_stock_history(code, start=start, end=end)
        flow = get_money_flow(code)
        fin = fin_map[code]

        mom = calc_momentum_factors(hist)
        tech = calc_technical_factors(hist)
        val = calc_value_factors(fin, all_financials)
        qual = calc_quality_factors(fin)
        mf = calc_money_flow_factors(flow, hist)

        row = {"code": code, "name": name}
        row.update(mom)
        row.update(tech)
        row.update(val)
        row.update(qual)
        row.update(mf)
        records.append(row)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Z-Score标准化各子因子列
    factor_cols = [c for c in df.columns if c not in ("code", "name")]
    for col in factor_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df[col] = zscore_normalize(df[col])

    # 按大类加权求和
    category_map = {
        "momentum": ["ret_5d", "ret_20d", "ret_60d", "volume_change"],
        "technical": ["macd", "rsi", "boll_position", "ma_alignment", "kdj"],
        "value": ["pe_percentile", "pb_percentile", "dividend_yield"],
        "quality": ["roe", "revenue_growth", "profit_growth"],
        "money_flow": ["main_net_inflow", "north_inflow"],
    }

    df["composite_score"] = 0.0
    for cat, sub_factors in category_map.items():
        cat_weight = weights.get(cat, 0)
        cat_score = 0.0
        sub_weight_sum = 0.0
        for sf in sub_factors:
            if sf in df.columns:
                sw = SUB_FACTOR_WEIGHTS.get(sf, 1.0 / len(sub_factors))
                cat_score = cat_score + df[sf] * sw
                sub_weight_sum += sw
        if sub_weight_sum > 0:
            cat_score = cat_score / sub_weight_sum
        df["composite_score"] += cat_score * cat_weight

    df["rank"] = df["composite_score"].rank(ascending=False).astype(int)
    df = df.sort_values("rank")

    return df
