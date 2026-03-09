"""Tushare Pro data source adapter — primary data provider for A-share market data."""
from __future__ import annotations

import os
import time
import logging
from datetime import datetime
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
                        "Tushare %s attempt %d/%d failed: %s",
                        func.__name__, attempt + 1, max_retries + 1, e,
                    )
            raise last_error
        return wrapper
    return decorator


# ── Symbol & date conversion helpers ──────────────────────────────────────────


def _to_tushare_code(symbol: str) -> str:
    """Convert 6-digit A-share code to Tushare format.

    Rules:
        0xxx, 3xxx → XXXXXX.SZ  (Shenzhen)
        6xxx, 9xxx → XXXXXX.SH  (Shanghai)
    """
    if "." in symbol:
        return symbol  # Already in Tushare format
    prefix = symbol[0] if symbol else ""
    if prefix in ("0", "3"):
        return f"{symbol}.SZ"
    elif prefix in ("6", "9"):
        return f"{symbol}.SH"
    return f"{symbol}.SZ"  # Default to Shenzhen


def _to_tushare_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to YYYYMMDD format."""
    return date_str.replace("-", "")


def _from_tushare_date(date_str: str) -> pd.Timestamp:
    """Convert YYYYMMDD to pandas Timestamp."""
    return pd.to_datetime(date_str, format="%Y%m%d")


# ── Futures contract mapping ─────────────────────────────────────────────────

_FUTURES_MAP = {
    "cu": "CU0.SHF",
    "al": "AL0.SHF",
    "zn": "ZN0.SHF",
    "ni": "NI0.SHF",
    "sn": "SN0.SHF",
    "pb": "PB0.SHF",
    "au": "AU0.SHF",
    "ag": "AG0.SHF",
    "LC": "LC0.INE",
}


class TushareSource:
    """Tushare Pro data adapter implementing the DataSource protocol."""

    def __init__(
        self,
        token: str | None = None,
        token_env: str = "TUSHARE_TOKEN",
        delay: float = 0.5,
        max_retries: int = 2,
        validate_token: bool = True,
    ):
        self.delay = delay
        self.max_retries = max_retries

        # Load token
        self._token = token or os.environ.get(token_env, "")
        if not self._token:
            raise ValueError(
                f"{token_env} environment variable not set.\n"
                f"Get your token from https://tushare.pro/user/token\n"
                f"Then set it in .env or as an environment variable:\n"
                f"  export {token_env}=your_token_here"
            )

        # Initialize Tushare Pro API
        import tushare as ts
        ts.set_token(self._token)
        self._pro = ts.pro_api(self._token)

        # Validate token
        if validate_token:
            self._validate_token()

    def _validate_token(self):
        """Validate token by making a lightweight API call."""
        try:
            today = datetime.now().strftime("%Y%m%d")
            df = self._pro.trade_cal(start_date=today, end_date=today)
            if df is None:
                raise ConnectionError("Tushare returned None for trade_cal")
        except Exception as e:
            raise ConnectionError(
                f"Tushare token validation failed: {e}\n"
                f"Please check your token at https://tushare.pro/user/token"
            ) from e

    @_retry()
    def fetch_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        ts_code = _to_tushare_code(symbol)
        sd = _to_tushare_date(start_date)
        ed = _to_tushare_date(end_date)

        df = self._pro.daily(ts_code=ts_code, start_date=sd, end_date=ed)
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.rename(columns={
            "trade_date": "date",
            "vol": "volume",
        })
        df["date"] = df["date"].apply(_from_tushare_date)
        df = df.sort_values("date").reset_index(drop=True)
        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    @_retry()
    def fetch_financials(self, symbol: str) -> pd.DataFrame:
        ts_code = _to_tushare_code(symbol)

        try:
            income = self._pro.income(
                ts_code=ts_code,
                fields="ts_code,end_date,revenue,n_income",
            )
            balance = self._pro.balancesheet(
                ts_code=ts_code,
                fields="ts_code,end_date,total_assets,total_liab",
            )
        except Exception:
            return pd.DataFrame()

        if income is None or income.empty:
            return pd.DataFrame()

        # Merge income and balance sheet on end_date
        df = income.rename(columns={
            "end_date": "report_date",
            "revenue": "total_revenue",
            "n_income": "net_profit",
        })
        df["symbol"] = symbol

        if balance is not None and not balance.empty:
            balance = balance.rename(columns={
                "end_date": "report_date",
                "total_liab": "total_liabilities",
            })
            df = df.merge(
                balance[["report_date", "total_assets", "total_liabilities"]],
                on="report_date",
                how="left",
            )

        return df

    @_retry()
    def fetch_futures_daily(
        self, metal: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        ts_code = _FUTURES_MAP.get(metal)
        if ts_code is None:
            logger.warning("No Tushare futures mapping for metal: %s", metal)
            return pd.DataFrame()

        sd = _to_tushare_date(start_date)
        ed = _to_tushare_date(end_date)

        try:
            df = self._pro.fut_daily(ts_code=ts_code, start_date=sd, end_date=ed)
        except Exception:
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.rename(columns={
            "trade_date": "date",
            "oi": "open_interest",
        })
        df["date"] = df["date"].apply(_from_tushare_date)
        df = df.sort_values("date").reset_index(drop=True)

        cols = ["date", "open", "high", "low", "close"]
        if "settle" in df.columns:
            cols.append("settle")
        cols.extend(["vol", "open_interest"])
        # vol in futures is already named vol (not volume)
        available = [c for c in cols if c in df.columns]
        result = df[available].copy()
        if "vol" in result.columns:
            result = result.rename(columns={"vol": "volume"})
        return result

    @_retry()
    def fetch_inventory(self, metal: str) -> pd.DataFrame:
        """Tushare does not have a direct warehouse inventory API."""
        return pd.DataFrame()

    @_retry()
    def fetch_macro(self, indicator: str) -> pd.DataFrame:
        macro_map = {
            "pmi": ("cn_pmi", "pmi010000"),
            "m1": ("cn_m", "m1_yoy"),
            "cpi": ("cn_cpi", "nt_yoy"),
            "ppi": ("cn_ppi", "ppi_yoy"),
        }

        entry = macro_map.get(indicator)
        if entry is None:
            logger.warning("Unsupported macro indicator: %s", indicator)
            return pd.DataFrame()

        func_name, value_col = entry

        try:
            func = getattr(self._pro, func_name)
            df = func()
        except Exception:
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        if "month" in df.columns:
            df["date"] = pd.to_datetime(df["month"], format="%Y%m") + pd.offsets.MonthBegin(0)
        elif "trade_date" in df.columns:
            df["date"] = df["trade_date"].apply(_from_tushare_date)

        if value_col not in df.columns:
            logger.warning("Column %s not found in %s response", value_col, func_name)
            return pd.DataFrame()

        df["value"] = pd.to_numeric(df[value_col], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        return df[["date", "value"]]

    @_retry()
    def fetch_fund_flow(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        ts_code = _to_tushare_code(symbol)
        sd = _to_tushare_date(start_date)
        ed = _to_tushare_date(end_date)

        # Margin data (per stock)
        try:
            margin = self._pro.margin_detail(
                ts_code=ts_code, start_date=sd, end_date=ed,
            )
        except Exception:
            margin = pd.DataFrame()

        # Northbound flow (market-wide)
        try:
            hsgt = self._pro.moneyflow_hsgt(start_date=sd, end_date=ed)
        except Exception:
            hsgt = pd.DataFrame()

        # Build margin DataFrame
        if margin is not None and not margin.empty:
            margin["date"] = margin["trade_date"].apply(_from_tushare_date)
            margin = margin.rename(columns={"rzrqye": "margin_balance"})
            margin_df = margin[["date", "margin_balance"]].copy()
        else:
            margin_df = pd.DataFrame(columns=["date", "margin_balance"])

        # Build northbound DataFrame
        if hsgt is not None and not hsgt.empty:
            hsgt["date"] = hsgt["trade_date"].apply(_from_tushare_date)
            hsgt = hsgt.rename(columns={"north_money": "northbound_net_buy"})
            hsgt_df = hsgt[["date", "northbound_net_buy"]].copy()
        else:
            hsgt_df = pd.DataFrame(columns=["date", "northbound_net_buy"])

        # Merge on date
        if margin_df.empty and hsgt_df.empty:
            return pd.DataFrame()

        if margin_df.empty:
            hsgt_df["margin_balance"] = float("nan")
            return hsgt_df[["date", "margin_balance", "northbound_net_buy"]]

        if hsgt_df.empty:
            margin_df["northbound_net_buy"] = float("nan")
            return margin_df[["date", "margin_balance", "northbound_net_buy"]]

        result = margin_df.merge(hsgt_df, on="date", how="outer").sort_values("date")
        return result[["date", "margin_balance", "northbound_net_buy"]].reset_index(drop=True)

    @_retry()
    def fetch_industry_stocks(self, industry_code: str) -> pd.DataFrame:
        try:
            # Try Tushare index member API for Shenwan index
            df = self._pro.index_member(index_code=industry_code)
        except Exception:
            df = None

        if df is None or df.empty:
            try:
                # Fallback: use stock_basic and filter by industry
                df = self._pro.stock_basic(
                    exchange="",
                    list_status="L",
                    fields="ts_code,name,industry",
                )
                if df is not None and not df.empty:
                    # Filter for non-ferrous metals related
                    df = df[df["industry"].str.contains("有色", na=False)]
            except Exception:
                return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        # Normalize columns
        col_map = {}
        for col in df.columns:
            cl = col.lower()
            if cl in ("ts_code", "con_code"):
                col_map[col] = "symbol"
            elif cl == "name" or "名称" in cl:
                col_map[col] = "name"
            elif cl == "industry" or "行业" in cl:
                col_map[col] = "industry_name"
        df = df.rename(columns=col_map)

        if "symbol" in df.columns:
            # Strip exchange suffix to get 6-digit code
            df["symbol"] = df["symbol"].str.replace(r"\.(SZ|SH|BJ)$", "", regex=True)

        if "name" not in df.columns:
            df["name"] = ""
        if "industry_name" not in df.columns:
            df["industry_name"] = ""
        if "industry_code" not in df.columns:
            df["industry_code"] = industry_code

        return df[["symbol", "name", "industry_code", "industry_name"]].reset_index(drop=True)
