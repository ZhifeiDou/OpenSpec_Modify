"""AKShare data source adapter — primary free data provider."""
from __future__ import annotations

import time
import logging
from functools import wraps

import pandas as pd

logger = logging.getLogger(__name__)


def _retry(max_retries: int = 2, delay: float = 0.5):
    """Decorator: retry on failure with delay between API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    time.sleep(delay)
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        "AKShare %s attempt %d/%d failed: %s",
                        func.__name__, attempt + 1, max_retries + 1, e,
                    )
            raise last_error
        return wrapper
    return decorator


class AKShareSource:
    """AKShare data adapter with 0.5s delay and 2 retries per call."""

    def __init__(self, delay: float = 0.5, max_retries: int = 2):
        self.delay = delay
        self.max_retries = max_retries

    @_retry()
    def fetch_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        import akshare as ak

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
            adjust="qfq",
        )
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume",
            "成交额": "amount",
        })
        df["date"] = pd.to_datetime(df["date"])
        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    @_retry()
    def fetch_financials(self, symbol: str) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_financial_abstract_em(symbol=symbol)
        except Exception:
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()
        return df

    @_retry()
    def fetch_futures_daily(
        self, metal: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        import akshare as ak

        # Main continuous contract symbol: metal + "0"
        symbol = f"{metal}0"
        try:
            df = ak.futures_zh_daily_sina(symbol=symbol)
        except Exception:
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df[["date", "open", "high", "low", "close", "volume"]].copy()

    @_retry()
    def fetch_inventory(self, metal: str) -> pd.DataFrame:
        import akshare as ak

        metal_names = {
            "cu": "铜", "al": "铝", "zn": "锌",
            "ni": "镍", "sn": "锡", "pb": "铅",
            "au": "黄金", "ag": "白银",
        }
        name = metal_names.get(metal, metal)
        try:
            df = ak.futures_inventory_em(symbol=name)
        except Exception:
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()
        return df

    @_retry()
    def fetch_macro(self, indicator: str) -> pd.DataFrame:
        import akshare as ak

        fetch_map = {
            "pmi": ak.macro_china_pmi,
            "m1": ak.macro_china_money_supply,
            "cpi": ak.macro_china_cpi,
            "ppi": ak.macro_china_ppi,
        }
        func = fetch_map.get(indicator)
        if func is None:
            logger.warning("Unsupported macro indicator: %s", indicator)
            return pd.DataFrame()

        try:
            df = func()
        except Exception:
            return pd.DataFrame()
        return df if df is not None else pd.DataFrame()

    @_retry()
    def fetch_fund_flow(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.stock_hsgt_individual_em(symbol=symbol)
        except Exception:
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        df["date"] = pd.to_datetime(df.iloc[:, 0])
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df

    @_retry()
    def fetch_industry_stocks(self, industry_code: str) -> pd.DataFrame:
        import akshare as ak

        try:
            df = ak.index_component_sw(symbol=industry_code)
        except Exception:
            try:
                df = ak.stock_board_industry_cons_em(symbol="有色金属")
            except Exception:
                return pd.DataFrame()

        return df if df is not None else pd.DataFrame()
