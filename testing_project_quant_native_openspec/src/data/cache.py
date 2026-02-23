"""SQLite caching layer with incremental update support."""

import sqlite3
import pandas as pd
from pathlib import Path


class DataCache:
    """SQLite-based data cache for market data."""

    def __init__(self, db_path: str = "data/cache.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                code TEXT, date TEXT, open REAL, high REAL, low REAL,
                close REAL, volume REAL, amount REAL,
                PRIMARY KEY (code, date)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fundamentals (
                code TEXT, date TEXT, pb REAL, roe_ttm REAL,
                gross_margin REAL, ev_ebitda REAL,
                PRIMARY KEY (code, date)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metal_futures (
                metal TEXT, date TEXT, close REAL,
                PRIMARY KEY (metal, date)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macro_data (
                indicator TEXT, date TEXT, value REAL,
                PRIMARY KEY (indicator, date)
            )
        """)
        self.conn.commit()

    def get_latest_date(self, table: str, key_col: str, key_val: str) -> str | None:
        """Get the latest cached date for a given key."""
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT MAX(date) FROM {table} WHERE {key_col} = ?", (key_val,)
        )
        result = cursor.fetchone()
        return result[0] if result and result[0] else None

    def has_data(self, table: str, key_col: str, key_val: str,
                 start_date: str, end_date: str) -> bool:
        """Check if date range is fully covered in cache."""
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT MIN(date), MAX(date) FROM {table} WHERE {key_col} = ? AND date >= ? AND date <= ?",
            (key_val, start_date, end_date)
        )
        result = cursor.fetchone()
        if result and result[0] and result[1]:
            return result[0] <= start_date and result[1] >= end_date
        return False

    def get_stock_prices(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieve cached stock prices."""
        query = "SELECT * FROM stock_prices WHERE code = ? AND date >= ? AND date <= ? ORDER BY date"
        df = pd.read_sql_query(query, self.conn, params=(code, start_date, end_date))
        if len(df) > 0:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def save_stock_prices(self, code: str, df: pd.DataFrame):
        """Save stock prices to cache."""
        if df.empty:
            return
        df = df.copy()
        df["code"] = code
        df["date"] = df["date"].astype(str)
        df.to_sql("stock_prices", self.conn, if_exists="append", index=False,
                   method="multi")
        self.conn.commit()

    def get_metal_futures(self, metal: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieve cached metal futures."""
        query = "SELECT * FROM metal_futures WHERE metal = ? AND date >= ? AND date <= ? ORDER BY date"
        df = pd.read_sql_query(query, self.conn, params=(metal, start_date, end_date))
        if len(df) > 0:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def save_metal_futures(self, metal: str, df: pd.DataFrame):
        """Save metal futures to cache."""
        if df.empty:
            return
        df = df.copy()
        df["metal"] = metal
        df["date"] = df["date"].astype(str)
        df.to_sql("metal_futures", self.conn, if_exists="append", index=False,
                   method="multi")
        self.conn.commit()

    def save_macro_data(self, indicator: str, df: pd.DataFrame, value_col: str):
        """Save macro indicator data to cache."""
        if df.empty:
            return
        records = df.copy()
        records["indicator"] = indicator
        records["value"] = records[value_col]
        records["date"] = records["date"].astype(str)
        records[["indicator", "date", "value"]].to_sql(
            "macro_data", self.conn, if_exists="append", index=False, method="multi"
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
