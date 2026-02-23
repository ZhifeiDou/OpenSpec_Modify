"""数据获取模块 — AKShare数据源 + SQLite缓存"""

import sqlite3
import json
import time
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

from config import DB_PATH, DEFAULT_STOCK_POOL


def _get_conn():
    """获取SQLite连接，自动建表"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            code TEXT, date TEXT, open REAL, high REAL, low REAL,
            close REAL, volume REAL, amount REAL,
            PRIMARY KEY (code, date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_info (
            code TEXT PRIMARY KEY, name TEXT, industry TEXT,
            pe REAL, pb REAL, roe REAL, dividend_yield REAL,
            revenue_growth REAL, profit_growth REAL,
            updated_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS money_flow (
            code TEXT, date TEXT, main_net_inflow REAL,
            PRIMARY KEY (code, date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache_meta (
            key TEXT PRIMARY KEY, updated_at TEXT
        )
    """)
    conn.commit()
    return conn


def _cache_fresh(conn, key, hours=4):
    """检查缓存是否仍然有效"""
    row = conn.execute(
        "SELECT updated_at FROM cache_meta WHERE key=?", (key,)
    ).fetchone()
    if not row:
        return False
    updated = datetime.fromisoformat(row[0])
    return (datetime.now() - updated) < timedelta(hours=hours)


def _update_cache_ts(conn, key):
    conn.execute(
        "INSERT OR REPLACE INTO cache_meta (key, updated_at) VALUES (?, ?)",
        (key, datetime.now().isoformat()),
    )
    conn.commit()


# ────────────────────────────────────────────
# 公开API
# ────────────────────────────────────────────

def get_nonferrous_stocks(force=False):
    """获取有色金属板块股票列表。
    优先从AKShare申万行业获取，失败则使用默认股票池。
    """
    conn = _get_conn()
    cache_key = "nonferrous_stocks"

    if not force and _cache_fresh(conn, cache_key, hours=24):
        rows = conn.execute("SELECT code, name FROM stock_info").fetchall()
        if rows:
            conn.close()
            return pd.DataFrame(rows, columns=["code", "name"])

    stocks = []
    try:
        # 尝试通过申万行业获取有色金属成分股
        df = ak.stock_board_industry_cons_em(symbol="有色金属")
        for _, row in df.iterrows():
            code = str(row["代码"]).zfill(6)
            name = row["名称"]
            stocks.append({"code": code, "name": name})
    except Exception as e:
        print(f"[WARN] 从AKShare获取行业成分股失败: {e}，使用默认股票池")
        # 回退到默认股票池
        for code in DEFAULT_STOCK_POOL:
            try:
                info = ak.stock_individual_info_em(symbol=code)
                name_row = info[info["item"] == "股票简称"]
                name = name_row["value"].values[0] if len(name_row) else code
            except Exception:
                name = code
            stocks.append({"code": code, "name": name})
            time.sleep(0.3)

    # 限制股票数量，避免请求过多
    stocks = stocks[:30]

    # 写入数据库
    for s in stocks:
        conn.execute(
            "INSERT OR REPLACE INTO stock_info (code, name, updated_at) VALUES (?, ?, ?)",
            (s["code"], s["name"], datetime.now().isoformat()),
        )
    _update_cache_ts(conn, cache_key)
    conn.close()

    return pd.DataFrame(stocks)


