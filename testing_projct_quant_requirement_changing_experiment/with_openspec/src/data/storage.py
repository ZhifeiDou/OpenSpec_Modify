"""Local data storage layer — SQLite backend with incremental update tracking."""
from __future__ import annotations

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

# Table schemas for SQLite initialization
_TABLE_SCHEMAS = {
    "stock_daily": """
        CREATE TABLE IF NOT EXISTS stock_daily (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL, high REAL, low REAL, close REAL,
            volume REAL, amount REAL,
            PRIMARY KEY (symbol, date)
        )
    """,
    "financials": """
        CREATE TABLE IF NOT EXISTS financials (
            symbol TEXT NOT NULL,
            report_date TEXT NOT NULL,
            pb REAL, roe_ttm REAL, gross_margin REAL,
            ev REAL, ebitda REAL,
            total_revenue REAL, net_profit REAL,
            total_assets REAL, total_liabilities REAL,
            PRIMARY KEY (symbol, report_date)
        )
    """,
    "futures_daily": """
        CREATE TABLE IF NOT EXISTS futures_daily (
            metal TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL, high REAL, low REAL, close REAL,
            settle REAL, volume REAL, open_interest REAL,
            PRIMARY KEY (metal, date)
        )
    """,
    "inventory": """
        CREATE TABLE IF NOT EXISTS inventory (
            metal TEXT NOT NULL,
            date TEXT NOT NULL,
            inventory REAL,
            PRIMARY KEY (metal, date)
        )
    """,
    "macro": """
        CREATE TABLE IF NOT EXISTS macro (
            indicator TEXT NOT NULL,
            date TEXT NOT NULL,
            value REAL,
            PRIMARY KEY (indicator, date)
        )
    """,
    "fund_flow": """
        CREATE TABLE IF NOT EXISTS fund_flow (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            margin_balance REAL,
            northbound_net_buy REAL,
            northbound_holding REAL,
            PRIMARY KEY (symbol, date)
        )
    """,
    "meta": """
        CREATE TABLE IF NOT EXISTS meta (
            category TEXT PRIMARY KEY,
            last_updated TEXT
        )
    """,
}


class DataStore:
    """SQLite-based local storage with incremental update tracking."""

    def __init__(self, db_path: str = "data/quant.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        with self._get_conn() as conn:
            for schema in _TABLE_SCHEMAS.values():
                conn.execute(schema)

    def get_last_updated(self, category: str) -> str | None:
        """Get the last update timestamp for a data category."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT last_updated FROM meta WHERE category = ?", (category,)
            ).fetchone()
        return row[0] if row else None

    def set_last_updated(self, category: str, timestamp: str | None = None):
        """Update the last-updated timestamp for a data category."""
        ts = timestamp or datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (category, last_updated) VALUES (?, ?)",
                (category, ts),
            )

    def save_dataframe(self, table: str, df: pd.DataFrame, if_exists: str = "append"):
        """Write a DataFrame to a table, deduplicating by primary key."""
        if df.empty:
            return
        with self._get_conn() as conn:
            df.to_sql(f"_{table}_staging", conn, if_exists="replace", index=False)
            # Upsert from staging into main table
            cols = ", ".join(df.columns)
            conn.execute(f"INSERT OR REPLACE INTO {table} ({cols}) SELECT {cols} FROM _{table}_staging")
            conn.execute(f"DROP TABLE IF EXISTS _{table}_staging")

    def read_table(
        self, table: str, where: str | None = None, params: tuple = ()
    ) -> pd.DataFrame:
        """Read data from a table with optional WHERE clause."""
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        with self._get_conn() as conn:
            return pd.read_sql(query, conn, params=params)

    def read_stock_daily(
        self, symbol: str, start_date: str | None = None, end_date: str | None = None
    ) -> pd.DataFrame:
        """Read stock daily data for a symbol within a date range."""
        conditions = ["symbol = ?"]
        params: list = [symbol]
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        where = " AND ".join(conditions)
        df = self.read_table("stock_daily", where=where, params=tuple(params))
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
        return df

    def read_futures_daily(
        self, metal: str, start_date: str | None = None, end_date: str | None = None
    ) -> pd.DataFrame:
        """Read futures daily data for a metal."""
        conditions = ["metal = ?"]
        params: list = [metal]
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        where = " AND ".join(conditions)
        df = self.read_table("futures_daily", where=where, params=tuple(params))
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
        return df

    def clear_table(self, table: str):
        """Delete all rows from a table (for force-refresh)."""
        with self._get_conn() as conn:
            conn.execute(f"DELETE FROM {table}")
        logger.info("Cleared table: %s", table)
