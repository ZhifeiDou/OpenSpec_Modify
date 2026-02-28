"""Data pipeline — orchestrates fetching, validating, and storing market data."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import pandas as pd

from src.data.storage import DataStore
from src.data.sources.akshare_source import AKShareSource
from src.data.sources.baostock_source import BaoStockSource
from src.data.validators import validate_stock_daily, validate_futures_daily, validate_dataframe

logger = logging.getLogger(__name__)


class DataPipeline:
    """Orchestrates incremental data fetching from multiple sources."""

    def __init__(self, config: dict):
        self.config = config
        data_cfg = config.get("data", {})
        self.store = DataStore(data_cfg.get("db_path", "data/quant.db"))
        self.primary = AKShareSource(
            delay=data_cfg.get("api_delay_seconds", 0.5),
            max_retries=data_cfg.get("max_retries", 2),
        )
        self.fallback = BaoStockSource()
        self._metals = ["cu", "al", "zn", "ni", "sn", "pb", "au", "ag"]

    def run(
        self,
        symbols: list[str] | None = None,
        categories: list[str] | None = None,
        force_refresh: bool = False,
    ):
        """Run the data update pipeline.

        Args:
            symbols: Stock symbols to update. If None, update all known.
            categories: Data categories to update ('stock', 'futures', 'macro', 'flow').
                       If None, update all.
            force_refresh: If True, clear existing data and re-download everything.
        """
        all_categories = ["stock", "futures", "macro", "flow"]
        cats = categories or all_categories

        today = datetime.now().strftime("%Y-%m-%d")
        default_start = "2020-01-01"

        summary = {}

        if "stock" in cats:
            summary["stock"] = self._update_stock_daily(
                symbols, default_start, today, force_refresh
            )

        if "futures" in cats:
            summary["futures"] = self._update_futures(
                default_start, today, force_refresh
            )

        if "macro" in cats:
            summary["macro"] = self._update_macro(force_refresh)

        if "flow" in cats and symbols:
            summary["flow"] = self._update_fund_flow(
                symbols, default_start, today, force_refresh
            )

        # Print summary
        print("\n数据更新摘要:")
        for cat, info in summary.items():
            print(f"  {cat}: {info}")

    def _get_start_date(self, category: str, default: str, force: bool) -> str:
        """Determine start date for incremental update."""
        if force:
            return default
        last = self.store.get_last_updated(category)
        if last:
            # Start from day after last update
            last_date = datetime.fromisoformat(last)
            return (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
        return default

    def _update_stock_daily(
        self, symbols: list[str] | None, default_start: str, end: str, force: bool
    ) -> str:
        if force:
            self.store.clear_table("stock_daily")

        if not symbols:
            return "skipped (no symbols provided)"

        total_rows = 0
        errors = 0
        for symbol in symbols:
            start = self._get_start_date(f"stock_{symbol}", default_start, force)
            try:
                df = self.primary.fetch_stock_daily(symbol, start, end)
                if df.empty:
                    df = self.fallback.fetch_stock_daily(symbol, start, end)
            except Exception as e:
                logger.error("Failed to fetch %s: %s", symbol, e)
                errors += 1
                continue

            result = validate_stock_daily(df)
            for w in result.warnings:
                logger.warning("%s: %s", symbol, w)

            if not result.clean_df.empty:
                result.clean_df["symbol"] = symbol
                self.store.save_dataframe("stock_daily", result.clean_df)
                total_rows += len(result.clean_df)
                self.store.set_last_updated(f"stock_{symbol}", end)

        self.store.set_last_updated("stock", end)
        return f"{total_rows} rows updated, {errors} errors"

    def _update_futures(self, default_start: str, end: str, force: bool) -> str:
        if force:
            self.store.clear_table("futures_daily")

        total_rows = 0
        for metal in self._metals:
            start = self._get_start_date(f"futures_{metal}", default_start, force)
            try:
                df = self.primary.fetch_futures_daily(metal, start, end)
            except Exception as e:
                logger.error("Failed to fetch futures %s: %s", metal, e)
                continue

            result = validate_futures_daily(df)
            if not result.clean_df.empty:
                result.clean_df["metal"] = metal
                self.store.save_dataframe("futures_daily", result.clean_df)
                total_rows += len(result.clean_df)
                self.store.set_last_updated(f"futures_{metal}", end)

        self.store.set_last_updated("futures", end)
        return f"{total_rows} rows updated"

    def _update_macro(self, force: bool) -> str:
        if force:
            self.store.clear_table("macro")

        indicators = ["pmi", "m1"]
        total = 0
        for ind in indicators:
            try:
                df = self.primary.fetch_macro(ind)
            except Exception as e:
                logger.error("Failed to fetch macro %s: %s", ind, e)
                continue

            result = validate_dataframe(df, name=f"macro_{ind}")
            if not result.clean_df.empty:
                total += len(result.clean_df)

        self.store.set_last_updated("macro")
        return f"{total} records"

    def _update_fund_flow(
        self, symbols: list[str], default_start: str, end: str, force: bool
    ) -> str:
        if force:
            self.store.clear_table("fund_flow")

        total = 0
        for symbol in symbols:
            try:
                df = self.primary.fetch_fund_flow(symbol, default_start, end)
            except Exception as e:
                logger.error("Failed to fetch fund flow %s: %s", symbol, e)
                continue
            if not df.empty:
                total += len(df)

        self.store.set_last_updated("flow")
        return f"{total} records"
