"""Data quality validators for incoming market data."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation."""
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    dropped_rows: int = 0
    clean_df: pd.DataFrame = field(default_factory=pd.DataFrame)


def validate_stock_daily(df: pd.DataFrame) -> ValidationResult:
    """Validate stock daily OHLCV data.

    Checks: null values, price > 0, date continuity, duplicates.
    """
    result = ValidationResult()
    if df.empty:
        result.clean_df = df
        return result

    original_len = len(df)

    # Drop duplicates by date
    df = df.drop_duplicates(subset=["date"], keep="last")
    if len(df) < original_len:
        n_dupes = original_len - len(df)
        result.warnings.append(f"Removed {n_dupes} duplicate rows")
        result.dropped_rows += n_dupes

    # Check for null values in required columns
    required = ["date", "open", "high", "low", "close"]
    nulls = df[required].isnull().sum()
    if nulls.any():
        null_cols = nulls[nulls > 0].to_dict()
        result.warnings.append(f"Null values found: {null_cols}")
        df = df.dropna(subset=required)
        result.dropped_rows += nulls.max()

    # Check price ranges (must be > 0)
    price_cols = ["open", "high", "low", "close"]
    bad_prices = (df[price_cols] <= 0).any(axis=1)
    if bad_prices.any():
        n_bad = bad_prices.sum()
        result.warnings.append(f"Removed {n_bad} rows with non-positive prices")
        result.dropped_rows += n_bad
        df = df[~bad_prices]

    if result.dropped_rows > 0:
        result.passed = len(df) > 0

    result.clean_df = df.reset_index(drop=True)
    return result


def validate_futures_daily(df: pd.DataFrame) -> ValidationResult:
    """Validate futures daily data."""
    result = ValidationResult()
    if df.empty:
        result.clean_df = df
        return result

    # Drop duplicates
    df = df.drop_duplicates(subset=["date"], keep="last")

    # Check prices > 0
    price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
    if price_cols:
        bad = (df[price_cols] <= 0).any(axis=1)
        if bad.any():
            n_bad = bad.sum()
            result.warnings.append(f"Removed {n_bad} rows with non-positive prices")
            result.dropped_rows += n_bad
            df = df[~bad]

    result.clean_df = df.reset_index(drop=True)
    result.passed = len(df) > 0 or result.dropped_rows == 0
    return result


def validate_dataframe(df: pd.DataFrame, name: str = "data") -> ValidationResult:
    """Generic validation: check for empty, duplicates, nulls."""
    result = ValidationResult()
    if df.empty:
        result.warnings.append(f"{name}: empty DataFrame")
        result.clean_df = df
        return result

    original_len = len(df)
    df = df.drop_duplicates()
    if len(df) < original_len:
        result.warnings.append(f"{name}: removed {original_len - len(df)} duplicates")
        result.dropped_rows = original_len - len(df)

    result.clean_df = df.reset_index(drop=True)
    return result
