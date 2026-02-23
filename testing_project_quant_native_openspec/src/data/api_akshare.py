"""AKShare data source wrapper for stock prices, fundamentals, futures, macro, fund flow."""

import time
import pandas as pd
import akshare as ak
from datetime import datetime


class AKShareAPI:
    """Primary data source using AKShare."""

    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self._last_call = 0.0

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_call = time.time()

    def fetch_stock_price(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch daily OHLCV data for a stock."""
        self._rate_limit()
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume", "成交额": "amount"
        })
        df["date"] = pd.to_datetime(df["date"])
        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch all A-share stock list with industry info."""
        self._rate_limit()
        df = ak.stock_info_a_code_name()
        return df

    def fetch_industry_classification(self) -> pd.DataFrame:
        """Fetch CSRC industry classification."""
        self._rate_limit()
        df = ak.stock_industry_category_cninfo(symbol="巨潮行业分类")
        return df

    def fetch_fundamental(self, code: str) -> dict:
        """Fetch fundamental data: PB, ROE, gross margin, EV/EBITDA."""
        self._rate_limit()
        try:
            df = ak.stock_financial_abstract_ths(symbol=code)
            latest = df.iloc[0] if len(df) > 0 else {}
            return {
                "pb": latest.get("市净率", None),
                "roe_ttm": latest.get("净资产收益率", None),
                "gross_margin": latest.get("毛利率", None),
            }
        except Exception:
            return {"pb": None, "roe_ttm": None, "gross_margin": None}

    def fetch_metal_futures(self, metal: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch metal futures daily prices."""
        self._rate_limit()
        symbol_map = {
            "copper": "CU0", "aluminum": "AL0", "gold": "AU0",
            "zinc": "ZN0", "lithium": "LC0",
        }
        symbol = symbol_map.get(metal, metal)
        df = ak.futures_zh_daily_sina(symbol=symbol)
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df[["date", "close"]]

    def fetch_macro_pmi(self) -> pd.DataFrame:
        """Fetch China PMI data."""
        self._rate_limit()
        df = ak.macro_china_pmi()
        df = df.rename(columns={"月份": "date", "制造业PMI": "pmi"})
        df["date"] = pd.to_datetime(df["date"])
        return df[["date", "pmi"]]

    def fetch_usd_index(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch USD index."""
        self._rate_limit()
        df = ak.index_us_stock_sina(symbol="DINIW")
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df[["date", "close"]].rename(columns={"close": "usd_index"})

    def fetch_northbound_flow(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch northbound fund flow data."""
        self._rate_limit()
        df = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
        df = df.rename(columns={"日期": "date", "净流入": "net_flow"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df[["date", "net_flow"]]

    def fetch_financing_balance(self, code: str) -> pd.DataFrame:
        """Fetch margin financing balance for a stock."""
        self._rate_limit()
        try:
            df = ak.stock_margin_detail_sse(code=code)
            df = df.rename(columns={"日期": "date", "融资余额": "financing_balance"})
            df["date"] = pd.to_datetime(df["date"])
            return df[["date", "financing_balance"]]
        except Exception:
            return pd.DataFrame(columns=["date", "financing_balance"])

    def fetch_m1_growth(self) -> pd.DataFrame:
        """Fetch M1 money supply growth rate."""
        self._rate_limit()
        df = ak.macro_china_money_supply()
        df = df.rename(columns={"月份": "date", "M1同比增长": "m1_growth"})
        df["date"] = pd.to_datetime(df["date"])
        return df[["date", "m1_growth"]]
