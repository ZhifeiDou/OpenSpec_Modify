"""BaoStock data source adapter — free fallback for historical stock data."""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class BaoStockSource:
    """BaoStock adapter for historical A-share data (fully free)."""

    def __init__(self):
        self._logged_in = False

    def _login(self):
        if not self._logged_in:
            import baostock as bs
            bs.login()
            self._logged_in = True

    def _logout(self):
        if self._logged_in:
            import baostock as bs
            bs.logout()
            self._logged_in = False

    def _to_baostock_code(self, symbol: str) -> str:
        """Convert 6-digit code to baostock format (sh.600000 or sz.000001)."""
        if symbol.startswith(("sh.", "sz.")):
            return symbol
        prefix = "sh" if symbol.startswith(("6", "9")) else "sz"
        return f"{prefix}.{symbol}"

    def fetch_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        import baostock as bs

        self._login()
        code = self._to_baostock_code(symbol)

        rs = bs.query_history_k_data_plus(
            code,
            "date,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2",  # Forward-adjusted
        )
        if rs.error_code != "0":
            logger.error("BaoStock error: %s %s", rs.error_code, rs.error_msg)
            return pd.DataFrame()

        df = rs.get_data()
        if df.empty:
            return df

        for col in ["open", "high", "low", "close", "volume", "amount"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])
        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    def fetch_financials(self, symbol: str) -> pd.DataFrame:
        """BaoStock provides limited financial data."""
        import baostock as bs

        self._login()
        code = self._to_baostock_code(symbol)

        frames = []
        for year in range(2020, 2027):
            for quarter in range(1, 5):
                try:
                    rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
                    if rs.error_code == "0":
                        df = rs.get_data()
                        if not df.empty:
                            frames.append(df)
                except Exception:
                    continue

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def fetch_futures_daily(self, metal, start_date, end_date):
        """BaoStock does not support futures data."""
        return pd.DataFrame()

    def fetch_inventory(self, metal):
        return pd.DataFrame()

    def fetch_macro(self, indicator):
        return pd.DataFrame()

    def fetch_fund_flow(self, symbol, start_date, end_date):
        return pd.DataFrame()

    def fetch_industry_stocks(self, industry_code):
        return pd.DataFrame()
