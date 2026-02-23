"""Tushare data source wrapper — second fallback."""

import time
import pandas as pd


class TushareAPI:
    """Second fallback data source using Tushare Pro."""

    def __init__(self, token: str = "", delay: float = 0.5):
        self.delay = delay
        self._last_call = 0.0
        self.pro = None
        if token:
            import tushare as ts
            ts.set_token(token)
            self.pro = ts.pro_api()

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_call = time.time()

    def _to_tushare_code(self, code: str) -> str:
        if code.startswith("6"):
            return f"{code}.SH"
        return f"{code}.SZ"

    def fetch_stock_price(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch daily OHLCV data for a stock."""
        if not self.pro:
            raise ConnectionError("Tushare token not configured")
        self._rate_limit()
        ts_code = self._to_tushare_code(code)
        df = self.pro.daily(
            ts_code=ts_code,
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
        )
        df = df.rename(columns={
            "trade_date": "date", "vol": "volume"
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    def fetch_fundamental(self, code: str) -> dict:
        """Fetch fundamental data."""
        if not self.pro:
            raise ConnectionError("Tushare token not configured")
        self._rate_limit()
        ts_code = self._to_tushare_code(code)
        try:
            df = self.pro.daily_basic(ts_code=ts_code, fields="ts_code,pb,pe_ttm")
            if len(df) > 0:
                return {
                    "pb": df.iloc[0]["pb"],
                    "roe_ttm": None,
                    "gross_margin": None,
                }
        except Exception:
            pass
        return {"pb": None, "roe_ttm": None, "gross_margin": None}

    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch stock list."""
        if not self.pro:
            raise ConnectionError("Tushare token not configured")
        self._rate_limit()
        df = self.pro.stock_basic(exchange="", list_status="L",
                                  fields="ts_code,symbol,name,industry,list_date")
        return df
