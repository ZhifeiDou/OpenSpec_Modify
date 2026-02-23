"""BaoStock data source wrapper — first fallback."""

import time
import pandas as pd
import baostock as bs


class BaoStockAPI:
    """Fallback data source using BaoStock."""

    def __init__(self, delay: float = 0.3):
        self.delay = delay
        self._last_call = 0.0
        self._logged_in = False

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_call = time.time()

    def _ensure_login(self):
        if not self._logged_in:
            bs.login()
            self._logged_in = True

    def logout(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False

    def _to_baostock_code(self, code: str) -> str:
        if code.startswith("6"):
            return f"sh.{code}"
        return f"sz.{code}"

    def fetch_stock_price(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch daily OHLCV data for a stock."""
        self._ensure_login()
        self._rate_limit()
        bscode = self._to_baostock_code(code)
        rs = bs.query_history_k_data_plus(
            bscode,
            "date,open,high,low,close,volume,amount",
            start_date=start_date, end_date=end_date,
            frequency="d", adjustflag="2"
        )
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume", "amount"])
        for col in ["open", "high", "low", "close", "volume", "amount"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])
        return df

    def fetch_fundamental(self, code: str) -> dict:
        """Fetch basic fundamental data."""
        self._ensure_login()
        self._rate_limit()
        bscode = self._to_baostock_code(code)
        rs = bs.query_profit_data(code=bscode, year=2024, quarter=4)
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if rows:
            return {
                "pb": None,
                "roe_ttm": float(rows[0][4]) if rows[0][4] else None,
                "gross_margin": None,
            }
        return {"pb": None, "roe_ttm": None, "gross_margin": None}

    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch stock list — limited support."""
        self._ensure_login()
        self._rate_limit()
        rs = bs.query_stock_basic()
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        df = pd.DataFrame(rows, columns=rs.fields)
        return df
