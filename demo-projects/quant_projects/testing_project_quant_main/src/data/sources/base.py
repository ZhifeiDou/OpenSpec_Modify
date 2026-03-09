"""DataSource protocol — unified interface for all data providers."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class DataSource(Protocol):
    """Unified interface for market data providers.

    Each concrete adapter (AKShare, BaoStock, Tushare) implements this protocol.
    The pipeline depends on this interface, not on specific implementations.
    """

    def fetch_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Fetch daily OHLCV for a stock.

        Returns DataFrame with columns:
            date, open, high, low, close, volume, amount
        """
        ...

    def fetch_financials(self, symbol: str) -> pd.DataFrame:
        """Fetch financial statement data for a stock.

        Returns DataFrame with columns:
            symbol, report_date, pb, roe_ttm, gross_margin, ev, ebitda,
            total_revenue, net_profit, total_assets, total_liabilities
        """
        ...

    def fetch_futures_daily(
        self, metal: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Fetch daily futures data for a metal (main contract).

        Args:
            metal: Futures symbol (cu, al, zn, ni, sn, pb, au, LC)

        Returns DataFrame with columns:
            date, open, high, low, close, settle, volume, open_interest
        """
        ...

    def fetch_inventory(self, metal: str) -> pd.DataFrame:
        """Fetch warehouse inventory data for a metal.

        Returns DataFrame with columns:
            date, inventory (tons)
        """
        ...

    def fetch_macro(self, indicator: str) -> pd.DataFrame:
        """Fetch macro indicator time series.

        Args:
            indicator: One of 'pmi', 'usd_cny', 'usd_index', 'm1', 'social_finance'

        Returns DataFrame with columns:
            date, value
        """
        ...

    def fetch_fund_flow(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Fetch fund flow data (margin + northbound) for a stock.

        Returns DataFrame with columns:
            date, margin_balance, northbound_net_buy, northbound_holding
        """
        ...

    def fetch_industry_stocks(self, industry_code: str) -> pd.DataFrame:
        """Fetch stocks in an industry classification.

        Returns DataFrame with columns:
            symbol, name, industry_code, industry_name
        """
        ...