def get_stock_history(code, start="20240101", end=None, force=False):
    """获取个股日K线数据，缓存到SQLite"""
    if end is None:
        end = datetime.now().strftime("%Y%m%d")

    conn = _get_conn()
    cache_key = f"history_{code}"

    if not force and _cache_fresh(conn, cache_key, hours=6):
        df = pd.read_sql(
            "SELECT * FROM stock_history WHERE code=? AND date>=? AND date<=? ORDER BY date",
            conn, params=(code, start, end),
        )
        if len(df) > 20:
            conn.close()
            return df

    try:
        df = ak.stock_zh_a_hist(
            symbol=code, period="daily",
            start_date=start, end_date=end, adjust="qfq"
        )
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume",
            "成交额": "amount",
        })
        df["code"] = code
        df["date"] = df["date"].astype(str).str.replace("-", "")
        cols = ["code", "date", "open", "high", "low", "close", "volume", "amount"]
        df = df[[c for c in cols if c in df.columns]]

        # 写入数据库
        for _, row in df.iterrows():
            conn.execute(
                """INSERT OR REPLACE INTO stock_history
                   (code, date, open, high, low, close, volume, amount)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (row.get("code"), row.get("date"), row.get("open"),
                 row.get("high"), row.get("low"), row.get("close"),
                 row.get("volume"), row.get("amount")),
            )
        _update_cache_ts(conn, cache_key)
        conn.commit()
    except Exception as e:
        print(f"[WARN] 获取 {code} 行情失败: {e}")
        df = pd.read_sql(
            "SELECT * FROM stock_history WHERE code=? ORDER BY date",
            conn, params=(code,),
        )

    conn.close()
    return df


def get_financial_data(code, force=False):
    """获取个股财务指标 (PE/PB/ROE/股息率/营收增长/净利润增长)"""
    conn = _get_conn()
    cache_key = f"financial_{code}"

    if not force and _cache_fresh(conn, cache_key, hours=24):
        row = conn.execute(
            "SELECT pe, pb, roe, dividend_yield, revenue_growth, profit_growth FROM stock_info WHERE code=?",
            (code,),
        ).fetchone()
        if row and row[0] is not None:
            conn.close()
            return {
                "pe": row[0], "pb": row[1], "roe": row[2],
                "dividend_yield": row[3], "revenue_growth": row[4],
                "profit_growth": row[5],
            }

    data = {"pe": None, "pb": None, "roe": None,
            "dividend_yield": None, "revenue_growth": None, "profit_growth": None}

    try:
        info = ak.stock_individual_info_em(symbol=code)
        # 提取可用字段
        for _, row in info.iterrows():
            item = row["item"]
            val = row["value"]
            try:
                val_f = float(val)
            except (ValueError, TypeError):
                continue
            if "市盈率" in str(item):
                data["pe"] = val_f
            elif "市净率" in str(item):
                data["pb"] = val_f
    except Exception as e:
        print(f"[WARN] 获取 {code} 基本信息失败: {e}")

    try:
        fin = ak.stock_financial_analysis_indicator(symbol=code)
        if len(fin) > 0:
            latest = fin.iloc[0]
            for col in fin.columns:
                col_str = str(col)
                if "净资产收益率" in col_str:
                    try:
                        data["roe"] = float(latest[col])
                    except (ValueError, TypeError):
                        pass
                elif "营业收入增长率" in col_str or "主营业务收入增长率" in col_str:
                    try:
                        data["revenue_growth"] = float(latest[col])
                    except (ValueError, TypeError):
                        pass
                elif "净利润增长率" in col_str:
                    try:
                        data["profit_growth"] = float(latest[col])
                    except (ValueError, TypeError):
                        pass
    except Exception as e:
        print(f"[WARN] 获取 {code} 财务指标失败: {e}")

    # 更新数据库
    conn.execute(
        """UPDATE stock_info SET pe=?, pb=?, roe=?, dividend_yield=?,
           revenue_growth=?, profit_growth=?, updated_at=? WHERE code=?""",
        (data["pe"], data["pb"], data["roe"], data["dividend_yield"],
         data["revenue_growth"], data["profit_growth"],
         datetime.now().isoformat(), code),
    )
    _update_cache_ts(conn, cache_key)
    conn.commit()
    conn.close()
    return data


def get_money_flow(code, force=False):
    """获取个股资金流向数据"""
    conn = _get_conn()
    cache_key = f"money_flow_{code}"

    if not force and _cache_fresh(conn, cache_key, hours=6):
        df = pd.read_sql(
            "SELECT * FROM money_flow WHERE code=? ORDER BY date DESC LIMIT 20",
            conn, params=(code,),
        )
        if len(df) > 0:
            conn.close()
            return df

    try:
        df = ak.stock_individual_fund_flow(stock=code, market="sh" if code.startswith("6") else "sz")
        df = df.rename(columns=lambda c: c.strip())
        # 尝试找到日期列和主力净流入列
        date_col = None
        flow_col = None
        for c in df.columns:
            if "日期" in c:
                date_col = c
            if "主力净流入" in c and "净占比" not in c:
                flow_col = c
        if date_col and flow_col:
            result = pd.DataFrame({
                "code": code,
                "date": df[date_col].astype(str).str.replace("-", ""),
                "main_net_inflow": pd.to_numeric(df[flow_col], errors="coerce"),
            })
            for _, row in result.dropna().iterrows():
                conn.execute(
                    "INSERT OR REPLACE INTO money_flow (code, date, main_net_inflow) VALUES (?, ?, ?)",
                    (row["code"], row["date"], row["main_net_inflow"]),
                )
            conn.commit()
            _update_cache_ts(conn, cache_key)
            conn.close()
            return result
    except Exception as e:
        print(f"[WARN] 获取 {code} 资金流向失败: {e}")

    df = pd.read_sql(
        "SELECT * FROM money_flow WHERE code=? ORDER BY date DESC LIMIT 20",
        conn, params=(code,),
    )
    conn.close()
    return df


def get_benchmark_history(start="20240101", end=None):
    """获取沪深300指数日K线作为基准"""
    if end is None:
        end = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zh_index_daily_em(symbol="sh000300")
        df = df.rename(columns={
            "date": "date", "open": "open", "high": "high",
            "low": "low", "close": "close", "volume": "volume",
        })
        df["date"] = df["date"].astype(str).str.replace("-", "")
        df = df[(df["date"] >= start) & (df["date"] <= end)]
        return df.sort_values("date").reset_index(drop=True)
    except Exception as e:
        print(f"[WARN] 获取沪深300基准失败: {e}")
        return pd.DataFrame()
